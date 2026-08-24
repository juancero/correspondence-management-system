import tkinter as tk
from tkinter import messagebox

from services.motivos_service import (
    listar_motivos,
    crear_motivo,
    cambiar_estado_motivo
)


def generar_codigo(nombre):
    return (
        nombre.strip()
        .lower()
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
        .replace("ñ", "n")
        .replace(" ", "_")
    )


class MotivosScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Motivos de Rendición")
        self.geometry("650x500")

        self.motivos = []

        self.build_ui()
        self.cargar_motivos()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Motivos de Rendición",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        frame_form = tk.Frame(self)
        frame_form.pack(pady=10)

        tk.Label(frame_form, text="Nuevo motivo:").pack(side=tk.LEFT)

        self.entry_nombre = tk.Entry(frame_form, width=35)
        self.entry_nombre.pack(side=tk.LEFT, padx=5)

        btn_agregar = tk.Button(
            frame_form,
            text="Agregar",
            command=self.agregar_motivo
        )
        btn_agregar.pack(side=tk.LEFT, padx=5)

        self.lista = tk.Listbox(self, width=85, height=18)
        self.lista.pack(pady=10)

        frame_buttons = tk.Frame(self)
        frame_buttons.pack(pady=10)

        btn_activar = tk.Button(
            frame_buttons,
            text="Activar",
            width=20,
            command=lambda: self.cambiar_estado(1)
        )
        btn_activar.pack(side=tk.LEFT, padx=5)

        btn_desactivar = tk.Button(
            frame_buttons,
            text="Desactivar",
            width=20,
            command=lambda: self.cambiar_estado(0)
        )
        btn_desactivar.pack(side=tk.LEFT, padx=5)

        btn_refrescar = tk.Button(
            frame_buttons,
            text="Refrescar",
            width=20,
            command=self.cargar_motivos
        )
        btn_refrescar.pack(side=tk.LEFT, padx=5)

    def cargar_motivos(self):
        self.lista.delete(0, tk.END)
        self.motivos = listar_motivos(activos_solo=False)

        for m in self.motivos:
            estado = "ACTIVO" if m["activo"] == 1 else "INACTIVO"
            self.lista.insert(
                tk.END,
                f"{m['nombre']} | {m['codigo']} | {estado}"
            )

    def agregar_motivo(self):
        nombre = self.entry_nombre.get().strip()

        if not nombre:
            messagebox.showwarning("Atención", "Ingresá un nombre de motivo.")
            return

        codigo = generar_codigo(nombre)

        respuesta = crear_motivo(nombre, codigo)

        if not respuesta["ok"]:
            messagebox.showerror("Error", respuesta["mensaje"])
            return

        self.entry_nombre.delete(0, tk.END)
        self.cargar_motivos()

        messagebox.showinfo("OK", respuesta["mensaje"])

    def cambiar_estado(self, activo):
        seleccion = self.lista.curselection()

        if not seleccion:
            messagebox.showwarning("Atención", "Seleccioná un motivo.")
            return

        motivo = self.motivos[seleccion[0]]

        cambiar_estado_motivo(motivo["id"], activo)

        self.cargar_motivos()
