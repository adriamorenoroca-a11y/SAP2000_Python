import comtypes


def crear_nodos_areas(SapModel, datos):
    """Crea nodos, anillos, modulos, areas y springs. Devuelve (modulos, areas_modulos, ejes)."""

    eje_long = datos["eje_long"]
    param    = datos["param"]

    Z_clave                            = float(param["Radio (eje):"])
    Nodos_por_anillo                   = int(param["nº de puntos en un circulo:"])
    Longitud_mallazo_en_longitudinal   = float(param["Longitud mallazo en longitudinal:"])
    n_areas_por_anillo_en_longitudinal = int(param["nº areas por anillo en longitudinal:"])
    Numero_modulos                     = int(param["nº de módulos:"])
    Separacion_modulos                 = float(param["Separación entre módulos:"])
    Nodos_entre_conectores             = int(param["nº de barras entre conectores:"])

    print(f"Módulos: {Numero_modulos} | Nodos/anillo: {Nodos_por_anillo} | Sep. módulos: {Separacion_modulos}")
