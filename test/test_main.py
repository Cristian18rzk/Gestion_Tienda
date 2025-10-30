import builtins
import pytest
from main import leer_int, leer_float, mostrar_lista, tienda_app, Producto, Cliente

def test_leer_int_vacio_permitido(monkeypatch):
    monkeypatch.setattr("rich.console.Console.input", lambda self, _: "")
    assert leer_int("Ingrese:", permitir_vacio=True) is None



# ---------- TEST leer_float ----------
def test_leer_float_valido(monkeypatch):
    monkeypatch.setattr("rich.console.Console.input", lambda self, _: "3.14")
    assert leer_float("Ingrese un decimal: ") == 3.14


def test_leer_float_vacio_permitido(monkeypatch):
    monkeypatch.setattr("rich.console.Console.input", lambda self, _: "")
    assert leer_float("Ingrese:", permitir_vacio=True) is None


def test_leer_float_invalido(monkeypatch, capsys):
    monkeypatch.setattr("rich.console.Console.input", lambda self, _: "abc")
    assert leer_float("Ingrese: ") is None
    salida = capsys.readouterr().out
    assert "Entrada inválida" in salida


# ---------- TEST mostrar_lista ----------
def test_mostrar_lista_productos(capsys):
    productos = [
        Producto(1, "Martillo", 10000, 5),
        Producto(2, "Clavos", 2000, 50)
    ]
    mostrar_lista("Productos", productos)
    salida = capsys.readouterr().out
    assert "Martillo" in salida
    assert "Clavos" in salida


def test_mostrar_lista_clientes(capsys):
    clientes = [
        Cliente(1, "Juan", "juan@test.com"),
        Cliente(2, "Camila", "camila@test.com")
    ]
    mostrar_lista("Clientes", clientes)
    salida = capsys.readouterr().out
    assert "Juan" in salida
    assert "camila@test.com" in salida

