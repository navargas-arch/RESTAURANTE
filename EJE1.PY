import sqlite3

def inicializar_bd():
    """Crea la base de datos sqlite y las tablas según el modelo ER."""
    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()

    # Tabla Usuario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tel TEXT NOT NULL,
            nombre TEXT NOT NULL,
            documento TEXT NOT NULL UNIQUE,
            otro_contacto TEXT
        )
    ''')

    # Tabla Mesa
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Mesa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num_mesa INTEGER NOT NULL UNIQUE,
            capacidad INTEGER NOT NULL,
            ubicacion TEXT NOT NULL
        )
    ''')

    # Tabla Reserva
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Reserva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            fk_usuario INTEGER NOT NULL,
            fk_mesa INTEGER NOT NULL,
            num_comensales INTEGER NOT NULL,
            observaciones TEXT,
            FOREIGN KEY (fk_usuario) REFERENCES Usuario(id),
            FOREIGN KEY (fk_mesa) REFERENCES Mesa(id)
        )
    ''')

    # Mesas iniciales de prueba
    cursor.execute("SELECT COUNT(*) FROM Mesa")
    if cursor.fetchone()[0] == 0:
        mesas_iniciales = [
            (1, 2, "Interior / Ventana"),
            (2, 4, "Interior / Centro"),
            (3, 6, "Terraza"),
            (4, 8, "Zona VIP")
        ]
        cursor.executemany("INSERT INTO Mesa (num_mesa, capacidad, ubicacion) VALUES (?, ?, ?)", mesas_iniciales)

    conn.commit()
    conn.close()

def crear_cuenta():
    """Formulario: Crear Cuenta"""
    print("\n--- FORMULARIO: CREAR CUENTA ---")
    nombre = input("Nombre: ").strip()
    documento = input("Documento: ").strip()
    tel = input("Teléfono (# Tel): ").strip()
    otro_contacto = input("Otro Contacto: ").strip()

    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO Usuario (tel, nombre, documento, otro_contacto)
            VALUES (?, ?, ?, ?)
        ''', (tel, nombre, documento, otro_contacto))
        conn.commit()
        usuario_id = cursor.lastrowid
        print(f"\n¡Cuenta creada exitosamente! ID de usuario asignado: {usuario_id}")
        return usuario_id
    except sqlite3.IntegrityError:
        print("\nError: El documento ya está registrado.")
        return None
    finally:
        conn.close()

def iniciar_sesion():
    """Iniciar sesión mediante Documento de Identidad"""
    print("\n--- INICIAR SESIÓN ---")
    documento = input("Ingrese su Documento de Identidad: ").strip()

    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM Usuario WHERE documento = ?", (documento,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        print(f"\n¡Bienvenido/a de nuevo, {usuario[1]}!")
        return usuario[0]
    else:
        print("\nUsuario no encontrado. Por favor cree una cuenta primero.")
        return None

def buscar_mesa_disponible(num_comensales):
    """Busca una mesa adecuada para el número de comensales"""
    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, num_mesa, capacidad, ubicacion 
        FROM Mesa 
        WHERE capacidad >= ? 
        ORDER BY capacidad ASC 
        LIMIT 1
    ''', (num_comensales,))
    mesa = cursor.fetchone()
    conn.close()
    return mesa

def llenar_formulario_reserva(usuario_id):
    """Formulario: Crear Reserva"""
    print("\n--- FORMULARIO: CREAR RESERVA ---")
    fecha_hora = input("Fecha y Hora (Ej: 2026-11-01 20:00): ").strip()
    
    try:
        num_comensales = int(input("Número de Comensales (# Comensales): "))
    except ValueError:
        print("El número de comensales debe ser un número entero.")
        return

    observaciones = input("Observaciones: ").strip()

    mesa = buscar_mesa_disponible(num_comensales)
    if not mesa:
        print("\nNo hay mesas disponibles para ese número de comensales.")
        return

    fk_mesa, num_mesa, _, ubicacion_mesa = mesa

    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Reserva (fecha_hora, fk_usuario, fk_mesa, num_comensales, observaciones)
        VALUES (?, ?, ?, ?, ?)
    ''', (fecha_hora, usuario_id, fk_mesa, num_comensales, observaciones))
    conn.commit()
    reserva_id = cursor.lastrowid
    conn.close()

    print("\n========================================")
    print("¡RESERVA REGISTRADA CON ÉXITO!")