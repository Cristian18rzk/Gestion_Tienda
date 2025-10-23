from builtins import ValueError
from datetime import datetime
from persistencia import PersistenciaCSV, PersistenciaJSON
from rich.console import Console

console = Console()


class Producto:
    def __init__(self, id_producto, nombre, precio, stock):  # CAMBIADO: __init__
        self.id_producto = int(id_producto)
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)

    def __str__(self):
        return f"ID: {self.id_producto} | Nombre: {self.nombre} | Precio: ${self.precio:.2f} | Stock: {self.stock}"

    def to_dict(self):
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }


class Cliente:
    def __init__(self, id_cliente, nombre, email):  # CAMBIADO: __init__
        self.id_cliente = int(id_cliente)
        self.nombre = nombre
        self.email = email

    def __str__(self):  # CAMBIADO: __str__
        return f"ID: {self.id_cliente} | Nombre: {self.nombre} | Email: {self.email}"

    def to_dict(self):
        return {
            "id_cliente": self.id_cliente,
            "nombre": self.nombre,
            "email": self.email,
        }


class Tienda:
    def __init__(self):
        self.productos = self._cargar_productos()
        self.clientes = self._cargar_clientes()
        # --- Corrección: garantizar que pedidos siempre sea lista ---
        pedidos_cargados = PersistenciaJSON.leer_pedidos("pedidos.json")
        self.pedidos = pedidos_cargados if isinstance(pedidos_cargados, list) else []

    # ... (el resto del código permanece igual)

    def _cargar_productos(self):
        datos = PersistenciaCSV.leer_datos(
            "productos.csv", ["id_producto", "nombre", "precio", "stock"]
        )
        return {int(p["id_producto"]): Producto(**p) for p in datos}

    def _cargar_clientes(self):
        datos = PersistenciaCSV.leer_datos(
            "clientes.csv", ["id_cliente", "nombre", "email"]
        )
        return {int(c["id_cliente"]): Cliente(**c) for c in datos}

    def _guardar_productos(self):
        PersistenciaCSV.escribir_datos(
            "productos.csv",
            list(self.productos.values()),
            ["id_producto", "nombre", "precio", "stock"],
        )

    def _guardar_clientes(self):
        PersistenciaCSV.escribir_datos(
            "clientes.csv",
            list(self.clientes.values()),
            ["id_cliente", "nombre", "email"],
        )

    def _guardar_pedidos(self):
        PersistenciaJSON.escribir_pedidos("pedidos.json", self.pedidos)

    def obtener_siguiente_id(self, coleccion):
        return max(coleccion.keys()) + 1 if coleccion else 1

    def obtener_lista(self, coleccion):
        return list(coleccion.values())

    def agregar_producto(self, nombre, precio, stock):
        nuevo_id = self.obtener_siguiente_id(self.productos)
        nuevo_producto = Producto(nuevo_id, nombre, precio, stock)
        self.productos[nuevo_id] = nuevo_producto
        self._guardar_productos()
        console.print(
            f"[bold green]✔ Producto '{nombre}' agregado con ID {nuevo_id}.[/bold green]"
        )

    def actualizar_producto(self, id_prod, nombre=None, precio=None, stock=None):
        prod = self.productos.get(id_prod)
        if not prod:
            console.print(
                f"[bold red]✗ Error:[/bold red] Producto ID {id_prod} no encontrado.",
                style="red",
            )
            return False

        if nombre is not None:
            prod.nombre = nombre
        if precio is not None:
            prod.precio = float(precio)
        if stock is not None:
            prod.stock = int(stock)

        self._guardar_productos()
        console.print(f"[bold green]✔ Producto ID {id_prod} actualizado.[/bold green]")
        return True

    def eliminar_producto(self, id_prod):
        if id_prod in self.productos:
            del self.productos[id_prod]
            self._guardar_productos()
            console.print(
                f"[bold green]✔ Producto ID {id_prod} eliminado.[/bold green]"
            )
            return True
        console.print(
            f"[bold red]✗ Error:[/bold red] Producto ID {id_prod} no encontrado.",
            style="red",
        )
        return False

    def crear_pedido(self, id_cliente, productos_con_cantidad):
        if id_cliente not in self.clientes:
            console.print(
                "[bold red]✗ Error:[/bold red] Cliente no encontrado.", style="red"
            )
            return

        items_pedido = []
        costo_total = 0

        for id_prod_str, cantidad in productos_con_cantidad.items():
            try:
                id_prod = int(id_prod_str)
                cantidad = int(cantidad)
            except ValueError:
                console.print(
                    "[bold red]✗ Error:[/bold red] ID de producto o cantidad inválida.",
                    style="red",
                )
                return

            producto = self.productos.get(id_prod)
            if not producto:
                console.print(
                    f"[bold red]✗ Error:[/bold red] Producto ID {id_prod} no encontrado. Pedido cancelado.",
                    style="red",
                )
                return

            if producto.stock < cantidad:
                console.print(
                    f"[bold red]✗ Error:[/bold red] Stock insuficiente para {producto.nombre}. Pedido cancelado.",
                    style="red",
                )
                return

            producto.stock -= cantidad

            items_pedido.append(
                {
                    "id_producto": id_prod,
                    "nombre": producto.nombre,
                    "cantidad": cantidad,
                    "precio_unitario": producto.precio,
                    "subtotal": round(producto.precio * cantidad, 2),
                }
            )
            costo_total += items_pedido[-1]["subtotal"]

        # --- Corrección: generación segura del ID ---
        if not self.pedidos:
            nuevo_id = 1
        else:
            nuevo_id = max(p["id_pedido"] for p in self.pedidos) + 1

        nuevo_pedido = {
            "id_pedido": nuevo_id,
            "id_cliente": id_cliente,
            "nombre_cliente": self.clientes[id_cliente].nombre,
            "fecha_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items_pedido,
            "total_pedido": round(costo_total, 2),
        }

        self.pedidos.append(nuevo_pedido)
        self._guardar_productos()
        self._guardar_pedidos()
        console.print(
            f"\n[bold green]✅ Pedido {nuevo_id} creado exitosamente.[/bold green] Total: [bold yellow]${costo_total:.2f}[/bold yellow]"
        )

    def historial_pedidos_cliente(self, id_cliente):
        if id_cliente not in self.clientes:
            return None
        return [p for p in self.pedidos if p["id_cliente"] == id_cliente]

    def buscar_productos_por_nombre(self, termino):
        return [
            p for p in self.productos.values() if termino.lower() in p.nombre.lower()
        ]

    def generar_reporte_ventas(self):
        total_vendido = sum(pedido.get("total_pedido", 0) for pedido in self.pedidos)
        return total_vendido
