import datetime
from builtins import ValueError
from time import sleep

from rich import box
from rich.align import Align
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from gestion import Tienda, Producto, Cliente
from persistencia import PersistenciaJSON

console = Console()
tienda_app = Tienda()


def leer_int(prompt: str, permitir_vacio: bool = False):
    """  Solicita un número entero al usuario.

     Args:
         prompt (str): Mensaje a mostrar al usuario.
         permitir_vacio (bool): Si es True, permite que el usuario deje el campo vacío.

     Returns:
         int | None: Devuelve un número entero o None si es vacío o inválido.
    """
    raw = console.input(prompt)
    if permitir_vacio and raw.strip() == "":
        return None
    try:
        return int(raw)
    except (ValueError, TypeError):
        console.print(
            "[bold red]✗ Entrada inválida. Se esperaba un número entero.[/bold red]"
        )
        return None


def leer_float(prompt: str, permitir_vacio: bool = False):
    raw = console.input(prompt)
    if permitir_vacio and raw.strip() == "":
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        console.print(
            "[bold red]✗ Entrada inválida. Se esperaba un número decimal.[/bold red]"
        )
        return None


def pausa():
    """Pausa la ejecución hasta que el usuario presione ENTER."""
    console.input("\n[dim]Presione ENTER para continuar...[/dim]")


def imprimir_encabezado():
    console.clear()
    logo_texto = """[bold green]
 ████████╗██╗██╗██████╗ ███╗   ██╗██████╗  █████╗ 
 ╚══██╔══╝██║██║██╔══  ╗████╗  ██║██╔══██╗██╔══██╗
    ██║   ██║██║██║██  ║██╔██╗ ██║██║  ██║███████║
    ██║   ██║██║██║    ║██║╚██╗██║██║  ██║██╔══██║
    ██║   ██║██║██████╔╝██║ ╚████║██████╔╝██║  ██║
    ╚═╝   ╚═╝╚═╝╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝
[/bold green]"""
    logo_panel = Panel(
        Align.center(logo_texto),
        border_style="green",
        padding=(0, 1),
        box=box.HEAVY,
        title="[bold green]GESTIÓN DE TIENDA[/bold green]",
        subtitle="[dim]Sistema de control y ventas[/dim]",
    )
    console.print(logo_panel)
    console.print(Rule(style="bright_black"))


def mostrar_menu():
    imprimir_encabezado()
    menu = Table.grid(padding=(0, 1))
    menu.add_column(justify="right", style="bold cyan", width=3)
    menu.add_column(style="white")
    menu.add_row("1", " Gestión de Productos")
    menu.add_row("2", " Gestión de Clientes")
    menu.add_row("3", " Crear nuevo pedido")
    menu.add_row("4", " Historial de pedidos")
    menu.add_row("5", " Buscar productos por nombre")
    menu.add_row("6", " Generar reporte de ventas")
    menu.add_row("0", " Salir del sistema")
    panel = Panel(
        Align.left(menu),
        title="[bold green]Menú Principal[/bold green]",
        border_style="bright_green",
        box=box.ROUNDED,
        padding=(0, 1),
        width=50,
    )
    console.print(panel, justify="left")
    console.print(Rule(style="green"))


