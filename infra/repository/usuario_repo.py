from sqlalchemy.orm import Session

from core.schemas.usuario_schema import UsuarioCreate, PerfilUsuarioCreate
from infra.db.models import Rol, Usuario, PerfilUsuario
class UsuarioRepository:
  def __init__(self, db: Session):
    self.db = db

  # ==========================================
  # 1. GESTIÓN DE ROLES
  # ==========================================
  def obtener_rol_por_nombre(self, nombre_rol:str):
    return self.db.query(Rol).filter(Rol.nombre.ilike(nombre_rol)).first()

  def crear_usuario(self, usuarioData: UsuarioCreate ):
    nuevo_usuario = Usuario (
      nombre = usuarioData.nombre,
      correo = usuarioData.correo,
      contrasenia = usuarioData.contrasenia
    )

    self.db.add(nuevo_usuario)
    self.db.commit()
    self.db.refresh(nuevo_usuario)

    return nuevo_usuario

  # ==========================================
  # 2. CREACIÓN DEL USUARIO COMPLETO
  # ==========================================

  def creacion_de_perfil_usuario(self, perfil_Data: PerfilUsuarioCreate, id_rol_encontrado: int,
                                 id_usuario_existente: int):
    nuevo_perfil = PerfilUsuario(
      id_usuario = id_usuario_existente,
      id_rol = id_rol_encontrado,
      es_temporal = perfil_Data.es_temporal,
      alergias = perfil_Data.alergias,
      preferencias = perfil_Data.preferencias,
      observaciones_ia = perfil_Data.observaciones_ia
    )

    self.db.add(nuevo_perfil)
    self.db.commit()
    return nuevo_perfil

  def actualizar_perfil_usuario(self, id_usuario: int, datos_perfil: PerfilUsuarioCreate):
    perfil = self.db.query(PerfilUsuario).filter(PerfilUsuario.id_usuario == id_usuario).first()

    if perfil:
      perfil.alergias = datos_perfil.alergias
      perfil.preferencias = datos_perfil.preferencias
      # No actualizamos es_temporal ni id_rol aquí por seguridad
      self.db.commit()
      self.db.refresh(perfil)
      return perfil
    return None