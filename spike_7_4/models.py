from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Tabla intermedia Muchos-a-Muchos
pedido_producto_table = Table(
    "pedido_producto",
    Base.metadata,
    Column("pedido_id", Integer, ForeignKey("pedidos.id"), primary_key=True),
    Column("producto_id", Integer, ForeignKey("productos.id"), primary_key=True)
)

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    # Relación Uno-a-Muchos
    pedidos = relationship("Pedido", back_populates="usuario")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    total = Column(Float, default=0.0)
    
    usuario = relationship("Usuario", back_populates="pedidos")
    # Relación Muchos-a-Muchos
    productos = relationship("Producto", secondary=pedido_producto_table)

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    precio = Column(Float, nullable=False)
