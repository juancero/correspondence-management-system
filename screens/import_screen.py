import tkinter as tk
from tkinter import filedialog, messagebox
from services.import_service import importar_archivo


class ImportScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Importar Correspondencia")
        self.geometry("600x400")
        self.resizable(False, False)

        self.ruta_archivo = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Importar Correspondencia",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=15)

        info = tk.Label(
            self,
            text=(
                "Estructura esperada del Excel:\n"
                "cod barra | Nro Envio/Orden | Nro Afiliado | Apellido y Nombre | "
                "Domicilio | CP | Localidad | Districto Electoral"
            ),
            fg="gray",
            justify="center"
        )
        info.pack(pady=5)

        nota = tk.Label(
            self,
            text="Importante: la columna 'cod barra' es obligatoria.",
            fg="red",
            font=("Arial", 9, "bold")
        )
        nota.pack(pady=3)

        frame_file = tk.Frame(self)
        frame_file.pack(pady=15)

        entry = tk.Entry(
            frame_file,
            textvariable=self.ruta_archivo,
            width=55,
            state="readonly"
        )
        entry.pack(side=tk.LEFT, padx=5)

        btn_buscar = tk.Button(
            frame_file,
            text="Buscar",
            command=self.seleccionar_archivo
        )
        btn_buscar.pack(side=tk.LEFT)

        btn_importar = tk.Button(
            self,
            text="Importar archivo",
            width=25,
            height=2,
            command=self.importar
        )
        btn_importar.pack(pady=10)

        self.resultado = tk.Text(self, height=12, width=70)
        self.resultado.pack(pady=10)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xlsm"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )

        if archivo:
            self.ruta_archivo.set(archivo)

    def importar(self):
        ruta = self.ruta_archivo.get()

        if not ruta:
            messagebox.showwarning(
                "Atención", "Seleccioná un archivo primero.")
            return

        try:
            self.resultado.delete("1.0", tk.END)
            self.resultado.insert(tk.END, "Importando archivo...\n")
            self.update_idletasks()

            resumen = importar_archivo(ruta)

            self.resultado.delete("1.0", tk.END)
            self.resultado.insert(
                tk.END, f"Insertados: {resumen['insertados']}\n")
            self.resultado.insert(
                tk.END, f"Duplicados: {resumen['duplicados']}\n")
            self.resultado.insert(tk.END, "\nErrores:\n")

            if resumen["errores"]:
                for error in resumen["errores"][:100]:
                    self.resultado.insert(tk.END, f"- {error}\n")

                if len(resumen["errores"]) > 100:
                    self.resultado.insert(
                        tk.END,
                        f"\nSe muestran solo los primeros 100 errores de {len(resumen['errores'])}.\n"
                    )
            else:
                self.resultado.insert(tk.END, "Sin errores.\n")

            messagebox.showinfo("Importación finalizada",
                                "El proceso terminó correctamente.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
