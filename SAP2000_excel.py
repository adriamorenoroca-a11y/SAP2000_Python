import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")


def leer_excel(ruta_excel):
    """Lee todos los datos del Excel en una sola pasada y devuelve un dict."""
    with pd.ExcelFile(ruta_excel) as xls:
        df_mat_raw    = pd.read_excel(xls, sheet_name="Materials & Area Properties", skiprows=4,  header=None, nrows=5)
        df_area_raw   = pd.read_excel(xls, sheet_name="Materials & Area Properties", usecols="C:E", skiprows=14, header=None, nrows=4)
        df_prop_raw   = pd.read_excel(xls, sheet_name="Materials & Area Properties", usecols="C:D", skiprows=21, nrows=1, header=None)
        df_asprings   = pd.read_excel(xls, sheet_name="Materials & Area Properties")
        df_modifiers  = pd.read_excel(xls, sheet_name="Materials & Area Properties", usecols="J:K", skiprows=27, nrows=10, header=None)
        df_reinf_raw  = pd.read_excel(xls, sheet_name="Reinforcement", usecols="E:F", skiprows=16, header=None, nrows=2)
        df_reinf2_raw = pd.read_excel(xls, sheet_name="Reinforcement", usecols="E",   skiprows=3,  header=None, nrows=3)
        df_localax    = pd.read_excel(xls, sheet_name="Local Axes")
        df_param      = pd.read_excel(xls, sheet_name="Nodes")
        df_nodos      = pd.read_excel(xls, sheet_name="Nodes", usecols="AN:AQ", skiprows=4, header=None)
        df_links      = pd.read_excel(xls, sheet_name="Links", usecols="B:AA", header=3, nrows=8)
        df_patterns   = pd.read_excel(xls, sheet_name="Loads", usecols="D:F", skiprows=6, nrows=9, header=None)
        df_load_params= pd.read_excel(xls, sheet_name="Loads", usecols="D:E", skiprows=15, nrows=7, header=None)
        df_opening    = pd.read_excel(xls, sheet_name="Nodes", usecols="C:D", skiprows=36, nrows=10, header=None)
        df_eje_long   = pd.read_excel(xls, sheet_name="Nodes", usecols="C:D", skiprows=28, nrows=1, header=None)

    # ── Parámetros de abertura ────────────────────────────────────────
    df_opening = df_opening.dropna(subset=[df_opening.columns[0]])
    opening_params = dict(zip(df_opening.iloc[:, 0], df_opening.iloc[:, 1]))

    opening = str(opening_params["Opening?"]).strip()
    side = str(opening_params["Side:"]).strip()
    method = str(opening_params["Opening method:"]).strip()
    Z_max_opening = float(opening_params["Height from 0 m (top):"])
    Z_min_opening = -abs(float(opening_params["Height to 0 m (bottom):"]))
    n_modulos_completos = int(opening_params["Number of complete rings:"])
    ancho_extra = float(opening_params["Width in last rings:"])

    print(f"Opening: {opening} | Side: {side} | Method: {method}")
    print(f"Z_max: {Z_max_opening} | Z_min: {Z_min_opening}")
    print(f"Módulos completos: {n_modulos_completos} | Ancho extra: {ancho_extra}m")

    # ── Parámetros de carga ───────────────────────────────────────────
    df_load_params = df_load_params.dropna(subset=[df_load_params.columns[0]])
    load_params    = dict(zip(df_load_params.iloc[:, 0], df_load_params.iloc[:, 1]))

    k0            = float(load_params["k0:"])
    gamma_terreno = float(load_params["Ground density (kN/m3):"])
    gamma_agua    = float(load_params["Water density (kN/m3):"])
    H_clave       = float(load_params["Ground Height at crown (m):"])
    H_agua_clave  = float(load_params["Groundwater Height at crown (m):"])

    print(f"k0={k0} | γ_t={gamma_terreno} | γ_w={gamma_agua} | H_clave={H_clave} | H_agua={H_agua_clave}")

    # ── Parámetros del modelo ─────────────────────────────────────────
    param = dict(zip(df_param.iloc[:, 2], df_param.iloc[:, 3]))
