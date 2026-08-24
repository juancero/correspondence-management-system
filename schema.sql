PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS correspondencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nro_envio_orden TEXT,
    nro_afiliado TEXT,
    apellido_nombre TEXT,
    domicilio TEXT,
    cp TEXT,
    localidad TEXT,
    distrito_electoral TEXT,
    observacion TEXT,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS despachos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL UNIQUE,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL DEFAULT 'abierto',
    observacion TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS despacho_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_despacho INTEGER NOT NULL,
    id_correspondencia INTEGER NOT NULL,
    codigo TEXT NOT NULL,
    escaneado_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_despacho) REFERENCES despachos(id),
    FOREIGN KEY (id_correspondencia) REFERENCES correspondencias(id),

    UNIQUE (id_despacho, id_correspondencia)
);

CREATE TABLE IF NOT EXISTS rendiciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_despacho INTEGER NOT NULL,
    numero TEXT NOT NULL UNIQUE,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL DEFAULT 'abierta',
    observacion TEXT,

    FOREIGN KEY (id_despacho) REFERENCES despachos(id)
);

CREATE TABLE IF NOT EXISTS rendicion_detalle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_rendicion INTEGER NOT NULL,
    id_despacho INTEGER NOT NULL,
    id_correspondencia INTEGER,
    codigo TEXT NOT NULL,
    resultado TEXT NOT NULL,
    observacion TEXT,
    escaneado_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_rendicion) REFERENCES rendiciones(id),
    FOREIGN KEY (id_despacho) REFERENCES despachos(id),
    FOREIGN KEY (id_correspondencia) REFERENCES correspondencias(id),

    UNIQUE (id_rendicion, codigo)
);

CREATE INDEX IF NOT EXISTS idx_correspondencias_codigo 
ON correspondencias(codigo);

CREATE INDEX IF NOT EXISTS idx_correspondencias_estado 
ON correspondencias(estado);

CREATE INDEX IF NOT EXISTS idx_despacho_detalle_despacho 
ON despacho_detalle(id_despacho);

CREATE INDEX IF NOT EXISTS idx_despacho_detalle_codigo 
ON despacho_detalle(codigo);

CREATE INDEX IF NOT EXISTS idx_rendicion_detalle_rendicion 
ON rendicion_detalle(id_rendicion);

CREATE INDEX IF NOT EXISTS idx_rendicion_detalle_codigo 
ON rendicion_detalle(codigo);