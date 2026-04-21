from sqlalchemy.orm import Session
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