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

