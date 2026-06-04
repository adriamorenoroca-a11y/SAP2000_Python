from SAP2000_conexion    import conectar_sap
from SAP2000_excel       import leer_excel
from SAP2000_materiales  import crear_materiales, crear_secciones, crear_armaduras
from SAP2000_geometria   import crear_nodos_areas



def generar_modelo(ruta_excel):

    # ── 1. Conexión SAP2000 ───────────────────────────────────────────
    SapModel = conectar_sap()

    # ── 2. Lectura Excel ──────────────────────────────────────────────
    datos = leer_excel(ruta_excel)

    # ── 3. Materiales + Secciones + Armaduras ─────────────────────────
    crear_materiales(SapModel, datos)
    crear_secciones(SapModel, datos)
    crear_armaduras(SapModel, datos)

    # ── 4. Geometría (nodos, anillos, módulos, áreas, springs) ────────
    modulos, areas_modulos, ejes = crear_nodos_areas(SapModel, datos)

if __name__ == "__main__":
    generar_modelo(r"C:\Users\adria.moreno\OneDrive - Global Infrastructure\Python - SAP2000\Coordenadas_Nodos.xlsx")
