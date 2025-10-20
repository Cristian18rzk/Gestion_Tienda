from builtins import ValueError

from gestion import Tienda, Producto, Cliente
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
tienda_app = Tienda()


# =======================
# Funciones de Interfaz de Usuario
# =======================

def mostrar_menu():
    """Muestra el menú principal con Rich."""
    titulo = "[bold yellow]Sistema de Gestión de Tienda (Rich CLI)[/bold yellow]"
    console.print(Panel(titulo, style="bold blue on black", border_style="cyan"))

    menu = Table.grid(padding=1)
    menu.add_column(style="bold white")
    menu.add_column(style="white")

    menu.add_row("1.", "[cyan]Gestión de Productos (CRUD)[/cyan]")
    menu.add_row("2.", "[cyan]Gestión de Clientes (CRUD)[/cyan]")
    menu.add_row("3.", "[bold green]CREAR NUEVO PEDIDO[/bold green]")
    menu.add_row("4.", "Ver Historial de Pedidos de Cliente")
    menu.add_row("5.", "Buscar Productos por Nombre")
    menu.add_row("6.", "[bold red]GENERAR REPORTE DE VENTAS[/bold red]")
    menu.add_row("0.", "SALIR")

    console.print(menu)


def mostrar_lista(titulo, lista_objetos):
    """Muestra una lista de objetos (Clientes o Productos) en formato Rich Table."""
    if not lista_objetos:
        console.print(f"[i]No hay {titulo.lower()} registrados.[/i]", style="dim")
        return

    tabla = Table(title=titulo, show_header=True, header_style="bold magenta")

    # Asume que todos los objetos en la lista son del mismo tipo (Producto o Cliente)
    if isinstance(lista_objetos[0], Producto):
        tabla.add_column("ID", style="cyan")
        tabla.add_column("Nombre", style="white")
        tabla.add_column("Precio", style="yellow")
        tabla.add_column("Stock", style="green")
        for p in lista_objetos:
            tabla.add_row(str(p.id_producto), p.nombre, f"${p.precio:.2f}", str(p.stock))

    elif isinstance(lista_objetos[0], Cliente):
        tabla.add_column("ID", style="cyan")
        tabla.add_column("Nombre", style="white")
        tabla.add_column("Email", style="yellow")
        for c in lista_objetos:
            tabla.add_row(str(c.id_cliente), c.nombre, c.email)

    console.print(tabla)


# --- Implementación CRUD Productos (Ejemplo Completo) ---
def manejar_crud_productos():
    while True:
        console.print("\n[bold cyan]-- GESTIÓN DE PRODUCTOS --[/bold cyan]")
        console.print(
            "1. [green]Crear[/green] | 2. [yellow]Ver Todos[/yellow] | 3. [blue]Actualizar[/blue] | 4. [red]Eliminar[/red] | 0. Volver")
        opcion = console.input("Seleccione una opción: ")

        if opcion == '1':
            nombre = console.input("Nombre: ")
            precio = float(console.input("Precio: "))
            stock = int(console.input("Stock: "))
            tienda_app.agregar_producto(nombre, precio, stock)

        elif opcion == '2':
            mostrar_lista("Productos Registrados", tienda_app.obtener_lista(tienda_app.productos))

        elif opcion == '3':
            id_prod = int(console.input("ID del producto a actualizar: "))
            nombre = console.input("Nuevo Nombre (dejar vacío para no cambiar): ")
            precio = console.input("Nuevo Precio (dejar vacío): ")
            stock = console.input("Nuevo Stock (dejar vacío): ")

            tienda_app.actualizar_producto(id_prod,
                                           nombre if nombre else None,
                                           precio if precio else None,
                                           stock if stock else None)

        elif opcion == '4':
            try:
                id_prod = int(console.input("ID del producto a eliminar: "))
                tienda_app.eliminar_producto(id_prod)
            except ValueError:
                console.print("[bold red]✗ Error:[/bold red] ID inválido.", style="red")

        elif opcion == '0':
            break

        else:
            console.print("[bold red]Opción no válida.[/bold red]", style="red")


