from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file
from reportlab.pdfgen import canvas
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from controladores.models import db, Usuario, Producto, Suscriptor
from controladores.models import db,Categoria,Favorito,Producto, PersonalizacionProducto, Cliente, Pedido, Disponibilidad, DetallePedido,Notificacion
from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask import session
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
    if not current_user.cliente:
        flash("No tienes perfil de cliente.")
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
            # Verificar correo duplicado
            if Usuario.query.filter(
                Usuario.Correo == correo,
                Usuario.ID_usuario != current_user.ID_usuario
            ).first():
                flash("Ese correo ya está registrado por otro usuario", "danger")
                return redirect(url_for("clientes.actualizar_datos"))

            # Actualizar datos
            current_user.Nombre = nombre
            current_user.Apellido = apellido
            current_user.Correo = correo
            current_user.cliente.Telefono = telefono
            current_user.cliente.Direccion = direccion

            db.session.commit()
            flash("Datos actualizados correctamente", "success")
            return redirect(url_for("clientes.actualizar_datos"))

        except Exception as e:
            db.session.rollback()
            flash("Ocurrió un error al actualizar: " + str(e), "danger")
            return redirect(url_for("clientes.actualizar_datos"))
    categorias = Categoria.query.all()
    return render_template("clientes/actualizar_dat.html", usuario=current_user, categorias=categorias)


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
    # 1️⃣ Identificar cliente
    cliente = Cliente.query.filter_by(ID_usuario=current_user.ID_usuario).first()
    if not cliente:
        flash("No tienes un perfil de cliente asociado.", "warning")
        return render_template("clientes/seguimiento_pedido.html", pedidos=[])

    # 2️⃣ Obtener sus pedidos
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

    # 3️⃣ Obtener notificaciones del usuario actual
    notificaciones = Notificacion.query.filter_by(usuario_id=current_user.ID_usuario).order_by(Notificacion.fecha.desc()).all()

    # 4️⃣ Marcar las no leídas como leídas al entrar a la página
    for n in notificaciones:
        if not n.leida:
            n.leida = True
    db.session.commit()

    # 5️⃣ Renderizar vista con pedidos + notificaciones
    categorias = Categoria.query.all()
    return render_template(
        "clientes/seguimiento_pedido.html",
        pedidos=pedidos_data,
        notificaciones=notificaciones,
        categorias=categorias
    )
def esta_en_horario():
    ahora = datetime.now()
    dia = ahora.weekday()
    hora_actual = ahora.hour + ahora.minute / 60

    if 0 <= dia <= 4:  
        return 7 <= hora_actual < 24
    else:  
        return 9 <= hora_actual < 17.5



@clientes_bp.route("/confirmacion_pedido", methods=["GET", "POST"])
@login_required
def confirmacion_pedido():
    carrito = session.get("carrito", [])
    categorias = Categoria.query.all()

    if not current_user.cliente:
        nuevo_cliente = Cliente(
            Direccion="Por definir",
            Telefono="0000000000",
            usuario=current_user  
        )
        db.session.add(nuevo_cliente)
        db.session.commit()

    cliente = current_user.cliente  
    if not esta_en_horario():
        flash("⏰ Estamos fuera del horario de atención. Tu pedido será procesado el siguiente día hábil.", "warning")
        return redirect(url_for('clientes.carrito'))

  
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

 
        carrito_json = request.form.get("carrito_json")
        if carrito_json:
            try:
                carrito = json.loads(carrito_json)
            except Exception:
                carrito = session.get("carrito", [])

        
        total = sum(item["precio"] * item["cantidad"] for item in carrito)

    
        pedido = Pedido(
            cliente=cliente,  
            Estado_Pedido="Pendiente",
            Total=total,
            Fecha_Solicitud=date.today(),
            Fecha_Entrega=datetime.strptime(fecha_entrega, "%Y-%m-%d").date() if fecha_entrega else None,
            Tiempo_Realizacion="Pendiente"
        )
        db.session.add(pedido)
        db.session.commit()

       
        session["ultimo_pedido_id"] = pedido.ID_Pedido
        session["carrito_detalle"] = carrito

        flash("✅ Pedido confirmado con éxito", "success")
        return redirect(url_for("clientes.detalle_pedido"))

    return render_template(
        "clientes/confirmacion_pedido.html",
        carrito=carrito,
        cliente=cliente,
        fechas_horas=fechas_horas, categorias=categorias
    )


