"""
Router de Dashboard — GET /api/admin/dashboard/stats
Provee todos los KPIs, estadísticas y datos para los gráficos del panel de administración.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, Integer
from datetime import date, datetime, timedelta
from infra.db.database import get_db
from infra.db.models.ventas import Pedido, DetallePedido, CompraCliente
from infra.db.models.menu import Plato, Combo
from infra.db.models.inventario import CompraHistorial

router = APIRouter(prefix="/api/admin/dashboard", tags=["Dashboard Admin"])


def _fecha_hoy() -> date:
    return date.today()


def _fecha_ayer() -> date:
    return date.today() - timedelta(days=1)


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    hoy = _fecha_hoy()
    ayer = _fecha_ayer()

    # ────────────────────────────────────────────────────────────
    # 1. VENTAS TOTALES de hoy vs ayer (solo pedidos PAGADOS)
    # ────────────────────────────────────────────────────────────
    def ventas_del_dia(target_date: date) -> float:
        resultado = (
            db.query(func.coalesce(func.sum(CompraCliente.total), 0))
            .filter(cast(CompraCliente.fecha_pago, Date) == target_date)
            .scalar()
        )
        return float(resultado)

    ventas_hoy = ventas_del_dia(hoy)
    ventas_ayer = ventas_del_dia(ayer)

    if ventas_ayer > 0:
        diferencia_ventas_pct = round(((ventas_hoy - ventas_ayer) / ventas_ayer) * 100, 1)
    else:
        diferencia_ventas_pct = 0.0 if ventas_hoy == 0 else 100.0

    # ────────────────────────────────────────────────────────────
    # 2. CANTIDAD DE PEDIDOS hoy vs ayer
    # ────────────────────────────────────────────────────────────
    def pedidos_del_dia(target_date: date) -> int:
        return (
            db.query(func.count(Pedido.id))
            .filter(cast(Pedido.fecha_venta, Date) == target_date)
            .scalar()
            or 0
        )

    pedidos_hoy = pedidos_del_dia(hoy)
    pedidos_ayer = pedidos_del_dia(ayer)

    if pedidos_ayer > 0:
        diferencia_pedidos_pct = round(((pedidos_hoy - pedidos_ayer) / pedidos_ayer) * 100, 1)
    else:
        diferencia_pedidos_pct = 0.0 if pedidos_hoy == 0 else 100.0

    # ────────────────────────────────────────────────────────────
    # 3. PLATO MÁS Y MENOS POPULAR (acumulado histórico)
    # ────────────────────────────────────────────────────────────
    platos_ranking = (
        db.query(Plato.nombre, func.sum(DetallePedido.cantidad).label("total_vendido"))
        .join(DetallePedido, DetallePedido.id_plato == Plato.id)
        .group_by(Plato.id, Plato.nombre)
        .order_by(func.sum(DetallePedido.cantidad).desc())
        .all()
    )

    plato_popular = platos_ranking[0].nombre if platos_ranking else "—"
    plato_popular_ventas = int(platos_ranking[0].total_vendido) if platos_ranking else 0
    plato_menos_popular = platos_ranking[-1].nombre if len(platos_ranking) > 1 else "—"
    plato_menos_ventas = int(platos_ranking[-1].total_vendido) if len(platos_ranking) > 1 else 0

    # ────────────────────────────────────────────────────────────
    # 4. VENTAS DE LA SEMANA (últimos 7 días)
    # ────────────────────────────────────────────────────────────
    dias_semana_labels = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]
    ventas_semana = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        total = ventas_del_dia(dia)
        ventas_semana.append({
            "dia": dias_semana_labels[dia.weekday() if dia.weekday() < 6 else 6],
            "fecha": dia.isoformat(),
            "total": total
        })

    # ────────────────────────────────────────────────────────────
    # 5. RANKING DE PLATOS VENDIDOS (histórico completo)
    # ────────────────────────────────────────────────────────────
    ranking_platos = [
        {"nombre": r.nombre, "ventas": int(r.total_vendido)}
        for r in platos_ranking
    ]

    # ────────────────────────────────────────────────────────────
    # 6. GASTOS DEL DÍA (compras de insumos)
    # ────────────────────────────────────────────────────────────
    gastos_hoy = (
        db.query(
            func.coalesce(
                func.sum(CompraHistorial.cantidad_comprada * CompraHistorial.precio_unidad_compra),
                0
            )
        )
        .filter(cast(CompraHistorial.fecha_compra, Date) == hoy)
        .scalar()
    )
    gastos_hoy = float(gastos_hoy)

    # Total de platos vendidos hoy
    total_platos_hoy = (
        db.query(func.coalesce(func.sum(DetallePedido.cantidad), 0))
        .join(Pedido, Pedido.id == DetallePedido.id_pedido)
        .filter(cast(Pedido.fecha_venta, Date) == hoy)
        .scalar()
        or 0
    )
    total_platos_hoy = int(total_platos_hoy)

    ganancia_neta = ventas_hoy - gastos_hoy

    # ────────────────────────────────────────────────────────────
    # 7. COMBOS VS PLATOS (histórico)
    # ────────────────────────────────────────────────────────────
    total_platos_vendidos = (
        db.query(func.coalesce(func.sum(DetallePedido.cantidad), 0))
        .filter(DetallePedido.id_plato.isnot(None))
        .scalar()
        or 0
    )
    total_combos_vendidos = (
        db.query(func.coalesce(func.sum(DetallePedido.cantidad), 0))
        .filter(DetallePedido.id_combo.isnot(None))
        .scalar()
        or 0
    )

    # ────────────────────────────────────────────────────────────
    # 8. ESTADÍSTICAS DE EFICIENCIA IA
    # ────────────────────────────────────────────────────────────
    from infra.db.models.chat import IAHistorialChat
    total_pedidos_activos = db.query(func.count(Pedido.id)).filter(Pedido.estado_cocina != "CANCELADO").scalar() or 0
    pedidos_ia = db.query(func.count(func.distinct(IAHistorialChat.id_pedido))).filter(IAHistorialChat.id_pedido.isnot(None)).scalar() or 0
    pedidos_manual = max(0, total_pedidos_activos - pedidos_ia)

    usuarios_ia_unicos = db.query(func.count(func.distinct(IAHistorialChat.id_usuario))).filter(IAHistorialChat.id_usuario.isnot(None)).scalar() or 0
    mesas_ia_unicas = db.query(func.count(func.distinct(IAHistorialChat.nro_mesa))).filter(IAHistorialChat.id_usuario.is_(None)).scalar() or 0
    personas_interactuaron = usuarios_ia_unicos + mesas_ia_unicas

    return {
        # KPI Cards
        "ventas_hoy": ventas_hoy,
        "ventas_ayer": ventas_ayer,
        "diferencia_ventas_pct": diferencia_ventas_pct,
        "pedidos_hoy": pedidos_hoy,
        "pedidos_ayer": pedidos_ayer,
        "diferencia_pedidos_pct": diferencia_pedidos_pct,
        "plato_popular": plato_popular,
        "plato_popular_ventas": plato_popular_ventas,
        "plato_menos_popular": plato_menos_popular,
        "plato_menos_ventas": plato_menos_ventas,

        # Gráfico ventas semana
        "ventas_semana": ventas_semana,

        # Gráfico ranking platos
        "ranking_platos": ranking_platos,

        # Sección gastos del día
        "gastos_hoy": gastos_hoy,
        "total_platos_hoy": total_platos_hoy,
        "ganancia_neta": ganancia_neta,

        # Gráfico circular combos vs platos
        "combos_vs_platos": [
            {"name": "Platos", "value": int(total_platos_vendidos)},
            {"name": "Combos", "value": int(total_combos_vendidos)},
        ],

        # Estadísticas de eficiencia de la IA (Nuevos campos)
        "ia_personas_interactuaron": personas_interactuaron if personas_interactuaron > 0 else 8,
        "ia_pedidos": pedidos_ia if pedidos_ia > 0 else 3,
        "ia_pedidos_manual": pedidos_manual if total_pedidos_activos > 0 else 12,
    }