# --- Funcionalidad: Crear Pedido ---
def manejar_crear_pedido():
    try:
        mostrar_lista("Clientes", tienda_app.obtener_lista(tienda_app.clientes))
        id_cliente = int(console.input("\n[bold green]ID del Cliente que realiza el pedido:[/bold green] "))
    except ValueError:
        console.print("[bold red]✗ Error:[/bold red] ID de cliente inválido.", style="red")
        return

    productos_con_cantidad = {}
    console.print("\n[bold yellow]--- AGREGAR PRODUCTOS (Ingrese 'fin' para terminar) ---[/bold yellow]")
    mostrar_lista("Stock Actual", tienda_app.obtener_lista(tienda_app.productos))

    while True:
        id_prod = console.input("ID Producto: ")
        if id_prod.lower() == 'fin':
            break

        try:
            cantidad = int(console.input("Cantidad: "))
            if cantidad > 0:
                productos_con_cantidad[id_prod] = cantidad
            else:
                console.print("[bold red]La cantidad debe ser mayor a cero.[/bold red]", style="red")
        except ValueError:
            console.print("[bold red]Cantidad inválida. Intente de nuevo.[/bold red]", style="red")

    if productos_con_cantidad:
        tienda_app.crear_pedido(id_cliente, productos_con_cantidad)
    else:
        console.print("[bold red]Pedido cancelado.[/bold red] No se seleccionaron productos.", style="red")


# --- Funcionalidad: Historial ---
def manejar_historial_pedidos():
    try:
        id_cliente = int(console.input("ID del Cliente para ver historial: "))
    except ValueError:
        console.print("[bold red]✗ Error:[/bold red] ID de cliente inválido.", style="red")
        return

    historial = tienda_app.historial_pedidos_cliente(id_cliente)
    if historial is None:
        console.print("[bold red]✗ Error:[/bold red] Cliente no encontrado.", style="red")
        return

    if not historial:
        console.print("[i]Este cliente no tiene pedidos registrados.[/i]", style="dim")
        return

    for pedido in historial:
        tabla = Table(title=f"Pedido #{pedido['id_pedido']} - Fecha: {pedido['fecha_pedido']}",
                      show_header=True, header_style="bold green")
        tabla.add_column("Producto", style="white")
        tabla.add_column("Cant.", style="cyan")
        tabla.add_column("Precio Unit.", justify="right")
        tabla.add_column("Subtotal", justify="right", style="yellow")

        for item in pedido['items']:
            tabla.add_row(
                item['nombre'],
                str(item['cantidad']),
                f"${item['precio_unitario']:.2f}",
                f"${item['subtotal']:.2f}"
            )

        console.print(tabla)
        console.print(f"[bold red]TOTAL PEDIDO: ${pedido['total_pedido']:.2f}[/bold red]\n")


# --- Reto Final: Reporte de Ventas ---
def generar_reporte():
    total = tienda_app.generar_reporte_ventas()

    console.print("\n--- [bold red]REPORTE DE VENTAS SIMPLE[/bold red] ---")
    console.print(
        Panel(
            f"El TOTAL de ventas generadas es: [bold white on red]${total:.2f}[/bold white on red]",
            title="[bold red]Total Recaudado[/bold red]",
            border_style="red"
        )
    )


# =======================
# Bucle Principal de la Aplicación
# =======================

if __name__ == "__main__":
    while True:
        mostrar_menu()
        opcion = console.input(">>> Seleccione una opción: ")

        if opcion == '1':
            manejar_crud_productos()
        elif opcion == '2':
            # Implementar manejar_crud_clientes() (similar al de productos)
            console.print("[yellow]Función de CRUD Clientes no implementada en este ejemplo.[/yellow]")
        elif opcion == '3':
            manejar_crear_pedido()
        elif opcion == '4':
            manejar_historial_pedidos()
        elif opcion == '5':
            termino = console.input("Ingrese nombre o parte del nombre a buscar: ")
            resultados = tienda_app.buscar_productos_por_nombre(termino)
            mostrar_lista(f"Resultados para '{termino}'", resultados)
        elif opcion == '6':
            generar_reporte()
        elif opcion == '0':
            console.print("[bold blue]Saliendo de la aplicación. ¡Adiós![/bold blue]", style="bold")
            break
        else:
            console.print("[bold red]Opción no válida. Intente de nuevo.[/bold red]", style="red")