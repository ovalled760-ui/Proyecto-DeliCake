import os
import shutil   
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user 
from controladores.models import db, Producto, Categoria, Pedido,Favorito, Disponibilidad,DetalleProducto, Calificacion, Reseña, Suscriptor , Notificacion
from werkzeug.utils import secure_filename
from decimal import Decimal


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

VIDEOS_FOLDER = "C:\\Users\\jerss\\Searches\\Downloads\\DeliCake\\DeliCake\\static\\videos"
BANNER_ACTUAL = os.path.join(VIDEOS_FOLDER, "banner_actual.mp4")




@admin_bp.route("/producto/<int:id>", methods=["GET", "POST"])
def  detalle(id):
    producto = Producto.query.get_or_404(id)
    categorias = Categoria.query.all()
    detalle = DetalleProducto.query.filter_by(ID_producto=id).first()
    
    sugerencias = Producto.query.filter(
        Producto.ID_Categoria == producto.ID_Categoria,
        Producto.ID_Producto != producto.ID_Producto).limit(4).all()    
    
    if request.method =="POST":
        puntuacion = int (request.form['puntuacion'])
        nueva_calificacion = Calificacion(Valor = puntuacion, ID_Producto = id)
        db.session.add(nueva_calificacion)
        db.session.commit()
        return redirect(url_for('admin.detalle', id=id))
    
    calificiones= Calificacion.query.filter_by(ID_Producto=id).all()
    promedio = None
    if calificiones:
        promedio = round(sum(c.Valor for c in calificiones)/len(calificiones),1)
      
    return render_template("clientes/detalle.html", producto=producto, categorias=categorias, detalle=detalle, promedio=promedio, sugerencias=sugerencias, calificiones= calificiones)


@admin_bp.route("/agregar", methods=["GET", "POST"])
def agregar_producto():
   
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        descuento = request.form["descuento"]
        id_categoria = request.form["categoria"]

 
        imagen_file = request.files["imagen"]
        if imagen_file and imagen_file.filename != "":
            imagen_path = imagen_file.filename
            imagen_file.save(os.path.join("static/img", imagen_path))
        else:
            imagen_path = "default.jpg" 

        nuevo = Producto(
            Nombre_producto=nombre,
            Descripcion_producto=descripcion,
            Precio_Unitario =precio,
            Descuento=descuento,
            Imagen=imagen_path,
            ID_Administrador=1,
            ID_Categoria = id_categoria
        )
        db.session.add(nuevo)
        db.session.commit()
        
        ingredientes = request.form['ingredientes']
        tiempo = request.form["tiempo"]
        detalle = DetalleProducto(
            Ingredientes = ingredientes,
            tiempo_preparacion = tiempo,
            ID_producto =nuevo.ID_Producto
        )        
        db.session.add(detalle)
        db.session.commit()
        
        
        flash("Producto agregado con éxito ")
        return redirect(url_for("admin.agregar_producto"))
    categorias = Categoria.query.filter_by().all() 
    return render_template("admin/agregar_producto.html",categorias=categorias)


@admin_bp.route("/categoria/<int:id_categoria>")
def productos_por_categoria(id_categoria):
    categorias = Categoria.query.all()
    productos = Producto.query.filter_by(ID_Categoria=id_categoria).all()
    favoritos_ids = []
    if current_user.is_authenticated:
        favoritos_ids = [f.ID_Producto for f in Favorito.query.filter_by(ID_usuario=current_user.ID_usuario).all()]
    return render_template("clientes/catalogo.html",  productos=productos, categorias=categorias, favoritos_ids=favoritos_ids
                           )

@admin_bp.route("/editar", methods=['GET'])
def editar_producto():
    productos = Producto.query.all()
    categorias=Categoria.query.all()

    for p in productos:
        p.Precio_Unitario = float(p.Precio_Unitario)
        p.Descuento = float (p.Descuento) if p.Descuento else 0.0
    return render_template("admin/editar_producto.html", productos=productos,  categorias=categorias)

@admin_bp.route("/actualizar/<int:id>", methods=["POST"])
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)

    producto.Nombre_producto = request.form["nombre"]
    producto.Descripcion_producto = request.form["descripcion"]

    producto.Precio_Unitario = Decimal(request.form["precio"])
    producto.Descuento = Decimal(request.form["descuento"]) if request.form["descuento"] else Decimal("0")

    producto.ID_Categoria = int(request.form["categoria"])
    

    imagen_file = request.files["imagen"]
    if imagen_file and imagen_file.filename != "":
        imagen_path = imagen_file.filename 
        imagen_file.save(os.path.join("static/img", imagen_path))
        producto.Imagen = imagen_path

    db.session.commit()
    flash("Producto actualizado con éxito", "success")

    return redirect(url_for("admin.editar_producto"))

@admin_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    producto = Producto.query.get_or_404(id)
    try:
      
        DetalleProducto.query.filter_by(ID_producto=id).delete(synchronize_session=False)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        db.session.delete(producto)
        db.session.commit()

        flash("Producto eliminado correctamente")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar producto: {str(e)}", "danger")

    return redirect(url_for("admin.listar_productos"))


