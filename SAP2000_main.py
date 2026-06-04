from SAP2000_conexion    import conectar_sap
from SAP2000_excel       import leer_excel
from SAP2000_materiales  import crear_materiales, crear_secciones, crear_armaduras
from SAP2000_geometria   import crear_nodos_areas
from SAP2000_cargas      import crear_load_patterns, crear_load_cases, aplicar_cargas
from SAP2000_links       import crear_propiedades_links, crear_links
from SAP2000_abertura    import crear_abertura


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

    # ── 5. Load Patterns + Load Cases ─────────────────────────────────
    crear_load_patterns(SapModel, datos)
    crear_load_cases(SapModel, datos)

    # ── 6. Links ──────────────────────────────────────────────────────
    links_modulos = crear_propiedades_links(SapModel, datos)
    links_modulos = crear_links(SapModel, datos, modulos, links_modulos, ejes)

    # ── 7. Abertura ───────────────────────────────────────────────────
    areas_nuevas_nombres = crear_abertura(SapModel, datos, modulos, areas_modulos, links_modulos, ejes)

if __name__ == "__main__":
    generar_modelo(r"C:\Users\adrim\OneDrive\Escritorio\SAP2000_Python\Coordenadas_Nodos.xlsx")
