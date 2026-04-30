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

if __name__ == "__main__":
    app = App()
    app.mainloop()
