def crear_abertura(SapModel, datos, modulos, areas_modulos, links_modulos, ejes):
    """Gestiona la abertura del tunel. Devuelve areas_nuevas_nombres."""

    opening = datos["opening"]
    if opening != "Yes":
        return []

    eje_long            = datos["eje_long"]
    side                = datos["side"]
    method              = datos["method"]
    Z_max_opening       = datos["Z_max_opening"]
    Z_min_opening       = datos["Z_min_opening"]
    n_modulos_completos = datos["n_modulos_completos"]
    ancho_extra         = datos["ancho_extra"]
    Numero_modulos      = int(datos["param"]["nº de módulos:"])

    prop_area   = ejes["prop_area"]
    spring_defs = ejes["spring_defs"]
    Vec         = ejes["Vec"]
    area_plane  = ejes["area_plane"]
    PlDir_area  = ejes["PlDir_area"]
    PlPt_area   = ejes["PlPt_area"]
    PlVect_area = ejes["PlVect_area"]
    joint_plane = ejes["joint_plane"]
    AxDir_jt    = ejes["AxDir_jt"]
    AxPt_jt     = ejes["AxPt_jt"]
    AxVect_jt   = ejes["AxVect_jt"]
    PlDir_jt    = ejes["PlDir_jt"]
    PlPt_jt     = ejes["PlPt_jt"]
    PlVect_jt   = ejes["PlVect_jt"]

    # ── Determinar lado ───────────────────────────────────────────────
    if eje_long == "Y":
        lado = (lambda t: t > 0) if side == "Right (x>0)" else (lambda t: t < 0)
    else:
        lado = (lambda t: t < 0) if side == "Right (x>0)" else (lambda t: t > 0)


