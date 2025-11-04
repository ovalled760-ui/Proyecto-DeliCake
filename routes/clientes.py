from flask_wtf.csrf import generate_csrf
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file
from reportlab.pdfgen import canvas
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from controladores.models import db, Usuario, Producto
from controladores.models import db,Categoria,Producto, PersonalizacionProducto, Cliente, Pedido, Disponibilidad, DetallePedido,Notificacion,Lanzamiento
from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask import session
from flask_migrate import Migrate
import os




from datetime import date, datetime 
import json  
app = Flask(__name__)


clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

@clientes_bp.route('/mi_cuenta')
@login_required
def mi_cuenta():
    if not current_user.cliente:
        flash("No tienes perfil de cliente.")
        return redirect(url_for("publica"))

    cliente = current_user.cliente
    return render_template(
        "clientes/mi_cuenta.html",
        usuario=current_user,
        cliente=cliente
    )


@clientes_bp.route("/actualizar_datos", methods=["GET", "POST"])
@login_required
def actualizar_datos():
    
    token = generate_csrf()

    if not current_user.cliente:
        flash("No tienes perfil de cliente.", "warning")
        return redirect(url_for("publica"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")

        # Verificar si hay cambios
        if (
            nombre == current_user.Nombre and
            apellido == current_user.Apellido and
            correo == current_user.Correo and
            telefono == current_user.cliente.Telefono and
            direccion == current_user.cliente.Direccion
        ):
            flash("No se han realizado cambios", "warning")
            return redirect(url_for("clientes.actualizar_datos"))

        try:
            # ✅ Verificar correo duplicado
            if Usuario.query.filter(
                Usuario.Correo == correo,
                Usuario.ID_usuario != current_user.ID_usuario
            ).first():
                flash("Ese correo ya está registrado por otro usuario", "danger")
                return redirect(url_for("clientes.actualizar_datos"))

            # ✅ Actualizar datos
            current_user.Nombre = nombre
            current_user.Apellido = apellido
            current_user.Correo = correo
            current_user.cliente.Telefono = telefono
            current_user.cliente.Direccion = direccion

            db.session.commit()
            flash("Datos actualizados correctamente ✅", "success")
            return redirect(url_for("clientes.mi_cuenta"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}", "danger")
            return redirect(url_for("clientes.actualizar_datos"))

    
    return render_template("clientes/actualizar_dat.html", csrf_token=token)


@clientes_bp.route("/cambiar_contrasena", methods=["GET", "POST"])
@login_required
def cambiar_contrasena():
    if request.method == "POST":
        actual = request.form.get("actual")
        nueva = request.form.get("nueva")
        confirmar = request.form.get("confirmar")

        if not check_password_hash(current_user.Contraseña, actual):
            flash("La contraseña actual es incorrecta", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        if nueva != confirmar:
            flash("Las nuevas contraseñas no coinciden", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        current_user.Contraseña = generate_password_hash(nueva)
        db.session.commit()
        flash("Contraseña actualizada con éxito", "success")
        return redirect(url_for("clientes.mi_cuenta"))
    categorias = Categoria.query.all()
    return render_template("clientes/cambiar_con.html",categorias=categorias)

    


#CAMBIOS 3
#
#
# 
#
#
#




@clientes_bp.route("/seguimiento", methods=["GET"])
@login_required
def seguimiento_pedido():
    
    cliente = Cliente.query.filter_by(ID_usuario=current_user.ID_usuario).first()
    if not cliente:
        flash("No tienes un perfil de cliente asociado.", "warning")
        return render_template("clientes/seguimiento_pedido.html", pedidos=[])

    
    pedidos = Pedido.query.filter_by(ID_Cliente=cliente.ID_cliente).all()

    pedidos_data = []
    for pedido in pedidos:
        pedidos_data.append({
            "ID_Pedido": pedido.ID_Pedido,
            "Cliente": f"{current_user.Nombre} {current_user.Apellido}",
            "Fecha_Solicitud": pedido.Fecha_Solicitud.strftime("%Y-%m-%d") if pedido.Fecha_Solicitud else "Pendiente",
            "Fecha_Entrega": pedido.Fecha_Entrega.strftime("%Y-%m-%d") if pedido.Fecha_Entrega else "Pendiente",
            "Total": f"{pedido.Total:.2f}" if pedido.Total else "0.00",
            "Estado_Pedido": pedido.Estado_Pedido
        })


    notificaciones = Notificacion.query.filter_by(usuario_id=current_user.ID_usuario).order_by(Notificacion.fecha.desc()).all()

   
    for n in notificaciones:
        if not n.leida:
            n.leida = True
    db.session.commit()


    categorias = Categoria.query.all()
    return render_template(
        "clientes/seguimiento_pedido.html",
        pedidos=pedidos_data,
        notificaciones=notificaciones,
        categorias=categorias
    )




@clientes_bp.route("/confirmacion_pedido", methods=["GET", "POST"])
@login_required
def confirmacion_pedido():
    carrito = session.get("carrito", [])
    categorias = Categoria.query.all()

    # Si el usuario no tiene un cliente asociado, lo crea
    if not current_user.cliente:
        nuevo_cliente = Cliente(
            Direccion="Por definir",
            usuario=current_user  
        )
        db.session.add(nuevo_cliente)
        db.session.commit()

    cliente = current_user.cliente  

    # Fechas y horas disponibles
    disponibilidades = Disponibilidad.query.order_by(Disponibilidad.Fecha, Disponibilidad.Hora).all()
    fechas_horas = {}
    for d in disponibilidades:
        if d.Fecha and d.Hora:
            fecha_str = d.Fecha.strftime("%Y-%m-%d")
            hora_str = d.Hora.strftime("%H:%M")
            fechas_horas.setdefault(fecha_str, []).append(hora_str)
    
    if request.method == "POST":
        direccion = request.form.get("direccion")
        metodo_pago = request.form.get("metodo_pago")
        fecha_entrega = request.form.get("fechaEntrega") 
        hora_entrega = request.form.get("horaEntrega")     

        # Recuperar carrito
        carrito_json = request.form.get("carrito_json")
        if carrito_json:
            try:
                carrito = json.loads(carrito_json)
            except Exception:
                carrito = session.get("carrito", [])
        else:
            carrito = session.get("carrito", [])

        # ✅ Recuperar datos temporales de confirmación (si existen)
        datos_guardados = session.get("datos_confirmacion", {})

        # Si el usuario tiene perfil, rellenar los campos del formulario con sus datos o los guardados
        direccion = datos_guardados.get("direccion") or current_user.cliente.Direccion
        metodo_pago = datos_guardados.get("metodo_pago") or None

        # 🔹 Inicializar valores
        subtotal = 0
        envio = 5000
        total = 0

        # 🔹 Calcular subtotal con descuentos
        for item in carrito:
            descuento_str = str(item.get("descuento", "0")).replace("%", "").strip()
            try:
                descuento = float(descuento_str)
            except ValueError:
                descuento = 0.0

            precio_con_descuento = item["precio"] - (item["precio"] * descuento / 100)
            subtotal += precio_con_descuento * item["cantidad"]

        total = subtotal + envio if carrito else 0

        # 🔹 Obtener el ID del producto
        id_producto = None
        if carrito:
            item = carrito[0]
            id_producto = (
                item.get("id")
                or item.get("ID_Producto")
                or item.get("producto_id")
            )

        # Validar que haya producto
        if not id_producto:
            flash("⚠️ No se pudo registrar el pedido porque no se encontró un producto válido.", "warning")
            return redirect(url_for("clientes.ver_carrito"))

        # Crear pedido con ID_Producto (relación a tabla Producto)
        pedido = Pedido(
            cliente=cliente,  
            Estado_Pedido="Pendiente",
            Total=total,
            Fecha_Solicitud=date.today(),
            Fecha_Entrega=datetime.strptime(fecha_entrega, "%Y-%m-%d").date() if fecha_entrega else None,
            Tiempo_Realizacion="Pendiente",
            ID_Producto=id_producto  # 👈 Relación directa
        )
        db.session.add(pedido)
        db.session.commit()

        # Guardar en sesión
        session["ultimo_pedido_id"] = pedido.ID_Pedido
        session["carrito_detalle"] = carrito

        flash("✅ Pedido confirmado con éxito", "success")
        return redirect(url_for("clientes.detalle_pedido"))

    # Mostrar plantilla
    subtotal = 0
    envio = 5000
    total = 0

    for item in carrito:
        descuento_str = str(item.get("descuento", "0")).replace("%", "").strip()
        try:
            descuento = float(descuento_str)
        except ValueError:
            descuento = 0.0

        precio_con_descuento = item["precio"] - (item["precio"] * descuento / 100)
        subtotal += precio_con_descuento * item["cantidad"]

    total = subtotal + envio if carrito else 0

    return render_template(
        "clientes/confirmacion_pedido.html",
        carrito=carrito,
        cliente=cliente,
        fechas_horas=fechas_horas,
        categorias=categorias,
        subtotal=subtotal,
        envio=envio,
        total=total
    )


@clientes_bp.route("/detalle_pedido", methods=["GET", "POST"])
@login_required
def detalle_pedido():
    pedido_id = session.get("ultimo_pedido_id")
    carrito = session.get("carrito_detalle", [])
    categorias = Categoria.query.all()

    if not pedido_id or not carrito:
        flash("⚠️ No hay pedido para mostrar.", "warning")
        return redirect(url_for("clientes.ver_carrito"))

    pedido = Pedido.query.get(pedido_id)
    cliente = current_user.cliente  

    # 🔹 Traer todas las personalizaciones del pedido actual
    personalizaciones = PersonalizacionProducto.query.filter_by(ID_Pedido=pedido_id).all()

    if request.method == "POST":
        for item in carrito:
            detalle = DetallePedido(
                Nombre=current_user.Nombre,
                Cantidad_unidades_producto=item["cantidad"],
                Nombre_producto=item["nombre"],
                Fecha_Solicitud=pedido.Fecha_Solicitud,
                Descuento=item.get("descuento", "0%"),
                Masa=item.get("masa", "batida"),
                Relleno=item.get("relleno", "vainilla"),
                Cobertura=item.get("cobertura", "chocolate"),
                Porciones=item.get("porciones", "entero"),
                Adicionales=item.get("adicionales", "ninguno"),
                Precio_Unitario=item["precio"],
                Total=pedido.Total,
                ID_pedido=pedido.ID_Pedido,
                ID_producto=item.get("id"),
                ID_Cliente=cliente.ID_cliente,
                ID_Personalizacion=item.get("personalizacion_id")
            )
            db.session.add(detalle)

        db.session.commit()

        # Limpiar sesión
        session.pop("carrito_detalle", None)
        session.pop("ultimo_pedido_id", None)

        return redirect(url_for("clientes.gracias"))

    return render_template(
        "clientes/detalle_pedido.html",
        pedido=pedido,
        carrito=carrito,
        cliente=cliente,
        categorias=categorias,
        personalizaciones=personalizaciones
    )




@clientes_bp.route("/personalizar/<int:producto_id>", methods=["GET", "POST"])
@login_required
def personalizar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    cliente_id = current_user.cliente.ID_cliente

    # 🔹 Buscar un pedido en curso (pendiente o en proceso)
    pedido_actual = Pedido.query.filter_by(
        ID_Cliente=cliente_id, Estado_Pedido='Pendiente'
    ).order_by(Pedido.ID_Pedido.desc()).first()

    if not pedido_actual:
        # Si no hay pedido pendiente, crea uno nuevo
        pedido_actual = Pedido(
            ID_Cliente=cliente_id,
            Fecha_Solicitud=date.today(),
            Estado_Pedido='Pendiente',
            Total=0
        )
        db.session.add(pedido_actual)
        db.session.commit()

    if request.method == "POST":
        masa = request.form.get("masa").strip()
        relleno = request.form.get("relleno").strip()
        cobertura = request.form.get("cobertura").strip()
        porciones = request.form.get("porciones").strip()
        adicionales = [a.strip() for a in request.form.getlist("adicionales")]
        adicionales_str = ",".join(adicionales) if adicionales else None

        try:
            # 🔹 Buscar si ya existe una personalización de ese producto en ese pedido
            personalizacion = PersonalizacionProducto.query.filter_by(
                ID_Producto=producto_id,
                ID_Cliente=cliente_id,
                ID_Pedido=pedido_actual.ID_Pedido
            ).first()

            if personalizacion:
                personalizacion.Masa = masa
                personalizacion.Relleno = relleno
                personalizacion.Cobertura = cobertura
                personalizacion.Porciones = porciones
                personalizacion.Adicionales = adicionales_str
            else:
                personalizacion = PersonalizacionProducto(
                    ID_Producto=producto_id,
                    ID_Cliente=cliente_id,
                    ID_Pedido=pedido_actual.ID_Pedido,  # ✅ nueva relación
                    Masa=masa,
                    Relleno=relleno,
                    Cobertura=cobertura,
                    Porciones=porciones,
                    Adicionales=adicionales_str
                )
                db.session.add(personalizacion)

            db.session.commit()
            flash("✅ Personalización guardada con éxito.", "success")

            # ✅ Actualizar carrito en sesión con la nueva personalización
            carrito = session.get("carrito", [])
            for item in carrito:
                if item.get("id") == producto_id:
                    item["masa"] = masa
                    item["relleno"] = relleno
                    item["cobertura"] = cobertura
                    item["porciones"] = porciones
                    item["adicionales"] = adicionales_str
                    item["personalizacion_id"] = personalizacion.ID_Personalizacion
                    break

            session["carrito"] = carrito
            session.modified = True

            return redirect(url_for("clientes.confirmacion_pedido"))

        except Exception as e:
            db.session.rollback()
            flash("❌ Error al guardar la personalización", "danger")
            print(f"Error al guardar personalización: {e}")

    # ✅ Mantener los datos de confirmación en la sesión para no perderlos al volver
    datos_confirmacion = session.get("datos_confirmacion")
    if not datos_confirmacion:
        datos_confirmacion = {}
    session["datos_confirmacion"] = datos_confirmacion

    return render_template("clientes/personalizacion_de_producto.html", producto=producto)



@clientes_bp.route("/politica_privacidad")
def politica_privacidad():
    return render_template("clientes/politica_privacidad.html")


@clientes_bp.route("/terminos_condiciones")
def terminos_condiciones():
    return render_template("clientes/terminos_condiciones.html")



def get_cart():
    if "carrito" not in session:
        session["carrito"] = []
    return session["carrito"]

@clientes_bp.route("/carrito")
@login_required
def carrito():
    carrito = session.get("carrito", [])
    total = 0

    for item in carrito:

        descuento_str = str(item.get("descuento", "0")).replace("%", "").strip()
        try:
            descuento = float(descuento_str)
        except ValueError:
            descuento = 0.0

      
        precio_con_descuento = item["precio"] - (item["precio"] * descuento / 100)
        total += precio_con_descuento * item["cantidad"]

    
    categorias = Categoria.query.all()


    return render_template("clientes/carrito.html", carrito=carrito, total=total, categorias=categorias)



   

@clientes_bp.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    data = request.get_json()
    carrito = get_cart()

    
    producto = Producto.query.get(data["id"])
    if not producto:
        return jsonify({"ok": False, "msg": "Producto no encontrado"}), 404


    for item in carrito:
        if str(item["id"]) == str(data["id"]):
            item["cantidad"] += int(data["cantidad"])
            break
    else:
        
        carrito.append({
    "id": str(data["id"]),
    "nombre": data["nombre"],
    "precio": float(data["precio"]),
    "cantidad": int(data["cantidad"]),
    "descuento": float(producto.Descuento or 0),
    "imagen": (
        data["imagen"]
        if data["imagen"].startswith("/static/")
        else url_for('static', filename=f"img/productos/{data['imagen']}")
    ),
})

    
    session["carrito"] = carrito
    session.modified = True

    return jsonify({"ok": True, "msg": "Producto agregado al carrito", "carrito": carrito})


@clientes_bp.route("/carrito/eliminar/<id>")
def carrito_eliminar(id):
    carrito = get_cart()
    carrito = [item for item in carrito if str(item["id"]) != str(id)]
    session["carrito"] = carrito
    session.modified = True
    return redirect(url_for("clientes.carrito"))


@clientes_bp.route("/carrito/vaciar")
def carrito_vaciar():
    session["carrito"] = []
    return redirect(url_for("clientes.carrito"))

@clientes_bp.route("/campanita")
@login_required
def campanita():
    if not current_user.cliente:
        flash("No tienes un perfil de cliente asociado.", "warning")
        return render_template("clientes/campanita.html", notificaciones=[])

    pedidos = current_user.cliente.pedidos

    notificaciones = []
    for pedido in pedidos:
        notificaciones.append(f"Pedido #{pedido.ID_Pedido} se encuentra {pedido.Estado_Pedido}")

    total_notificaciones = len(notificaciones)

    return render_template(
        "clientes/campanita.html",
        notificaciones=notificaciones,
        total_notificaciones=total_notificaciones
    )

@clientes_bp.route('/suscribir1', methods=["POST"])
def suscribir1():
    correo = request.form.get("correo", "").strip()  
    
    if not correo or "@" not in correo or "." not in correo:
        flash("Correo inválido, intente de nuevo", "error")
        return redirect(url_for('publica'))
    existente = Suscriptor.query.filter_by(correo=correo).first()
    if existente:
        flash("Este correo ya está suscrito", "warning")
        return redirect(url_for('publica'))

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
    return redirect(url_for('publica'))


@clientes_bp.route('/historial-pedidos')
def historial_pedidos():
    if not current_user.cliente:
        flash("Este usuario no tiene perfil de cliente.")
        return redirect(url_for('login'))

    pedidos = current_user.cliente.pedidos
    return render_template('clientes/historial_pedidos.html', pedidos=pedidos)



@clientes_bp.route("/notificaciones_json")
@login_required
def notificaciones_json():
    notificaciones = Notificacion.query.filter_by(
        usuario_id=current_user.ID_usuario,
        leida=False
    ).order_by(Notificacion.fecha.desc()).all()

    data = [{
        
        "mensaje": n.mensaje,
        "fecha": n.fecha.strftime("%Y-%m-%d %H:%M:%S")
    } for n in notificaciones]

    return jsonify(data)

@clientes_bp.route("/marcar_leidas", methods=["POST"])
@login_required
def marcar_leidas():
    Notificacion.query.filter_by(usuario_id=current_user.ID_usuario, leida=False).update({"leida": True})
    db.session.commit()
    return jsonify({"success": True})


@clientes_bp.route('/lanzamientos')
def lanzamientos():
    # Trae todos los lanzamientos ordenados por fecha (opcional)
    lanzamientos = Lanzamiento.query.order_by(Lanzamiento.fecha_catalogo).all()

    return render_template('clientes/lanzamientos.html', lanzamientos=lanzamientos)

@clientes_bp.route("/gracias")
@login_required
def gracias():
    return render_template("clientes/gracias.html")


