import comtypes


mat_types = {
    "Steel": 1, "Concrete": 2, "NoDesign": 3,
    "Aluminum": 4, "ColdFormed": 5, "Rebar": 6, "Tendon": 7
}

shell_types = {
    "Shell - Thin": 1, "Shell - Thick": 2, "Plate - Thin": 3,
    "Plate - Thick": 4, "Membrane": 5, "Shell Nonlinear": 6
}

rebar_layout = {"Default": 0, "One layer": 1, "Two layers": 2}


def crear_materiales(SapModel, datos):
    df_mat = datos["df_mat_raw"].iloc[:, 2:]
    df_mat = df_mat.dropna(axis=1, how="all")

    for col in df_mat.columns[1:]:
        d        = dict(zip(df_mat.iloc[:, 0], df_mat[col]))
        region   = str(d["Region:"]).strip()
        material = str(d["Material:"]).strip()
        standard = str(d["Standard:"]).strip()
        grade    = str(d["Grade:"]).strip()
        SapModel.PropMaterial.AddMaterial("", mat_types[material], region, standard, grade, grade)
        print(f"✔ Material: {grade}")


def crear_secciones(SapModel, datos):
    import pandas as pd
    df_area        = datos["df_area_raw"].dropna(axis=1, how="all")
    modifiers_dict = datos["modifiers_dict"]

    for col in df_area.columns[1:]:
        d = dict(zip(df_area.iloc[:, 0], df_area[col]))
        if pd.isna(d.get("Name:")):
            continue

        name       = str(d["Name:"]).strip()
        material   = str(d["Material:"]).strip()
        shell_type = shell_types[str(d["Shell type:"]).strip()]
        thickness  = float(d["Thickness (m):"])
        matang     = float(d.get("MatAng:", 0))

        SapModel.PropArea.SetShell(name, shell_type, material, matang, thickness, thickness)
        print(f"✔ Sección área: {name}")

        modifiers = (comtypes.c_double * 10)(
            float(modifiers_dict.get("Membrane f11 modifier:", 1.0)),
            float(modifiers_dict.get("Membrane f22 modifier:", 1.0)),
            float(modifiers_dict.get("Membrane f12 modifier:", 1.0)),
            float(modifiers_dict.get("Bending m11 modifier:", 1.0)),
            float(modifiers_dict.get("Bending m22 modifier:", 1.0)),
            float(modifiers_dict.get("Bending m12 modifier:", 1.0)),
            float(modifiers_dict.get("Shear v13 modifier:", 1.0)),
            float(modifiers_dict.get("Shear v23 modifier:", 1.0)),
            float(modifiers_dict.get("Mass modifier:", 1.0)),
            float(modifiers_dict.get("Weight modifier:", 1.0)),
        )
        ret  = SapModel.PropArea.SetModifiers(name, modifiers)
        code = ret[-1] if isinstance(ret, (list, tuple)) else ret
        if code != 0:
            print(f"  ⚠ Error modifiers en {name}")
        else:
            print(f"✔ Modifiers asignados: {name}")


def crear_armaduras(SapModel, datos):
    df_reinf_raw  = datos["df_reinf_raw"]
    df_reinf2_raw = datos["df_reinf2_raw"]

    top_layer1    = float(df_reinf_raw.iloc[0, 0]) / 1000
    bottom_layer1 = float(df_reinf_raw.iloc[0, 1]) / 1000
    top_layer2    = float(df_reinf_raw.iloc[1, 0]) / 1000
    bottom_layer2 = float(df_reinf_raw.iloc[1, 1]) / 1000

    area_reinf   = str(df_reinf2_raw.iloc[0, 0])
    rebar_mat    = str(df_reinf2_raw.iloc[1, 0])
    reinf_layout = str(df_reinf2_raw.iloc[2, 0])
    rebar        = rebar_layout[reinf_layout]

    SapModel.PropArea.SetShellDesign(
        area_reinf, rebar_mat, rebar,
        top_layer1, top_layer2, bottom_layer1, bottom_layer2
    )
    print(f"✔ Armadura definida: {area_reinf} | {rebar_mat} | {reinf_layout}")
