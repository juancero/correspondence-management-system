import tkinter as tk
from tkinter import messagebox

from database import get_connection


class BusquedaPiezaScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Búsqueda de Pieza")
        self.geometry("950x500")

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Búsqueda Global de Pieza",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        frame_busqueda = tk.Frame(self)
        frame_busqueda.pack(pady=10)

        tk.Label(frame_busqueda, text="Código:").pack(side=tk.LEFT)

        self.entry_codigo = tk.Entry(
            frame_busqueda,
            width=40,
            font=("Arial", 12)
        )
        self.entry_codigo.pack(side=tk.LEFT, padx=5)

        self.entry_codigo.bind("<Return>", self.buscar)

        btn_buscar = tk.Button(
            frame_busqueda,
            text="Buscar",
            width=15,
            command=self.buscar
        )
        btn_buscar.pack(side=tk.LEFT, padx=5)

        self.lbl_estado = tk.Label(
            self,
            text="",
            font=("Arial", 11, "bold"),
            fg="blue"
        )
        self.lbl_estado.pack(pady=10)

        self.lista = tk.Listbox(
            self,
            width=140,
            height=18,
            font=("Consolas", 10)
        )
        self.lista.pack(pady=10)

    def buscar(self, event=None):
        codigo = self.entry_codigo.get().strip()

        self.lista.delete(0, tk.END)

        if not codigo:
            messagebox.showwarning("Atención", "Ingresá un código.")
            return

        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute("""
                SELECT 
                    c.codigo,
                    c.apellido_nombre,
                    c.domicilio,
                    c.localidad,
                    c.estado,
                    c.resultado_rendicion,
                    c.fecha_rendicion,
                    c.numero_rendicion,
                    d.numero AS numero_despacho

                FROM correspondencias c

                LEFT JOIN despacho_detalle dd
                    ON dd.id_correspondencia = c.id

                LEFT JOIN despachos d
                    ON d.id = dd.id_despacho

                WHERE c.codigo = ?
            """, (codigo,))

            pieza = cur.fetchone()

        if not pieza:
            self.lbl_estado.config(
                text="Pieza no encontrada",
                fg="red"
            )
            return

        self.lbl_estado.config(
            text=f"Pieza encontrada: {pieza['codigo']}",
            fg="green"
        )

        datos = [
            f"Código: {pieza['codigo']}",
            f"Nombre: {pieza['apellido_nombre']}",
            f"Domicilio: {pieza['domicilio']}",
            f"Localidad: {pieza['localidad']}",
            f"Estado: {pieza['estado']}",
            f"Despacho: {pieza['numero_despacho'] or '-'}",
            f"Rendición: {pieza['numero_rendicion'] or '-'}",
            f"Resultado: {pieza['resultado_rendicion'] or '-'}",
            f"Fecha Rendición: {pieza['fecha_rendicion'] or '-'}",
        ]

        for d in datos:
            self.lista.insert(tk.END, d)
