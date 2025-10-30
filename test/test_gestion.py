import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from gestion import Producto, Cliente, Tienda


# -------------------------------
# PRUEBAS CLASE PRODUCTO
# -------------------------------

def test_producto_str():
    p = Producto(1, "Martillo", 25000, 10)
    esperado = "ID: 1 | Nombre: Martillo | Precio: $25000.00 | Stock: 10"
    assert str(p) == esperado


def test_producto_to_dict():
    p = Producto(2, "Clavos", 1500, 100)
    esperado = {'id_producto': 2, 'nombre': 'Clavos', 'precio': 1500.0, 'stock': 100}
    assert p.to_dict() == esperado


# -------------------------------
# PRUEBAS CLASE CLIENTE
# -------------------------------

def test_cliente_str():
    c = Cliente(1, "Juan Pérez", "juan@example.com")
    esperado = "ID: 1 | Nombre: Juan Pérez | Email: juan@example.com"
    assert str(c) == esperado


def test_cliente_to_dict():
    c = Cliente(2, "Ana Gómez", "ana@example.com")
    esperado = {'id_cliente': 2, 'nombre': 'Ana Gómez', 'email': 'ana@example.com'}
    assert c.to_dict() == esperado


# -------------------------------
# PRUEBAS CLASE TIENDA
# -------------------------------

@pytest.fixture
def tienda_vacia():
    """Crea una instancia de Tienda sin depender de archivos."""
    with patch("persistencia.PersistenciaCSV.leer_datos", return_value=[]), \
         patch("persistencia.PersistenciaJSON.leer_pedidos", return_value=[]):
        return Tienda()


def test_agregar_producto(tienda_vacia):
    with patch.object(tienda_vacia, "_guardar_productos", return_value=None):
        tienda_vacia.agregar_producto("Destornillador", 5000, 20)
        assert len(tienda_vacia.productos) == 1
        producto = list(tienda_vacia.productos.values())[0]
        assert producto.nombre == "Destornillador"
        assert producto.precio == 5000
        assert producto.stock == 20


def test_actualizar_producto_existente(tienda_vacia):
    tienda_vacia.productos = {1: Producto(1, "Martillo", 25000, 10)}
    with patch.object(tienda_vacia, "_guardar_productos", return_value=None):
        actualizado = tienda_vacia.actualizar_producto(1, nombre="Martillo XL", precio=30000, stock=5)
        assert actualizado is True
        p = tienda_vacia.productos[1]
        assert p.nombre == "Martillo XL"
        assert p.precio == 30000
        assert p.stock == 5


def test_actualizar_producto_inexistente(tienda_vacia):
    with patch.object(tienda_vacia, "_guardar_productos", return_value=None):
        resultado = tienda_vacia.actualizar_producto(999, nombre="Ficticio")
        assert resultado is False


def test_eliminar_producto(tienda_vacia):
    tienda_vacia.productos = {1: Producto(1, "Martillo", 25000, 10)}
    with patch.object(tienda_vacia, "_guardar_productos", return_value=None):
        eliminado = tienda_vacia.eliminar_producto(1)
        assert eliminado is True
        assert len(tienda_vacia.productos) == 0


def test_eliminar_producto_inexistente(tienda_vacia):
    with patch.object(tienda_vacia, "_guardar_productos", return_value=None):
        eliminado = tienda_vacia.eliminar_producto(999)
        assert eliminado is False


def test_crear_pedido_exitoso(tienda_vacia):
    tienda_vacia.clientes = {1: Cliente(1, "Juan", "juan@example.com")}
    tienda_vacia.productos = {1: Producto(1, "Clavos", 1000, 10)}

    with patch.object(tienda_vacia, "_guardar_productos", return_value=None), \
         patch.object(tienda_vacia, "_guardar_pedidos", return_value=None):
        tienda_vacia.crear_pedido(1, {"1": 2})
        assert len(tienda_vacia.pedidos) == 1
        pedido = tienda_vacia.pedidos[0]
        assert pedido["id_cliente"] == 1
        assert pedido["total_pedido"] == 2000.0
        assert tienda_vacia.productos[1].stock == 8





def test_buscar_productos_por_nombre(tienda_vacia):
    tienda_vacia.productos = {
        1: Producto(1, "Martillo", 25000, 10),
        2: Producto(2, "Clavos", 1000, 100)
    }
    resultados = tienda_vacia.buscar_productos_por_nombre("mart")
    assert len(resultados) == 1
    assert resultados[0].nombre == "Martillo"


def test_generar_reporte_ventas(tienda_vacia):
    tienda_vacia.pedidos = [
        {"id_pedido": 1, "total_pedido": 5000},
        {"id_pedido": 2, "total_pedido": 3000}
    ]
    total = tienda_vacia.generar_reporte_ventas()
    assert total == 8000
