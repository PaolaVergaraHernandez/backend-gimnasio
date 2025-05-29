
from sqlalchemy import Column, Integer, String, ForeignKey, Time, DateTime, Text

from database import Base


class Clase(Base):
    __tablename__ = "clases" 

    id_clase = Column(Integer, primary_key=True, index=True) 

    nombre = Column(String(255)) 
    descripcion = Column(Text, nullable=True) 
    instructor = Column(String(255)) 

    horario = Column(Time, nullable=True) 
    duracion = Column(Integer) 
    cupo_maximo = Column(Integer) 
    fecha_alta = Column(DateTime, nullable=True) 

    def __repr__(self):

        return f"<Clase(id={self.id_clase}, nombre='{self.nombre}', instructor='{self.instructor}', horario='{self.horario}', duracion={self.duracion}, cupo_maximo={self.cupo_maximo})>"

