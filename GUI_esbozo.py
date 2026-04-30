import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Modelos SAP2000 — Túnel Segmentado")
        self.geometry("950x650")
        self.resizable(False, False)

        self.seccion_activa = "Geometría"
        self.botones_nav = {}
        self.frames_seccion = {}

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel izquierdo
        self.panel_izq = ctk.CTkFrame(self, width=220)
        self.panel_izq.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        self.panel_izq.grid_propagate(False)

        ctk.CTkLabel(self.panel_izq, text="Archivo Excel",
                     font=("Arial", 11, "bold")).pack(padx=10, pady=(16, 4), anchor="w")
        ctk.CTkLabel(self.panel_izq, text="Ningún archivo seleccionado",
                     font=("Arial", 10), text_color="gray",
                     wraplength=190).pack(padx=10, pady=2, anchor="w")
        ctk.CTkButton(self.panel_izq, text="Seleccionar",
                      height=30).pack(padx=10, pady=6, fill="x")

        ctk.CTkLabel(self.panel_izq, text="Navegación",
                     font=("Arial", 11, "bold")).pack(padx=10, pady=(16, 4), anchor="w")

        for seccion in ["Geometría", "Materiales", "Links", "Cargas"]:
            btn = ctk.CTkButton(
                self.panel_izq, text=seccion,
                fg_color="transparent",
                text_color=("black", "white"),
                anchor="w", height=32,
            )
            btn.pack(padx=10, fill="x")
            self.botones_nav[seccion] = btn

        ctk.CTkButton(self.panel_izq, text="Generar modelo",
                      height=40, font=("Arial", 13, "bold")
                      ).pack(padx=10, pady=20, fill="x", side="bottom")

        # Panel derecho
        self.panel_der = ctk.CTkFrame(self)
        self.panel_der.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        self.panel_der.grid_rowconfigure(0, weight=1)
        self.panel_der.grid_columnconfigure(0, weight=1)

        self._crear_frame_geometria()
        self._crear_frame_cargas()

        self.cambiar_seccion("Geometría")

    def _crear_frame_geometria(self):
        f = ctk.CTkScrollableFrame(self.panel_der)
        self.frames_seccion["Geometría"] = f

        ctk.CTkLabel(f, text="Geometría del túnel",
                     font=("Arial", 14, "bold")).pack(padx=16, pady=(16, 8), anchor="w")

        params = [
            ("Radio (eje) (m)", "—"),
            ("Nº nodos por anillo", "—"),
            ("Nº módulos", "—"),
            ("Longitud longitudinal (m)", "—"),
            ("Áreas por anillo", "—"),
            ("Separación módulos (m)", "—"),
        ]

        frame_grid = ctk.CTkFrame(f, fg_color="transparent")
        frame_grid.pack(padx=16, fill="x")

        for i, (label, placeholder) in enumerate(params):
            col = i % 2
            row = i // 2
            frame_grid.grid_columnconfigure(col, weight=1)
            sub = ctk.CTkFrame(frame_grid, fg_color="transparent")
            sub.grid(row=row, column=col, padx=8, pady=4, sticky="ew")
            ctk.CTkLabel(sub, text=label, font=("Arial", 10),
                         text_color="gray").pack(anchor="w")
            entry = ctk.CTkEntry(sub, height=30, placeholder_text=placeholder,
                                 state="disabled", fg_color=("gray90", "gray20"))
            entry.pack(fill="x")

    def _crear_frame_cargas(self):
        f = ctk.CTkScrollableFrame(self.panel_der)
        self.frames_seccion["Cargas"] = f

        ctk.CTkLabel(f, text="Parámetros de carga",
                     font=("Arial", 14, "bold")).pack(padx=16, pady=(16, 8), anchor="w")

        params_c = [
            ("k0", "—"),
            ("Densidad terreno (kN/m³)", "—"),
            ("Densidad agua (kN/m³)", "—"),
            ("Altura tierras en clave (m)", "—"),
            ("Altura agua en clave (m)", "—"),
        ]

        frame_grid = ctk.CTkFrame(f, fg_color="transparent")
        frame_grid.pack(padx=16, fill="x")

        for i, (label, placeholder) in enumerate(params_c):
            col = i % 2
            row = i // 2
            frame_grid.grid_columnconfigure(col, weight=1)
            sub = ctk.CTkFrame(frame_grid, fg_color="transparent")
            sub.grid(row=row, column=col, padx=8, pady=4, sticky="ew")
            ctk.CTkLabel(sub, text=label, font=("Arial", 10),
                         text_color="gray").pack(anchor="w")
            entry = ctk.CTkEntry(sub, height=30, placeholder_text=placeholder,
                                 state="disabled", fg_color=("gray90", "gray20"))
            entry.pack(fill="x")

    def cambiar_seccion(self, seccion):
        self.seccion_activa = seccion
        for nombre, frame in self.frames_seccion.items():
            if nombre == seccion:
                frame.pack(fill="both", expand=True, padx=4, pady=4)
            else:
                frame.pack_forget()
        for nombre, btn in self.botones_nav.items():
            if nombre == seccion:
                btn.configure(fg_color=("gray75", "gray30"))
            else:
                btn.configure(fg_color="transparent")

if __name__ == "__main__":
    app = App()
    app.mainloop()
