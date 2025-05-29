
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text 
from database import Base 


class Producto(Base):
    __tablename__ = "productos" 
    
    id_producto = Column(Integer, primary_key=True, index=True) # PK
    nombre = Column(String(255), index=True)
    descripcion = Column(Text, nullable=True) # Text para descripciones, nullable si puede ser NULL
    precio = Column(Numeric(10, 2)) # Numeric para precios con precision decimal (10 digitos en total, 2 decimales)
    stock = Column(Integer)
    fecha_alta = Column(DateTime, nullable=True) # Mapea a DATETIME/TIMESTAMP


    def __repr__(self):
        return f"<Producto(id={self.id_producto}, nombre='{self.nombre}', descripcion='{self.descripcion}', stock='{self.stock}', precio={self.precio})>"

  