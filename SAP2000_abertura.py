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

def _snap_to_nodes(SapModel, datos, modulos, areas_modulos, links_modulos,
                   lado, idx_completos, idx_parcial_inf, idx_parcial_sup,
                   Y_limites_modulos, Z_max_opening, Z_min_opening, ancho_extra, eje_long):

    todos_z = set()
    for anillos_modulo in modulos:
        for anillo in anillos_modulo:
            for nodo in anillo:
                x, y, z, ret = SapModel.PointObj.GetCoordCartesian(nodo)
                todos_z.add(round(z, 6))

    todos_z    = sorted(todos_z)
    Z_max_snap = max((z for z in todos_z if z <= Z_max_opening), default=None)
    Z_min_snap = min((z for z in todos_z if z >= Z_min_opening), default=None)
    print(f"Snap Z_max ajustado: {Z_max_snap} | Z_min ajustado: {Z_min_snap}")

    areas_a_eliminar = []

    for m, areas_modulo in enumerate(areas_modulos):
        if m not in idx_completos and m != idx_parcial_inf and m != idx_parcial_sup:
            continue

        for area_data in areas_modulo:
            area_name = area_data[1]
            n_pts, nodos, ret = SapModel.AreaObj.GetPoints(area_name)

            xs, ys, zs = [], [], []
            for nodo in nodos:
                x, y, z, ret = SapModel.PointObj.GetCoordCartesian(nodo)
                xs.append(x); ys.append(y); zs.append(z)

            x_c    = sum(xs) / n_pts
            y_c    = sum(ys) / n_pts
            z_c    = sum(zs) / n_pts
            long_c = x_c if eje_long == "X" else y_c
            trans_c= x_c if eje_long == "Y" else y_c

            if not lado(trans_c):
                continue
            if not (Z_min_snap <= z_c <= Z_max_snap):
                continue

            if m == idx_parcial_inf:
                long_ini, long_fin = Y_limites_modulos[m]
                if not (long_fin - long_c <= ancho_extra):
                    continue
            elif m == idx_parcial_sup:
                long_ini, long_fin = Y_limites_modulos[m]
                if not (long_c - long_ini <= ancho_extra):
                    continue

            areas_a_eliminar.append((area_name, list(nodos)))

    nodos_candidatos = set()
    for area_name, nodos_area in areas_a_eliminar:
        for nodo in nodos_area:
            nodos_candidatos.add(nodo)
        SapModel.AreaObj.Delete(area_name)

    print(f"Areas eliminadas: {len(areas_a_eliminar)}")


    # Eliminar links
    links_eliminados = 0
    for tipo, modulos_links in links_modulos.items():
        for m, lista_links in enumerate(modulos_links):
            if m not in [idx_parcial_inf, idx_completos[0] - 1] + \
                    list(range(idx_completos[0], idx_completos[-1] + 1)) + \
                    [idx_parcial_sup - 1]:
                continue

            for link in lista_links:
                link = str(link)
                x1, y1, z1, _ = SapModel.PointObj.GetCoordCartesian(SapModel.LinkObj.GetPoints(link)[0])
                x2, y2, z2, _ = SapModel.PointObj.GetCoordCartesian(SapModel.LinkObj.GetPoints(link)[1])

                x_c = (x1 + x2) / 2
                y_c = (y1 + y2) / 2
                z_c = (z1 + z2) / 2

                trans_c = x_c if eje_long == "Y" else y_c
                if not lado(trans_c):
                    continue
                if not (Z_min_snap <= z_c <= Z_max_snap):
                    continue

                SapModel.LinkObj.Delete(link)
                links_eliminados += 1

    print(f"Links eliminados: {links_eliminados}")

    # Eliminar nodos huerfanos
    nodos_eliminados = 0
    for nodo in nodos_candidatos:
        ret  = SapModel.PointObj.DeleteSpecialPoint(nodo)
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code == 0:
            nodos_eliminados += 1

    print(f"Nodos huerfanos eliminados: {nodos_eliminados}")
    return []

