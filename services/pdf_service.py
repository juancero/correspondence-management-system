from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from database import get_connection


def generar_pdf_despacho(id_despacho, ruta):
    doc = SimpleDocTemplate(ruta, pagesize=A4)

    estilos = getSampleStyleSheet()
    elementos = []

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT numero, fecha 
            FROM despachos 
            WHERE id = ?
        """, (id_despacho,))
        despacho = cur.fetchone()

        if not despacho:
            raise ValueError("Despacho no encontrado")

        cur.execute("""
            SELECT c.codigo, c.apellido_nombre, c.domicilio, c.localidad
            FROM despacho_detalle d
            JOIN correspondencias c ON c.id = d.id_correspondencia
            WHERE d.id_despacho = ?
        """, (id_despacho,))
        filas = cur.fetchall()

    elementos.append(
        Paragraph(f"<b>DESPACHO N° {despacho['numero']}</b>", estilos["Heading2"]))
    elementos.append(Spacer(1, 5))
    elementos.append(
        Paragraph(f"Fecha: {despacho['fecha']}", estilos["Normal"]))
    elementos.append(
        Paragraph(f"Total de piezas: {len(filas)}", estilos["Normal"]))
    elementos.append(Spacer(1, 5))

    if not filas:
        elementos.append(
            Paragraph("Sin piezas registradas.", estilos["Normal"]))
        doc.build(elementos)
        return

    data = [["Código", "Nombre", "Domicilio", "Localidad"]]

    for f in filas:
        data.append([
            f["codigo"],
            f["apellido_nombre"],
            f["domicilio"],
            f["localidad"]
        ])

    tabla = Table(data, repeatRows=1)

    tabla.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)


def generar_pdf_rendicion(id_rendicion, ruta):
    doc = SimpleDocTemplate(ruta, pagesize=A4)

    estilos = getSampleStyleSheet()
    elementos = []

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("""
            SELECT numero, fecha
            FROM rendiciones
            WHERE id = ?
        """, (id_rendicion,))
        rendicion = cur.fetchone()

        if not rendicion:
            raise ValueError("Rendición no encontrada")

        cur.execute("""
            SELECT 
                c.codigo,
                c.apellido_nombre,
                c.domicilio,
                c.localidad,
                rd.resultado
            FROM rendicion_detalle rd
            JOIN correspondencias c ON c.id = rd.id_correspondencia
            WHERE rd.id_rendicion = ?
            ORDER BY rd.id ASC
        """, (id_rendicion,))
        filas = cur.fetchall()

    elementos.append(
        Paragraph(f"<b>RENDICIÓN N° {rendicion['numero']}</b>", estilos["Heading2"]))
    elementos.append(Spacer(1, 5))
    elementos.append(
        Paragraph(f"Fecha: {rendicion['fecha']}", estilos["Normal"]))
    elementos.append(
        Paragraph(f"Total de piezas: {len(filas)}", estilos["Normal"]))
    elementos.append(Spacer(1, 5))

    if not filas:
        elementos.append(
            Paragraph("Sin piezas registradas.", estilos["Normal"]))
        doc.build(elementos)
        return

    data = [["Código", "Nombre", "Domicilio", "Localidad", "Resultado"]]

    for f in filas:
        data.append([
            f["codigo"],
            f["apellido_nombre"],
            f["domicilio"],
            f["localidad"],
            f["resultado"]
        ])

    tabla = Table(data, repeatRows=1)

    tabla.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
    ]))

    elementos.append(tabla)

    doc.build(elementos)
