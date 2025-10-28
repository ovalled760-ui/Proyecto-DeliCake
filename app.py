from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager,UserMixin, login_user, logout_user, login_required, current_user
from controladores.models import db, Usuario, Cliente, Administrador, Categoria, Producto,Reseña,Suscriptor
from reportlab.pdfgen import canvas
from flask_mail import Mail, Message
from datetime import datetime
from routes.clientes import clientes_bp
from routes.admin import admin_bp
from flask_login import current_user, login_required
import random
import string
from datetime import datetime
from email.mime.image import MIMEImage
import os

app = Flask(__name__)
#configurar mi SECRECT KEY para que session funcione correctamente
app.secret_key = "12345678"
def generar_codigo():
    return ''.join(random.choices(string.digits, k=6))

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/delicake'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'deli.cake404@gmail.com'
app.config['MAIL_PASSWORD'] = 'xmwh hxnu zzvd pslv'  
app.config['MAIL_DEFAULT_SENDER'] = ('DeliCake', 'deli.cake404@gmail.com')

mail = Mail(app)
# Inicialización de la base de datos y Flask-Login
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    #La función debe devolver una instancia de la clase que hereda de UserMixin
    return Usuario.query.get(int(user_id))




def obtener_banner_actual():
    """Devuelve la ruta del banner actual si existe, sino None"""
    banner_actual_path = os.path.join('static', 'videos', 'banner_actual.mp4')
    if os.path.exists(banner_actual_path):
        return 'videos/banner_actual.mp4'
    return None


@app.route('/')
def home():
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    sugerencias = random.sample(productos, min(len(productos), 9))
    reseñas = Reseña.query.filter_by(estado="aprobada").all()
    banner_actual = obtener_banner_actual()
    return render_template(
        "index.html",
        categorias=categorias,
        sugerencias=sugerencias,
        reseñas=reseñas,
        banner_actual=banner_actual
    )

from flask_login import current_user

def esta_en_horario():
    ahora = datetime.now()
    dia = ahora.weekday()
    hora_actual = ahora.hour + ahora.minute / 60

    if 0 <= dia <= 4:  
        return 7 <= hora_actual < 20
    else:  
        return 9 <= hora_actual < 17.5
@app.route('/publica')
def publica():
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    sugerencias = random.sample(productos, min(len(productos), 9))
    reseñas = Reseña.query.filter_by(estado="aprobada").all()
    banner_actual = obtener_banner_actual()
    en_horario = esta_en_horario()

    # 🔹 Si el usuario tiene pedidos, crear notificaciones de estado:
    if current_user.is_authenticated and current_user.cliente:
        pedidos = current_user.cliente.pedidos
        notificaciones = [f"Pedido #{p.ID_Pedido} está en {p.Estado_Pedido}" for p in pedidos]
    else:
        notificaciones = []

    total_notificaciones = len(notificaciones)

    return render_template(
        "clientes/index-1.html",
        categorias=categorias,
        sugerencias=sugerencias,
        reseñas=reseñas,
        banner_actual=banner_actual,
        total_notificaciones=total_notificaciones,
        en_horario=en_horario
    )



