from SAP2000_conexion    import conectar_sap




def generar_modelo(ruta_excel):

    # ── 1. Conexión SAP2000 ───────────────────────────────────────────
    SapModel = conectar_sap()



if __name__ == "__main__":
    generar_modelo(r"C:\Users\adria.moreno\OneDrive - Global Infrastructure\Python - SAP2000\Coordenadas_Nodos.xlsx")
