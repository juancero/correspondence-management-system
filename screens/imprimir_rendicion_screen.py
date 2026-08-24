import tkinter as tk
from tkinter import messagebox, filedialog

from database import get_connection
from services.pdf_service import generar_pdf_rendicion


class ImprimirRendicionScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Imprimir Rendición")
        self.geometry("700x500")

        self.rendiciones = []

        self.build_ui()
        self.cargar_rendiciones()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Imprimir Rendición",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        self.lista = tk.Listbox(self, width=100, height=18)
        self.lista.pack(pady=10)

        btn_pdf = tk.Button(
            self,
            text="Generar PDF",
            width=25,
            height=2,
            command=self.generar_pdf
        )
        btn_pdf.pack(pady=10)

        btn_refrescar = tk.Button(
            self,
            text="Refrescar",
            width=25,
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
                    r.estado,
                    COUNT(rd.id) AS total
                FROM rendiciones r
                LEFT JOIN rendicion_detalle rd ON rd.id_rendicion = r.id
                GROUP BY r.id
                ORDER BY r.id DESC
            """)

            rows = cur.fetchall()

        for r in rows:
            self.rendiciones.append(r)
            self.lista.insert(
                tk.END,
                f"{r['numero']} | Fecha: {r['fecha']} | Estado: {r['estado']} | Piezas: {r['total']}"
            )

    def generar_pdf(self):
        seleccion = self.lista.curselection()

        if not seleccion:
            messagebox.showwarning("Atención", "Seleccioná una rendición.")
            return

        rendicion = self.rendiciones[seleccion[0]]

        ruta = filedialog.asksaveasfilename(
            title="Guardar PDF de rendición",
            defaultextension=".pdf",
            initialfile=f"rendicion_{rendicion['numero']}.pdf",
            filetypes=[("PDF", "*.pdf")]
        )

        if not ruta:
            return

        generar_pdf_rendicion(rendicion["id"], ruta)

        messagebox.showinfo("OK", "PDF generado correctamente.")