def mostrar_lista(titulo: str, lista_objetos: list):
    """
        Muestra una lista de objetos en formato tabla.

        Args:
            titulo (str): Título de la tabla.
            lista_objetos (list): Lista de objetos a mostrar.
        """
    if not lista_objetos:
        console.print(
            f"[bold yellow]⚠ No hay {titulo.lower()} registrados.[/bold yellow]"
        )
        return
    tabla = Table(
        title=f"[bold cyan]{titulo}[/bold cyan]",
        show_header=True,
        header_style="bold green",
        box=box.SIMPLE,
        style="white",
    )
    primera = lista_objetos[0]
    if isinstance(primera, Producto):
        tabla.add_column("ID", justify="center", style="cyan", width=6)
        tabla.add_column("Nombre", style="white")
        tabla.add_column("Precio", justify="right", style="yellow", width=10)
        tabla.add_column("Stock", justify="center", style="bright_green", width=6)
        for p in lista_objetos:
            color_stock = (
                "green" if p.stock > 10 else "yellow" if p.stock > 0 else "red"
            )
            tabla.add_row(
                str(p.id_producto),
                p.nombre,
                f"$ {p.precio:.2f}",
                f"[{color_stock}]{p.stock}[/{color_stock}]",
            )
    elif isinstance(primera, Cliente):
        tabla.add_column("ID", justify="center", style="cyan", width=6)
        tabla.add_column("Nombre", style="white")
        tabla.add_column("Email", style="yellow")
        for c in lista_objetos:
            tabla.add_row(str(c.id_cliente), c.nombre, c.email)
    else:
        keys = list(vars(primera).keys())
        for k in keys:
            tabla.add_column(k, style="white")
        for obj in lista_objetos:
            tabla.add_row(*[str(getattr(obj, k)) for k in keys])
    console.print(tabla)


