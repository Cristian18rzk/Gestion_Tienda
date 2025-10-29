from builtins import ValueError
from datetime import datetime
from persistencia import PersistenciaCSV, PersistenciaJSON
from rich.console import Console

console = Console()
console.print("[bold blue]¡Rich está funcionando en azul![/bold blue]")


class Producto:
    """
    Representa un producto disponible en la tienda.

    Atributos:
        id_producto (int): Identificador único del producto.
        nombre (str): Nombre del producto.
        precio (float): Precio unitario del producto.
        stock (int): Cantidad disponible en inventario.
    """

    def __init__(self, id_producto, nombre, precio, stock):
        """
        Inicializa un nuevo producto con su información básica.

        Args:
            id_producto (int): ID único del producto.
            nombre (str): Nombre del producto.
            precio (float): Precio unitario del producto.
            stock (int): Cantidad disponible.
        """
        self.id_producto = int(id_producto)
        self.nombre = nombre
        self.precio = float(precio)
        self.stock = int(stock)

    def __str__(self):
        """
        Retorna una representación legible del producto.

        Returns:
            str: Cadena con el ID, nombre, precio y stock del producto.

        Ejemplo:
            >>> p = Producto(1, "Martillo", 25000, 10)
            >>> print(p)
            ID: 1 | Nombre: Martillo | Precio: $25000.00 | Stock: 10
        """
        return f"ID: {self.id_producto} | Nombre: {self.nombre} | Precio: ${self.precio:.2f} | Stock: {self.stock}"

    def to_dict(self):
        """
        Convierte el producto en un diccionario.

        Returns:
            dict: Diccionario con los datos del producto.
        """
        return {'id_producto': self.id_producto, 'nombre': self.nombre, 'precio': self.precio, 'stock': self.stock}


class Cliente:
    """
    Representa un cliente de la tienda.

    Atributos:
        id_cliente (int): Identificador único del cliente.
        nombre (str): Nombre completo del cliente.
        email (str): Correo electrónico del cliente.
    """

    def __init__(self, id_cliente, nombre, email):
        """
        Inicializa un nuevo cliente con su información básica.

        Args:
            id_cliente (int): ID único del cliente.
            nombre (str): Nombre completo.
            email (str): Dirección de correo electrónico.
        """
        self.id_cliente = int(id_cliente)
        self.nombre = nombre
        self.email = email

    def __str__(self):
        """
        Retorna una representación legible del cliente.

        Returns:
            str: Cadena con el ID, nombre y correo del cliente.

        Ejemplo:
            >>> c = Cliente(1, "Juan Pérez", "juan@example.com")
            >>> print(c)
            ID: 1 | Nombre: Juan Pérez | Email: juan@example.com
        """
        return f"ID: {self.id_cliente} | Nombre: {self.nombre} | Email: {self.email}"

    def to_dict(self):
        """
        Convierte el cliente en un diccionario.

        Returns:
            dict: Diccionario con los datos del cliente.
        """
        return {'id_cliente': self.id_cliente, 'nombre': self.nombre, 'email': self.email}


