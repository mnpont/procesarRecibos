import os
import json      # Módulo estándar para leer y parsear archivos en formato JSON a diccionarios Python
import glob      # Módulo estándar para buscar archivos en el sistema usando patrones (ej: "*.json")
import pandas as pd  # Librería para crear y manipular tablas de datos, y exportarlas a CSV u otros formatos


# =============================================================================
# CONFIGURACIÓN
# Define las rutas de entrada y salida. Modificar estos valores si cambia
# la ubicación de los archivos o el nombre del CSV resultante.
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_JSONS = os.path.join(BASE_DIR, "tickets/")
ARCHIVO_SALIDA = os.path.join(BASE_DIR, "tickets_output.csv")


# =============================================================================
# CARGA DE ARCHIVOS JSON
# glob.glob devuelve una lista con todas las rutas que coincidan con el patrón
# indicado (en este caso, todos los .json dentro de la carpeta). Por cada
# archivo encontrado, se abre y se parsea su contenido a un diccionario Python
# usando json.load(). Todos los diccionarios se acumulan en la lista `receipts`.
# =============================================================================
receipts = []

for filepath in glob.glob(f"{CARPETA_JSONS}*.json"):
    with open(filepath, encoding="utf-8") as f:
        receipts.append(json.load(f))


# =============================================================================
# ORDENAMIENTO Y ASIGNACIÓN DE RECEIPT_ID
# Los tickets se ordenan por el campo "fecha" (formato YYYY-MM-DD). Este formato
# ISO 8601 tiene la propiedad de ordenar correctamente como string, sin necesidad
# de convertirlo a objeto datetime. Una vez ordenados del más antiguo al más
# reciente, se asigna un ID secuencial con relleno de ceros a la izquierda
# (00001, 00002, ...) usando formato de string f"{i:05d}".
# =============================================================================
receipts.sort(key=lambda x: x["fecha"])

for i, receipt in enumerate(receipts, start=1):
    receipt["receipt_id"] = f"{i:05d}"


# =============================================================================
# APLANAMIENTO DE ÍTEMS (JSON anidado → filas planas)
# Cada ticket contiene una lista de ítems en el campo "items". Como CSV es un
# formato plano (una fila por registro), se "expande" esa lista: por cada ítem
# se genera una fila separada que combina los datos del ticket (receipt_id, fecha,
# comercio, etc.) con los datos del ítem (descripcion, precio_unitario, total_item).
# Los campos del ticket se repiten en cada fila para mantener la trazabilidad
# completa — es decir, siempre se puede saber a qué ticket pertenece cada ítem.
# =============================================================================
rows = []

for receipt in receipts:
    for item in receipt.get("items", []):   # .get() evita error si "items" no existe
        rows.append({
            "receipt_id":       receipt["receipt_id"],
            "fecha":            receipt["fecha"],
            "comercio":         receipt["comercio"],
            "categoria":        receipt["categoria"],
            "descripcion":      item["descripcion"],
            "precio_unitario":  item["precio_unitario"],
            "total_item":       item["total_item"],
            "iva":              receipt["iva"],              # Puede ser null → None en Python
            "iva_discriminado": receipt["iva_discriminado"],
            "total_ticket":     receipt["total"]
        })


# =============================================================================
# CREACIÓN DEL DATAFRAME Y EXPORTACIÓN A CSV
# pd.DataFrame convierte la lista de diccionarios en una tabla estructurada,
# donde cada clave se vuelve una columna y cada diccionario una fila.
# .to_csv() exporta esa tabla al archivo definido en ARCHIVO_SALIDA.
#   - index=False: evita que pandas agregue una columna extra con su índice interno
#   - encoding="utf-8-sig": agrega el BOM (Byte Order Mark) necesario para que
#     Excel interprete correctamente caracteres como ñ, tildes y otros del español
# =============================================================================
df = pd.DataFrame(rows)
df.to_csv(ARCHIVO_SALIDA, index=False, encoding="utf-8-sig")


# =============================================================================
# RESUMEN DE EJECUCIÓN
# Imprime un resumen para confirmar que el proceso terminó correctamente,
# indicando cuántos tickets se procesaron y cuántas filas tiene el CSV final.
# =============================================================================
print(f"✓ CSV generado: {ARCHIVO_SALIDA}")
print(f"  {len(receipts)} tickets procesados → {len(df)} filas en el CSV")