# ---------------------- MANEJO CRUD PRODUCTOS ----------------------
def manejar_crud_productos():
    """Gestiona las operaciones de crear, ver, actualizar y eliminar productos."""
    while True:
        console.print(
            Panel.fit(
                "⚙  [bold bright_cyan]Gestión de Productos[/bold bright_cyan]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )
        tabla_menu = Table(
            box=box.SIMPLE,
            show_header=False,
            pad_edge=False,
            border_style="bright_cyan",
            padding=(0, 0),
            width=48,
        )
        tabla_menu.add_column("", justify="center", width=3, style="bold green")
        tabla_menu.add_column("", justify="left", style="white")
        tabla_menu.add_row("1", "Crear producto")
        tabla_menu.add_row("2", "Ver productos")
        tabla_menu.add_row("3", "Actualizar producto")
        tabla_menu.add_row("4", "Eliminar producto")
        tabla_menu.add_row("0", "Volver al menú principal")
        console.print(
            Panel(
                Align.left(tabla_menu),
                border_style="bright_cyan",
                box=box.ROUNDED,
                padding=(0, 1),
            ),
            justify="left",
        )

        opcion = console.input(
            "\n[bold cyan]>>> Seleccione una opción: [/bold cyan]"
        ).strip()
        if opcion == "1":
            nombre = console.input("[bold white]Nombre:[/bold white] ").strip()
            if not nombre:
                console.print("[bold red]✗ El nombre no puede quedar vacío.[/bold red]")
                pausa()
                continue
            precio = None
            while precio is None:
                precio = leer_float("[bold white]Precio:[/bold white] ")
            stock = None
            while stock is None:
                stock = leer_int("[bold white]Stock:[/bold white] ")
            tienda_app.agregar_producto(nombre, precio, stock)
            console.print("[bold green]✔ Producto creado correctamente.[/bold green]")
            pausa()
        elif opcion == "2":
            console.print(
                Rule("[bold cyan]LISTA DE PRODUCTOS[/bold cyan]", style="cyan")
            )
            mostrar_lista(
                "Productos Registrados", tienda_app.obtener_lista(tienda_app.productos)
            )
            pausa()
        elif opcion == "3":
            id_prod = leer_int(
                "[bold white]ID del producto a actualizar:[/bold white] "
            )
            if id_prod is None:
                pausa()
                continue
            nombre = console.input("Nuevo Nombre (vacío = no cambiar): ").strip()
            precio = leer_float(
                "Nuevo Precio (vacío = no cambiar): ", permitir_vacio=True
            )
            stock = leer_int("Nuevo Stock (vacío = no cambiar): ", permitir_vacio=True)
            tienda_app.actualizar_producto(id_prod, nombre or None, precio, stock)
            console.print(
                "[bold green]✔ Producto actualizado correctamente.[/bold green]"
            )
            pausa()
        elif opcion == "4":
            id_prod = leer_int("[bold white]ID del producto a eliminar:[/bold white] ")
            if id_prod is None:
                pausa()
                continue
            try:
                tienda_app.eliminar_producto(id_prod)
                console.print(
                    "[bold green]✔ Producto eliminado correctamente.[/bold green]"
                )
            except Exception as e:
                console.print(f"[bold red]✗ Error al eliminar:[/bold red] {e}")
            pausa()
        elif opcion == "0":
            console.print(
                Panel(
                    "[yellow]↩ Volviendo al menú principal...[/yellow]",
                    border_style="yellow",
                    box=box.ROUNDED,
                    padding=(0, 1),
                )
            )
            break
        else:
            console.print("[bold red]✗ Opción no válida. Intente de nuevo.[/bold red]")
            pausa()


# ---------------------- MANEJO CRUD CLIENTES ----------------------
def manejar_crud_clientes():
    while True:
        console.print(
            Panel.fit(
                ""
                ". [bold bright_cyan]Gestión de Clientes[/bold bright_cyan]",
                border_style="cyan",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )
        tabla_menu = Table(
            box=box.SIMPLE,
            show_header=False,
            pad_edge=False,
            border_style="bright_cyan",
            padding=(0, 0),
            width=48,
        )
        tabla_menu.add_column("", justify="center", width=3, style="bold green")
        tabla_menu.add_column("", justify="left", style="white")
        tabla_menu.add_row("1", "Crear cliente")
        tabla_menu.add_row("2", "Ver clientes")
        tabla_menu.add_row("3", "Actualizar cliente")
        tabla_menu.add_row("4", "Eliminar cliente")
        tabla_menu.add_row("0", "Volver al menú principal")
        console.print(
            Panel(
                Align.left(tabla_menu),
                border_style="bright_cyan",
                box=box.ROUNDED,
                padding=(0, 1),
            ),
            justify="left",
        )

        opcion = console.input(
            "\n[bold cyan]>>> Seleccione una opción: [/bold cyan]"
        ).strip()
        if opcion == "1":
            nombre = console.input("[bold white]Nombre completo:[/bold white] ").strip()
            if not nombre:
                console.print("[bold red]✗ El nombre no puede quedar vacío.[/bold red]")
                pausa()
                continue
            email = console.input("[bold white]Email:[/bold white] ").strip()
            if not email:
                console.print("[bold red]✗ El email no puede quedar vacío.[/bold red]")
                pausa()
                continue
            nuevo_id = tienda_app.obtener_siguiente_id(tienda_app.clientes)
            cliente = Cliente(nuevo_id, nombre, email)
            tienda_app.clientes[nuevo_id] = cliente
            try:
                tienda_app._guardar_clientes()
            except Exception:
                console.print(
                    "[bold yellow] No se pudo guardar en persistencia. Cliente creado en memoria.[/bold yellow]"
                )
            console.print(
                f"[bold green]✔ Cliente creado con ID {nuevo_id}.[/bold green]"
            )
            pausa()
        elif opcion == "2":
            console.print(
                Rule("[bold cyan]LISTA DE CLIENTES[/bold cyan]", style="cyan")
            )
            mostrar_lista(
                "Clientes Registrados", tienda_app.obtener_lista(tienda_app.clientes)
            )
            pausa()
        elif opcion == "3":
            id_cli = leer_int("[bold white]ID del cliente a actualizar:[/bold white] ")
            if id_cli is None:
                pausa()
                continue
            cliente = tienda_app.clientes.get(id_cli)
            if not cliente:
                console.print(
                    f"[bold red]✗ Cliente ID {id_cli} no encontrado.[/bold red]"
                )
                pausa()
                continue
            nombre = console.input("Nuevo Nombre (vacío = no cambiar): ").strip()
            email = console.input("Nuevo Email (vacío = no cambiar): ").strip()
            if nombre:
                cliente.nombre = nombre
            if email:
                cliente.email = email
            try:
                tienda_app._guardar_clientes()
            except Exception:
                console.print(
                    "[bold yellow]⚠ No se pudo guardar en persistencia. Cambios aplicados en memoria.[/bold yellow]"
                )
            console.print(
                "[bold green]✔ Cliente actualizado correctamente.[/bold green]"
            )
            pausa()
        elif opcion == "4":
            id_cli = leer_int("[bold white]ID del cliente a eliminar:[/bold white] ")
            if id_cli is None:
                pausa()
                continue
            if id_cli in tienda_app.clientes:
                del tienda_app.clientes[id_cli]
                try:
                    tienda_app._guardar_clientes()
                except Exception:
                    console.print(
                        "[bold yellow]⚠ No se pudo guardar en persistencia. Eliminado en memoria.[/bold yellow]"
                    )
                console.print(
                    "[bold green]✔ Cliente eliminado correctamente.[/bold green]"
                )
            else:
                console.print(
                    f"[bold red]✗ Cliente ID {id_cli} no encontrado.[/bold red]"
                )
            pausa()
        elif opcion == "0":
            console.print(
                Panel(
                    "[yellow]↩ Volviendo al menú principal...[/yellow]",
                    border_style="yellow",
                    box=box.ROUNDED,
                    padding=(0, 1),
                )
            )
            break
        else:
            console.print("[bold red]✗ Opción no válida. Intente de nuevo.[/bold red]")
            pausa()


# ---------------------- CREAR NUEVO PEDIDO ----------------------
def manejar_crear_pedido():
    console.print(
        Panel.fit(
            "🧾  [bold bright_cyan]Crear Nuevo Pedido[/bold bright_cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )

    # Mostrar clientes disponibles
    clientes = tienda_app.obtener_lista(tienda_app.clientes)
    if not clientes:
        console.print(
            "[bold red]✗ No hay clientes registrados. Debe crear al menos un cliente primero.[/bold red]"
        )
        pausa()
        return

    console.print(Rule("[bold cyan]CLIENTES DISPONIBLES[/bold cyan]", style="cyan"))
    mostrar_lista("Clientes", clientes)

    # Seleccionar cliente
    id_cliente = leer_int("\n[bold white]ID del cliente:[/bold white] ")
    if id_cliente is None:
        pausa()
        return

    cliente = tienda_app.clientes.get(id_cliente)
    if not cliente:
        console.print(f"[bold red]✗ Cliente ID {id_cliente} no encontrado.[/bold red]")
        pausa()
        return

    # Mostrar productos disponibles
    productos = tienda_app.obtener_lista(tienda_app.productos)
    if not productos:
        console.print(
            "[bold red]✗ No hay productos registrados. Debe crear al menos un producto primero.[/bold red]"
        )
        pausa()
        return

    console.print(Rule("[bold cyan]PRODUCTOS DISPONIBLES[/bold cyan]", style="cyan"))
    mostrar_lista("Productos", productos)

    # Crear pedido
    pedido_items = []
    total_pedido = 0.0

    while True:
        console.print("\n[bold cyan]Agregar producto al pedido:[/bold cyan]")
        id_producto = leer_int(
            "[bold white]ID del producto (0 para terminar):[/bold white] "
        )

        if id_producto == 0:
            break

        if id_producto is None:
            continue

        producto = tienda_app.productos.get(id_producto)
        if not producto:
            console.print(
                f"[bold red]✗ Producto ID {id_producto} no encontrado.[/bold red]"
            )
            continue

        if producto.stock <= 0:
            console.print(
                f"[bold red]✗ Producto '{producto.nombre}' sin stock disponible.[/bold red]"
            )
            continue

        cantidad = leer_int(
            f"[bold white]Cantidad de '{producto.nombre}' (stock: {producto.stock}):[/bold white] "
        )
        if cantidad is None or cantidad <= 0:
            console.print("[bold red]✗ Cantidad inválida.[/bold red]")
            continue

        if cantidad > producto.stock:
            console.print(
                f"[bold red]✗ Stock insuficiente. Solo hay {producto.stock} unidades.[/bold red]"
            )
            continue

        # Agregar al pedido
        subtotal = producto.precio * cantidad
        pedido_items.append(
            {"producto": producto, "cantidad": cantidad, "subtotal": subtotal}
        )
        total_pedido += subtotal

        console.print(
            f"[bold green]✔ Agregado: {cantidad} x {producto.nombre} = ${subtotal:.2f}[/bold green]"
        )
        console.print(
            f"[bold yellow]Total acumulado: ${total_pedido:.2f}[/bold yellow]"
        )

    if not pedido_items:
        console.print(
            "[bold yellow]⚠ Pedido cancelado. No se agregaron productos.[/bold yellow]"
        )
        pausa()
        return

    # Confirmar pedido
    console.print("\n[bold cyan]RESUMEN DEL PEDIDO:[/bold cyan]")
    console.print(f"Cliente: {cliente.nombre} ({cliente.email})")
    console.print(f"Total: ${total_pedido:.2f}")

    confirmar = (
        console.input("\n[bold white]¿Confirmar pedido? (s/n): [/bold white]")
        .strip()
        .lower()
    )

    if confirmar == "s":
        # Procesar pedido: actualizar stock en objetos Producto
        for item in pedido_items:
            producto = item["producto"]
            cantidad = item["cantidad"]
            producto.stock -= cantidad

        # --- CAMBIO: construir pedido en formato persistible y guardarlo ---
        try:
            # Convertir items a estructura serializable esperada por la persistencia
            items_serializables = []
            for item in pedido_items:
                prod_obj = item["producto"]
                items_serializables.append(
                    {
                        "id_producto": prod_obj.id_producto,
                        "nombre": prod_obj.nombre,
                        "cantidad": int(item["cantidad"]),
                        "precio_unitario": float(prod_obj.precio),
                        "subtotal": round(float(item["subtotal"]), 2),
                    }
                )

            # Generar nuevo id de pedido (igual lógica que en gestion.py)
            nuevo_id = (
                tienda_app.obtener_siguiente_id(
                    {p["id_pedido"]: p for p in tienda_app.pedidos}
                )
                if tienda_app.pedidos
                else 1
            )

            nuevo_pedido = {
                "id_pedido": nuevo_id,
                "id_cliente": id_cliente,
                "nombre_cliente": cliente.nombre,
                "fecha_pedido": __import__("datetime")
                .datetime.now()
                .strftime("%Y-%m-%d %H:%M:%S"),
                "items": items_serializables,
                "total_pedido": round(total_pedido, 2),
            }

            tienda_app.pedidos.append(nuevo_pedido)  # agregar al listado en memoria
            tienda_app._guardar_productos()  # guardar cambios de stock
            tienda_app._guardar_pedidos()  # --- CAMBIO: guardar pedidos persistente

            console.print("[bold green]✔ Pedido creado exitosamente![/bold green]")
            console.print(f"[bold green]Total: ${total_pedido:.2f}[/bold green]")
        except Exception as e:
            console.print(
                f"[bold yellow]⚠ No se pudo guardar en persistencia: {e}[/bold yellow]"
            )
    else:
        console.print("[bold yellow]⚠ Pedido cancelado.[/bold yellow]")

    pausa()


# ---------------------- HISTORIAL DE PEDIDOS ----------------------
def mostrar_historial_pedidos():
    console.print(
        Panel.fit(
            "📜  [bold bright_cyan]Historial de Pedidos[/bold bright_cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )

    pedidos = tienda_app.pedidos
    if not pedidos:
        console.print("[bold yellow]⚠ No hay pedidos registrados.[/bold yellow]")
        pausa()
        return

    tabla = Table(
        title="[bold cyan]Historial de Pedidos[/bold cyan]",
        show_header=True,
        header_style="bold green",
        box=box.SIMPLE,
        style="white",
    )
    tabla.add_column("ID", style="cyan", width=6, justify="center")
    tabla.add_column("Fecha", style="white", width=19, justify="center")
    tabla.add_column("Cliente", style="white")
    tabla.add_column("Productos", style="white")
    tabla.add_column("Total", style="yellow", justify="right", width=12)

    for pedido in pedidos:
        productos = ", ".join(
            f"{it.get('nombre')} ({it.get('cantidad')})"
            for it in pedido.get("items", [])
        )
        tabla.add_row(
            str(pedido.get("id_pedido")),
            pedido.get("fecha_pedido", ""),
            pedido.get("nombre_cliente", ""),
            productos,
            f"$ {pedido.get('total_pedido', 0):.2f}",
        )

    console.print("\n")
    console.print(tabla)
    pausa()


# ---------------------- BUSCAR PRODUCTOS POR NOMBRE ----------------------
def manejar_buscar_productos():
    console.print(
        Panel.fit(
            "🔍  [bold bright_cyan]Buscar Productos por Nombre[/bold bright_cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )

    termino = console.input(
        "[bold white]Ingrese el nombre o parte del nombre a buscar: [/bold white]"
    ).strip()

    if not termino:
        console.print("[bold red]✗ Debe ingresar un término de búsqueda.[/bold red]")
        pausa()
        return

    productos = tienda_app.obtener_lista(tienda_app.productos)
    productos_encontrados = []

    for producto in productos:
        if termino.lower() in producto.nombre.lower():
            productos_encontrados.append(producto)

    if productos_encontrados:
        console.print(
            f"\n[bold green]✔ Se encontraron {len(productos_encontrados)} producto(s):[/bold green]"
        )
        mostrar_lista(f"Productos que contienen '{termino}'", productos_encontrados)
    else:
        console.print(
            f"\n[bold yellow]⚠ No se encontraron productos que contengan '{termino}'.[/bold yellow]"
        )
        # Mostrar sugerencias
        sugerencias = []
        for producto in productos:
            if any(
                palabra in producto.nombre.lower()
                for palabra in termino.lower().split()
            ):
                sugerencias.append(producto)

        if sugerencias:
            console.print("\n[bold cyan]Sugerencias:[/bold cyan]")
            mostrar_lista("Productos similares", sugerencias)

    pausa()


# ---------------------- GENERAR REPORTE DE VENTAS ----------------------
def manejar_generar_reporte():
    console.print(
        Panel.fit(
            "📊  [bold bright_cyan]Generar Reporte de Ventas[/bold bright_cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )

    # cargamos pedidos actuales desde tienda_app (ya inicializado)
    pedidos = tienda_app.pedidos

    # Submenu de opciones
    while True:
        menu_tabla = Table.grid(padding=(0, 1))
        menu_tabla.add_column(justify="center", width=3)
        menu_tabla.add_column()
        menu_tabla.add_row("1", "[bold]Ver resumen general[/bold]")
        menu_tabla.add_row("2", "[bold]Filtrar por fecha[/bold] (rango)")
        menu_tabla.add_row(
            "3", "[bold]Estadísticas históricas[/bold] (por mes / top productos)"
        )
        menu_tabla.add_row("4", "[bold]Exportar a Excel (.xlsx)[/bold]")
        menu_tabla.add_row("5", "[bold]Exportar a PDF[/bold]")
        menu_tabla.add_row("0", "[bold]Volver[/bold]")
        console.print(
            Panel(
                Align.left(menu_tabla),
                title="[bold cyan]Opciones de Reporte[/bold cyan]",
                box=box.ROUNDED,
                border_style="bright_green",
            )
        )

        opcion = console.input(
            "\n[bold cyan]>>> Seleccione una opción: [/bold cyan]"
        ).strip()
        if opcion == "0":
            break

        # --- resumen general ---
        if opcion == "1":
            if not pedidos:
                console.print(
                    "[bold yellow]⚠ No hay pedidos registrados.[/bold yellow]"
                )
                pausa()
                continue

            total_vendido = sum(p.get("total_pedido", 0) for p in pedidos)
            total_pedidos = len(pedidos)
            clientes_unicos = len(set(p.get("id_cliente") for p in pedidos))
            # tabla resumen
            tabla_resumen = Table(
                show_header=True, header_style="bold green", box=box.SIMPLE
            )
            tabla_resumen.add_column("Métrica", style="cyan")
            tabla_resumen.add_column("Valor", style="white", justify="right")
            tabla_resumen.add_row("Pedidos Totales", str(total_pedidos))
            tabla_resumen.add_row("Clientes distintos", str(clientes_unicos))
            tabla_resumen.add_row("Total vendido", f"$ {total_vendido:.2f}")
            console.print(tabla_resumen)
            pausa()
            continue

        # --- filtrar por fecha ---
        if opcion == "2":
            desde = console.input(
                "Fecha desde (YYYY-MM-DD, vacío = sin límite): "
            ).strip()
            hasta = console.input(
                "Fecha hasta  (YYYY-MM-DD, vacío = sin límite): "
            ).strip()
            desde_val = desde if desde else None
            hasta_val = hasta if hasta else None
            pedidos_filtrados = PersistenciaJSON.filtrar_pedidos_por_fecha(
                pedidos, desde=desde_val, hasta=hasta_val
            )
            if not pedidos_filtrados:
                console.print(
                    "[bold yellow]⚠ No se encontraron pedidos en ese rango.[/bold yellow]"
                )
                pausa()
                continue
            # Mostrar tabla compacta de pedidos filtrados
            tabla = Table(
                title="[bold cyan]Pedidos (filtrados)[/bold cyan]",
                show_header=True,
                header_style="bold green",
                box=box.SIMPLE,
            )
            tabla.add_column("ID", style="cyan", width=6, justify="center")
            tabla.add_column("Fecha", style="white", width=19, justify="center")
            tabla.add_column("Cliente", style="white")
            tabla.add_column("Total", style="yellow", justify="right", width=12)
            for p in pedidos_filtrados:
                tabla.add_row(
                    str(p.get("id_pedido")),
                    p.get("fecha_pedido", ""),
                    p.get("nombre_cliente", ""),
                    f"$ {p.get('total_pedido', 0):.2f}",
                )
            console.print(tabla)
            pausa()
            continue

        # --- estadísticas históricas (por mes, top productos) ---
        if opcion == "3":
            if not pedidos:
                console.print(
                    "[bold yellow]⚠ No hay pedidos para generar estadísticas.[/bold yellow]"
                )
                pausa()
                continue

            # ventas por mes
            from collections import defaultdict, Counter

            ventas_por_mes = defaultdict(float)
            productos_counter = Counter()
            ventas_por_cliente = defaultdict(float)

            for p in pedidos:
                fecha = p.get("fecha_pedido", "")
                try:
                    dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    try:
                        dt = datetime.strptime(fecha, "%Y-%m-%d")
                    except Exception:
                        continue
                key_mes = f"{dt.year}-{dt.month:02d}"
                ventas_por_mes[key_mes] += float(p.get("total_pedido", 0))
                ventas_por_cliente[p.get("nombre_cliente", "Desconocido")] += float(
                    p.get("total_pedido", 0)
                )
                for it in p.get("items", []):
                    productos_counter.update(
                        {it.get("nombre", "SinNombre"): int(it.get("cantidad", 0))}
                    )

            # Mostrar ventas por mes en tabla compacta
            tabla_mes = Table(
                title="[bold cyan]Ventas por Mes[/bold cyan]",
                show_header=True,
                header_style="bold green",
                box=box.SIMPLE,
            )
            tabla_mes.add_column("Mes", style="cyan")
            tabla_mes.add_column("Ventas", style="yellow", justify="right")
            for mes, monto in sorted(ventas_por_mes.items()):
                tabla_mes.add_row(mes, f"$ {monto:.2f}")
            console.print(tabla_mes)

            # Top productos vendidos (por unidades)
            tabla_top = Table(
                title="[bold cyan]Top Productos (unidades vendidas)[/bold cyan]",
                show_header=True,
                header_style="bold green",
                box=box.SIMPLE,
            )
            tabla_top.add_column("Producto", style="white")
            tabla_top.add_column("Unidades", style="yellow", justify="right")
            for prod, cnt in productos_counter.most_common(10):
                tabla_top.add_row(prod, str(cnt))
            console.print(tabla_top)

            # Top clientes por monto
            tabla_clientes = Table(
                title="[bold cyan]Top Clientes (por monto)[/bold cyan]",
                show_header=True,
                header_style="bold green",
                box=box.SIMPLE,
            )
            tabla_clientes.add_column("Cliente", style="white")
            tabla_clientes.add_column("Total Comprado", style="yellow", justify="right")
            for cliente, monto in sorted(
                ventas_por_cliente.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                tabla_clientes.add_row(cliente, f"$ {monto:.2f}")
            console.print(tabla_clientes)

            pausa()
            continue

        # --- exportar Excel ---
        if opcion == "4":
            if not pedidos:
                console.print(
                    "[bold yellow]⚠ No hay pedidos para exportar.[/bold yellow]"
                )
                pausa()
                continue
            archivo = (
                console.input(
                    "Nombre archivo destino (ej: reporte_pedidos.xlsx): "
                ).strip()
                or "reporte_pedidos.xlsx"
            )
            try:
                PersistenciaJSON.exportar_pedidos_excel(archivo, pedidos)
                console.print(
                    f"[bold green]✔ Exportado a Excel: {archivo}[/bold green]"
                )
            except Exception as e:
                console.print(f"[bold red]✗ Error exportando a Excel:[/bold red] {e}")
            pausa()
            continue

        # --- exportar PDF ---
        if opcion == "5":
            if not pedidos:
                console.print(
                    "[bold yellow]⚠ No hay pedidos para exportar.[/bold yellow]"
                )
                pausa()
                continue
            archivo = (
                console.input(
                    "Nombre archivo destino (ej: reporte_pedidos.pdf): "
                ).strip()
                or "reporte_pedidos.pdf"
            )
            try:
                PersistenciaJSON.exportar_pedidos_pdf(
                    archivo, pedidos, titulo="Reporte de Pedidos"
                )
                console.print(f"[bold green]✔ Exportado a PDF: {archivo}[/bold green]")
            except Exception as e:
                console.print(f"[bold red]✗ Error exportando a PDF:[/bold red] {e}")
            pausa()
            continue

        console.print("[bold red]✗ Opción no válida. Intente de nuevo.[/bold red]")
        pausa()


# ---------------------- MAIN LOOP ----------------------
if __name__ == "__main__":
    while True:
        mostrar_menu()
        opcion = console.input(
            "\n[bold cyan]>>> Seleccione una opción: [/bold cyan]"
        ).strip()

        if opcion == "1":
            manejar_crud_productos()
        elif opcion == "2":
            manejar_crud_clientes()
        elif opcion == "3":
            manejar_crear_pedido()
        elif opcion == "4":
            mostrar_historial_pedidos()
        elif opcion == "5":
            manejar_buscar_productos()
        elif opcion == "6":
            manejar_generar_reporte()
        elif opcion == "0":
            console.clear()

            # Mensaje inicial de cierre
            console.print(
                Align.center(
                    Panel(
                        " [bold green]Cerrando aplicación...[/bold green]",
                        border_style="green",
                        box=box.ROUNDED,
                        padding=(1, 2),
                    )
                )
            )

            # Barra de progreso centrada
            with Progress(
                TextColumn("{task.description}"),
                BarColumn(bar_width=40, complete_style="green"),
                TextColumn("[green]{task.percentage:>3.0f}%[/green]"),
                transient=True,
                console=console,
                expand=False,
            ) as progress:
                tarea = progress.add_task("Procesando cierre...", total=100)
                for _ in range(100):
                    sleep(0.015)
                    progress.advance(tarea)

            sleep(0.3)
            console.clear()

            # Mensaje final centrado y estético
            despedida = Group(
                Align.center(
                    Text("Aplicación cerrada correctamente", style="bold green")
                ),
                Align.center(Text("by Proyecto No. 1", style="italic yellow")),
            )
            console.print(
                Align.center(
                    Panel(
                        despedida, border_style="green", box=box.ROUNDED, padding=(1, 2)
                    )
                )
            )

            sleep(1.5)
            console.clear()
            break
