import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data_demo.db"

CANTIDAD = 100


nombres = [
    "Ana Pérez",
    "Carlos Gómez",
    "Laura Fernández",
    "Martín Rodríguez",
    "Sofía Martínez",
    "Diego López",
    "Valentina García",
    "Nicolás Romero",
    "Camila Sánchez",
    "Federico Torres",
]

calles = [
    "Calle Ficticia",
    "Avenida Demo",
    "Pasaje Ejemplo",
    "Calle Prueba",
    "Boulevard Central",
    "Avenida Norte",
    "Pasaje Sur",
    "Calle del Parque",
    "Avenida del Sol",
    "Calle Modelo",
]

localidades = [
    ("Rosario", "2000"),
    ("Funes", "2132"),
    ("Roldán", "2134"),
    ("Villa Gobernador Gálvez", "2124"),
    ("Granadero Baigorria", "2152"),
]

distritos = [
    "Centro",
    "Norte",
    "Sur",
    "Oeste",
    "Noroeste",
]


if not DB_PATH.exists():
    raise FileNotFoundError(
        f"No existe la base demo: {DB_PATH}"
    )


with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()

    existentes = cur.execute(
        "SELECT COUNT(*) FROM correspondencias"
    ).fetchone()[0]

    if existentes > 0:
        raise RuntimeError(
            f"La base demo ya contiene {existentes} correspondencias.\n"
            "No se cargaron datos para evitar duplicados."
        )

    datos = []

    for i in range(1, CANTIDAD + 1):
        nombre = nombres[(i - 1) % len(nombres)]
        calle = calles[(i - 1) % len(calles)]

        localidad, cp = localidades[
            (i - 1) % len(localidades)
        ]

        distrito = distritos[
            (i - 1) % len(distritos)
        ]

        codigo = f"DEMO{i:06d}"
        nro_envio = f"ENV-DEMO-{i:06d}"
        nro_afiliado = f"AF-DEMO-{i:06d}"
        domicilio = f"{calle} {100 + i}"

        datos.append(
            (
                codigo,
                nro_envio,
                nro_afiliado,
                nombre,
                domicilio,
                cp,
                localidad,
                distrito,
                "Registro ficticio para demostración",
            )
        )

    cur.executemany(
        """
        INSERT INTO correspondencias (
            codigo,
            nro_envio_orden,
            nro_afiliado,
            apellido_nombre,
            domicilio,
            cp,
            localidad,
            distrito_electoral,
            observacion,
            estado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
        """,
        datos,
    )

    conn.commit()

    cantidad_final = cur.execute(
        "SELECT COUNT(*) FROM correspondencias"
    ).fetchone()[0]


print(f"Base utilizada: {DB_PATH}")
print(f"Correspondencias ficticias cargadas: {cantidad_final}")