@app.route('/index_ADMIN')
def index_ADMIN():
    categorias = Categoria.query.all()
    productos = Producto.query.all()
    sugerencias = random.sample(productos, min(len(productos), 9))

   
    import os
    banner_actual_path = os.path.join('static', 'videos', 'banner_actual.mp4')
    banner_existe = os.path.exists(banner_actual_path)

    banner_actual = None
    if banner_existe:
        banner_actual = 'videos/banner_actual.mp4'


    return render_template(
        'admin/index_ADMIN.html',
        categorias=categorias,
        sugerencias=sugerencias,
        banner_actual=banner_actual  
    )




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        contraseña = request.form.get('contraseña')
        confirmar_contraseña = request.form.get('confirmar_contraseña')

        # Verificar si las contraseñas coinciden
        if contraseña != confirmar_contraseña:
            flash('Las contraseñas no coinciden.')
            return redirect(url_for('register'))

        # Verificar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(Correo=correo).first()
        if usuario_existente:
            flash('Este correo ya está registrado.')
            return redirect(url_for('register'))
            
        hashed_password = generate_password_hash(contraseña)

        try:
            # Crear Usuario
            nuevo_usuario = Usuario(
                Nombre=nombre,
                Apellido=apellido,
                Correo=correo,
                Contraseña=hashed_password
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
        
            
            nuevo_cliente = Cliente(
                Direccion=direccion,
                Telefono=telefono,
                ID_usuario=nuevo_usuario.ID_usuario
                )
            db.session.add(nuevo_cliente)
            db.session.commit()
            
            flash('Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {e}")
            flash('Ocurrió un error durante el registro. Por favor, revisa la consola para más detalles.')
            return redirect(url_for('register'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        
        usuario = Usuario.query.filter_by(Correo=correo).first()

        if not usuario:
            flash("Correo incorrecto.")
            return redirect(url_for('login'))

        if not check_password_hash(usuario.Contraseña, contraseña):
            flash("Contraseña incorrecta.")
            return redirect(url_for('login'))


        if not usuario.cliente:
            flash("Este usuario no tiene perfil de cliente.")
            return redirect(url_for('login'))

        login_user(usuario)
        flash('Inicio de sesión exitos')
        return redirect(url_for('publica'))

    return render_template('clientes/inicio de sesion.html')


#LOGIN ADMIN

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')
        codigo_validacion = request.form.get('codigo_validacion')

        usuario = Usuario.query.filter_by(Correo=correo).first()

        if not usuario:
            flash("Correo incorrecto.")
            return redirect(url_for("login_admin"))

        if not check_password_hash(usuario.Contraseña, contraseña):
            flash("Contraseña incorrecta.")
            return redirect(url_for("login_admin"))

        admin = Administrador.query.filter_by(ID_usuario=usuario.ID_usuario).first()
        if not admin:
            flash("Este usuario no tiene permisos de administrador.")
            return redirect(url_for("login_admin"))

    
        if not (codigo_validacion.isdigit() and len(codigo_validacion) == 6):
            flash("El código de validación debe contener exactamente 6 números, sin letras.")
            return redirect(url_for("login_admin"))

        if admin.Clave_validacion != int(codigo_validacion):
            flash("Código de validación incorrecto.")
            return redirect(url_for("login_admin"))

        login_user(usuario)
        flash("Inicio de sesión exitoso como Administrador.")
        return redirect(url_for("index_ADMIN"))

    return render_template('admin/inicio_sesion_ADMIN.html')




#RECUPERAR CONTRASEÑA


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    if request.method == "POST":
        correo = request.form["correo"]

        # Verificar si el usuario existe
        usuario = Usuario.query.filter_by(Correo=correo).first()
        if not usuario:
            flash("Correo no registrado", "danger")
            return redirect(url_for("recuperar"))

        # Generar código
        codigo = generar_codigo()
        session["reset_correo"] = correo
        session["reset_codigo"] = codigo
        session["codigo_verificado"] = False  

        # Enviar correo
        try:
            msg = Message(
                subject="Código de recuperación - DeliCake",
                sender=app.config['MAIL_USERNAME'],
                recipients=[correo],
                body=f"""
Hola 👋,

Has solicitado recuperar tu contraseña en DeliCake 🧁.

Tu código de verificación es: {codigo}

Este código expira en 10 minutos. Si no solicitaste este cambio, ignora este correo.
                """
            )
            mail.send(msg)
            flash("Se ha enviado un código a tu correo", "info")
        except Exception as e:
            import traceback
            print(f"Error enviando correo: {e}")
            traceback.print_exc()
            flash("No se pudo enviar el correo. Intenta más tarde.", "danger")

        return redirect(url_for("verificar_codigo"))

    return render_template("recuperar_con.html")




@app.route("/verificar", methods=["GET", "POST"])
def verificar_codigo():
    if request.method == "POST":
        codigo_ingresado = request.form.get("codigo")

        if codigo_ingresado == session.get("reset_codigo"):
            session["codigo_verificado"] = True
            flash("Código validado correctamente", "success")
            return redirect(url_for("nueva_contrasena"))  
        else:
            flash("Código inválido", "danger")

    return render_template("verificar_con.html")


@app.route("/nueva_contrasena", methods=["GET", "POST"])
def nueva_contrasena():
    if not session.get("codigo_verificado"):
        flash("Primero debes verificar tu código", "warning")
        return redirect(url_for("recuperar"))

    if request.method == "POST":
        pass1 = request.form["password"]
        pass2 = request.form["password2"]

        if pass1 != pass2:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("nueva_contrasena"))

        correo = session.get("reset_correo")
        usuario = Usuario.query.filter_by(Correo=correo).first()

        if usuario:
            usuario.Contraseña = generate_password_hash(pass1)
            db.session.commit()

        # Limpiar datos de recuperación
        session.pop("reset_correo", None)
        session.pop("reset_codigo", None)
        session.pop("codigo_verificado", None)

        flash("Contraseña actualizada con éxito", "success")
        return redirect(url_for("login"))

    return render_template("nueva_con.html")



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('home'))


app.register_blueprint(admin_bp)
app.register_blueprint(clientes_bp)
@app.route('/suscribir', methods=["POST"])
def suscribir():
    correo = request.form.get("correo", "").strip()  
    
    if not correo or "@" not in correo or "." not in correo:
        flash("Correo inválido, intente de nuevo", "error")
        return redirect(url_for('home'))
    existente = Suscriptor.query.filter_by(correo=correo).first()
    if existente:
        flash("Este correo ya está suscrito", "warning")
        return redirect(url_for('home'))

    nuevo = Suscriptor(correo=correo)
    db.session.add(nuevo)
    db.session.commit()

    msg = Message(
        subject="🎉 ¡Gracias por suscribirte a DeliCake!",
        sender=app.config['MAIL_USERNAME'],
        recipients=[correo]
    )

    msg.html = """
    <div style="text-align:center; font-family: Arial, sans-serif; padding:20px;">
        <img src="cid:logo_delicake" width="150" style="border-radius:50%;"><br>
        <h2 style="color:#d63384;">🎀 Bienvenido a la familia DeliCake 🎀</h2>
        <p style="font-size:16px; color:#333;">
            Gracias por suscribirte a nuestro boletín 💌.<br>
            A partir de ahora recibirás nuestras mejores ofertas, novedades y consejos dulces directamente en tu bandeja de entrada.
        </p>
        <p style="margin-top:20px; color:#d63384; font-weight:bold;">
            ¡Que tu día sea tan dulce como nuestros postres! 🧁
        </p>
    </div>
    """
    with app.open_resource("static/img/nuestrasdelicias.png") as img:
        msg.attach(
            filename="nuestrasdelicias.png",
            content_type="image/png",
            data=img.read(),
            disposition="inline",
            headers={'Content-ID':'<logo_delicake>'}       
            
        )

    
    mail.send(msg)

    flash("¡Gracias por suscribirte! Revisa tu correo 📩", "success")
    return redirect(url_for('home'))
@app.route("/reseñar", methods=["POST"])
@login_required
def reseñar():
    if not current_user.is_authenticated:
        flash("Debes iniciar sesión para dejar una reseña.", "error")
        return redirect(url_for("login"))

    estrellas = request.form.get("estrellas")
    comentario = request.form.get("comentario")
    correo = current_user.Correo  

    if not estrellas or not comentario:
        flash("Todos los campos son obligatorios.", "error")
        return redirect(url_for("publica"))

    if int(estrellas) < 1 or int(estrellas) > 5:
        flash("La calificación debe estar entre 1 y 5 estrellas.", "error")
        return redirect(url_for("publica"))

    PALABRAS_PROHIBIDAS = ["grosería", "tonto", "estúpido", "maldito", "idiota",
                           "imbécil", "pendejo", "mierda", "puta", "verga", 
                           "bobo marica", "perro setenta hijueputa", "puta mierda"]
    if any(p in comentario.lower() for p in PALABRAS_PROHIBIDAS):
        flash("Tu comentario contiene palabras inapropiadas.", "error")
        return redirect(url_for("publica"))

    nueva = Reseña(
        ID_usuario=current_user.ID_usuario,
        correo=correo,
        estrellas=int(estrellas),
        comentario=comentario,
        estado="pendiente"
    )
    db.session.add(nueva)
    db.session.commit()

    flash("¡Gracias por tu opinión! Tu reseña será publicada tras ser aprobada.", "success")
    return redirect(url_for("publica"))

@app.route("/productos/<int:id_categoria>")
def productos_admin(id_categoria):
    categorias = Categoria.query.all()
    productos = Producto.query.filter_by(ID_Categoria=id_categoria).all()
    return render_template("admin/productos.html",  productos=productos, categorias=categorias)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