@clientes_bp.route("/detalle_pedido", methods=["GET", "POST"])
def detalle_pedido():
    carrito = session.get("carrito_detalle", [])
    pedido_id = session.get("ultimo_pedido_id")
    cliente_id = session.get("cliente_id")

    if not carrito or not pedido_id:
        flash("⚠️ No hay pedido para mostrar.", "danger")
        return redirect(url_for("clientes.confirmacion_pedido"))

    if request.method == "POST":
       
        for item in carrito:
            detalle = DetallePedido(
                Nombre="Cliente",  
                Cantidad_unidades_producto=item["cantidad"],
                Nombre_producto=item["nombre_producto"],
                Fecha_Solicitud=date.today(),
                Fecha_Entrega=item.get("fecha_entrega", date.today()),  
                Tiempo_Realizacion="Pendiente",
                Descuento=item.get("descuento", "0%"),
                Masa=item.get("masa", "batida"),
                Relleno=item.get("relleno", "vainilla"),
                Cobertura=item.get("cobertura", "chocolate"),
                Porciones=item.get("porciones", "1 porcion"),
                Adicionales=item.get("adicionales"),
                Precio_Unitario=item["precio"],
                IVA=item.get("iva", 0),
                Total=item["precio"] * item["cantidad"],
                Estado_pedido="Pendiente",
                ID_pedido=pedido_id,
                ID_producto=item["id_producto"],
                ID_Cliente=cliente_id,
                ID_Personalizacion=item.get("id_personalizacion")
            )
            db.session.add(detalle)
        db.session.commit()

        # limpiar sesión
        session.pop("carrito_detalle", None)
        session.pop("ultimo_pedido_id", None)

        flash("✅ Detalle del pedido guardado con éxito.", "success")
        return redirect(url_for("clientes.seguimiento_pedido"))

    return render_template("clientes/detalle_pedido.html", carrito=carrito)


@clientes_bp.route("/personalizar/<int:producto_id>", methods=["GET", "POST"])
def personalizar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    cliente_id = 1  

    if request.method == "POST":
        masa = request.form.get("masa").strip()
        relleno = request.form.get("relleno").strip()
        cobertura = request.form.get("cobertura").strip()
        porciones = request.form.get("porciones").strip()
        adicionales = [a.strip() for a in request.form.getlist("adicionales")]
        adicionales_str = ",".join(adicionales) if adicionales else None

        try:
            personalizacion = PersonalizacionProducto.query.filter_by(
                ID_Producto=producto_id,
                ID_Cliente=cliente_id,
               
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
                    
                    Masa=masa,
                    Relleno=relleno,
                    Cobertura=cobertura,
                    Porciones=porciones,
                    Adicionales=adicionales_str
                )
                db.session.add(personalizacion)

            db.session.commit()
            flash("✅ Personalización guardada/actualizada con éxito.", "success")
            return redirect(url_for("clientes.confirmacion_pedido"))

        except Exception as e:
            db.session.rollback()
            flash("❌ Error al guardar la personalización", "danger")
            print(f"Error al guardar personalización: {e}")

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
def carrito():
    carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    categorias = Categoria.query.all()
    return render_template("clientes/carrito.html", categorias=categorias,carrito=carrito, total=total)

@clientes_bp.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    data = request.get_json()
    carrito = get_cart()

    # Buscar si ya existe
    for item in carrito:
        if str(item["id"]) == str(data["id"]):  # compara como string
            item["cantidad"] += int(data["cantidad"])
            break
    else:
        carrito.append({
            "id": str(data["id"]),
            "nombre": data["nombre"],
            "precio": float(data["precio"]),
            "cantidad": int(data["cantidad"]),
            "imagen": data["imagen"]
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
        notificaciones.append(f"Pedido #{pedido.ID_Pedido} está en {pedido.Estado_Pedido}")

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

    
    Mail.send(msg)

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
@clientes_bp.route('/toggle_favorito/<int:producto_id>', methods=['POST'])
@login_required
def toggle_favorito(producto_id):
    favorito = Favorito.query.filter_by(
        ID_usuario=current_user.ID_usuario,
        ID_Producto=producto_id
    ).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({'favorito': False, 'mensaje': 'Producto eliminado de favoritos 💔'})
    else:
        nuevo = Favorito(ID_usuario=current_user.ID_usuario, ID_Producto=producto_id)
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({'favorito': True, 'mensaje': 'Producto añadido a favoritos 💖'})


@clientes_bp.route('/mis_favoritos')
@login_required
def mis_favoritos():
    categorias = Categoria.query.all()
    favoritos = Favorito.query.filter_by(ID_usuario=current_user.ID_usuario).all()
    productos = [f.producto for f in favoritos]
    return render_template('clientes/Favoritos.html', productos=productos, categorias=categorias,favoritos=favoritos)

@clientes_bp.route('/eliminar_favorito/<int:id_favorito>', methods=['POST'])
@login_required
def eliminar_favorito(id_favorito):
    favorito = Favorito.query.filter_by(
        ID_Favorito=id_favorito,
        ID_usuario=current_user.ID_usuario
    ).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        flash('Producto eliminado de favoritos 💔', 'success')
    else:
        flash('No se encontró el producto en tus favoritos.', 'danger')

    return redirect(url_for('clientes.mis_favoritos'))