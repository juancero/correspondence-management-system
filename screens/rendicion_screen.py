import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import date

from services.excel_service import generar_excel_rendicion
from services.motivos_service import listar_motivos

from services.rendicion_service import (
    buscar_pieza,
    guardar_rendicion_completa,
)


class RendicionScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Rendición")
        self.geometry("900x620")

        self.id_rendicion = None
        self.numero_rendicion = None

        self.piezas_temporales = []
        self.codigos_temporales = set()

        self.motivos = listar_motivos()
        self.motivo_actual = tk.StringVar()

        if self.motivos:
            self.motivo_actual.set(self.motivos[0]["nombre"])
        else:
            self.motivo_actual.set("")

        self.fecha_rendicion = tk.StringVar(
            value=date.today().strftime("%Y-%m-%d")
        )

        self.build_ui()
        self.bloquear_scanner()

    def build_ui(self):
        frame_top = tk.Frame(self)
        frame_top.pack(pady=10)

        self.btn_nueva = tk.Button(
            frame_top,
            text="Nueva rendición",
            width=20,
            command=self.nueva_rendicion
        )
        self.btn_nueva.pack(side=tk.LEFT, padx=5)

        self.btn_cerrar = tk.Button(
            frame_top,
            text="Generar rendición",
            width=20,
            command=self.generar_rendicion
        )
        self.btn_cerrar.pack(side=tk.LEFT, padx=5)

        self.btn_cancelar = tk.Button(
            frame_top,
            text="Cancelar rendición",
            width=20,
            command=self.cancelar
        )
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)

        self.btn_excel = tk.Button(
            frame_top,
            text="Generar Excel",
            width=20,
            command=self.exportar_excel
        )
        self.btn_excel.pack(side=tk.LEFT, padx=5)

        self.lbl_estado = tk.Label(self, text="Sin rendición activa", fg="red")
        self.lbl_estado.pack(pady=5)

        frame_config = tk.Frame(self)
        frame_config.pack(pady=8)

        tk.Label(frame_config, text="Fecha:").pack(side=tk.LEFT)
        self.entry_fecha = tk.Entry(
            frame_config,
            textvariable=self.fecha_rendicion,
            width=12
        )
        self.entry_fecha.pack(side=tk.LEFT, padx=5)

        tk.Label(frame_config, text="Motivo:").pack(side=tk.LEFT, padx=(20, 5))
        motivos_nombres = [m["nombre"] for m in self.motivos]

        self.combo_motivo = tk.OptionMenu(
            frame_config,
            self.motivo_actual,
            *motivos_nombres
        )
        self.combo_motivo.pack(side=tk.LEFT)

        tk.Label(self, text="Escanear código").pack(pady=(15, 0))

        self.scanner = tk.Entry(self, width=45, font=("Arial", 14))
        self.scanner.pack(pady=8)
        self.scanner.bind("<Return>", self.scan)

        self.lbl_ultima = tk.Label(
            self,
            text="---",
            font=("Arial", 16, "bold")
        )
        self.lbl_ultima.pack(pady=5)

        self.lista = tk.Listbox(self, width=130, height=22)
        self.lista.pack(pady=10)

        self.lbl_total = tk.Label(
            self,
            text="Piezas rendidas: 0",
            font=("Arial", 11, "bold")
        )
        self.lbl_total.pack()

    def nueva_rendicion(self):
        fecha = self.fecha_rendicion.get().strip()

        if not fecha:
            messagebox.showwarning("Atención", "Ingresá una fecha.")
            return

        self.id_rendicion = None
        self.numero_rendicion = "BORRADOR"

        self.piezas_temporales = []
        self.codigos_temporales = set()

        self.lbl_estado.config(
            text="Rendición en preparación",
            fg="orange"
        )

        self.lbl_ultima.config(text="---", fg="black")
        self.lista.delete(0, tk.END)
        self.lbl_total.config(text="Piezas rendidas: 0")

        self.habilitar_scanner()
        self.btn_excel.config(state="disabled")
        self.btn_nueva.config(state="disabled")
        self.entry_fecha.config(state="disabled")

    def scan(self, event):
        codigo = self.scanner.get().strip()
        self.scanner.delete(0, tk.END)

        if self.numero_rendicion != "BORRADOR":
            self.lbl_ultima.config(text="❌ SIN RENDICIÓN", fg="red")
            return

        if not codigo:
            return

        if codigo in self.codigos_temporales:
            self.lbl_ultima.config(text="❌ YA ESCANEADA", fg="red")
            return

        motivo_label = self.motivo_actual.get()
        resultado = None

        for m in self.motivos:
            if m["nombre"] == motivo_label:
                resultado = m["codigo"]
                break

        if not resultado:
            self.lbl_ultima.config(text="❌ MOTIVO INVÁLIDO", fg="red")
            return

        pieza = buscar_pieza(codigo)

        if not pieza:
            self.lbl_ultima.config(text="❌ NO EXISTE", fg="red")
            return

        if pieza["estado"] == "rendida":
            self.lbl_ultima.config(
                text=f"❌ YA EN {pieza['numero_rendicion']}",
                fg="red"
            )
            return

        pieza_dict = dict(pieza)
        pieza_dict["resultado"] = resultado
        pieza_dict["motivo_label"] = motivo_label

        self.piezas_temporales.append(pieza_dict)
        self.codigos_temporales.add(codigo)

        self.lbl_ultima.config(
            text=f"✔ {pieza_dict['codigo']} - {motivo_label}",
            fg="green"
        )

        self.refresh_lista()

    def refresh_lista(self):
        self.lista.delete(0, tk.END)

        for p in self.piezas_temporales:
            self.lista.insert(
                tk.END,
                f"{p['codigo']} | {p['apellido_nombre']} | {p['domicilio']} | "
                f"{p['localidad']} | {p['motivo_label']}"
            )

        self.lbl_total.config(
            text=f"Piezas rendidas: {len(self.piezas_temporales)}"
        )

        if self.id_rendicion:
            self.btn_excel.config(state="normal")
        else:
            self.btn_excel.config(state="disabled")

    def generar_rendicion(self):
        if self.numero_rendicion != "BORRADOR":
            messagebox.showwarning(
                "Atención",
                "No hay rendición en preparación."
            )
            return

        if not self.piezas_temporales:
            messagebox.showwarning(
                "Atención",
                "No hay piezas cargadas."
            )
            return

        confirmar = messagebox.askyesno(
            "Generar rendición",
            f"¿Generar rendición?\n\n"
            f"Total de piezas: {len(self.piezas_temporales)}\n\n"
            "Recién ahora se guardará en la base."
        )

        if not confirmar:
            return

        fecha = self.fecha_rendicion.get().strip()

        rendicion = guardar_rendicion_completa(
            fecha,
            self.piezas_temporales
        )

        self.id_rendicion = rendicion["id"]
        self.numero_rendicion = rendicion["numero"]

        self.lbl_estado.config(
            text=f"Rendición generada: {self.numero_rendicion}",
            fg="green"
        )

        self.scanner.config(state="disabled")
        self.btn_cerrar.config(state="disabled")
        self.btn_cancelar.config(state="disabled")
        self.btn_excel.config(state="normal")

        messagebox.showinfo(
            "Rendición generada",
            f"Rendición {self.numero_rendicion} generada correctamente."
        )

        self.refresh_lista()

    def exportar_excel(self):
        if not self.id_rendicion:
            messagebox.showwarning("Atención", "Primero generá la rendición.")
            return

        ruta = filedialog.asksaveasfilename(
            title="Guardar Excel de rendición",
            defaultextension=".xlsx",
            initialfile=f"rendicion_{self.numero_rendicion}.xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )

        if not ruta:
            return

        generar_excel_rendicion(self.id_rendicion, ruta)

        messagebox.showinfo(
            "Excel generado",
            f"Excel de la rendición {self.numero_rendicion} generado correctamente."
        )

        self.limpiar_pantalla()

    def cancelar(self):
        if self.numero_rendicion != "BORRADOR":
            self.limpiar_pantalla()
            return

        if not self.piezas_temporales:
            self.limpiar_pantalla()
            return

        confirmar = messagebox.askyesno(
            "Cancelar rendición",
            "¿Descartar la rendición en preparación?\n\n"
            "No se guardará nada en la base."
        )

        if not confirmar:
            return

        self.limpiar_pantalla()

    def limpiar_pantalla(self):
        self.id_rendicion = None
        self.numero_rendicion = None

        self.piezas_temporales = []
        self.codigos_temporales = set()

        self.lbl_estado.config(text="Sin rendición activa", fg="red")
        self.lbl_ultima.config(text="---", fg="black")
        self.lista.delete(0, tk.END)
        self.lbl_total.config(text="Piezas rendidas: 0")

        self.bloquear_scanner()
        self.btn_nueva.config(state="normal")
        self.entry_fecha.config(state="normal")

    def bloquear_scanner(self):
        self.scanner.config(state="disabled")
        self.btn_cerrar.config(state="disabled")
        self.btn_cancelar.config(state="disabled")
        self.btn_excel.config(state="disabled")

    def habilitar_scanner(self):
        self.scanner.config(state="normal")
        self.btn_cerrar.config(state="normal")
        self.btn_cancelar.config(state="normal")
        self.btn_excel.config(state="disabled")
        self.scanner.focus_set()
