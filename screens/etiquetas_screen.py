import tkinter as tk
from tkinter import messagebox, filedialog

from services.etiquetas_service import generar_pdf_etiquetas


class EtiquetasScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Generar Etiquetas de Prueba")
        self.geometry("400x250")

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Etiquetas de Prueba",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=15)

        info = tk.Label(
            self,
            text=(
                "Genera etiquetas con código de barras\n"
                "para probar scanner, despacho y rendición."
            ),
            justify="center"
        )
        info.pack(pady=5)

        frame = tk.Frame(self)
        frame.pack(pady=20)

        tk.Label(frame, text="Cantidad:").pack(side=tk.LEFT)

        self.entry_cantidad = tk.Entry(frame, width=10)
        self.entry_cantidad.insert(0, "20")
        self.entry_cantidad.pack(side=tk.LEFT, padx=5)

        btn_generar = tk.Button(
            self,
            text="Generar PDF",
            width=20,
            height=2,
            command=self.generar
        )
        btn_generar.pack(pady=15)

    def generar(self):
        cantidad = self.entry_cantidad.get().strip()

        if not cantidad.isdigit():
            messagebox.showwarning(
                "Atención",
                "Ingresá una cantidad válida."
            )
            return

        cantidad = int(cantidad)

        if cantidad <= 0:
            messagebox.showwarning(
                "Atención",
                "La cantidad debe ser mayor a cero."
            )
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar etiquetas",
            defaultextension=".pdf",
            initialfile="etiquetas_prueba.pdf",
            filetypes=[("PDF", "*.pdf")]
        )

        if not ruta:
            return

        generar_pdf_etiquetas(cantidad, ruta)

        messagebox.showinfo(
            "OK",
            "PDF de etiquetas generado correctamente."
        )
