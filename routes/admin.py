from flask import Blueprint, render_template, request, redirect, url_for, flash
from controladores.models import db, Producto, Categoria
import os

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/agregar", methods=["GET", "POST"])
def agregar_producto():
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        descuento = request.form["descuento"]
        ID_Categoria = request.form["categoria"]

 
        imagen_file = request.files["imagen"]
        if imagen_file and imagen_file.filename != "":
            imagen_path = imagen_file.filename
            imagen_file.save(os.path.join("static/img", imagen_path))
        else:
            imagen_path = "default.jpg"

        nuevo = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            descuento=descuento,
            categoria=categoria,
            imagen=imagen_path
        )
        db.session.add(nuevo)
        db.session.commit()
        
        categoria = Categoria.query.get(ID_Categoria)
        if categoria:
            categoria.ID_Producto = nuevo.ID_Producto
            categoria.Nombre_Producto  = nuevo.nombre
            db.session.commit() 
        flash("Producto agregado con éxito ✅")
        return redirect(url_for("admin.catalogo"))
    categorias = Categoria.query.filter_by(Estado="Activa").all() 
    return render_template("admin/agregar_producto.html",categorias=categorias)


