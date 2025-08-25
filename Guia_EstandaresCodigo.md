# Guía de Estándares de Codificación

## 1. Reglas de Nombres
- Variables: usar **snake_case** en Python (`nombre_usuario`, `total_pedido`).
- Constantes: usar **MAYÚSCULAS** (`MAX_INTENTOS`, `PI`).
- Funciones y métodos: usar **snake_case** (`calcular_total()`, `obtener_usuario()`).
- Clases: usar **PascalCase** (`Cliente`, `PedidoOnline`).
- Archivos: en **minúscula** y con guion bajo (`main.py`, `scripts.sql`).

## 2. Comentarios y Documentación
- Usar comentarios **en español o inglés consistente**.
- Comentarios breves con `#` en Python.
- Documentar funciones con docstrings:

```python
def calcular_total(precio, cantidad):
    """
    Calcula el total de un pedido.
    :param precio: float - precio unitario
    :param cantidad: int - cantidad de unidades
    :return: float - total calculado
    """
    return precio * cantidad
3. Identación y Estilo
En Python usar 4 espacios por nivel de sangría.

Máximo 80–100 caracteres por línea.

Dejar una línea en blanco entre funciones y clases.

En HTML usar identación de 2 espacios.

4. Ejemplos
Correcto:

python
Copiar
Editar
class Usuario:
    def __init__(self, nombre, correo):
        self.nombre = nombre
        self.correo = correo
Incorrecto:

python
Copiar
Editar
class usuario:
 def __init__(self,nombre,correo):
  self.nombre=nombre
  self.correo=correo