def _exact_cut(SapModel, datos, modulos, areas_modulos, links_modulos, ejes,
               lado, idx_completos, idx_parcial_inf, idx_parcial_sup,
               Y_limites_modulos, Z_max_opening, Z_min_opening, ancho_extra,
               eje_long, side, prop_area, spring_defs, Vec, area_plane,
               PlDir_area, PlPt_area, PlVect_area, joint_plane,
               AxDir_jt, AxPt_jt, AxVect_jt, PlDir_jt, PlPt_jt, PlVect_jt):

    Y_corte_inf = Y_limites_modulos[idx_parcial_inf][1] - ancho_extra
    Y_corte_sup = Y_limites_modulos[idx_parcial_sup][0] + ancho_extra
    print(f"Long_corte_inf: {Y_corte_inf:.3f} | Long_corte_sup: {Y_corte_sup:.3f}")

    def interpolar_nodo(nodo1, nodo2, corte, eje="Z"):
        x1, y1, z1, _ = SapModel.PointObj.GetCoordCartesian(nodo1)
        x2, y2, z2, _ = SapModel.PointObj.GetCoordCartesian(nodo2)

        if eje == "Z":
            if abs(z2 - z1) < 1e-9:
                return nodo1
            t = (corte - z1) / (z2 - z1)
        else:
            if eje_long == "Y":
                if abs(y2 - y1) < 1e-9:
                    return nodo1
                t = (corte - y1) / (y2 - y1)
            else:
                if abs(x2 - x1) < 1e-9:
                    return nodo1
                t = (corte - x1) / (x2 - x1)

        x_new = x1 + t * (x2 - x1)
        y_new = y1 + t * (y2 - y1)
        z_new = z1 + t * (z2 - z1)
        nombre, ret = SapModel.PointObj.AddCartesian(x_new, y_new, z_new)
        SapModel.PointObj.SetLocalAxesAdvanced(
            nombre, True, 1, "GLOBAL", AxDir_jt, AxPt_jt, AxVect_jt,
            joint_plane, 1, "GLOBAL", PlDir_jt, PlPt_jt, PlVect_jt
        )
        return nombre

    areas_a_eliminar = []
    areas_nuevas     = []

    for m, areas_modulo in enumerate(areas_modulos):
        if m not in idx_completos and m != idx_parcial_inf and m != idx_parcial_sup:
            continue

        for area_data in areas_modulo:
            area_name = area_data[1]
            n_pts, nodos, ret = SapModel.AreaObj.GetPoints(area_name)
            code = ret[-1] if isinstance(ret, (list, tuple)) else ret
            if code != 0 or n_pts == 0:
                continue

            coords = {}
            for nodo in nodos:
                x, y, z, _ = SapModel.PointObj.GetCoordCartesian(nodo)
                coords[nodo] = (x, y, z)

            n1, n2, n2_next, n1_next = nodos
            x1,  y1,  z1  = coords[n1]
            x2,  y2,  z2  = coords[n2]
            x2n, y2n, z2n = coords[n2_next]
            x1n, y1n, z1n = coords[n1_next]

            x_c    = (x1 + x2 + x2n + x1n) / 4
            y_c    = (y1 + y2 + y2n + y1n) / 4
            z_c    = (z1 + z2 + z2n + z1n) / 4
            trans_c= x_c if eje_long == "Y" else y_c
            long_c = x_c if eje_long == "X" else y_c
            long1  = x1 if eje_long == "X" else y1
            long2  = x2 if eje_long == "X" else y2

            if not lado(trans_c):
                continue

            cruza_Zmax = (z1 < Z_max_opening < z1n) or (z1n < Z_max_opening < z1)
            cruza_Zmin = (z1 > Z_min_opening > z1n) or (z1n > Z_min_opening > z1)

            cruza_Y = False
            Y_corte = None
            if m == idx_parcial_inf and long1 < Y_corte_inf < long2:
                cruza_Y = True; Y_corte = Y_corte_inf
            elif m == idx_parcial_sup and long1 < Y_corte_sup < long2:
                cruza_Y = True; Y_corte = Y_corte_sup

            dentro_Z = Z_min_opening <= z_c <= Z_max_opening
            if m == idx_parcial_inf:
                dentro_Y = long_c >= Y_corte_inf
            elif m == idx_parcial_sup:
                dentro_Y = long_c <= Y_corte_sup
            else:
                dentro_Y = True

            # CASO 1
            if dentro_Z and dentro_Y and not cruza_Zmax and not cruza_Zmin and not cruza_Y:
                areas_a_eliminar.append(area_name)

            # CASO 2
            elif cruza_Zmax and not cruza_Y and dentro_Y:
                n_za = interpolar_nodo(n1, n1_next, Z_max_opening, "Z")
                n_zb = interpolar_nodo(n2, n2_next, Z_max_opening, "Z")
                areas_a_eliminar.append(area_name)
                if z1 < Z_max_opening:
                    areas_nuevas.append(((n_za, n_zb, n2_next, n1_next), prop_area))
                else:
                    areas_nuevas.append(((n1, n2, n_zb, n_za), prop_area))

            # CASO 3
            elif cruza_Zmin and not cruza_Y and dentro_Y:
                n_za = interpolar_nodo(n1, n1_next, Z_min_opening, "Z")
                n_zb = interpolar_nodo(n2, n2_next, Z_min_opening, "Z")
                areas_a_eliminar.append(area_name)
                if z1 > Z_min_opening:
                    areas_nuevas.append(((n_za, n_zb, n2_next, n1_next), prop_area))
                else:
                    areas_nuevas.append(((n1, n2, n_zb, n_za), prop_area))

            # CASO 4
            elif cruza_Y and not cruza_Zmax and not cruza_Zmin and dentro_Z:
                n_ya = interpolar_nodo(n1, n2, Y_corte, "Y")
                n_yb = interpolar_nodo(n1_next, n2_next, Y_corte, "Y")
                areas_a_eliminar.append(area_name)
                if m == idx_parcial_inf:
                    areas_nuevas.append(((n1, n_ya, n_yb, n1_next), prop_area))
                else:
                    areas_nuevas.append(((n_ya, n2, n2_next, n_yb), prop_area))

            # CASO 5
            elif cruza_Zmax and cruza_Y:
                n_za  = interpolar_nodo(n1,    n1_next, Z_max_opening, "Z")
                n_zb  = interpolar_nodo(n2,    n2_next, Z_max_opening, "Z")
                n_ya  = interpolar_nodo(n1,    n2,      Y_corte, "Y")
                n_yb  = interpolar_nodo(n1_next, n2_next, Y_corte, "Y")
                n_yza = interpolar_nodo(n_za,  n_zb,    Y_corte, "Y")
                areas_a_eliminar.append(area_name)

                if m == idx_parcial_inf:
                    if z1 < Z_max_opening:
                        if side == "Right (x>0)":
                            areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                            areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                            areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                        else:
                            if eje_long == "Y":
                                areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                                areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                                areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                            else:
                                areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                                areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                                areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                    else:
                        areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                        areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                        areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                else:
                    if z1 < Z_max_opening:
                        if side == "Right (x>0)":
                            areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                            areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                            areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                        else:
                            if eje_long == "Y":
                                areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                                areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                                areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                            else:
                                areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                                areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                                areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                    else:
                        if side == "Right (x>0)":
                            if eje_long == "Y":
                                areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                                areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                                areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                            else:
                                areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                                areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                                areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                        else:
                            areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                            areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                            areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))

            # CASO 6
            elif cruza_Zmin and cruza_Y:
                n_za  = interpolar_nodo(n1,    n1_next, Z_min_opening, "Z")
                n_zb  = interpolar_nodo(n2,    n2_next, Z_min_opening, "Z")
                n_ya  = interpolar_nodo(n1,    n2,      Y_corte, "Y")
                n_yb  = interpolar_nodo(n1_next, n2_next, Y_corte, "Y")
                n_yza = interpolar_nodo(n_za,  n_zb,    Y_corte, "Y")
                areas_a_eliminar.append(area_name)

                if m == idx_parcial_inf:
                    if z1 > Z_min_opening:
                        areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                        areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                        areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                    else:
                        areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                        areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                        areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                else:
                    if z1 > Z_min_opening:
                        areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                        areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                        areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                    else:
                        if side == "Right (x>0)":
                            areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                            areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                            areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                        elif eje_long == "Y":
                            areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                            areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))
                            areas_nuevas.append(((n_za, n_yza, n_yb, n1_next), prop_area))
                        else:
                            areas_nuevas.append(((n2, n_zb, n_yza, n_ya), prop_area))
                            areas_nuevas.append(((n_zb, n2_next, n_yb, n_yza), prop_area))
                            areas_nuevas.append(((n1, n_ya, n_yza, n_za), prop_area))


    # Eliminar areas originales
    nodos_candidatos = set()
    for area_name in areas_a_eliminar:
        n_pts, nodos, ret = SapModel.AreaObj.GetPoints(area_name)
        for nodo in nodos:
            nodos_candidatos.add(nodo)
        SapModel.AreaObj.Delete(area_name)
    print(f"Areas eliminadas: {len(areas_a_eliminar)}")

    # Crear areas nuevas + ejes locales + springs
    areas_nuevas_nombres = []
    for nodos_area, prop in areas_nuevas:

        area_data = SapModel.AreaObj.AddByPoint(4, nodos_area, prop)
        area_name = area_data[1]
        areas_nuevas_nombres.append(area_name)

        ret  = SapModel.AreaObj.SetLocalAxesAdvanced(
            area_name, True, area_plane, 1, "GLOBAL", PlDir_area, PlPt_area, PlVect_area
        )
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code != 0:
            print(f"  Warning ejes area nueva {area_name}, code={code}")

        for stiffness, nonlinear_type, direction, replace in spring_defs:
            SapModel.AreaObj.SetSpring(
                area_name, 1, stiffness, nonlinear_type,
                "", -2, 1, direction, True, Vec, 0.0, replace, "Local"
            )

    print(f"Areas nuevas creadas: {len(areas_nuevas)}")

    # Eliminar links
    links_eliminados = 0
    for tipo, modulos_links in links_modulos.items():
        for m, lista_links in enumerate(modulos_links):
            if m not in [idx_parcial_inf, idx_completos[0] - 1] + \
                    list(range(idx_completos[0], idx_completos[-1] + 1)) + \
                    [idx_parcial_sup - 1]:
                continue

            for link in lista_links:
                link = str(link)
                pt1, pt2, ret = SapModel.LinkObj.GetPoints(link)
                x1, y1, z1, _ = SapModel.PointObj.GetCoordCartesian(pt1)
                x2, y2, z2, _ = SapModel.PointObj.GetCoordCartesian(pt2)

                x_c = (x1 + x2) / 2
                y_c = (y1 + y2) / 2
                z_c = (z1 + z2) / 2

                trans_c = x_c if eje_long == "Y" else y_c
                if not lado(trans_c):
                    continue
                if not (Z_min_opening <= z_c <= Z_max_opening):
                    continue

                long_c = y_c if eje_long == "Y" else x_c
                if m == idx_parcial_inf - 1:
                    if long_c < Y_corte_inf:
                        continue
                elif m == idx_parcial_sup - 1:
                    if long_c > Y_corte_sup:
                        continue

                SapModel.LinkObj.Delete(link)
                links_eliminados += 1

    print(f"Links eliminados: {links_eliminados}")

    # Eliminar nodos huerfanos
    nodos_eliminados = 0
    for nodo in nodos_candidatos:
        ret  = SapModel.PointObj.DeleteSpecialPoint(nodo)
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code == 0:
            nodos_eliminados += 1
    print(f"Nodos huerfanos eliminados: {nodos_eliminados}")

    # Guardar Y_corte_inf y Y_corte_sup para exportar_parametros_cp
    datos["Y_corte_inf"] = Y_corte_inf
    datos["Y_corte_sup"] = Y_corte_sup
    datos["lado"]        = lado

    return areas_nuevas_nombres
