import pandas as pd


load_pattern_types = {
    "Dead": 1, "Live": 3, "Roof Live": 11,
    "Quake": 5, "Wind": 6, "Snow": 7, "Other": 8,
}


def crear_load_patterns(SapModel, datos):
    df_pat = datos["df_patterns"].dropna(subset=[datos["df_patterns"].columns[0]])
    datos["df_pat"] = df_pat

    for _, fila in df_pat.iterrows():
        name    = str(fila.iloc[0]).strip()
        ltype   = load_pattern_types[str(fila.iloc[1]).strip()]
        self_wt = float(fila.iloc[2]) if pd.notna(fila.iloc[2]) else 0.0

        ret = SapModel.LoadPatterns.Add(name, ltype, self_wt, True)
        if ret != 0:
            print(f"  ⚠ Error load pattern: {name}")
        else:
            print(f"✔ Load pattern: {name}")


def crear_load_cases(SapModel, datos):
    df_pat = datos["df_pat"]
    todos_los_casos = ["DEAD"] + [str(fila.iloc[0]).strip() for _, fila in df_pat.iterrows()]

    for name in todos_los_casos:
        ret  = SapModel.LoadCases.StaticNonlinear.SetCase(name)
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code != 0:
            print(f"  ⚠ Error load case nonlinear: {name}")
        else:
            print(f"✔ Load case nonlinear: {name}")


def aplicar_cargas(SapModel, datos, areas_modulos, areas_nuevas_nombres, ejes):
    k0            = datos["k0"]
    gamma_terreno = datos["gamma_terreno"]
    gamma_agua    = datos["gamma_agua"]
    H_clave       = datos["H_clave"]
    H_agua_clave  = datos["H_agua_clave"]
    Z_clave       = float(datos["param"]["Radio (eje):"])
    eje_long      = datos["eje_long"]
    dir_proj_H    = datos["dir_proj_H"]
    opening       = datos["opening"]

    gamma_t_eff = gamma_terreno - gamma_agua
    H_seco      = max(H_clave - H_agua_clave, 0)
    H_sumerg    = min(H_clave, H_agua_clave)

    # Verificacion de presiones
    dZ_ecuador   = Z_clave
    p_v_clave    = gamma_terreno * H_clave
    p_veff_clave = gamma_terreno * H_seco + gamma_t_eff * H_sumerg
    p_h_ec       = k0 * gamma_terreno * (H_clave + dZ_ecuador)
    p_heff_ec    = k0 * (gamma_terreno * H_seco + gamma_t_eff * (H_sumerg + dZ_ecuador))
    p_gw_clave   = gamma_agua * H_agua_clave
    p_gw_ecuador = gamma_agua * (H_agua_clave + dZ_ecuador)

    print("=" * 50)
    print("VERIFICACION DE PRESIONES")
    print("=" * 50)
    print(f"  Vertical total en clave:       {p_v_clave:.2f} kN/m2")
    print(f"  Vertical efectiva en clave:    {p_veff_clave:.2f} kN/m2")
    print(f"  Horizontal total en Z=0:       {p_h_ec:.2f} kN/m2")
    print(f"  Horizontal efectiva en Z=0:    {p_heff_ec:.2f} kN/m2")
    print(f"  Agua en clave:                 {p_gw_clave:.2f} kN/m2")
    print(f"  Agua en Z=0 (ecuador):         {p_gw_ecuador:.2f} kN/m2")
    print("=" * 50)

    def aplicar_a_area(area_name):
        n_pts, nodos, ret = SapModel.AreaObj.GetPoints(area_name)
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code != 0 or n_pts == 0:
            return

        xs, ys, zs = [], [], []
        for nodo in nodos:
            x, y, z, _ = SapModel.PointObj.GetCoordCartesian(nodo)
            xs.append(x)
            ys.append(y)
            zs.append(z)

        x_c = sum(xs) / n_pts
        y_c = sum(ys) / n_pts
        z_c = sum(zs) / n_pts
        dZ  = Z_clave - z_c

        trans_c = x_c if eje_long == "Y" else y_c

        # Agua todas las areas
        p_gw = gamma_agua * (H_agua_clave + dZ)
        SapModel.AreaObj.SetLoadUniform(area_name, "Ground Water (GW)", -p_gw, 3, True, "Local")

