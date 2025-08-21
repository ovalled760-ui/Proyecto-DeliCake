from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'Usuario'
    ID_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(100))
    Apellido = db.Column(db.String(100))
    Correo = db.Column(db.String(100), unique=True, nullable=False)
    Contraseña = db.Column(db.String(255), nullable=False)

    clientes = db.relationship('Cliente', backref='usuario', lazy=True)
    administradores = db.relationship('Administrador', backref='usuario', lazy=True)

    def get_id(self):
        return str(self.ID_usuario)


class Cliente(db.Model):
    __tablename__ = 'Cliente'
    ID_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(29))
    Direccion = db.Column(db.String(200))
    Telefono = db.Column(db.String(20))
    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'))

    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)


class Administrador(db.Model):
    __tablename__ = 'Administrador'
    ID_admin = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(29))
    Rol = db.Column(db.String(50))
    ID_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.ID_usuario'))
    Contraseña = db.Column(db.String(255)) # Corregido: para almacenar el hash de la contraseña

    productos = db.relationship('Producto', backref='administrador', lazy=True)


class Producto(db.Model):
    __tablename__ = 'Producto'
    ID_Producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_producto = db.Column(db.String(255))
    Descripcion_producto = db.Column(db.Text)
    Precio_Unitario = db.Column(db.Numeric(10, 2))
    Unidades_disponibles = db.Column(db.Integer)
    Fecha_Disponibilidad = db.Column(db.Date)
    ID_Administrador = db.Column(db.Integer, db.ForeignKey('Administrador.ID_admin'))

    personalizaciones = db.relationship('PersonalizacionProducto', backref='producto', lazy=True)
    categorias = db.relationship('Categoria', backref='producto', lazy=True)


class PersonalizacionProducto(db.Model):
    __tablename__ = 'Personalizacion_Producto'
    ID_Personalizacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Masa = db.Column(db.Enum('batida', 'azucarada', 'fermentadas'), default='batida', nullable=False)
    Relleno = db.Column(db.Enum('vainilla', 'dulce de leche', 'nueces', 'crema de limon'), nullable=False)
    Cobertura = db.Column(db.Enum('chocolate', 'maracuya', 'vainilla', 'fresa', 'melocoton'), nullable=False)
    Porciones = db.Column(db.Enum('1 porcion', '2 porciones', '1/2', 'entero', '3 a 5 porciones'), nullable=False)
    Adicionales = db.Column(db.Enum('chantilly', 'leche condensada', 'arequipe ', 'chocolate', 'fresa'))
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'))
    ID_Cliente = db.Column(db.Integer, db.ForeignKey('Cliente.ID_cliente'))


class Pedido(db.Model):
    __tablename__ = 'Pedido'
    ID_Pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Fecha_Solicitud = db.Column(db.Date)
    Fecha_Entrega = db.Column(db.Date)
    Tiempo_Realizacion = db.Column(db.String(50))
    Estado_Pedido = db.Column(db.Enum('Pendiente', 'En proceso', 'Enviado', 'Entregado', 'Cancelado'))
    Total = db.Column(db.Numeric(10, 2))
    ID_Cliente = db.Column(db.Integer, db.ForeignKey('Cliente.ID_cliente'))


class DetallePedido(db.Model):
    __tablename__ = 'Detalle_Pedido'
    ID_detalle_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre = db.Column(db.String(29))
    Cantidad_unidades_producto = db.Column(db.Integer)
    Nombre_producto = db.Column(db.String(300))
    Fecha_Solicitud = db.Column(db.Date)
    Fecha_Entrega = db.Column(db.Date)
    Tiempo_Realizacion = db.Column(db.String(50))
    Descuento = db.Column(db.String(100))
    Masa = db.Column(db.Enum('batida', 'azucarada', 'fermentadas'), default='batida', nullable=False)
    Relleno = db.Column(db.Enum('vainilla', 'dulce de leche', 'nueces', 'crema de limon'), nullable=False)
    Cobertura = db.Column(db.Enum('chocolate', 'maracuya', 'vainilla', 'fresa', 'melocoton'), nullable=False)
    Porciones = db.Column(db.Enum('1 porcion', '2 porciones', '1/2', 'entero', '3 a 5 porciones'), nullable=False)
    Adicionales = db.Column(db.Enum('chantilly', 'leche condensada', 'arequipe ', 'chocolate', 'fresa'))
    Precio_Unitario = db.Column(db.Numeric(10, 2))
    IVA = db.Column(db.Integer)
    Total = db.Column(db.Numeric(10, 2))
    Estado_pedido = db.Column(db.Enum('Pendiente', 'En proceso', 'Enviado', 'Entregado', 'Cancelado'))
    ID_pedido = db.Column(db.Integer, db.ForeignKey('Pedido.ID_Pedido'))
    ID_producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'))
    ID_Cliente = db.Column(db.Integer, db.ForeignKey('Cliente.ID_cliente'))
    ID_Personalizacion = db.Column(db.Integer, db.ForeignKey('Personalizacion_Producto.ID_Personalizacion'))


class Categoria(db.Model):
    __tablename__ = 'Categoria'
    ID_Categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Nombre_categoria = db.Column(db.String(20))
    Nombre_producto = db.Column(db.String(40))
    Estado = db.Column(db.Enum('Activa', 'Inactiva'))
    ID_Producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'))


class DetalleProducto(db.Model):
    __tablename__ = 'Detalle_Producto'
    ID_detalle_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Ingredientes = db.Column(db.String(70))
    tiempo_preparacion = db.Column(db.Date)
    Nombre_Categoria = db.Column(db.String(80))
    Nombre_Producto = db.Column(db.String(70))
    Descripcion_producto = db.Column(db.String(100))
    ID_Categoria = db.Column(db.Integer, db.ForeignKey('Categoria.ID_Categoria'))
    ID_producto = db.Column(db.Integer, db.ForeignKey('Producto.ID_Producto'))


class Pago(db.Model):
    __tablename__ = 'Pago'
    ID_pago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Monto = db.Column(db.Numeric(10, 2))
    Metodo_Pago = db.Column(db.Enum('Nequi', 'Daviplata', 'Tarjeta'))
    fecha_pago = db.Column(db.Date)
    URL_Comprobante = db.Column(db.String(300))
    ID_Detalle_Pedido = db.Column(db.Integer, db.ForeignKey('Detalle_Pedido.ID_detalle_pedido'))

