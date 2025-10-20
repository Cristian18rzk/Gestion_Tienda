import csv
import json
from builtins import FileNotFoundError


# =======================
# Lógica de Persistencia CSV
# =======================

class PersistenciaCSV:
    """Maneja la lectura y escritura en archivos CSV para Productos y Clientes."""

    @staticmethod
    def leer_datos(nombre_archivo, campos):
        datos = []
        try:
            with open(nombre_archivo, mode='r', newline='', encoding='utf-8') as file:
                # Usamos DictReader para leer filas como diccionarios
                reader = csv.DictReader(file, fieldnames=campos)
                next(reader, None)  # Saltar la línea de encabezado si existe
                for row in reader:
                    datos.append(row)
        except FileNotFoundError:
            # Crea el archivo con encabezados si no existe
            PersistenciaCSV.escribir_datos(nombre_archivo, [], campos)
        return datos

    @staticmethod
    def escribir_datos(nombre_archivo, lista_objetos, campos):
        """Escribe una lista de objetos (con método .to_dict()) al CSV."""
        with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=campos)
            writer.writeheader()
            for obj in lista_objetos:
                writer.writerow(obj.to_dict())


# =======================
# Lógica de Persistencia JSON
# =======================

class PersistenciaJSON:
    """Maneja la lectura y escritura en archivos JSON para Pedidos."""

    @staticmethod
    def leer_pedidos(nombre_archivo):
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(
                f"[bold yellow]Advertencia:[/bold yellow] Archivo '{nombre_archivo}' vacío o corrupto. Inicializando lista de pedidos vacía.")
            return []

    @staticmethod
    def escribir_pedidos(nombre_archivo, pedidos):
        with open(nombre_archivo, 'w', encoding='utf-8') as file:
            # Usamos indent=4 para que el JSON sea legible
            json.dump(pedidos, file, indent=4)