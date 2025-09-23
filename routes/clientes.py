from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

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