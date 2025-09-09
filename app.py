from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from controladores.models import db, Usuario, Cliente
from routes.admin import bp as admin_bp

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/delicake'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_secreta'

# Inicialización de la base de datos y Flask-Login
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    #La función debe devolver una instancia de la clase que hereda de UserMixin
    return Usuario.query.get(int(user_id))

# Rutas de la aplicación
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/publica')
def publica():
    return render_template('index-1.html')

@app.route('/register', methods=['GET', 'POST', ])
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

        # Crear una nueva instancia de usuario
        nuevo_usuario = Usuario(
            Nombre=nombre,
            Apellido=apellido,
            Correo=correo,
            Contraseña=hashed_password
        )
        
        try:
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            # Obtener el ID del nuevo usuario
            id_usuario = nuevo_usuario.ID_usuario

            # Crear una nueva instancia de cliente
            nuevo_cliente = Cliente(
                Nombre=nombre,
                Direccion=direccion,
                Telefono=telefono,
                ID_usuario=id_usuario
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
        
        # Buscar el usuario en la base de datos
        usuario = Usuario.query.filter_by(Correo=correo).first()

        # Verificar si el usuario existe y la contraseña es co
        # rrecta
        if usuario and check_password_hash(usuario.Contraseña, contraseña):
            # Usar la instancia de la base de datos directamente, ya que hereda de UserMixin
            login_user(usuario)
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('publica'))
        else:
            flash('Correo o contraseña incorrectos.')
            
    return render_template('inicio de sesion.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('publica'))


app.register_blueprint(admin_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

