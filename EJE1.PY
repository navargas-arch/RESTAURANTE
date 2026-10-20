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

    # Mesas iniciales de prueba según el modelo
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
        cursor.execute("SELECT id, nombre FROM Usuario WHERE documento = ?", (documento,))
        usuario = cursor.fetchone()
        if usuario:
            print(f"\nEl documento ya está registrado a nombre de: {usuario[1]}. Redirigiendo a crear reserva...")
            return usuario[0]
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

def obtener_mesas_disponibles():
    """Obtiene y retorna la lista completa de mesas registradas."""
    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, num_mesa, capacidad, ubicacion FROM Mesa')
    mesas = cursor.fetchall()
    conn.close()
    return mesas

def seleccionar_mesa(num_comensales):
    """Muestra el catálogo de mesas y permite al usuario elegir una mesa apta."""
    mesas = obtener_mesas_disponibles()
    
    print("\n--- MESAS REGISTRADAS EN EL RESTAURANTE ---")
    print(f"{'ID':<4} | {'Mesa #':<8} | {'Capacidad':<10} | {'Ubicación':<20}")
    print("-" * 50)
    
    mesas_validas = {}
    for m in mesas:
        m_id, num_m, cap, ubic = m
        es_apta = "✓ Apta" if cap >= num_comensales else "x Capacidad insuficiente"
        print(f"{m_id:<4} | Mesa #{num_m:<3} | {cap} personas   | {ubic:<20} ({es_apta})")
        if cap >= num_comensales:
            mesas_validas[m_id] = m

    if not mesas_validas:
        print(f"\nNo hay ninguna mesa con capacidad suficiente para {num_comensales} comensales.")
        return None

    while True:
        try:
            opcion_id = int(input("\nIngrese el ID de la Mesa que desea elegir: "))
            if opcion_id in mesas_validas:
                return mesas_validas[opcion_id]
            else:
                print("ID no válido o la mesa seleccionada no soporta esa cantidad de comensales. Intente de nuevo.")
        except ValueError:
            print("Por favor ingrese un número entero válido para el ID de la mesa.")

def llenar_formulario_reserva(usuario_id):
    """Formulario: Crear Reserva con Selección Manual de Mesa"""
    print("\n--- FORMULARIO: CREAR RESERVA ---")
    fecha_hora = input("Fecha y Hora (Ej: 2026-11-01 20:00): ").strip()
    
    try:
        num_comensales = int(input("Número de Comensales (# Comensales): "))
    except ValueError:
        print("El número de comensales debe ser un número entero.")
        return

    # Selección visual y manual de la mesa
    mesa_seleccionada = seleccionar_mesa(num_comensales)
    if not mesa_seleccionada:
        return

    fk_mesa, num_mesa, capacidad_mesa, ubicacion_mesa = mesa_seleccionada
    observaciones = input("\nObservaciones: ").strip()

    # Guardar Reserva en SQLite
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
    print(f"ID Reserva: {reserva_id}")
    print(f"Fecha/Hora: {fecha_hora}")
    print(f"Mesa Asignada: Mesa #{num_mesa} ({ubicacion_mesa} - Capacidad: {capacidad_mesa} personas)")
    print(f"Comensales: {num_comensales}")
    print(f"Observaciones: {observaciones}")
    print("========================================")

def menu_principal():
    inicializar_bd()
    usuario_actual_id = None

    while True:
        print("\n=== SISTEMA DE RESERVAS DE RESTAURANTE ===")
        print("1. Crear Cuenta")
        print("2. Iniciar Sesión")
        print("3. Crear Reserva")
        print("4. Salir")
        
        opcion = input("Seleccione una opción: ").strip()

        if opcion == '1':
            usuario_actual_id = crear_cuenta()
            if usuario_actual_id is not None:
                llenar_formulario_reserva(usuario_actual_id)

        elif opcion == '2':
            usuario_actual_id = iniciar_sesion()
            if usuario_actual_id is not None:
                llenar_formulario_reserva(usuario_actual_id)

        elif opcion == '3':
            if usuario_actual_id is None:
                print("\nDebe Iniciar Sesión o Crear Cuenta primero para hacer una reserva.")
            else:
                llenar_formulario_reserva(usuario_actual_id)

        elif opcion == '4':
            print("\n¡Gracias por utilizar el sistema de reservas!")
            break
        else:
            print("\nOpción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu_principal()