import os
import tempfile

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Paragraph,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet

from barcode import Code128
from barcode.writer import ImageWriter

from database import get_connection


def obtener_piezas_prueba(cantidad):
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                codigo,
                apellido_nombre,
                localidad
            FROM correspondencias
            WHERE estado = 'pendiente'
            ORDER BY RANDOM()
            LIMIT ?
        """, (cantidad,))

        return cur.fetchall()


def generar_pdf_etiquetas(cantidad, ruta_pdf):
    piezas = obtener_piezas_prueba(cantidad)

    doc = SimpleDocTemplate(ruta_pdf, pagesize=A4)

    estilos = getSampleStyleSheet()
    elementos = []

    carpeta_temp = tempfile.mkdtemp()

    for pieza in piezas:
        codigo = str(pieza["codigo"])

        barcode_path = os.path.join(carpeta_temp, codigo)

        barcode = Code128(
            codigo,
            writer=ImageWriter()
        )

        barcode.save(barcode_path)

        barcode_img = barcode_path + ".png"

        elementos.append(
            Paragraph(
                f"<b>{codigo}</b>",
                estilos["Normal"]
            )
        )

        elementos.append(
            Image(
                barcode_img,
                width=180,
                height=40
            )
        )

        elementos.append(
            Paragraph(
                pieza["apellido_nombre"] or "",
                estilos["Normal"]
            )
        )

        elementos.append(
            Paragraph(
                pieza["localidad"] or "",
                estilos["Normal"]
            )
        )

        elementos.append(Spacer(1, 8))

    doc.build(elementos)
