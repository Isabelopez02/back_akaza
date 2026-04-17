-- ==========================================================
-- 1. SEGURIDAD, ROLES Y PERFILES (OPTIMIZADO PARA DJANGO)
-- ==========================================================

-- Tabla de Roles (Puedes mantenerla o usar los "Groups" nativos de Django)
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL -- 'ADMIN', 'COCINERO', 'CAJERO', 'CLIENTE'
);

-- Tabla Base de Usuario (En Django, esta suele ser su tabla nativa 'auth_user')
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    contrasenia VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modificado_en TIMESTAMP
);

-- ¡AQUÍ ESTÁ LA MAGIA! UNA SOLA TABLA DE PERFIL UNIFICADA
CREATE TABLE perfil_usuario (
    id_usuario INT PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    id_rol INT REFERENCES roles(id),
    es_temporal BOOLEAN DEFAULT FALSE,     -- TRUE para escaneo de QR en mesa
    id_mesa_actual INT NULL,               -- Contexto de qué mesa atiende la IA
    alergias TEXT,                         -- Ej: 'Mariscos, Lactosa'
    preferencias TEXT,                     -- Ej: 'Bajo en sal, Vegano'
    observaciones_ia TEXT                  -- Notas que la IA guarda para el futuro
);

-- ==========================================================
-- 2. INVENTARIO Y GESTIÓN DE COSTOS (LOGÍSTICA)
-- ==========================================================
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad_medida VARCHAR(20), -- 'KG', 'UNI', 'L', 'GR'
    stock_actual DECIMAL(10,2) DEFAULT 0,
    stock_minimo_alerta DECIMAL(10,2)
);

-- Dato de Ingeniería: Historial para no perder precios antiguos
CREATE TABLE compras_historial (
    id SERIAL PRIMARY KEY,
    id_producto INT REFERENCES productos(id),
    cantidad_comprada DECIMAL(10,2),
    precio_unidad_compra DECIMAL(10,2),
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rango de mermas para el cálculo de "estimación" al final del día
CREATE TABLE mermas_estimadas (
    id_producto INT PRIMARY KEY REFERENCES productos(id),
    merma_min_porcentaje DECIMAL(5,2), -- Ej: 0.10 (10%)
    merma_max_porcentaje DECIMAL(5,2)  -- Ej: 0.20 (20%)
);

-- ==========================================================
-- 3. MENÚ, RECETAS Y COMBOS (OFICINA TÉCNICA)
-- ==========================================================
CREATE TABLE platos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_venta DECIMAL(10,2)
);

CREATE TABLE recetas (
    id SERIAL PRIMARY KEY,
    id_plato INT REFERENCES platos(id),
    id_producto INT REFERENCES productos(id),
    cantidad_estimada DECIMAL(10,2),
    unidad_medida VARCHAR(20), 
    es_opcional BOOLEAN DEFAULT FALSE -- La IA lo usa para saber si puede quitarlo
);

CREATE TABLE combos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    precio_venta DECIMAL(10,2),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE combo_platos (
    id_combo INT REFERENCES combos(id) ON DELETE CASCADE,
    id_plato INT REFERENCES platos(id) ON DELETE CASCADE,
    PRIMARY KEY (id_combo, id_plato)
);

-- Reglas para que la IA sepa qué puede cambiar
CREATE TABLE sustituciones_permitidas (
    id SERIAL PRIMARY KEY,
    id_producto_original INT REFERENCES productos(id),
    id_producto_nuevo INT REFERENCES productos(id),
    costo_adicional DECIMAL(10,2) DEFAULT 0.00
);

-- ==========================================================
-- 4. VENTAS, PEDIDOS Y CIERRE (OPERACIÓN)
-- ==========================================================
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id), -- Usuario temporal o logueado
    nro_mesa INT,
    estado_cocina VARCHAR(50) DEFAULT 'ESPERA', -- 'ESPERA', 'COCINANDO', 'LISTO'
    estado_pago VARCHAR(50) DEFAULT 'PENDIENTE', -- 'PENDIENTE', 'PAGADO'
    total DECIMAL(10,2),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detalle_pedido (
    id SERIAL PRIMARY KEY,
    id_pedido INT REFERENCES pedidos(id),
    id_plato INT REFERENCES platos(id) NULL,
    id_combo INT REFERENCES combos(id) NULL,
    cantidad INT DEFAULT 1,
    nota_personalizacion TEXT, -- Ej: 'Sin ají', 'Ceviche con Lenguado'
    id_prod_quitado INT REFERENCES productos(id) NULL, -- Insumo que no se usó
    id_prod_sustituto INT REFERENCES productos(id) NULL -- Insumo que reemplazó al original
);

CREATE TABLE venta_dia_resumen (
    id SERIAL PRIMARY KEY,
    fecha DATE UNIQUE DEFAULT CURRENT_DATE,
    total_recaudado DECIMAL(10,2),
    total_platos_vendidos INT,
    merma_total_estimada_gr DECIMAL(10,2) -- Cálculo post-cierre
);

-- ¡NUEVA! TABLA PARA LA MEMORIA DE LA IA
CREATE TABLE ia_historial_chat (
    id SERIAL PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id) ON DELETE CASCADE, -- ¡Agregado!
    id_pedido INT REFERENCES pedidos(id) ON DELETE SET NULL, -- ¡Agregado!
    mensaje_cliente TEXT NOT NULL,
    respuesta_ia TEXT NOT NULL,
    contexto_enviado JSONB, 
    fecha_interaccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);