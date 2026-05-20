def crear_propiedades_links(SapModel, datos):
    df_links = datos["df_links"].copy()
    df_links.columns = df_links.columns.astype(str).str.strip()
    propiedades_links = []

    for _, fila in df_links.iterrows():
        tipo   = str(fila["Type:"]).strip()
        nombre = str(fila["Name:"]).strip()
        propiedades_links.append(nombre)

        DOF      = [bool(fila[k]) for k in ["U1", "U2", "U3", "R1", "R2", "R3"]]
        Fixed    = [bool(fila.get(f"F_{k}", 0)) for k in ["U1", "U2", "U3", "R1", "R2", "R3"]]
        Ke       = [float(fila.get(f"Ke_{k}", 0.0)) for k in ["U1", "U2", "U3", "R1", "R2", "R3"]]
        Ce       = [0.0] * 6

        if tipo == "Linear":
            SapModel.PropLink.SetLinear(nombre, DOF, Fixed, Ke, Ce, 0.0, 0.0)
            print(f"Linear link: {nombre}")

        elif tipo == "MultiLinear Elastic":
            NonLinear = [bool(fila.get(f"NL_{k}", 0)) for k in ["U1", "U2", "U3", "R1", "R2", "R3"]]
            SapModel.PropLink.SetMultiLinearElastic(nombre, DOF, Fixed, NonLinear, Ke, Ce, 0.0, 0.0)
            print(f"MultiLinear Elastic link: {nombre}")

    datos["propiedades_links"] = propiedades_links
    datos["df_links_clean"]    = df_links
    return {nombre: [] for nombre in propiedades_links}

