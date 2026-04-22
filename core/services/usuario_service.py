from sqlalchemy.orm import Session

from core.security.security import encriptar_password
from infra.db.models import Usuario, PerfilUsuario


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db

    def obtener_perfil(self, id_usuario: int):
        return self.db.query(PerfilUsuario).filter_by(id_usuario=id_usuario).first()

    def actualizar_preferencias(self, id_usuario: int, alergias: str, preferencias: str):
        perfil = self.obtener_perfil(id_usuario)
        if not perfil:
            raise Exception("Perfil no encontrado")

        perfil.alergias = alergias
        perfil.preferencias = preferencias
        self.db.commit()
        self.db.refresh(perfil)
        return perfil

    def registrar_usuario(self, data):
        # Encriptamos antes de guardar
        clave_segura = encriptar_password(data.contrasenia)

        nuevo_usuario = Usuario(
            nombre=data.nombre,
            correo=data.correo,
            contrasenia=clave_segura  # Guardamos la versión encriptada ($2b$12...)
        )
        try:
            self.db.add(nuevo_usuario)
            self.db.commit()
            self.db.refresh(nuevo_usuario)
            return nuevo_usuario
        except Exception:
            self.db.rollback()
            raise