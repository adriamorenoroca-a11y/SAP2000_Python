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
