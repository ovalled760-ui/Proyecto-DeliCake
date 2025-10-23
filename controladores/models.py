from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class Usuario(db.Model, UserMixin):
    __tablename__ = "Usuario"
    ID_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100), nullable=False)
    Apellido = db.Column(db.String(100), nullable=False)
    Correo = db.Column(db.String(100), unique=True, nullable=False)
    Contraseña = db.Column(db.String(255), nullable=False)

    # Relaciones
    cliente = db.relationship("Cliente", back_populates="usuario", uselist=False)
    administrador = db.relationship("Administrador", back_populates="usuario", uselist=False)

    # 👇 Relación uno-a-muchos con Notificacion
    notificaciones = db.relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")

    def get_id(self):
        return str(self.ID_usuario)



class Cliente(db.Model):
    __tablename__ = "Cliente"
    ID_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Direccion = db.Column(db.String(200)) 
    Telefono = db.Column(db.String(20))
    ID_usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_usuario"))

    usuario = db.relationship("Usuario", back_populates="cliente")
    pedidos = db.relationship("Pedido", back_populates="cliente")
    personalizaciones = db.relationship("PersonalizacionProducto", back_populates="cliente")
    detalles_pedido = db.relationship("DetallePedido", back_populates="cliente")



class Administrador(db.Model):
    __tablename__ = "Administrador"
    ID_admin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Rol = db.Column(db.String(50))
    ID_usuario = db.Column(db.Integer, db.ForeignKey("Usuario.ID_usuario"))
    Clave_validacion = db.Column(db.Integer)

    usuario = db.relationship("Usuario", back_populates="administrador")
    productos = db.relationship("Producto", back_populates="administrador")



class Producto(db.Model):
    __tablename__ = 'Producto'
    ID_Producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_producto = db.Column(db.String(255))
    Descripcion_producto = db.Column(db.Text)
    Precio_Unitario = db.Column(db.Numeric(10, 2))
    Unidades_disponibles = db.Column(db.Integer)
    Fecha_Disponibilidad = db.Column(db.Date)
    ID_Administrador = db.Column(db.Integer, db.ForeignKey('Administrador.ID_admin'))
    Imagen = db.Column(db.String(255))
    Descuento = db.Column(db.Numeric(5,2),default=0.00)
    ID_Categoria = db.Column(db.Integer, db.ForeignKey('Categoria.ID_Categoria'),nullable=False)
    administrador = db.relationship("Administrador", back_populates="productos")
    personalizaciones = db.relationship("PersonalizacionProducto", back_populates="producto")
    detalles_pedido = db.relationship("DetallePedido", back_populates="producto")
    detalles= db.relationship('DetalleProducto', back_populates='producto', cascade='all, delete-orphan')
    calificaciones = db.relationship("Calificacion", back_populates="producto")
  
  
class PersonalizacionProducto(db.Model):
    __tablename__ = "Personalizacion_Producto"
    ID_Personalizacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Masa = db.Column(db.Enum('batida', 'azucarada', 'fermentadas'), default='batida')
    Relleno = db.Column(db.Enum('vainilla', 'dulce de leche', 'nueces', 'crema de limon'))
    Cobertura = db.Column(db.Enum('chocolate', 'maracuya', 'vainilla', 'fresa', 'melocoton'))
    Porciones = db.Column(db.Enum('1 porcion', '2 porciones', '1/2', 'entero', '3 a 5 porciones'))
    Adicionales = db.Column(db.Enum('chantilly', 'leche condensada', 'arequipe ', 'chocolate', 'fresa'))

    ID_Producto = db.Column(db.Integer, db.ForeignKey("Producto.ID_Producto"))
    ID_Cliente = db.Column(db.Integer, db.ForeignKey("Cliente.ID_cliente"))

    producto = db.relationship("Producto", back_populates="personalizaciones")
    cliente = db.relationship("Cliente", back_populates="personalizaciones")
    detalles_pedido = db.relationship("DetallePedido", back_populates="personalizacion")



class Pedido(db.Model):
    __tablename__ = "Pedido"
    ID_Pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha_Solicitud = db.Column(db.Date)
    Fecha_Entrega = db.Column(db.Date)
    Tiempo_Realizacion = db.Column(db.String(50))
    Estado_Pedido = db.Column(db.Enum('Pendiente', 'En proceso', 'Enviado', 'Entregado', 'Cancelado'))
    Total = db.Column(db.Numeric(10, 2))

    ID_Cliente = db.Column(db.Integer, db.ForeignKey("Cliente.ID_cliente"), nullable=False)

    cliente = db.relationship("Cliente", back_populates="pedidos")
    detalles_pedido = db.relationship("DetallePedido", back_populates="pedido")



