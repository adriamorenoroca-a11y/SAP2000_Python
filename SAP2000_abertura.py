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

    # ── Modulos afectados ─────────────────────────────────────────────
    centro          = Numero_modulos // 2
    mitad_inf       = n_modulos_completos // 2
    mitad_sup       = n_modulos_completos - mitad_inf
    idx_completos   = list(range(centro - mitad_inf, centro + mitad_sup))
    idx_parcial_inf = idx_completos[0] - 1
    idx_parcial_sup = idx_completos[-1] + 1

    print(f"Módulos completos abiertos: {[m+1 for m in idx_completos]}")
    print(f"Módulos parciales: {idx_parcial_inf+1} y {idx_parcial_sup+1}")

    # ── Limites longitudinales de cada modulo ─────────────────────────
    Y_limites_modulos = {}
    for m, anillos_modulo in enumerate(modulos):
        todos_long = []
        for anillo in anillos_modulo:
            for nodo in anillo:
                x, y, z, ret = SapModel.PointObj.GetCoordCartesian(nodo)
                todos_long.append(x if eje_long == "X" else y)
        Y_limites_modulos[m] = (min(todos_long), max(todos_long))

    print("Y limites modulos:", {m+1: v for m, v in Y_limites_modulos.items()})

    areas_nuevas_nombres = []

    if method == "Snap to nodes":
        areas_nuevas_nombres = _snap_to_nodes(
            SapModel, datos, modulos, areas_modulos, links_modulos,
            lado, idx_completos, idx_parcial_inf, idx_parcial_sup,
            Y_limites_modulos, Z_max_opening, Z_min_opening, ancho_extra, eje_long
        )

    elif method == "Exact cut":
        areas_nuevas_nombres = _exact_cut(
            SapModel, datos, modulos, areas_modulos, links_modulos, ejes,
            lado, idx_completos, idx_parcial_inf, idx_parcial_sup,
            Y_limites_modulos, Z_max_opening, Z_min_opening, ancho_extra,
            eje_long, side, prop_area, spring_defs, Vec, area_plane,
            PlDir_area, PlPt_area, PlVect_area, joint_plane,
            AxDir_jt, AxPt_jt, AxVect_jt, PlDir_jt, PlPt_jt, PlVect_jt
        )

    return areas_nuevas_nombres

