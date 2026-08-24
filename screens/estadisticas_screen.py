import tkinter as tk
from tkinter import messagebox

from database import get_connection


class EstadisticasScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Estadísticas")
        self.geometry("1050x720")

        self.build_ui()
        self.cargar_estadisticas()

    def build_ui(self):
        titulo = tk.Label(
            self,
            text="Estadísticas generales y por grupo",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=15)

        frame_resumen = tk.Frame(self)
        frame_resumen.pack(pady=5)

        self.lbl_general = tk.Label(
            frame_resumen,
            text="",
            font=("Arial", 11, "bold"),
            justify=tk.LEFT,
            anchor="w"
        )
        self.lbl_general.grid(row=0, column=0, padx=25, sticky="n")

        self.lbl_grupo_1 = tk.Label(
            frame_resumen,
            text="",
            font=("Arial", 11, "bold"),
            justify=tk.LEFT,
            anchor="w"
        )
        self.lbl_grupo_1.grid(row=0, column=1, padx=25, sticky="n")

        self.lbl_grupo_2 = tk.Label(
            frame_resumen,
            text="",
            font=("Arial", 11, "bold"),
            justify=tk.LEFT,
            anchor="w"
        )
        self.lbl_grupo_2.grid(row=0, column=2, padx=25, sticky="n")

        tk.Label(
            self,
            text="Cantidades por motivo de rendición",
            font=("Arial", 13, "bold")
        ).pack(pady=(20, 8))

        self.lista_motivos = tk.Listbox(
            self,
            width=145,
            height=22,
            font=("Consolas", 10)
        )
        self.lista_motivos.pack(pady=8)

        btn_refrescar = tk.Button(
            self,
            text="Refrescar",
            width=20,
            command=self.cargar_estadisticas
        )
        btn_refrescar.pack(pady=10)

    def obtener_resumen(self, id_desde=None, id_hasta=None):
        condiciones = []
        parametros = []

        if id_desde is not None and id_hasta is not None:
            condiciones.append("id BETWEEN ? AND ?")
            parametros.extend([id_desde, id_hasta])

        where = ""

        if condiciones:
            where = "WHERE " + " AND ".join(condiciones)

        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute(
                f"""
                SELECT COUNT(*) AS total
                FROM correspondencias
                {where}
                """,
                parametros
            )

            total = cur.fetchone()["total"]

            cur.execute(
                f"""
                SELECT estado, COUNT(*) AS cantidad
                FROM correspondencias
                {where}
                GROUP BY estado
                """,
                parametros
            )

            rows = cur.fetchall()

        cantidades = {
            "pendiente": 0,
            "despachada": 0,
            "rendida": 0
        }

        for fila in rows:
            estado = fila["estado"]

            if estado in cantidades:
                cantidades[estado] = fila["cantidad"]

        return {
            "total": total,
            "pendiente": cantidades["pendiente"],
            "despachada": cantidades["despachada"],
            "rendida": cantidades["rendida"]
        }

    def obtener_motivos(self, id_desde=None, id_hasta=None):
        condiciones = [
            "c.estado = 'rendida'"
        ]

        parametros = []

        if id_desde is not None and id_hasta is not None:
            condiciones.append("c.id BETWEEN ? AND ?")
            parametros.extend([id_desde, id_hasta])

        where = "WHERE " + " AND ".join(condiciones)

        with get_connection() as conn:
            cur = conn.cursor()

            cur.execute(
                f"""
                SELECT
                    COALESCE(
                        mr.nombre,
                        c.resultado_rendicion,
                        'Sin motivo'
                    ) AS motivo,
                    COUNT(*) AS cantidad
                FROM correspondencias c
                LEFT JOIN motivos_rendicion mr
                    ON mr.codigo = c.resultado_rendicion
                {where}
                GROUP BY
                    COALESCE(
                        mr.nombre,
                        c.resultado_rendicion,
                        'Sin motivo'
                    )
                ORDER BY cantidad DESC
                """,
                parametros
            )

            return cur.fetchall()

    def formatear_resumen(self, titulo, datos):
        return (
            f"{titulo}\n\n"
            f"Total: {datos['total']}\n"
            f"Pendientes: {datos['pendiente']}\n"
            f"Despachadas: {datos['despachada']}\n"
            f"Rendidas: {datos['rendida']}"
        )

    def agregar_motivos_a_lista(self, titulo, motivos):
        self.lista_motivos.insert(tk.END, titulo)
        self.lista_motivos.insert(tk.END, "-" * 100)

        if not motivos:
            self.lista_motivos.insert(
                tk.END,
                "No hay piezas rendidas en este grupo."
            )
        else:
            for fila in motivos:
                motivo = str(fila["motivo"] or "Sin motivo")
                cantidad = fila["cantidad"]

                linea = (
                    f"{motivo[:60]:62}"
                    f"{cantidad:12}"
                )

                self.lista_motivos.insert(tk.END, linea)

        self.lista_motivos.insert(tk.END, "")

    def cargar_estadisticas(self):
        try:
            general = self.obtener_resumen()

            grupo_1 = self.obtener_resumen(
                id_desde=1,
                id_hasta=10877
            )

            grupo_2 = self.obtener_resumen(
                id_desde=10878,
                id_hasta=30616
            )

            self.lbl_general.config(
                text=self.formatear_resumen(
                    "GENERAL",
                    general
                ),
                fg="black"
            )

            self.lbl_grupo_1.config(
                text=self.formatear_resumen(
                    "NORTE",
                    grupo_1
                ),
                fg="blue"
            )

            self.lbl_grupo_2.config(
                text=self.formatear_resumen(
                    "SUR",
                    grupo_2
                ),
                fg="green"
            )

            motivos_general = self.obtener_motivos()

            motivos_grupo_1 = self.obtener_motivos(
                id_desde=1,
                id_hasta=10877
            )

            motivos_grupo_2 = self.obtener_motivos(
                id_desde=10878,
                id_hasta=30616
            )

            self.lista_motivos.delete(0, tk.END)

            self.agregar_motivos_a_lista(
                "GENERAL",
                motivos_general
            )

            self.agregar_motivos_a_lista(
                "NORTE",
                motivos_grupo_1
            )

            self.agregar_motivos_a_lista(
                "SUR",
                motivos_grupo_2
            )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudieron cargar las estadísticas:\n\n{e}"
            )
