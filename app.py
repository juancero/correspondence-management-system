import tkinter as tk
from tkinter import messagebox

from database import init_db, get_db_name
from services.backup_service import crear_backup
from screens.import_screen import ImportScreen
from screens.despacho_screen import DespachoScreen
from screens.rendicion_screen import RendicionScreen
from screens.imprimir_rendicion_screen import ImprimirRendicionScreen
from screens.motivos_screen import MotivosScreen
from screens.imprimir_despacho_screen import ImprimirDespachoScreen
from screens.estado_despachos_screen import EstadoDespachosScreen
from screens.estado_rendiciones_screen import EstadoRendicionesScreen
from screens.busqueda_pieza_screen import BusquedaPiezaScreen
from screens.etiquetas_screen import EtiquetasScreen
from screens.estadisticas_screen import EstadisticasScreen


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Correspondencia")
        self.root.geometry("600x800")

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="Sistema de Correspondencia",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=20)

        lbl_base = tk.Label(
            self.root,
            text=f"Base activa: {get_db_name()}",
            fg="blue",
            font=("Arial", 9, "bold")
        )
        lbl_base.pack(pady=3)

        btn_importar = tk.Button(
            self.root,
            text="Importar Correspondencia",
            width=30,
            height=1,
            command=self.importar
        )
        btn_importar.pack(pady=5)

        btn_despacho = tk.Button(
            self.root,
            text="Crear / Abrir Despacho",
            width=30,
            height=1,
            command=self.despacho
        )
        btn_despacho.pack(pady=5)

        btn_rendicion = tk.Button(
            self.root,
            text="Rendir Despacho",
            width=30,
            height=1,
            command=self.rendicion
        )
        btn_rendicion.pack(pady=5)

        btn_imprimir_rendicion = tk.Button(
            self.root,
            text="Imprimir Rendición",
            width=30,
            height=1,
            command=self.imprimir_rendicion
        )
        btn_imprimir_rendicion.pack(pady=5)

        btn_motivos = tk.Button(
            self.root,
            text="Motivos de Rendición",
            width=30,
            height=1,
            command=self.motivos
        )
        btn_motivos.pack(pady=5)

        btn_imprimir_despacho = tk.Button(
            self.root,
            text="Reimprimir Despacho",
            width=30,
            height=1,
            command=self.imprimir_despacho
        )
        btn_imprimir_despacho.pack(pady=5)

        btn_estado_despachos = tk.Button(
            self.root,
            text="Estado de Despachos",
            width=30,
            height=1,
            command=self.estado_despachos
        )
        btn_estado_despachos.pack(pady=5)

        btn_estado_rendiciones = tk.Button(
            self.root,
            text="Estado de Rendiciones",
            width=30,
            height=1,
            command=self.estado_rendiciones
        )
        btn_estado_rendiciones.pack(pady=5)

        btn_busqueda = tk.Button(
            self.root,
            text="Buscar Pieza",
            width=30,
            height=1,
            command=self.buscar_pieza
        )
        btn_busqueda.pack(pady=5)

        btn_etiquetas = tk.Button(
            self.root,
            text="Etiquetas de Prueba",
            width=30,
            height=1,
            command=self.etiquetas
        )
        btn_etiquetas.pack(pady=5)

        btn_backup = tk.Button(
            self.root,
            text="Crear Backup",
            width=30,
            height=1,
            command=self.crear_backup
        )
        btn_backup.pack(pady=5)

        btn_estadisticas = tk.Button(
            self.root,
            text="Estadísticas",
            width=30,
            height=1,
            command=self.estadisticas
        )
        btn_estadisticas.pack(pady=5)

        btn_salir = tk.Button(
            self.root,
            text="Salir",
            width=30,
            height=1,
            command=self.root.quit
        )
        btn_salir.pack(pady=20)

    def importar(self):
        ImportScreen(self.root)

    def despacho(self):
        DespachoScreen(self.root)

    def rendicion(self):
        RendicionScreen(self.root)

    def estadisticas(self):
        EstadisticasScreen(self.root)

    def imprimir_rendicion(self):
        ImprimirRendicionScreen(self.root)

    def motivos(self):
        MotivosScreen(self.root)

    def imprimir_despacho(self):
        ImprimirDespachoScreen(self.root)

    def estado_despachos(self):
        EstadoDespachosScreen(self.root)

    def estado_rendiciones(self):
        EstadoRendicionesScreen(self.root)

    def buscar_pieza(self):
        BusquedaPiezaScreen(self.root)

    def etiquetas(self):
        EtiquetasScreen(self.root)

    def crear_backup(self):
        try:
            destino = crear_backup()
            messagebox.showinfo(
                "Backup creado",
                f"Backup generado correctamente:\n\n{destino}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo crear el backup:\n\n{e}")


if __name__ == "__main__":
    # Inicializa base si no existe
    init_db()

    root = tk.Tk()
    app = App(root)
    root.mainloop()
