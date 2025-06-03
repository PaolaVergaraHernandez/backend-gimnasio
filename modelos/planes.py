
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text # Importa Numeric
from database import Base 


class Plan(Base):
    __tablename__ = "planes" 

    id_plan = Column(Integer, primary_key=True, index=True) # PK
    nombre = Column(String(255), index=True)
    descripcion = Column(Text, nullable=True) # Text para descripciones, nullable si puede ser NULL
    precio = Column(Numeric(10, 2)) # Numeric para precios
    duracion_dias = Column(Integer) # Asumo que es un entero simple
    fecha_alta = Column(DateTime, nullable=True) # Mapea a DATETIME/TIMESTAMP

    def __repr__(self):
        return f"<Plan(id={self.id_plan}, nombre='{self.nombre}', descripcion='{self.descripcion}', fecha_alta='{self.fecha_alta}', duracion_dias={self.duracion_dias}), precio={self.precio})>"

    