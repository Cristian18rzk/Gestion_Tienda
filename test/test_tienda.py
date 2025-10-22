import pytest
from gestion import Tienda, Producto, Cliente

@pytest.fixture
def tienda_vacia(monkeypatch):
    tienda = Tienda()
    tienda.productos = {}
    tienda.clientes = {1: Cliente(1, "Cristian Rodriguez", "Cristiank18@gmail.com")}
    tienda.pedidos = []
    monkeypatch.setattr(tienda, "_guardar_productos", lambda: None)
    monkeypatch.setattr(tienda, "_guardar_pedidos", lambda: None)
    return tienda


def test_creacion_producto():
    producto = Producto(60, "Arroz", 12000, 15)
    assert producto.nombre == "Arroz"
    assert producto.precio == 12000
    assert producto.stock == 15


def test_creacion_cliente():
    cliente = Cliente(1, "Mariana Zapata", "mariana@gmail.com")
    assert cliente.nombre == "Mariana Zapata"
    assert "@" in cliente.email


def test_agregar_producto(tienda_vacia):
    tienda_vacia.agregar_producto("Pan", 500, 15)
    assert len(tienda_vacia.productos) == 1
    p = list(tienda_vacia.productos.values())[0]
    assert p.nombre == "Pan"
    assert p.precio == 500


def test_agregar_producto_duplicado(tienda_vacia):
    tienda_vacia.agregar_producto("Pan", 500, 10)
    exito = tienda_vacia.agregar_producto("Pan", 500, 10)
    assert not exito or len(tienda_vacia.productos) == 1


def test_actualizar_producto(tienda_vacia):
    tienda_vacia.productos = {1: Producto(1, "Pan", 500, 15)}
    exito = tienda_vacia.actualizar_producto(1, nombre="Pan Integral", precio=700)
    assert exito
    assert tienda_vacia.productos[1].nombre == "Pan Integral"
    assert tienda_vacia.productos[1].precio == 700


def test_actualizar_producto_inexistente(tienda_vacia):
    exito = tienda_vacia.actualizar_producto(99, nombre="Ficticio")
    assert not exito


def test_eliminar_producto(tienda_vacia):
    tienda_vacia.productos = {1: Producto(1, "Pan", 500, 5)}
    exito = tienda_vacia.eliminar_producto(1)
    assert exito
    assert len(tienda_vacia.productos) == 0


def test_eliminar_producto_inexistente(tienda_vacia):
    exito = tienda_vacia.eliminar_producto(999)
    assert not exito


def test_crear_pedido_y_reporte(tienda_vacia):
    tienda_vacia.productos = {
        1: Producto(1, "Arroz", 12000, 15),
        2: Producto(2, "Pan", 500, 15)
    }
    tienda_vacia.crear_pedido(1, {1: 2, 2: 3})
    assert len(tienda_vacia.pedidos) == 1
    pedido = tienda_vacia.pedidos[0]
    assert pedido["total_pedido"] == pytest.approx(2 * 12000 + 3 * 500)
    total_reporte = tienda_vacia.generar_reporte_ventas()
    assert total_reporte == pedido["total_pedido"]


def test_crear_pedido_cliente_inexistente(tienda_vacia):
    tienda_vacia.productos = {1: Producto(1, "Pan", 500, 5)}
    exito = tienda_vacia.crear_pedido(999, {1: 2})
    assert not exito


def test_crear_pedido_stock_insuficiente(tienda_vacia):
    tienda_vacia.productos = {1: Producto(1, "Pan", 500, 1)}
    exito = tienda_vacia.crear_pedido(1, {1: 3})
    assert not exito


def test_generar_reporte_sin_pedidos(tienda_vacia):
    total = tienda_vacia.generar_reporte_ventas()
    assert total == 0


def test_buscar_producto_por_nombre(tienda_vacia):
    tienda_vacia.productos = {
        1: Producto(1, "Arroz", 12000, 15),
        2: Producto(2, "Pan", 500, 15)
    }
    resultados = tienda_vacia.buscar_productos_por_nombre("pan")
    assert len(resultados) == 1
    assert resultados[0].nombre == "Pan"