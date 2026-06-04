import threading
import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import filedialog
import tkinter as tk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

AZUL       = "#1F4E79"
AZUL_MED   = "#2E75B6"
AZUL_LIGHT = "#EEF6FC"
VERDE      = "#2D9E5F"
GRIS       = "#F5F7FA"
GRIS_MED   = "#E0E6ED"
TEXTO      = "#1A1A2E"
TEXTO_GRIS = "#6B7280"


def campo(parent, label, valor="—", col=0, row=0):
    """Crea un campo label + entry deshabilitado en un grid."""
    parent.grid_columnconfigure(col, weight=1)
    sub = ctk.CTkFrame(parent, fg_color="transparent")
    sub.grid(row=row, column=col, padx=8, pady=4, sticky="ew")
    ctk.CTkLabel(sub, text=label, font=("Helvetica", 10),
                 text_color=TEXTO_GRIS).pack(anchor="w")
    e = ctk.CTkEntry(sub, height=32, font=("Helvetica", 11),
                     state="disabled", fg_color=GRIS,
                     border_color=GRIS_MED, text_color=TEXTO)
    e.pack(fill="x")
    if valor != "—":
        e.configure(state="normal")
        e.insert(0, str(valor))
        e.configure(state="disabled")
    return e


def titulo_seccion(parent, texto, pady=(20, 8)):
    ctk.CTkLabel(parent, text=texto, font=("Helvetica", 15, "bold"),
                 text_color=AZUL).pack(padx=18, pady=pady, anchor="w")


