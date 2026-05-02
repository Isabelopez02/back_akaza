from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from infra.db.database import Base


class Rol(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    correo = Column(String(100), unique=True)
    contrasenia = Column(String(255))
    id_rol = Column(Integer, ForeignKey("roles.id")) # Movido desde PerfilUsuario
    creado_en = Column(TIMESTAMP, default=datetime.utcnow)
    modificado_en = Column(TIMESTAMP)

    perfil = relationship("PerfilUsuario", back_populates="usuario", uselist=False)
    rol = relationship("Rol") # Relación directa con el rol


class PerfilUsuario(Base):
    __tablename__ = "perfil_usuario"

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    # id_rol eliminado de aquí
    es_temporal = Column(Boolean, default=False)
    id_mesa_actual = Column(Integer, nullable=True)
    alergias = Column(Text)
    preferencias = Column(Text)
    observaciones_ia = Column(Text)

    usuario = relationship("Usuario", back_populates="perfil")