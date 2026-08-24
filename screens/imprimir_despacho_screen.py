import tkinter as tk
from tkinter import messagebox, filedialog

from database import get_connection
from services.pdf_service import generar_pdf_despacho


class ImprimirDespachoScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Reimprimir Despacho")
        self.geometry("700x500")

        self.despachos = []

        self.build_ui()
        self.cargar_despachos()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Reimprimir Despacho",
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
            command=self.cargar_despachos
        )
        btn_refrescar.pack(pady=5)

    def cargar_despachos(self):
        self.lista.delete(0, tk.END)
        self.despachos = []

        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    d.id,
                    d.numero,
                    d.fecha,
                    d.estado,
                    COUNT(dd.id) AS total
                FROM despachos d
                LEFT JOIN despacho_detalle dd ON dd.id_despacho = d.id
                GROUP BY d.id
                ORDER BY d.id DESC
            """)

            rows = cur.fetchall()

        for d in rows:
            self.despachos.append(d)
            self.lista.insert(
                tk.END,
                f"{d['numero']} | Fecha: {d['fecha']} | Estado: {d['estado']} | Piezas: {d['total']}"
            )

    def generar_pdf(self):
        seleccion = self.lista.curselection()

        if not seleccion:
            messagebox.showwarning("Atención", "Seleccioná un despacho.")
            return

        despacho = self.despachos[seleccion[0]]

        ruta = filedialog.asksaveasfilename(
            title="Guardar PDF de despacho",
            defaultextension=".pdf",
            initialfile=f"despacho_{despacho['numero']}.pdf",
            filetypes=[("PDF", "*.pdf")]
        )

        if not ruta:
            return

        generar_pdf_despacho(despacho["id"], ruta)

        messagebox.showinfo("OK", "PDF generado correctamente.")
