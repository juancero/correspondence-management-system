import tkinter as tk
from tkinter import filedialog, messagebox

from database import get_connection
from services.excel_service import generar_excel_estado_despacho
from services.despacho_service import quitar_pieza_de_despacho


class DetalleDespachoScreen(tk.Toplevel):
    def __init__(self, parent, id_despacho, numero_despacho):
        super().__init__(parent)

        self.id_despacho = id_despacho
        self.numero_despacho = numero_despacho

        self.title(f"Detalle Despacho {numero_despacho}")
        self.geometry("1100x600")

        self.build_ui()
        self.cargar_detalle()

    def build_ui(self):
        title = tk.Label(
            self,
            text=f"Detalle Despacho {self.numero_despacho}",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        self.lbl_resumen = tk.Label(
            self,
            text="",
            font=("Arial", 11, "bold"),
            fg="blue"
        )
        self.lbl_resumen.pack(pady=5)

        self.lista = tk.Listbox(
            self,
            width=170,
            height=28,
            font=("Consolas", 10)
        )
        self.lista.pack(pady=10)

        btn_refrescar = tk.Button(
            self,
            text="Refrescar",
            width=20,
            command=self.cargar_detalle
        )
        btn_refrescar.pack(pady=5)

        btn_excel = tk.Button(
            self,
            text="Exportar Excel",
            width=20,
            command=self.exportar_excel
        )
        btn_excel.pack(pady=5)

        btn_quitar = tk.Button(
            self,
            text="Quitar pieza seleccionada",
            width=25,
            command=self.quitar_pieza
        )
        btn_quitar.pack(pady=5)

    def cargar_detalle(self):
        self.lista.delete(0, tk.END)

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
                    c.numero_rendicion
                FROM despacho_detalle dd
                JOIN correspondencias c ON c.id = dd.id_correspondencia
                WHERE dd.id_despacho = ?
                ORDER BY dd.id ASC
            """, (self.id_despacho,))

            rows = cur.fetchall()

            total = len(rows)

            pendientes = 0
            rendidas = 0

            estadisticas = {}

            for r in rows:
                if r["estado"] == "rendida":
                    rendidas += 1

                    resultado = r["resultado_rendicion"] or "sin_resultado"

                    if resultado not in estadisticas:
                        estadisticas[resultado] = 0

                    estadisticas[resultado] += 1
                else:
                    pendientes += 1
            resumen = (
                f"Total: {total}   |   "
                f"Pendientes: {pendientes}   |   "
                f"Rendidas: {rendidas}"
            )

            if estadisticas:
                detalle_stats = "   |   ".join(
                    [f"{k}: {v}" for k, v in estadisticas.items()]
                )

                resumen += f"\n{detalle_stats}"

            self.lbl_resumen.config(text=resumen)

        header = (
            f"{'Código':18}"
            f"{'Nombre':35}"
            f"{'Domicilio':40}"
            f"{'Localidad':25}"
            f"{'Estado':15}"
            f"{'Resultado':25}"
            f"{'Rendición':15}"
        )

        self.lista.insert(tk.END, header)
        self.lista.insert(tk.END, "-" * 175)

        for r in rows:
            linea = (
                f"{str(r['codigo'] or ''):18}"
                f"{str(r['apellido_nombre'] or '')[:34]:35}"
                f"{str(r['domicilio'] or '')[:39]:40}"
                f"{str(r['localidad'] or '')[:24]:25}"
                f"{str(r['estado'] or ''):15}"
                f"{str(r['resultado_rendicion'] or ''):25}"
                f"{str(r['numero_rendicion'] or ''):15}"
            )

            self.lista.insert(tk.END, linea)

    def exportar_excel(self):
        ruta = filedialog.asksaveasfilename(
            title="Guardar estado de despacho",
            defaultextension=".xlsx",
            initialfile=f"estado_despacho_{self.numero_despacho}.xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )

        if not ruta:
            return

        try:
            generar_excel_estado_despacho(
                self.id_despacho,
                ruta
            )

            messagebox.showinfo(
                "OK",
                "Excel generado correctamente."
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo generar el Excel:\n\n{e}"
            )

    def quitar_pieza(self):
        seleccion = self.lista.curselection()

        if not seleccion:
            messagebox.showwarning(
                "Atención",
                "Seleccioná una pieza de la lista."
            )
            return

        index = seleccion[0]

        if index < 2:
            messagebox.showwarning(
                "Atención",
                "Seleccioná una pieza válida, no el encabezado."
            )
            return

        linea = self.lista.get(index)
        codigo = linea[:18].strip()

        if not codigo:
            messagebox.showwarning(
                "Atención",
                "No se pudo obtener el código de la pieza."
            )
            return

        confirmar = messagebox.askyesno(
            "Quitar pieza",
            f"¿Quitar la pieza {codigo} del despacho {self.numero_despacho}?\n\n"
            "La pieza volverá a estado pendiente."
        )

        if not confirmar:
            return

        resultado = quitar_pieza_de_despacho(
            self.id_despacho,
            codigo
        )

        if not resultado["ok"]:
            messagebox.showerror(
                "No se pudo quitar",
                resultado["mensaje"]
            )
            return

        messagebox.showinfo(
            "OK",
            resultado["mensaje"]
        )

        self.cargar_detalle()
