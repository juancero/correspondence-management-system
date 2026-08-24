import tkinter as tk

from database import get_connection
from screens.detalle_despacho_screen import DetalleDespachoScreen


class EstadoDespachosScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Estado de Despachos")
        self.geometry("1000x600")

        self.despachos = []

        self.build_ui()
        self.cargar_despachos()

    def build_ui(self):
        title = tk.Label(
            self,
            text="Estado de Despachos",
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
        self.lista.bind("<Double-Button-1>", self.abrir_detalle)

        btn_refrescar = tk.Button(
            self,
            text="Refrescar",
            width=20,
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

                    COUNT(dd.id) AS total,

                    SUM(
                        CASE 
                            WHEN c.estado = 'rendida' THEN 1
                            ELSE 0
                        END
                    ) AS rendidas,

                    SUM(
                        CASE 
                            WHEN c.estado != 'rendida' THEN 1
                            ELSE 0
                        END
                    ) AS pendientes

                FROM despachos d

                LEFT JOIN despacho_detalle dd 
                    ON dd.id_despacho = d.id

                LEFT JOIN correspondencias c 
                    ON c.id = dd.id_correspondencia

                GROUP BY d.id

                ORDER BY d.id DESC
            """)

            rows = cur.fetchall()

        header = (
            f"{'Despacho':15}"
            f"{'Fecha':30}"
            f"{'Total':10}"
            f"{'Pendientes':15}"
            f"{'Rendidas':15}"
        )

        self.lista.insert(tk.END, header)
        self.lista.insert(tk.END, "-" * 90)

        for r in rows:
            self.despachos.append(r)
            linea = (
                f"{r['numero']:15}"
                f"{r['fecha']:22}"
                f"{r['total']:10}"
                f"{r['pendientes'] or 0:15}"
                f"{r['rendidas'] or 0:15}"
            )

            self.lista.insert(tk.END, linea)

    def abrir_detalle(self, event):
        seleccion = self.lista.curselection()

        if not seleccion:
            return

        index = seleccion[0]

        # Evita abrir detalle si hacen doble click en encabezado
        if index < 2:
            return

        despacho = self.despachos[index - 2]

        DetalleDespachoScreen(
            self,
            despacho["id"],
            despacho["numero"]
        )
