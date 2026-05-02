import sys
import os

# Añadir el directorio actual al path para poder importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from infra.db.database import SessionLocal, engine, Base
from infra.db.models.usuarios import Rol, Usuario, PerfilUsuario
from core.security.security import encriptar_password

def seed():
    db = SessionLocal()
    try:
        print("[SEED] Iniciando insercion de datos base...")

        # 1. Crear Roles si no existen
        roles_nombres = ["cliente", "administrador", "cocinero"]
        roles_db = {}
        
        for nombre in roles_nombres:
            rol = db.query(Rol).filter(Rol.nombre == nombre).first()
            if not rol:
                rol = Rol(nombre=nombre)
                db.add(rol)
                db.commit()
                db.refresh(rol)
                print(f"[SEED] Rol '{nombre}' creado.")
            roles_db[nombre] = rol

        # 2. Crear Administrador por defecto si no existe
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
            print(f"[SEED] Usuario Administrador creado: {admin_email} / admin123")

            # Crear perfil para el admin
            admin_perfil = PerfilUsuario(
                id_usuario=admin_user.id,
                es_temporal=False,
                alergias="",
                preferencias="",
                observaciones_ia="Administrador del sistema"
            )
            db.add(admin_perfil)
            db.commit()
            print("[SEED] Perfil de Administrador creado.")
        else:
            print("[SEED] El usuario administrador ya existe.")

        print("[SEED] Datos base insertados correctamente.")

    except Exception as e:
        print(f"[SEED] Error durante el seed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Asegurarse de que las tablas existan
    Base.metadata.create_all(bind=engine)
    seed()
