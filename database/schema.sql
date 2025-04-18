-- Crear tipos ENUM personalizados
CREATE TYPE tipo_usuario AS ENUM ('administrador', 'vendedor', 'comprador');
CREATE TYPE tipo_cliente AS ENUM ('exportador', 'cafeteria');
CREATE TYPE estado_pago AS ENUM ('pendiente', 'pagado', 'parcial');

-- Crear tablas principales

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tipo_usuario tipo_usuario NOT NULL,
    activo BOOLEAN DEFAULT true,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de proveedores (campesinos)
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    documento_identidad VARCHAR(20) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    direccion TEXT,
    activo BOOLEAN DEFAULT true,
    creado_por INTEGER REFERENCES usuarios(id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de clientes (exportadores y cafeterías)
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre_empresa VARCHAR(200) NOT NULL,
    nit VARCHAR(20) UNIQUE NOT NULL,
    tipo_cliente tipo_cliente NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT,
    activo BOOLEAN DEFAULT true,
    creado_por INTEGER REFERENCES usuarios(id),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de precios del café
CREATE TABLE precios_cafe (
    id SERIAL PRIMARY KEY,
    precio_kg DECIMAL(10,2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fuente VARCHAR(100) NOT NULL,
    registrado_por INTEGER REFERENCES usuarios(id)
   
);
ALTER TABLE precios_cafe 
ADD COLUMN precio_carga DECIMAL(12,2);

-- Tabla de compras
CREATE TABLE compras (
    id SERIAL PRIMARY KEY,
    proveedor_id INTEGER REFERENCES proveedores(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    cantidad_kg DECIMAL(10,2) NOT NULL,
    precio_kg DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_pago estado_pago NOT NULL,
    notas TEXT
);

-- Tabla para registrar los pagos de las compras
CREATE TABLE pagos_compras (
    id SERIAL PRIMARY KEY,
    compra_id INTEGER REFERENCES compras(id),
    monto DECIMAL(10,2) NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id),
    metodo_pago VARCHAR(50),
    referencia_pago VARCHAR(100)
);

-- Tabla de ventas
CREATE TABLE ventas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id),
    usuario_id INTEGER REFERENCES usuarios(id),
    cantidad_kg DECIMAL(10,2) NOT NULL,
    precio_kg DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_cobro estado_pago NOT NULL,
    notas TEXT
);

-- Tabla para registrar los cobros de las ventas
CREATE TABLE cobros_ventas (
    id SERIAL PRIMARY KEY,
    venta_id INTEGER REFERENCES ventas(id),
    monto DECIMAL(10,2) NOT NULL,
    fecha_cobro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id),
    metodo_cobro VARCHAR(50),
    referencia_cobro VARCHAR(100)
);

-- Tabla para el inventario de café
CREATE TABLE inventario_cafe (
    id SERIAL PRIMARY KEY,
    cantidad_kg DECIMAL(10,2) NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_movimiento VARCHAR(20) NOT NULL, -- 'entrada' o 'salida'
    referencia_id INTEGER, -- ID de compra o venta
    tipo_referencia VARCHAR(20), -- 'compra' o 'venta'
    usuario_id INTEGER REFERENCES usuarios(id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_compras_proveedor ON compras(proveedor_id);
CREATE INDEX idx_ventas_cliente ON ventas(cliente_id);
CREATE INDEX idx_pagos_compra ON pagos_compras(compra_id);
CREATE INDEX idx_cobros_venta ON cobros_ventas(venta_id);
CREATE INDEX idx_inventario_fecha ON inventario_cafe(fecha_actualizacion); 

-- Primero aseguramos que exista el tipo enum tipo_usuario
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_usuario') THEN
        CREATE TYPE tipo_usuario AS ENUM ('administrador', 'vendedor', 'comprador');
    END IF;
END $$;

-- Insertar el usuario administrador
INSERT INTO usuarios (
    id,
    nombre, 
    apellido, 
    email, 
    password_hash, 
    tipo_usuario, 
    activo, 
    fecha_creacion
) VALUES (
    1,  -- ID específico que usa el sistema
    'Admin',
    'Sistema',
    'admin@cafexport.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFuWQR3hXXu/4TG',  -- Este es el hash de la contraseña 'admin'
    'administrador',
    true,
    CURRENT_TIMESTAMP
);

-- Establecer la secuencia para que futuros registros empiecen después del ID 1
SELECT setval('usuarios_id_seq', 1);