@admin_bp.route("/listar_productos")
def listar_productos():
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template("admin/eliminar_producto.html", productos=productos, categorias=categorias)
@admin_bp.route('/buscar')
def buscar():
    categorias=Categoria.query.all()
    query= request.args.get("q","").strip()
    productos=[]
    
    if query:
        
        productos = Producto.query.filter(
            Producto.Nombre_producto.ilike(f"%{query}%")).all()
    
   
    return render_template('clientes/buscar.html', productos=productos, query=query, categorias=categorias)
@admin_bp.route('/panel')
def panel():
    categorias=Categoria.query.all()
    return render_template("admin/mi_cuenta_ADM.html", categorias=categorias )
    

@admin_bp.route("/seguimiento", methods=["GET"])
def seguimiento_pedidos():
    pedidos = Pedido.query.all()
    categorias=Categoria.query.all()
    return render_template("admin/seguimiento de pedido ADM.html", pedidos=pedidos, categorias=categorias)


@admin_bp.route("/actualizar_estado/<int:pedido_id>", methods=["POST"])
def actualizar_estado(pedido_id):
    nuevo_estado = request.form.get("estado")
    pedido = Pedido.query.get(pedido_id)

    if pedido:
        pedido.Estado_Pedido = nuevo_estado
        db.session.commit()

        # Crear notificación automática SOLO para el cliente
        cliente = pedido.cliente
        if cliente and cliente.usuario:
            mensaje = f"Tu pedido #{pedido.ID_Pedido} cambió de estado a '{nuevo_estado}'."
            noti = Notificacion(usuario_id=cliente.usuario.ID_usuario, mensaje=mensaje)
            db.session.add(noti)
            db.session.commit()

        flash(f"Estado del pedido {pedido_id} actualizado a {nuevo_estado}", "success")
    else:
        flash("Pedido no encontrado ❌", "danger")

    return redirect(url_for("admin.seguimiento_pedidos"))







@admin_bp.route("/disponibilidad", methods=["GET", "POST"])
def gestionar_disponibilidad():
    if request.method == "POST":
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")

        if fecha and hora:
           
            from datetime import datetime
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora, "%H:%M").time()

            nueva_disponibilidad = Disponibilidad(Fecha=fecha_obj, Hora=hora_obj)
            db.session.add(nueva_disponibilidad)
            db.session.commit()
            flash("✅ Disponibilidad agregada", "success")
        return redirect(url_for("admin.gestionar_disponibilidad"))

  
    disponibilidades = Disponibilidad.query.order_by(Disponibilidad.Fecha, Disponibilidad.Hora).all()
    return render_template("admin/disponibilidad.html", disponibilidades=disponibilidades)

@admin_bp.route("/disponibilidad/borrar/<int:id>", methods=["POST"])
def borrar_disponibilidad(id):
    disp = Disponibilidad.query.get_or_404(id)
    db.session.delete(disp)
    db.session.commit()
    flash("🗑️ Disponibilidad eliminada", "success")
    return redirect(url_for("admin.gestionar_disponibilidad"))

@admin_bp.route("/suscriptores")
def lista_suscriptores():
    suscriptores = Suscriptor.query.all()
    categorias = Categoria.query.all()
    return render_template("admin/suscripciones.html", suscriptores=suscriptores,categorias=categorias)

@admin_bp.route("/reseñas")
def lista_reseñas():
    reseñas = Reseña.query.all()
    categorias = Categoria.query.all()
    return render_template("admin/reseñas.html", reseñas=reseñas, categorias=categorias)

@admin_bp.route("/aprobar/<int:id>")
def aprobar_reseña(id):
    reseña = Reseña.query.get_or_404(id)
    reseña.estado = "aprobada"
    db.session.commit()
    return redirect(url_for("admin.lista_reseñas"))



@admin_bp.route("/eliminar/<int:id>")
def eliminar_reseña(id):
    reseña = Reseña.query.get_or_404(id)
    db.session.delete(reseña)
    db.session.commit()
    return redirect(url_for("admin.lista_reseñas"))

@admin_bp.route('/anuncios', methods=['GET', 'POST'])
def anuncios():
    """Vista para que el administrador cambie el banner actual"""

   
    banners = [f for f in os.listdir(VIDEOS_FOLDER) if f.endswith(('.mp4', '.webm'))]

    if request.method == 'POST':
        banner = request.form.get('banner')

    
        if banner and banner in banners:
            nuevo_banner = os.path.join(VIDEOS_FOLDER, banner)
            shutil.copy(nuevo_banner, BANNER_ACTUAL)
            flash(f'🎥 Banner "{banner}" establecido como actual.', 'success')
            return redirect(url_for('admin.anuncios'))


    banner_actual = None
    if os.path.exists(BANNER_ACTUAL):
    
        banner_actual = url_for('static', filename='videos/banner_actual.mp4')

    return render_template(
        'admin/cambiar_anuncios.html',
        banners=banners,
        banner_actual=banner_actual
    )