class DetallePedido(db.Model):
    __tablename__ = "Detalle_Pedido"
    ID_detalle_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(29))
    Cantidad_unidades_producto = db.Column(db.Integer)
    Nombre_producto = db.Column(db.String(300))
    Fecha_Solicitud = db.Column(db.Date)
    Fecha_Entrega = db.Column(db.Date)
    Tiempo_Realizacion = db.Column(db.String(50))
    Descuento = db.Column(db.String(100))
    Masa = db.Column(db.Enum('batida', 'azucarada', 'fermentadas'), default='batida')
    Relleno = db.Column(db.Enum('vainilla', 'dulce de leche', 'nueces', 'crema de limon'))
    Cobertura = db.Column(db.Enum('chocolate', 'maracuya', 'vainilla', 'fresa', 'melocoton'))
    Porciones = db.Column(db.Enum('1 porcion', '2 porciones', '1/2', 'entero', '3 a 5 porciones'))
    Adicionales = db.Column(db.Enum('chantilly', 'leche condensada', 'arequipe ', 'chocolate', 'fresa'))
    Precio_Unitario = db.Column(db.Numeric(10, 2))
    IVA = db.Column(db.Integer)
    Total = db.Column(db.Numeric(10, 2))
    Estado_pedido = db.Column(db.Enum('Pendiente', 'En proceso', 'Enviado', 'Entregado', 'Cancelado'))

    ID_pedido = db.Column(db.Integer, db.ForeignKey("Pedido.ID_Pedido"))
    ID_producto = db.Column(db.Integer, db.ForeignKey("Producto.ID_Producto"))
    ID_Cliente = db.Column(db.Integer, db.ForeignKey("Cliente.ID_cliente"))
    ID_Personalizacion = db.Column(db.Integer, db.ForeignKey("Personalizacion_Producto.ID_Personalizacion"))

    pedido = db.relationship("Pedido", back_populates="detalles_pedido")
    producto = db.relationship("Producto", back_populates="detalles_pedido")
    cliente = db.relationship("Cliente", back_populates="detalles_pedido")
    personalizacion = db.relationship("PersonalizacionProducto", back_populates="detalles_pedido")
    pagos = db.relationship("Pago", back_populates="detalle_pedido")




class Categoria(db.Model):
    __tablename__ = 'Categoria'
    ID_Categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_categoria = db.Column(db.String(20))
    Nombre_producto = db.Column(db.String(40))
    Estado = db.Column(db.Enum('Activa', 'Inactiva'))
    
    productos=db.relationship('Producto', backref = 'Categoria', lazy =True)


class DetalleProducto(db.Model):
    __tablename__ = 'Detalle_Producto'
    ID_detalle_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Ingredientes = db.Column(db.String(70))
    tiempo_preparacion = db.Column(db.String(50))
    ID_producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto', ondelete= 'CASCADE'), nullable=False)
    producto=db.relationship('Producto', back_populates='detalles')


class Pago(db.Model):
    __tablename__ = "Pago"
    ID_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Monto = db.Column(db.Numeric(10, 2))
    Metodo_Pago = db.Column(db.Enum('Nequi', 'Daviplata', 'Tarjeta'))
    fecha_pago = db.Column(db.Date)
    URL_Comprobante = db.Column(db.String(300))

    ID_Detalle_Pedido = db.Column(db.Integer, db.ForeignKey("Detalle_Pedido.ID_detalle_pedido"))
    detalle_pedido = db.relationship("DetallePedido", back_populates="pagos")


class Disponibilidad(db.Model):
    __tablename__ = "Disponibilidad"
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha = db.Column(db.Date, nullable=False)
    Hora = db.Column(db.Time, nullable=False)



class Calificacion(db.Model):
    __tablename__ = "Calificacion"
    ID_Calificacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ID_Producto = db.Column(db.Integer, db.ForeignKey("Producto.ID_Producto"), nullable=False)
    Valor = db.Column(db.Integer, nullable=False)
    producto = db.relationship("Producto", back_populates="calificaciones")

class Reseña(db.Model):
    __tablename__ = "reseña"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo = db.Column(db.String(100), nullable=False)
    estrellas = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default="pendiente") 
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    ID_usuario= db.Column(db.Integer, db.ForeignKey("Usuario.ID_usuario", ondelete= 'CASCADE'), nullable=False)

class Suscriptor(db.Model):
    __tablename__="suscriptor"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    correo = db.Column(db.String(120), unique=True, nullable=False)

class Notificacion(db.Model):
    __tablename__ = "Notificacion"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("Usuario.ID_usuario"), nullable=False)

    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.now())
    leida = db.Column(db.Boolean, default=False)

    # Relación inversa
    usuario = db.relationship("Usuario", back_populates="notificaciones")

class Favorito(db.Model):
    __tablename__ = "favoritos"

    id_favorito = db.Column(db.Integer, primary_key=True)
    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'), nullable=False)
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'), nullable=False)

    usuario = db.relationship('Usuario', backref='favoritos', lazy=True)
    producto = db.relationship('Producto', backref='favoritos', lazy=True)
