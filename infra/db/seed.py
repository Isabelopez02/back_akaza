from sqlalchemy.orm import Session
from infra.db.database import SessionLocal
from infra.db.models.usuarios import Rol, Usuario, PerfilUsuario
from core.security.security import encriptar_password

def seed():
    db = SessionLocal()
    try:
        # Verificar si ya existen roles en la base de datos para no duplicar datos
        if db.query(Rol).first() is not None:
            return

        roles_nombres = ["cliente", "administrador", "cocinero"]
        roles_db = {}
        
        for nombre in roles_nombres:
            rol = db.query(Rol).filter(Rol.nombre == nombre).first()
            if not rol:
                rol = Rol(nombre=nombre)
                db.add(rol)
                db.commit()
                db.refresh(rol)
            roles_db[nombre] = rol

        # Crear administrador por defecto si no existe
        admin_email = "admin@akaza.com"
        admin_user = db.query(Usuario).filter(Usuario.correo == admin_email).first()
        if not admin_user:
            admin_user = Usuario(
                nombre="Administrador Akaza",
                correo=admin_email,
                contrasenia=encriptar_password("admin123"),
                id_rol=roles_db["administrador"].id
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Crear perfil para el administrador
            admin_perfil = PerfilUsuario(
                id_usuario=admin_user.id,
                es_temporal=False,
                alergias="",
                preferencias="",
                observaciones_ia="Administrador del sistema"
            )
            db.add(admin_perfil)
            db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
