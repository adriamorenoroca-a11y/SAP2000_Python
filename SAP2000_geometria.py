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

    # ── Ejes locales ──────────────────────────────────────────────────
    local_axes = {
        "+X": 1,  "+Y": 2,  "+Z": 3,
        "+CR": 4, "+CA": 5, "+CZ": 6,
        "+SR": 7, "+SA": 8, "+SB": 9,
        "-X": -1, "-Y": -2, "-Z": -3,
        "-CR": -4, "-CA": -5, "-CZ": -6,
        "-SR": -7, "-SA": -8, "-SB": -9,
    }

    df_localax = datos["df_localax"].dropna(subset=[datos["df_localax"].columns[3]])
    localax    = dict(zip(df_localax.iloc[:, 3], df_localax.iloc[:, 4]))

    area_plane  = int(str(localax["Plane (area):"]).replace("-", ""))
    area_PD     = str(localax["Primary direction (area):"])
    area_SD     = str(localax["Secondary direction (area):"])
    link_plane  = int(str(localax["Plane (link):"]).replace("-", ""))
    link_AD     = str(localax["Axial direction (link):"])
    link_PD     = str(localax["Primary direction (link):"])
    link_SD     = str(localax["Secondary direction (link):"])
    joint_plane = int(str(localax["Plane (joint):"]).replace("-", ""))
    joint_AD    = str(localax["Axial direction (joint):"])
    joint_PD    = str(localax["Primary direction (joint):"])
    joint_SD    = str(localax["Secondary direction (joint):"])

    def make_local_axes_vectors(AD, PD, SD):
        AxDir  = (comtypes.c_long   * 2)(local_axes[AD], local_axes[PD])
        PlDir  = (comtypes.c_long   * 2)(local_axes[PD], local_axes[SD])
        AxPt   = ["None", "None"]
        PlPt   = ["None", "None"]
        AxVect = (comtypes.c_double * 3)(0.0, 0.0, 0.0)
        PlVect = (comtypes.c_double * 3)(0.0, 0.0, 0.0)
        return AxDir, AxPt, AxVect, PlDir, PlPt, PlVect

    ax_area  = make_local_axes_vectors(area_PD,  area_PD,  area_SD)
    ax_joint = make_local_axes_vectors(joint_AD, joint_PD, joint_SD)
    ax_link  = make_local_axes_vectors(link_AD,  link_PD,  link_SD)

    _, _, _,        PlDir_area, PlPt_area, PlVect_area = ax_area
    AxDir_jt, AxPt_jt, AxVect_jt, PlDir_jt, PlPt_jt, PlVect_jt = ax_joint
    AxDir_lk, AxPt_lk, AxVect_lk, PlDir_lk, PlPt_lk, PlVect_lk = ax_link

    ejes = {
        "area_plane":  area_plane,
        "link_plane":  link_plane,
        "joint_plane": joint_plane,
        "PlDir_area":  PlDir_area, "PlPt_area":  PlPt_area, "PlVect_area":  PlVect_area,
        "AxDir_jt":    AxDir_jt,   "AxPt_jt":    AxPt_jt,   "AxVect_jt":    AxVect_jt,
        "PlDir_jt":    PlDir_jt,   "PlPt_jt":    PlPt_jt,   "PlVect_jt":    PlVect_jt,
        "AxDir_lk":    AxDir_lk,   "AxPt_lk":    AxPt_lk,   "AxVect_lk":    AxVect_lk,
        "PlDir_lk":    PlDir_lk,   "PlPt_lk":    PlPt_lk,   "PlVect_lk":    PlVect_lk,
        "Nodos_entre_conectores": Nodos_entre_conectores,
        "Nodos_por_anillo": Nodos_por_anillo,
    }

    def set_point_local_axes(name):
        ret  = SapModel.PointObj.SetLocalAxesAdvanced(
            name, True, 1, "GLOBAL", AxDir_jt, AxPt_jt, AxVect_jt,
            joint_plane, 1, "GLOBAL", PlDir_jt, PlPt_jt, PlVect_jt
        )
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code != 0:
            print(f"  Warning ejes nodo {name}, code={code}")

    def crear_nodo(x_excel, y_long, z_excel):
        if eje_long == "Y":
            x_sap, y_sap, z_sap = x_excel, y_long, z_excel
        else:
            x_sap, y_sap, z_sap = y_long, x_excel, z_excel
        nombre, ret = SapModel.PointObj.AddCartesian(x_sap, y_sap, z_sap)
        if ret != 0:
            raise Exception(f"Error creando nodo ({x_sap}, {y_sap}, {z_sap})")
        set_point_local_axes(nombre)
        return nombre

    def copiar_anillo(anillo_origen, dy):
        anillo_nuevo = []
        for nodo in anillo_origen:
            x, y, z, ret = SapModel.PointObj.GetCoordCartesian(nodo)
            if ret != 0:
                raise Exception(f"Error leyendo nodo {nodo}")
            if eje_long == "Y":
                anillo_nuevo.append(crear_nodo(x, y + dy, z))
            else:
                anillo_nuevo.append(crear_nodo(y, x + dy, z))
        return anillo_nuevo

    # ── Anillo base ───────────────────────────────────────────────────
    df_nodos = datos["df_nodos"].copy()
    df_nodos.columns = ["Nodo", "X", "Y_excel", "Z"]
    df_nodos = df_nodos.dropna(subset=["Nodo", "X", "Z"])

    anillo_base = [
        crear_nodo(float(f["X"]), 0.0, float(f["Z"]))
        for _, f in df_nodos.iterrows()
    ]

    # ── Construir modulos ─────────────────────────────────────────────
    modulos       = []
    anillo_actual = anillo_base

    for m in range(Numero_modulos):
        print(f"Creando módulo {m + 1}")
        anillos_modulo = [anillo_actual]

        for _ in range(n_areas_por_anillo_en_longitudinal):
            anillo_actual = copiar_anillo(anillo_actual, Longitud_mallazo_en_longitudinal)
            anillos_modulo.append(anillo_actual)

        modulos.append(anillos_modulo)

        if m < Numero_modulos - 1:
            anillo_actual = copiar_anillo(anillo_actual, Separacion_modulos)

    print("Nodos creados con ejes locales asignados")

    # ── Springs ───────────────────────────────────────────────────────
    df_asprings = datos["df_asprings"].dropna(subset=[datos["df_asprings"].columns[2]])
    asprings    = dict(zip(df_asprings.iloc[:, 2], df_asprings.iloc[:, 3]))
    axis_3      = float(asprings["Compression only - Axis 3 (kN/m/m2):"])
    axis_2      = float(asprings["Tension and Compression - Axis 2 (kN/m/m2):"])
    axis_1      = float(asprings["Tension and Compression - Axis 1 (kN/m/m2):"])
    Vec         = [0.0, 0.0, 0.0]

    spring_defs = [
        (axis_3, 2, -3, True),
        (axis_2, 1, -2, False),
        (axis_1, 1, -1, False),
    ]

    prop_area = str(datos["df_prop_raw"].iloc[0, 1]).strip()
    print(f"Lining area: {prop_area}")

    # ── Crear areas + ejes locales + springs ──────────────────────────
    areas_modulos = []

    for m, anillos_modulo in enumerate(modulos):
        print(f"Creando áreas módulo {m + 1}")
        areas_modulo = []
        n = len(anillos_modulo[0])

        for j in range(len(anillos_modulo) - 1):
            anillo_inf = anillos_modulo[j]
            anillo_sup = anillos_modulo[j + 1]

            for i in range(n):
                n1      = anillo_inf[i]
                n2      = anillo_sup[i]
                n1_next = anillo_inf[(i + 1) % n]
                n2_next = anillo_sup[(i + 1) % n]

                if eje_long == "Y":
                    area_data = SapModel.AreaObj.AddByPoint(4, (n1, n2, n2_next, n1_next), prop_area)
                else:
                    area_data = SapModel.AreaObj.AddByPoint(4, (n1_next, n2_next, n2, n1), prop_area)
                area_name = area_data[1]

                ret  = SapModel.AreaObj.SetLocalAxesAdvanced(
                    area_name, True, area_plane, 1, "GLOBAL", PlDir_area, PlPt_area, PlVect_area
                )
                code = ret[-1] if isinstance(ret, (list, tuple)) else ret
                if code != 0:
                    print(f"  Warning ejes area {area_name}, code={code}")

                for stiffness, nonlinear_type, direction, replace in spring_defs:
                    SapModel.AreaObj.SetSpring(
                        area_name, 1, stiffness, nonlinear_type,
                        "", -2, 1, direction, True, Vec, 0.0, replace, "Local"
                    )

                areas_modulo.append(area_data)

        areas_modulos.append(areas_modulo)

    print(f"Areas creadas: {sum(len(m) for m in areas_modulos)}")

    # Guardar prop_area y spring_defs en ejes para uso posterior
    ejes["prop_area"]   = prop_area
    ejes["spring_defs"] = spring_defs
    ejes["Vec"]         = Vec

    return modulos, areas_modulos, ejes