import tkinter as tk
from tkinter import messagebox

from services.rendicion_service import (
    listar_piezas_rendicion,
    quitar_pieza_de_rendicion
)


class DetalleRendicionScreen(tk.Toplevel):
    def __init__(self, parent, id_rendicion, numero_rendicion):
        super().__init__(parent)

        self.id_rendicion = id_rendicion
        self.numero_rendicion = numero_rendicion

        self.title(f"Detalle Rendición {numero_rendicion}")
        self.geometry("1000x600")

        self.build_ui()
        self.cargar_detalle()

    def build_ui(self):
        title = tk.Label(
            self,
            text=f"Detalle Rendición {self.numero_rendicion}",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        self.lista = tk.Listbox(
            self,
            width=150,
            height=28,
            font=("Consolas", 10)
        )
        self.lista.pack(pady=10)

        btn_quitar = tk.Button(
            self,
            text="Quitar pieza seleccionada",
            width=30,
            command=self.quitar_pieza
        )
        btn_quitar.pack(pady=5)

        btn_refrescar = tk.Button(
            self,
            text="Refrescar",
            width=20,
            command=self.cargar_detalle
        )
        btn_refrescar.pack(pady=5)

    def cargar_detalle(self):
        self.lista.delete(0, tk.END)

        rows = listar_piezas_rendicion(self.id_rendicion)

        header = (
            f"{'Código':18}"
            f"{'Nombre':35}"
            f"{'Domicilio':40}"
            f"{'Localidad':25}"
            f"{'Resultado':25}"
            f"{'Fecha':15}"
        )

        self.lista.insert(tk.END, header)
        self.lista.insert(tk.END, "-" * 160)

        for r in rows:
            linea = (
                f"{str(r['codigo'] or ''):18}"
                f"{str(r['apellido_nombre'] or '')[:34]:35}"
                f"{str(r['domicilio'] or '')[:39]:40}"
                f"{str(r['localidad'] or '')[:24]:25}"
                f"{str(r['resultado'] or '')[:24]:25}"
                f"{str(r['fecha_rendicion'] or ''):15}"
            )

            self.lista.insert(tk.END, linea)

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
            f"¿Quitar la pieza {codigo} de la rendición {self.numero_rendicion}?\n\n"
            "Si tenía despacho volverá a despachada.\n"
            "Si no tenía despacho volverá a pendiente."
        )

        if not confirmar:
            return

        resultado = quitar_pieza_de_rendicion(
            self.id_rendicion,
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