class Tienda:
    """
    Gestiona los productos, clientes y pedidos de la tienda.

    Métodos principales:
        - agregar_producto(): Añade un nuevo producto.
        - actualizar_producto(): Modifica un producto existente.
        - eliminar_producto(): Elimina un producto.
        - crear_pedido(): Registra un nuevo pedido.
        - historial_pedidos_cliente(): Devuelve pedidos de un cliente.
        - buscar_productos_por_nombre(): Busca productos por coincidencia parcial.
        - generar_reporte_ventas(): Calcula las ventas totales.
    """

    def __init__(self):
        """
        Inicializa la tienda cargando los productos, clientes y pedidos
        desde los archivos de persistencia correspondientes.
        """
        self.productos = self._cargar_productos()
        self.clientes = self._cargar_clientes()
        pedidos_cargados = PersistenciaJSON.leer_pedidos('pedidos.json')
        self.pedidos = pedidos_cargados if isinstance(pedidos_cargados, list) else []

    def _cargar_productos(self):
        """
        Carga los productos desde el archivo CSV.

        Returns:
            dict: Diccionario de productos con ID como clave.
        """
        datos = PersistenciaCSV.leer_datos('productos.csv', ['id_producto', 'nombre', 'precio', 'stock'])
        return {int(p['id_producto']): Producto(**p) for p in datos}

    def _cargar_clientes(self):
        """
        Carga los clientes desde el archivo CSV.

        Returns:
            dict: Diccionario de clientes con ID como clave.
        """
        datos = PersistenciaCSV.leer_datos('clientes.csv', ['id_cliente', 'nombre', 'email'])
        return {int(c['id_cliente']): Cliente(**c) for c in datos}

    def _guardar_productos(self):
        """Guarda todos los productos en el archivo CSV."""
        PersistenciaCSV.escribir_datos('productos.csv', list(self.productos.values()),
                                       ['id_producto', 'nombre', 'precio', 'stock'])

    def _guardar_clientes(self):
        """Guarda todos los clientes en el archivo CSV."""
        PersistenciaCSV.escribir_datos('clientes.csv', list(self.clientes.values()),
                                       ['id_cliente', 'nombre', 'email'])

    def _guardar_pedidos(self):
        """Guarda todos los pedidos en el archivo JSON."""
        PersistenciaJSON.escribir_pedidos('pedidos.json', self.pedidos)

    def obtener_siguiente_id(self, coleccion):
        """
        Calcula el siguiente ID disponible para una colección (clientes o productos).

        Args:
            coleccion (dict): Colección existente (productos o clientes).

        Returns:
            int: Nuevo ID generado.
        """
        return max(coleccion.keys()) + 1 if coleccion else 1

    def obtener_lista(self, coleccion):
        """
        Convierte una colección (dict) en una lista de objetos.

        Args:
            coleccion (dict): Colección de objetos.

        Returns:
            list: Lista con los valores del diccionario.
        """
        return list(coleccion.values())

    def agregar_producto(self, nombre, precio, stock):
        """
        Registra un nuevo producto en el sistema.

        Args:
            nombre (str): Nombre del producto.
            precio (float): Precio unitario.
            stock (int): Cantidad inicial en inventario.
        """
        nuevo_id = self.obtener_siguiente_id(self.productos)
        nuevo_producto = Producto(nuevo_id, nombre, precio, stock)
        self.productos[nuevo_id] = nuevo_producto
        self._guardar_productos()
        console.print(f"[bold green] Producto '{nombre}' agregado con ID {nuevo_id}.[/bold green]")

    def actualizar_producto(self, id_prod, nombre=None, precio=None, stock=None):
        """
        Actualiza los datos de un producto existente.

        Args:
            id_prod (int): ID del producto.
            nombre (str, opcional): Nuevo nombre.
            precio (float, opcional): Nuevo precio.
            stock (int, opcional): Nuevo stock.

        Returns:
            bool: True si se actualizó correctamente, False si no se encontró el producto.
        """
        prod = self.productos.get(id_prod)
        if not prod:
            console.print(f"[bold red] Error:[/bold red] Producto ID {id_prod} no encontrado.", style="red")
            return False

        if nombre is not None:
            prod.nombre = nombre
        if precio is not None:
            prod.precio = float(precio)
        if stock is not None:
            prod.stock = int(stock)

        self._guardar_productos()
        console.print(f"[bold green] Producto ID {id_prod} actualizado.[/bold green]")
        return True

    def eliminar_producto(self, id_prod):
        """
        Elimina un producto del inventario.

        Args:
            id_prod (int): ID del producto a eliminar.

        Returns:
            bool: True si se eliminó, False si no existe.
        """
        if id_prod in self.productos:
            del self.productos[id_prod]
            self._guardar_productos()
            console.print(f"[bold green] Producto ID {id_prod} eliminado.[/bold green]")
            return True
        console.print(f"[bold red] Error:[/bold red] Producto ID {id_prod} no encontrado.", style="red")
        return False

    def crear_pedido(self, id_cliente, productos_con_cantidad):
        """
        Crea un nuevo pedido para un cliente, actualizando el inventario.

        Args:
            id_cliente (int): ID del cliente que realiza el pedido.
            productos_con_cantidad (dict): Diccionario con ID del producto y cantidad.

        Raises:
            ValueError: Si los datos del pedido son inválidos o no existen.
        """
        if id_cliente not in self.clientes:
            console.print("[bold red] Error:[/bold red] Cliente no encontrado.", style="red")
            return

        items_pedido = []
        costo_total = 0

        for id_prod_str, cantidad in productos_con_cantidad.items():
            try:
                id_prod = int(id_prod_str)
                cantidad = int(cantidad)
            except ValueError:
                console.print("[bold red] Error:[/bold red] ID de producto o cantidad inválida.", style="red")
                return

            producto = self.productos.get(id_prod)
            if not producto:
                console.print(f"[bold red] Error:[/bold red] Producto ID {id_prod} no encontrado. Pedido cancelado.",
                              style="red")
                return

            if producto.stock < cantidad:
                console.print(
                    f"[bold red] Error:[/bold red] Stock insuficiente para {producto.nombre}. Pedido cancelado.",
                    style="red")
                return

            producto.stock -= cantidad

            items_pedido.append({
                'id_producto': id_prod,
                'nombre': producto.nombre,
                'cantidad': cantidad,
                'precio_unitario': producto.precio,
                'subtotal': round(producto.precio * cantidad, 2)
            })
            costo_total += items_pedido[-1]['subtotal']

        nuevo_id = 1 if not self.pedidos else max(p['id_pedido'] for p in self.pedidos) + 1

        nuevo_pedido = {
            'id_pedido': nuevo_id,
            'id_cliente': id_cliente,
            'nombre_cliente': self.clientes[id_cliente].nombre,
            'fecha_pedido': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'items': items_pedido,
            'total_pedido': round(costo_total, 2)
        }

        self.pedidos.append(nuevo_pedido)
        self._guardar_productos()
        self._guardar_pedidos()
        console.print(
            f"\n[bold green] Pedido {nuevo_id} creado exitosamente.[/bold green] Total: [bold yellow]${costo_total:.2f}[/bold yellow]"
        )

    def historial_pedidos_cliente(self, id_cliente):
        """
        Obtiene el historial de pedidos de un cliente.

        Args:
            id_cliente (int): ID del cliente.

        Returns:
            list | None: Lista de pedidos si existe el cliente, None en caso contrario.
        """
        if id_cliente not in self.clientes:
            return None
        return [p for p in self.pedidos if p['id_cliente'] == id_cliente]

    def buscar_productos_por_nombre(self, termino):
        """
        Busca productos que contengan una palabra en su nombre.

        Args:
            termino (str): Palabra o parte del nombre del producto.

        Returns:
            list: Lista de productos coincidentes.
        """
        return [p for p in self.productos.values() if termino.lower() in p.nombre.lower()]

    def generar_reporte_ventas(self):
        """
        Calcula el valor total vendido hasta el momento.

        Returns:
            float: Suma total de todos los pedidos realizados.
        """
        total_vendido = sum(pedido.get('total_pedido', 0) for pedido in self.pedidos)
        return total_vendido
