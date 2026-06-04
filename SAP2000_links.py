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

def crear_links(SapModel, datos, modulos, links_modulos, ejes):
    propiedades_links       = datos["propiedades_links"]
    Nodos_por_anillo        = ejes["Nodos_por_anillo"]
    Nodos_entre_conectores  = ejes["Nodos_entre_conectores"]
    link_plane              = ejes["link_plane"]
    AxDir_lk                = ejes["AxDir_lk"]
    AxPt_lk                 = ejes["AxPt_lk"]
    AxVect_lk               = ejes["AxVect_lk"]
    PlDir_lk                = ejes["PlDir_lk"]
    PlPt_lk                 = ejes["PlPt_lk"]
    PlVect_lk               = ejes["PlVect_lk"]

    for m in range(len(modulos) - 1):
        anillo_inf   = modulos[m][-1]
        anillo_sup   = modulos[m + 1][0]
        links_modulo = {nombre: [] for nombre in propiedades_links}

        for i in range(Nodos_por_anillo):
            nodo_inf = anillo_inf[i]
            nodo_sup = anillo_sup[i]

            for nombre in propiedades_links:
                if nombre == "Connector" and (i % Nodos_entre_conectores) != 0:
                    continue

                link_name, ret = SapModel.LinkObj.AddByPoint(nodo_inf, nodo_sup, "", False)
                SapModel.LinkObj.SetProperty(link_name, nombre)
                links_modulo[nombre].append(link_name)
                ret2 = SapModel.LinkObj.SetLocalAxesAdvanced(
                    link_name, True, 1, "GLOBAL", AxDir_lk, AxPt_lk, AxVect_lk,
                    link_plane, 1, "GLOBAL", PlDir_lk, PlPt_lk, PlVect_lk
                )
                links_modulo[nombre].append(link_name)

        for nombre in propiedades_links:
            links_modulos[nombre].append(links_modulo[nombre])

    for tipo, modulos_links in links_modulos.items():
        for m, lista in enumerate(modulos_links):
            print(f"{tipo} | Módulo {m+1}-{m+2}: {len(lista)} links")

    return links_modulos