def separador(parent):
    ctk.CTkFrame(parent, height=1, fg_color=GRIS_MED).pack(
        padx=18, pady=4, fill="x")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Modelos SAP2000 — Túnel Segmentado")
        self.geometry("1050x700")
        self.resizable(True, True)
        self.configure(fg_color=GRIS)

        self.ruta_archivo = None
        self.seccion_activa = "Geometría"
        self.botones_nav = {}
        self.frames_seccion = {}
        self.entries = {}
        self._log_items = []
        self._progreso_val = 0.0

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_panel_izquierdo()
        self._crear_panel_derecho()
        self.cambiar_seccion("Geometría")

    # ── Panel izquierdo ───────────────────────────────────────────────
    def _crear_panel_izquierdo(self):
        panel = ctk.CTkFrame(self, width=210, fg_color="white",
                             corner_radius=12)
        panel.grid(row=0, column=0, padx=(12, 6), pady=12, sticky="ns")
        panel.grid_propagate(False)

        # Logo / título
        ctk.CTkLabel(panel, text="SAP2000\nGenerador",
                     font=("Helvetica", 16, "bold"),
                     text_color=AZUL).pack(padx=14, pady=(20, 4))
        ctk.CTkLabel(panel, text="Túnel Segmentado",
                     font=("Helvetica", 10), text_color=TEXTO_GRIS).pack(padx=14)

        ctk.CTkFrame(panel, height=1, fg_color=GRIS_MED).pack(
            padx=14, pady=14, fill="x")

        # Selector Excel
        ctk.CTkLabel(panel, text="Archivo Excel",
                     font=("Helvetica", 11, "bold"),
                     text_color=TEXTO).pack(padx=14, anchor="w")

        self.lbl_archivo = ctk.CTkLabel(
            panel, text="Sin archivo", font=("Helvetica", 9),
            text_color=TEXTO_GRIS, wraplength=180, justify="left")
        self.lbl_archivo.pack(padx=14, pady=(2, 6), anchor="w")

        ctk.CTkButton(panel, text="Seleccionar Excel",
                      height=32, font=("Helvetica", 11),
                      fg_color=AZUL_MED, hover_color=AZUL,
                      command=self.seleccionar_archivo).pack(
                          padx=14, pady=(0, 10), fill="x")

        ctk.CTkFrame(panel, height=1, fg_color=GRIS_MED).pack(
            padx=14, pady=4, fill="x")

        # Navegación
        ctk.CTkLabel(panel, text="Secciones",
                     font=("Helvetica", 11, "bold"),
                     text_color=TEXTO).pack(padx=14, pady=(10, 6), anchor="w")

        secciones = ["Geometría", "Materiales", "Armaduras", "Links",
                     "Cargas", "Generación"]
        iconos    = ["⬡", "🧱", "🔩", "🔗", "⚖️", "▶"]

        for sec, ico in zip(secciones, iconos):
            btn = ctk.CTkButton(
                panel, text=f"  {ico}  {sec}",
                fg_color="transparent",
                text_color=TEXTO,
                hover_color=AZUL_LIGHT,
                anchor="w", height=34,
                font=("Helvetica", 11),
                command=lambda s=sec: self.cambiar_seccion(s)
            )
            btn.pack(padx=10, pady=1, fill="x")
            self.botones_nav[sec] = btn

        # Estado
        ctk.CTkFrame(panel, height=1, fg_color=GRIS_MED).pack(
            padx=14, pady=(10, 4), fill="x", side="bottom")
        self.lbl_estado = ctk.CTkLabel(
            panel, text="Sin archivo cargado",
            font=("Helvetica", 9), text_color=TEXTO_GRIS,
            wraplength=180)
        self.lbl_estado.pack(padx=14, pady=(0, 14), anchor="w", side="bottom")

    # ── Panel derecho ─────────────────────────────────────────────────
    def _crear_panel_derecho(self):
        self.panel_der = ctk.CTkFrame(self, fg_color="white",
                                      corner_radius=12)
        self.panel_der.grid(row=0, column=1, padx=(6, 12),
                            pady=12, sticky="nsew")
        self.panel_der.grid_rowconfigure(0, weight=1)
        self.panel_der.grid_columnconfigure(0, weight=1)

        self._crear_frame_geometria()
        self._crear_frame_materiales()
        self._crear_frame_armaduras()
        self._crear_frame_links()
        self._crear_frame_cargas()
        self._crear_frame_generacion()

    # ── GEOMETRÍA ─────────────────────────────────────────────────────
    def _crear_frame_geometria(self):
        f = ctk.CTkScrollableFrame(self.panel_der, fg_color="white")
        self.frames_seccion["Geometría"] = f

        titulo_seccion(f, "Geometría del túnel")

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(padx=18, fill="x")

        params = [
            ("radio",            "Radio (eje) [m]"),
            ("n_conectores",     "Nº conectores"),
            ("disc_conectores",  "Discretización entre conectores"),
            ("long_malla",       "Longitud de malla [m]"),
            ("areas_anillo",     "Áreas por anillo"),
            ("n_modulos",        "Nº módulos"),
            ("sep_modulos",      "Separación entre módulos [mm]"),
            ("eje_long",         "Eje longitudinal"),
        ]

        self.entries["geo"] = {}
        for i, (key, lbl) in enumerate(params):
            e = campo(grid, lbl, col=i % 2, row=i // 2)
            self.entries["geo"][key] = e

        separador(f)
        titulo_seccion(f, "Abertura", pady=(12, 8))

        grid2 = ctk.CTkFrame(f, fg_color="transparent")
        grid2.pack(padx=18, fill="x")

        aber_params = [
            ("opening",         "Abertura (Yes/No)"),
            ("method",          "Método de abertura"),
            ("altura_opening",  "Altura abertura [m]"),
            ("modulos_cortados","Módulos cortados completos"),
        ]

        self.entries["aber"] = {}
        for i, (key, lbl) in enumerate(aber_params):
            e = campo(grid2, lbl, col=i % 2, row=i // 2)
            self.entries["aber"][key] = e

        separador(f)
        titulo_seccion(f, "Vista previa — anillo base", pady=(12, 8))

        self.frame_grafico = ctk.CTkFrame(f, height=300,
                                          fg_color=GRIS, corner_radius=8)
        self.frame_grafico.pack(padx=18, pady=(0, 16), fill="x")
        self.frame_grafico.pack_propagate(False)
        self.lbl_grafico = ctk.CTkLabel(
            self.frame_grafico,
            text="Carga el Excel para ver el anillo base",
            text_color=TEXTO_GRIS, font=("Helvetica", 11))
        self.lbl_grafico.place(relx=0.5, rely=0.5, anchor="center")

    # ── MATERIALES ────────────────────────────────────────────────────
    def _crear_frame_materiales(self):
        f = ctk.CTkScrollableFrame(self.panel_der, fg_color="white")
        self.frames_seccion["Materiales"] = f

        titulo_seccion(f, "Materiales y secciones")

        self.frame_mats = ctk.CTkFrame(f, fg_color="transparent")
        self.frame_mats.pack(padx=18, fill="x")

        ctk.CTkLabel(self.frame_mats,
                     text="Carga el Excel para ver los materiales.",
                     text_color=TEXTO_GRIS).pack(pady=20)

    # ── ARMADURAS ─────────────────────────────────────────────────────
    def _crear_frame_armaduras(self):
        f = ctk.CTkScrollableFrame(self.panel_der, fg_color="white")
        self.frames_seccion["Armaduras"] = f

        titulo_seccion(f, "Armaduras — Recubrimientos")

        # Material
        grid0 = ctk.CTkFrame(f, fg_color="transparent")
        grid0.pack(padx=18, fill="x")
        self.entries["arm"] = {}
        self.entries["arm"]["material"] = campo(grid0, "Material armadura", col=0, row=0)

        # Dirección 1
        separador(f)
        ctk.CTkLabel(f, text="Dirección 1",
                     font=("Helvetica", 12, "bold"),
                     text_color=AZUL_MED).pack(padx=18, pady=(10, 4), anchor="w")

        grid1 = ctk.CTkFrame(f, fg_color="transparent")
        grid1.pack(padx=18, fill="x")
        self.entries["arm"]["d1_top"] = campo(grid1, "Recubrimiento superior [mm]", col=0, row=0)
        self.entries["arm"]["d1_bot"] = campo(grid1, "Recubrimiento inferior [mm]", col=1, row=0)

        # Dirección 2
        separador(f)
        ctk.CTkLabel(f, text="Dirección 2",
                     font=("Helvetica", 12, "bold"),
                     text_color=AZUL_MED).pack(padx=18, pady=(10, 4), anchor="w")

        grid2 = ctk.CTkFrame(f, fg_color="transparent")
        grid2.pack(padx=18, fill="x")
        self.entries["arm"]["d2_top"] = campo(grid2, "Recubrimiento superior [mm]", col=0, row=0)
        self.entries["arm"]["d2_bot"] = campo(grid2, "Recubrimiento inferior [mm]", col=1, row=0)

    # ── LINKS ─────────────────────────────────────────────────────────
    def _crear_frame_links(self):
        f = ctk.CTkScrollableFrame(self.panel_der, fg_color="white")
        self.frames_seccion["Links"] = f

        titulo_seccion(f, "Links entre módulos")

        self.frame_links_cont = ctk.CTkFrame(f, fg_color="transparent")
        self.frame_links_cont.pack(padx=18, fill="x")

        ctk.CTkLabel(self.frame_links_cont,
                     text="Carga el Excel para ver los links.",
                     text_color=TEXTO_GRIS).pack(pady=20)

    # ── CARGAS ────────────────────────────────────────────────────────
    def _crear_frame_cargas(self):
        f = ctk.CTkScrollableFrame(self.panel_der, fg_color="white")
        self.frames_seccion["Cargas"] = f

        titulo_seccion(f, "Parámetros de carga")

        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(padx=18, fill="x")

        params_c = [
            ("k0",          "Coeficiente k0"),
            ("gamma_t",     "Densidad terreno [kN/m³]"),
            ("gamma_w",     "Densidad agua [kN/m³]"),
            ("H_clave",     "Altura tierras en clave [m]"),
            ("H_agua",      "Altura agua en clave [m]"),
        ]

        self.entries["cargas"] = {}
        for i, (key, lbl) in enumerate(params_c):
            e = campo(grid, lbl, col=i % 2, row=i // 2)
            self.entries["cargas"][key] = e

        separador(f)
        titulo_seccion(f, "Verificación de presiones", pady=(12, 8))

        self.frame_presiones = ctk.CTkFrame(f, fg_color=GRIS,
                                            corner_radius=8)
        self.frame_presiones.pack(padx=18, pady=(0, 16), fill="x")
        ctk.CTkLabel(self.frame_presiones,
                     text="Carga el Excel para ver las presiones.",
                     text_color=TEXTO_GRIS).pack(pady=16)

    # ── GENERACIÓN ────────────────────────────────────────────────────
    def _crear_frame_generacion(self):
        f = ctk.CTkScrollableFrame(self.panel_der, fg_color="white")
        self.frames_seccion["Generación"] = f

        titulo_seccion(f, "Generación del modelo")

        # Botón generar
        self.btn_generar = ctk.CTkButton(
            f, text="▶  Generar modelo SAP2000",
            height=46, font=("Helvetica", 14, "bold"),
            fg_color=AZUL, hover_color=AZUL_MED,
            corner_radius=8,
            command=self.generar)
        self.btn_generar.pack(padx=18, pady=(0, 16), fill="x")

        separador(f)
        titulo_seccion(f, "Progreso", pady=(12, 8))

        # Barra de progreso
        self.barra_prog = ctk.CTkProgressBar(f, height=14,
                                              progress_color=VERDE,
                                              fg_color=GRIS_MED)
        self.barra_prog.pack(padx=18, pady=(0, 4), fill="x")
        self.barra_prog.set(0)

        self.lbl_pct = ctk.CTkLabel(f, text="0%",
                                     font=("Helvetica", 10),
                                     text_color=TEXTO_GRIS)
        self.lbl_pct.pack(padx=18, anchor="e")

        separador(f)
        titulo_seccion(f, "Log de generación", pady=(12, 8))

        self.frame_log = ctk.CTkFrame(f, fg_color=GRIS, corner_radius=8)
        self.frame_log.pack(padx=18, pady=(0, 16), fill="x")

        self.lbl_log_vacio = ctk.CTkLabel(
            self.frame_log,
            text="El log aparecerá aquí durante la generación.",
            text_color=TEXTO_GRIS, font=("Helvetica", 10))
        self.lbl_log_vacio.pack(pady=16)

    # ── Seleccionar archivo ───────────────────────────────────────────
    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")])
        if not ruta:
            return
        self.ruta_archivo = ruta
        nombre = ruta.split("/")[-1].split("\\")[-1]
        self.lbl_archivo.configure(text=nombre)
        self.lbl_estado.configure(text="Cargando parámetros...")
        self.after(100, self.cargar_datos)

    # ── Cargar datos del Excel ────────────────────────────────────────
    def cargar_datos(self):
        try:
            xls = pd.ExcelFile(self.ruta_archivo)
            self._cargar_geometria(xls)
            self._cargar_materiales(xls)
            self._cargar_armaduras(xls)
            self._cargar_links(xls)
            self._cargar_cargas(xls)
            self._cargar_grafico(xls)
            self.lbl_estado.configure(
                text="✓ Parámetros cargados", text_color=VERDE)
        except Exception as e:
            self.lbl_estado.configure(
                text=f"Error: {e}", text_color="#C0392B")

    def _set_entry(self, entry, valor):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, str(valor) if valor is not None else "—")
        entry.configure(state="disabled")

    def _cargar_geometria(self, xls):
        try:
            df = pd.read_excel(xls, sheet_name="Nodes", header=None)

            vals = {
                "radio": df.iloc[3, 3],  # D4
                "n_conectores": df.iloc[6, 3],  # D7
                "disc_conectores": df.iloc[7, 3],  # D8
                "long_malla": df.iloc[19, 3],  # D20
                "areas_anillo": df.iloc[20, 3],  # D21
                "n_modulos": df.iloc[23, 3],  # D24
                "sep_modulos": df.iloc[22, 3],  # D23
                "eje_long": df.iloc[28, 3],  # D29
            }

            aber_vals = {
                "opening": df.iloc[36, 3],  # D37
                "method": df.iloc[39, 3],  # D40
                "altura_opening": "—",
                "modulos_cortados": df.iloc[44, 3],  # D45
            }

            try:
                zmax = float(df.iloc[41, 3])  # D42
                zmin = float(df.iloc[42, 3])  # D43
                aber_vals["altura_opening"] = round(abs(zmax) + abs(zmin), 3)
            except Exception:
                pass

            for key, val in vals.items():
                if key in self.entries["geo"]:
                    self._set_entry(self.entries["geo"][key],
                                    round(val, 4) if isinstance(val, float) else val)

            for key, val in aber_vals.items():
                if key in self.entries["aber"]:
                    self._set_entry(self.entries["aber"][key],
                                    round(val, 4) if isinstance(val, float) else val)
        except Exception as e:
            print(f"Error geometría: {e}")

    def _cargar_materiales(self, xls):
        try:
            df = pd.read_excel(xls, sheet_name="Materials & Area Properties", header=None)

            for widget in self.frame_mats.winfo_children():
                widget.destroy()

            # ── Materiales ────────────────────────────────────────────────
            ctk.CTkLabel(self.frame_mats, text="Materiales",
                         font=("Helvetica", 12, "bold"),
                         text_color=AZUL_MED).pack(anchor="w", pady=(8, 4))

            mats = [
                (df.iloc[5, 3], df.iloc[6, 3], df.iloc[7, 3], df.iloc[8, 3]),  # D6,D7,D8,D9
                (df.iloc[5, 4], df.iloc[6, 4], df.iloc[7, 4], df.iloc[8, 4]),  # E6,E7,E8,E9
            ]

            for region, material, norma, grado in mats:
                if str(material).strip() in ("nan", ""):
                    continue
                card = ctk.CTkFrame(self.frame_mats, fg_color=AZUL_LIGHT,
                                    corner_radius=8)
                card.pack(fill="x", pady=4)
                ctk.CTkLabel(card, text=f"Material: {material}",
                             font=("Helvetica", 12, "bold"),
                             text_color=AZUL).pack(padx=12, pady=(8, 2), anchor="w")
                ctk.CTkLabel(card,
                             text=f"Región: {region}  |  Norma: {norma}  |  Grado: {grado}",
                             font=("Helvetica", 10),
                             text_color=TEXTO_GRIS).pack(padx=12, pady=(0, 8), anchor="w")

            # ── Sección de área ───────────────────────────────────────────
            ctk.CTkFrame(self.frame_mats, height=1, fg_color=GRIS_MED).pack(
                pady=10, fill="x")
            ctk.CTkLabel(self.frame_mats, text="Sección de área",
                         font=("Helvetica", 12, "bold"),
                         text_color=AZUL_MED).pack(anchor="w", pady=(0, 4))

            nombre_area = df.iloc[14, 3]  # D15
            material_area = df.iloc[15, 3]  # D16
            espesor = df.iloc[17, 3]  # D18

            card = ctk.CTkFrame(self.frame_mats, fg_color=AZUL_LIGHT,
                                corner_radius=8)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=f"Nombre: {nombre_area}",
                         font=("Helvetica", 12, "bold"),
                         text_color=AZUL).pack(padx=12, pady=(8, 2), anchor="w")
            ctk.CTkLabel(card,
                         text=f"Material: {material_area}  |  Espesor: {espesor} m",
                         font=("Helvetica", 10),
                         text_color=TEXTO_GRIS).pack(padx=12, pady=(0, 8), anchor="w")

        except Exception as e:
            print(f"Error materiales: {e}")

    def _cargar_armaduras(self, xls):
        try:
            df = pd.read_excel(xls, sheet_name="Reinforcement", header=None)

            # Material armadura E5
            material_arm = df.iloc[4, 4]  # E5
            self._set_entry(self.entries["arm"]["material"], material_arm)

            d1_top = df.iloc[16, 4]  # E17
            d1_bot = df.iloc[16, 5]  # F17
            d2_top = df.iloc[17, 4]  # E18
            d2_bot = df.iloc[17, 5]  # F18

            self._set_entry(self.entries["arm"]["d1_top"], d1_top)
            self._set_entry(self.entries["arm"]["d1_bot"], d1_bot)
            self._set_entry(self.entries["arm"]["d2_top"], d2_top)
            self._set_entry(self.entries["arm"]["d2_bot"], d2_bot)
        except Exception as e:
            print(f"Error armaduras: {e}")

    def _cargar_links(self, xls):
        try:
            df = pd.read_excel(xls, sheet_name="Links", header=0)
            for widget in self.frame_links_cont.winfo_children():
                widget.destroy()

            for _, row in df.iterrows():
                try:
                    nombre = str(row.get("Name:", "")).strip()
                    tipo   = str(row.get("Type:", "")).strip()
                    if nombre in ("nan", ""):
                        continue
                    card = ctk.CTkFrame(self.frame_links_cont,
                                        fg_color=AZUL_LIGHT,
                                        corner_radius=8)
                    card.pack(fill="x", pady=4)
                    ctk.CTkLabel(card, text=nombre,
                                 font=("Helvetica", 12, "bold"),
                                 text_color=AZUL).pack(
                                     padx=12, pady=(8, 2), anchor="w")
                    ctk.CTkLabel(card, text=f"Tipo: {tipo}",
                                 font=("Helvetica", 10),
                                 text_color=TEXTO_GRIS).pack(
                                     padx=12, pady=(0, 8), anchor="w")
                except Exception:
                    continue
        except Exception as e:
            print(f"Error links: {e}")

    def _cargar_cargas(self, xls):
        try:
            df = pd.read_excel(xls, sheet_name="Loads", header=None)
            keys_rows = {
                "k0":      (15, 4),  # E16
                "gamma_t": (17, 4),  # E18
                "gamma_w": (18, 4),  # E19
                "H_clave": (20, 4),  # E21
                "H_agua":  (21, 4),  # E22
            }
            for key, (row, col) in keys_rows.items():
                try:
                    val = df.iloc[row, col]
                    self._set_entry(self.entries["cargas"][key],
                                    round(float(val), 4))
                except Exception:
                    pass

            # Verificación de presiones
            for w in self.frame_presiones.winfo_children():
                w.destroy()

            try:
                k0      = float(df.iloc[15, 4])
                gamma_t = float(df.iloc[17, 4])
                gamma_w = float(df.iloc[18, 4])
                H       = float(df.iloc[20, 4])
                H_w     = float(df.iloc[21, 4])

                sigma_v = round(gamma_t * H, 2)
                sigma_h = round(k0 * gamma_t * H, 2)
                sigma_w = round(gamma_w * H_w, 2)

                pres_data = [
                    ("σ vertical (clave)",   f"{sigma_v} kN/m²"),
                    ("σ horizontal (clave)", f"{sigma_h} kN/m²"),
                    ("Presión agua (clave)", f"{sigma_w} kN/m²"),
                ]
                grd = ctk.CTkFrame(self.frame_presiones, fg_color="transparent")
                grd.pack(padx=12, pady=12, fill="x")
                grd.grid_columnconfigure((0, 1, 2), weight=1)

                for i, (lbl, val) in enumerate(pres_data):
                    card = ctk.CTkFrame(grd, fg_color=AZUL_LIGHT, corner_radius=8)
                    card.grid(row=0, column=i, padx=6, sticky="ew")
                    ctk.CTkLabel(card, text=lbl, font=("Helvetica", 9),
                                 text_color=TEXTO_GRIS).pack(pady=(8, 2))
                    ctk.CTkLabel(card, text=val,
                                 font=("Helvetica", 13, "bold"),
                                 text_color=AZUL).pack(pady=(0, 8))
            except Exception:
                ctk.CTkLabel(self.frame_presiones,
                             text="No se pudieron calcular las presiones.",
                             text_color=TEXTO_GRIS).pack(pady=12)

        except Exception as e:
            print(f"Error cargas: {e}")

        except Exception as e:
            print(f"Error cargas: {e}")

    def _cargar_grafico(self, xls):
        try:
            df = pd.read_excel(xls, sheet_name="Nodes", header=None)

            # Leer nodos del anillo base
            nodos = []
            for i in range(200):
                try:
                    x = float(df.iloc[i, 1])
                    y = float(df.iloc[i, 2])
                    if pd.isna(x) or pd.isna(y):
                        break
                    nodos.append((x, y))
                except Exception:
                    break

            if len(nodos) < 3:
                return

            # Limpiar frame
            for w in self.frame_grafico.winfo_children():
                w.destroy()

            xs = [n[0] for n in nodos] + [nodos[0][0]]
            ys = [n[1] for n in nodos] + [nodos[0][1]]

            fig, ax = plt.subplots(figsize=(6, 3.2),
                                   facecolor=GRIS)
            ax.set_facecolor(GRIS)
            ax.plot(xs, ys, color=AZUL_MED, linewidth=1.5)
            ax.scatter([n[0] for n in nodos],
                       [n[1] for n in nodos],
                       color=AZUL, s=18, zorder=5)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.set_title("Anillo base", fontsize=10,
                         color=TEXTO_GRIS, pad=6)
            fig.tight_layout(pad=0.5)

            canvas = FigureCanvasTkAgg(fig, master=self.frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True,
                                        padx=8, pady=8)
            plt.close(fig)

        except Exception as e:
            print(f"Error gráfico: {e}")

    # ── Navegación ────────────────────────────────────────────────────
    def cambiar_seccion(self, seccion):
        self.seccion_activa = seccion
        for nombre, frame in self.frames_seccion.items():
            if nombre == seccion:
                frame.pack(fill="both", expand=True, padx=4, pady=4)
            else:
                frame.pack_forget()
        for nombre, btn in self.botones_nav.items():
            if nombre == seccion:
                btn.configure(fg_color=AZUL_LIGHT,
                              text_color=AZUL,
                              font=("Helvetica", 11, "bold"))
            else:
                btn.configure(fg_color="transparent",
                              text_color=TEXTO,
                              font=("Helvetica", 11))

    # ── Generar modelo ────────────────────────────────────────────────
    def generar(self):
        if not self.ruta_archivo:
            self.lbl_estado.configure(
                text="⚠ Selecciona un archivo Excel primero",
                text_color="#E67E22")
            self.cambiar_seccion("Generación")
            return

        self.btn_generar.configure(state="disabled",
                                   text="Generando...")
        self._limpiar_log()
        self.barra_prog.set(0)
        self.lbl_pct.configure(text="0%")

        threading.Thread(target=self._run_generacion,
                         daemon=True).start()

    def _run_generacion(self):
        try:
            from SAP2000_main import generar_modelo

            pasos = [
                (0.05,  "Conectando a SAP2000..."),
                (0.10,  "Leyendo Excel..."),
                (0.20,  "Creando materiales y secciones..."),
                (0.30,  "Creando load patterns y load cases..."),
                (0.55,  "Generando geometría (nodos, áreas, springs)..."),
                (0.65,  "Creando links entre módulos..."),
                (0.75,  "Aplicando abertura..."),
                (0.90,  "Aplicando cargas..."),
                (1.0,   "✓ Modelo generado correctamente"),
            ]

            import time

            def progreso_callback(paso_idx):
                pct, msg = pasos[paso_idx]
                self.after(0, self._actualizar_progreso, pct, msg,
                           paso_idx == len(pasos) - 1)

            # Simular pasos hasta llamar a generar_modelo
            for i in range(len(pasos) - 1):
                progreso_callback(i)
                time.sleep(0.3)

            generar_modelo(self.ruta_archivo)
            progreso_callback(len(pasos) - 1)
            self.after(0, self._fin_generacion, True)

        except Exception as e:
            self.after(0, self._fin_generacion, False, str(e))

    def _actualizar_progreso(self, pct, msg, es_final=False):
        self.barra_prog.set(pct)
        self.lbl_pct.configure(text=f"{int(pct*100)}%")
        color = VERDE if es_final else AZUL_MED
        self._añadir_log(msg, color)

    def _añadir_log(self, texto, color=None):
        if color is None:
            color = TEXTO_GRIS
        if self.lbl_log_vacio.winfo_exists():
            try:
                self.lbl_log_vacio.destroy()
            except Exception:
                pass

        fila = ctk.CTkFrame(self.frame_log, fg_color="transparent")
        fila.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(fila, text=texto, font=("Helvetica", 10),
                     text_color=color, anchor="w").pack(
                         side="left", fill="x")
        self._log_items.append(fila)

    def _limpiar_log(self):
        for w in self.frame_log.winfo_children():
            w.destroy()
        self._log_items = []
        self.lbl_log_vacio = ctk.CTkLabel(
            self.frame_log,
            text="Iniciando generación...",
            text_color=TEXTO_GRIS, font=("Helvetica", 10))
        self.lbl_log_vacio.pack(pady=8)

    def _fin_generacion(self, ok, error=None):
        self.btn_generar.configure(state="normal",
                                   text="▶  Generar modelo SAP2000")
        if ok:
            self.lbl_estado.configure(
                text="✓ Modelo generado", text_color=VERDE)
        else:
            self.lbl_estado.configure(
                text=f"Error: {error}", text_color="#C0392B")
            self._añadir_log(f"✗ Error: {error}", "#C0392B")


if __name__ == "__main__":
    app = App()
    app.mainloop()
