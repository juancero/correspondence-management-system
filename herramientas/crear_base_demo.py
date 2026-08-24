import sqlite3
from pathlib import Path


ORIGEN = Path(
    r"C:\correspondencia para subir a git\correspodencia_app\data_copia.db"
)

DESTINO = Path(
    r"C:\correspondencia para subir a git\correspodencia_app\data_demo.db"
)


# Datos maestros necesarios para utilizar el sistema
MOTIVOS_RENDICION = [
    ("Entregada", "entregada"),
    ("Se mudó", "se_mudo"),
    ("Destinatario desconocido", "destinatario_desconocido"),
    ("Rechazada", "rechazada"),
    ("Domicilio insuficiente", "domicilio_insuficiente"),
    ("Fallecido", "fallecido"),
    ("Otro", "otro"),
    ("Domicilio desconocido", "domicilio_desconocido"),
    ("No visitado", "no_visitado"),
    ("No Operable", "no_operable"),
    ("No Existe Numero", "no_existe_numero"),
    ("En Construccion", "en_construccion"),
    ("Direccion Inexistente", "direccion_inexistente"),
    ("Deshabitado", "deshabitado"),
]


# --------------------------------------------------
# VALIDACIONES
# --------------------------------------------------

if not ORIGEN.exists():
    raise FileNotFoundError(
        f"No existe la base origen: {ORIGEN}"
    )

if DESTINO.exists():
    raise FileExistsError(
        f"Ya existe la base destino: {DESTINO}\n"
        "Eliminala antes de generar una nueva."
    )


# --------------------------------------------------
# LEER ESTRUCTURA DE LA BASE
# --------------------------------------------------

with sqlite3.connect(ORIGEN) as origen:

    objetos = origen.execute("""
        SELECT type, name, sql
        FROM sqlite_master
        WHERE sql IS NOT NULL
          AND name NOT LIKE 'sqlite_%'
        ORDER BY
            CASE type
                WHEN 'table' THEN 1
                WHEN 'index' THEN 2
                WHEN 'trigger' THEN 3
                WHEN 'view' THEN 4
                ELSE 5
            END,
            name
    """).fetchall()


# --------------------------------------------------
# CREAR BASE DEMO
# --------------------------------------------------

with sqlite3.connect(DESTINO) as destino:

    destino.execute("PRAGMA foreign_keys = OFF")

    for tipo, nombre, sql in objetos:

        try:
            destino.execute(sql)
            print(f"Creado: {tipo} -> {nombre}")

        except sqlite3.OperationalError as e:
            print(
                f"No se pudo crear {tipo} {nombre}: {e}"
            )

    destino.commit()


# --------------------------------------------------
# CARGAR DATOS MAESTROS
# --------------------------------------------------

with sqlite3.connect(DESTINO) as demo:

    demo.executemany(
        """
        INSERT INTO motivos_rendicion (
            nombre,
            codigo
        )
        VALUES (?, ?)
        """,
        MOTIVOS_RENDICION,
    )

    demo.commit()


print()
print("Motivos de rendición cargados correctamente.")

print()
print("Base demo creada correctamente:")
print(DESTINO)


# --------------------------------------------------
# VERIFICAR REGISTROS
# --------------------------------------------------

print()
print("Verificando cantidad de registros por tabla...")


with sqlite3.connect(DESTINO) as demo:

    cur = demo.cursor()

    tablas = cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    for (tabla,) in tablas:

        cantidad = cur.execute(
            f'SELECT COUNT(*) FROM "{tabla}"'
        ).fetchone()[0]

        print(f"{tabla}: {cantidad}")