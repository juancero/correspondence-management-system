import tkinter as tk
from tkinter import messagebox

from database import get_connection
from screens.detalle_rendicion_screen import DetalleRendicionScreen


class EstadoRendicionesScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Estado de Rendiciones")
        self.geometry("750x500")

        self.rendiciones = []

        self.build_ui()
        self.cargar_rendiciones()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Estado de Rendiciones",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        self.lista = tk.Listbox(
            self,
            width=100,
            height=22,
            font=("Consolas", 10)
        )
        self.lista.pack(pady=10)

        self.lista.bind("<Double-Button-1>", self.abrir_detalle)

        btn_refrescar = tk.Button(
            self,
            text="Refrescar",
            width=20,
            command=self.cargar_rendiciones
        )
        btn_refrescar.pack(pady=5)

    def cargar_rendiciones(self):
        self.lista.delete(0, tk.END)
        self.rendiciones = []

        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT
                    r.id,
                    r.numero,
                    r.fecha,
                    COUNT(rd.id) AS total
                FROM rendiciones r
                LEFT JOIN rendicion_detalle rd ON rd.id_rendicion = r.id
                GROUP BY r.id, r.numero, r.fecha
                ORDER BY r.id DESC
            """)

            rows = cur.fetchall()

        header = (
            f"{'Rendición':15}"
            f"{'Fecha':15}"
            f"{'Total piezas':15}"
        )

        self.lista.insert(tk.END, header)
        self.lista.insert(tk.END, "-" * 50)

        for r in rows:
            self.rendiciones.append(r)

            linea = (
                f"{str(r['numero'] or ''):15}"
                f"{str(r['fecha'] or ''):15}"
                f"{str(r['total'] or 0):15}"
            )

            self.lista.insert(tk.END, linea)

    def abrir_detalle(self, event=None):
        seleccion = self.lista.curselection()

        if not seleccion:
            return

        index = seleccion[0]

        if index < 2:
            messagebox.showwarning(
                "Atención",
                "Seleccioná una rendición válida."
            )
            return

        rendicion = self.rendiciones[index - 2]

        DetalleRendicionScreen(
            self,
            rendicion["id"],
            rendicion["numero"]
        )
