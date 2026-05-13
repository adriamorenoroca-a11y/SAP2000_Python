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
