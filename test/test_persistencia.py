import os
import json
import tempfile
import pytest
from persistencia import PersistenciaCSV, PersistenciaJSON


class DummyObjeto:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

    def to_dict(self):
        return {"id": self.id, "nombre": self.nombre}




def test_escribir_y_leer_csv(tmp_path):
    """Debe escribir y luego leer correctamente un archivo CSV."""
    archivo = tmp_path / "productos.csv"
    campos = ["id", "nombre"]
    objetos = [DummyObjeto(1, "Martillo"), DummyObjeto(2, "Clavo")]

    PersistenciaCSV.escribir_datos(archivo, objetos, campos)
    assert os.path.exists(archivo)

    datos = PersistenciaCSV.leer_datos(archivo, campos)
    assert isinstance(datos, list)
    assert len(datos) == 2
    assert datos[0]["nombre"] == "Martillo"


def test_leer_csv_inexistente(tmp_path):
    """Si el archivo no existe, debe crearlo con encabezados."""
    archivo = tmp_path / "nuevo.csv"
    campos = ["id", "nombre"]
    datos = PersistenciaCSV.leer_datos(archivo, campos)
    assert datos == []
    assert os.path.exists(archivo)

def test_escribir_y_leer_json(tmp_path):
    """Debe escribir y leer correctamente un archivo JSON."""
    archivo = tmp_path / "pedidos.json"
    pedidos = [{"id_pedido": 1, "cliente": "Juan"}]

    PersistenciaJSON.escribir_pedidos(archivo, pedidos)
    assert os.path.exists(archivo)

    leidos = PersistenciaJSON.leer_pedidos(archivo)
    assert leidos[0]["cliente"] == "Juan"


def test_leer_json_inexistente(tmp_path):
    """Si el archivo JSON no existe, debe devolver una lista vacía."""
    archivo = tmp_path / "no_existe.json"
    datos = PersistenciaJSON.leer_pedidos(archivo)
    assert datos == []


def test_leer_json_corrupto(tmp_path):
    """Si el JSON está corrupto, debe devolver una lista vacía."""
    archivo = tmp_path / "corrupto.json"
    archivo.write_text("{no_valido}", encoding="utf-8")
    resultado = PersistenciaJSON.leer_pedidos(archivo)
    assert resultado == []


def test_exportar_excel(tmp_path):
    """Debe generar un archivo Excel (.xlsx) con pedidos."""
    archivo = tmp_path / "pedidos.xlsx"
    pedidos = [{
        "id_pedido": 1,
        "id_cliente": 10,
        "nombre_cliente": "Carlos",
        "fecha_pedido": "2025-10-29",
        "total_pedido": 30000,
        "items": [
            {"id_producto": 1, "nombre": "Martillo", "cantidad": 2, "precio_unitario": 15000, "subtotal": 30000}
        ]
    }]
    PersistenciaJSON.exportar_pedidos_excel(archivo, pedidos)
    assert os.path.exists(archivo)
    assert archivo.stat().st_size > 0

def test_filtrar_pedidos_por_fecha():
    pedidos = [
        {"fecha": "2025-01-01"},
        {"fecha": "2025-02-01"},
        {"fecha": "2025-03-01"},
    ]
    filtrados = PersistenciaJSON.filtrar_pedidos_por_fecha(pedidos, "2025-01-15", "2025-02-15")
    assert len(filtrados) == 1
    assert filtrados[0]["fecha"] == "2025-02-01"


def test_filtrar_pedidos_por_fecha_vacios():
    """Si las fechas son inválidas o fuera de rango, debe devolver lista vacía."""
    pedidos = [{"fecha": "no_valida"}]
    resultado = PersistenciaJSON.filtrar_pedidos_por_fecha(pedidos, "2025-01-01", "2025-12-31")
    assert resultado == []
