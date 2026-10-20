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

def solicitar_campo_obligatorio(mensaje):
    """Solicita un dato y si está vacío lanza un error y vuelve a pedirlo."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("❌ ¡ERROR! Este campo es obligatorio y no puede quedar vacío. Vuelva a ingresarlo.\n")

def crear_cuenta():
    """Formulario: Crear Cuenta"""
    print("\n--- FORMULARIO: CREAR CUENTA ---")
    nombre = solicitar_campo_obligatorio("Nombre: ")
    documento = solicitar_campo_obligatorio("Documento: ")
    tel = solicitar_campo_obligatorio("Teléfono (# Tel): ")
    otro_contacto = input("Otro Contacto (Opcional): ").strip()
    if not otro_contacto:
        otro_contacto = "Ninguno"

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
    while True:
        documento = solicitar_campo_obligatorio("Ingrese su Documento de Identidad: ")

        conn = sqlite3.connect('restaurante.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM Usuario WHERE documento = ?", (documento,))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            print(f"\n¡Bienvenido/a de nuevo, {usuario[1]}!")
            return usuario[0]
        else:
            print("❌ ¡ERROR! Usuario no encontrado con ese documento. Intente de nuevo.\n")

def obtener_mesas_disponibles():
    """Obtiene y retorna la lista completa de mesas."""
    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, num_mesa, capacidad, ubicacion FROM Mesa')
    mesas = cursor.fetchall()
    conn.close()
    return mesas

def seleccionar_mesa(num_comensales):
    """Muestra las mesas y permite al usuario elegir una."""
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
                print("❌ ¡ERROR! ID no válido o la mesa no soporta esa cantidad de comensales. Intente de nuevo.")
        except ValueError:
            print("❌ ¡ERROR! Debe ingresar un número entero válido para el ID de la mesa.")

def llenar_formulario_reserva(usuario_id):
    """Formulario: Crear Reserva"""
    print("\n--- FORMULARIO: CREAR RESERVA ---")
    fecha_hora = solicitar_campo_obligatorio("Fecha y Hora (Ej: 2026-11-01 20:00): ")
    
    while True:
        try:
            num_comensales = int(solicitar_campo_obligatorio("Número de Comensales (# Comensales): "))
            if num_comensales > 0:
                break
            print("❌ ¡ERROR! El número de comensales debe ser mayor a 0.\n")
        except ValueError:
            print("❌ ¡ERROR! Debe ingresar un número entero para los comensales.\n")

    mesa_seleccionada = seleccionar_mesa(num_comensales)
    if not mesa_seleccionada:
        return

    fk_mesa, num_mesa, capacidad_mesa, ubicacion_mesa = mesa_seleccionada
    observaciones = input("\nObservaciones (Opcional): ").strip()
    if not observaciones:
        observaciones = "ninguna"

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
    print("¡Muchas gracias por realizar tu reserva con nosotros! Te esperamos con gusto.")

def ver_mis_reservas(usuario_id):
    """Consulta y muestra las reservas realizadas por el usuario actual"""
    conn = sqlite3.connect('restaurante.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            r.id, 
            r.fecha_hora, 
            m.num_mesa, 
            m.ubicacion, 
            r.num_comensales, 
            r.observaciones
        FROM Reserva r
        INNER JOIN Mesa m ON r.fk_mesa = m.id
        WHERE r.fk_usuario = ?
        ORDER BY r.id DESC
    ''', (usuario_id,))

    reservas = cursor.fetchall()
    conn.close()

    print("\n========================================")
    print("        MIS RESERVAS REALIZADAS         ")
    print("========================================")

    if not reservas:
        print("No tienes reservas registradas hasta el momento.")
        return []
    else:
        for res in reservas:
            r_id, fecha, num_mesa, ubicacion, comensales, obs = res
            print(f"ID Reserva  : {r_id}")
            print(f"Fecha / Hora: {fecha}")
            print(f"Mesa        : Mesa #{num_mesa} ({ubicacion})")
            print(f"Comensales  : {comensales}")
            print(f"Observaciones: {obs if obs else 'ninguna'}")
            print("-" * 40)
        return [r[0] for r in reservas]

def cancelar_reserva(usuario_id):
    """Permite al usuario cancelar una reserva existente por su ID"""
    print("\n--- CANCELAR RESERVA ---")
    ids_reservas_activas = ver_mis_reservas(usuario_id)

    if not ids_reservas_activas:
        return

    while True:
        try:
            reserva_id = int(input("\nIngrese el ID de la reserva que desea cancelar (o 0 para volver): "))
            if reserva_id == 0:
                print("Operación cancelada.")
                break
            
            if reserva_id in ids_reservas_activas:
                confirmacion = input(f"¿Está seguro/a de que desea cancelar la reserva #{reserva_id}? (s/n): ").strip().lower()
                if confirmacion == 's':
                    conn = sqlite3.connect('restaurante.db')
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Reserva WHERE id = ? AND fk_usuario = ?", (reserva_id, usuario_id))
                    conn.commit()
                    conn.close()
                    print(f"\n✅ ¡La reserva #{reserva_id} ha sido cancelada exitosamente!")
                    break
                else:
                    print("Cancelación de reserva abortada.")
                    break
            else:
                print("❌ ¡ERROR! El ID ingresado no corresponde a ninguna de sus reservas activas. Intente de nuevo.")
        except ValueError:
            print("❌ ¡ERROR! Debe ingresar un número entero para el ID de la reserva.")

def menu_principal():
    inicializar_bd()
    usuario_actual_id = None

    while True:
        print("\n=== SISTEMA DE RESERVAS DE RESTAURANTE ===")
        print("1. Crear Cuenta")
        print("2. Iniciar Sesión")
        print("3. Crear Reserva")
        print("4. Ver Mis Reservas")
        print("5. Cancelar Reserva")
        print("6. Salir")
        
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
                usuario_actual_id = iniciar_sesion()
            
            if usuario_actual_id is not None:
                llenar_formulario_reserva(usuario_actual_id)

        elif opcion == '4':
            if usuario_actual_id is None:
                print("\nDebe Iniciar Sesión primero para consultar sus reservas.")
                usuario_actual_id = iniciar_sesion()
            
            if usuario_actual_id is not None:
                ver_mis_reservas(usuario_actual_id)

        elif opcion == '5':
            if usuario_actual_id is None:
                print("\nDebe Iniciar Sesión primero para cancelar una reserva.")
                usuario_actual_id = iniciar_sesion()
            
            if usuario_actual_id is not None:
                cancelar_reserva(usuario_actual_id)

        elif opcion == '6':
            print("\n¡Gracias por utilizar el sistema de reservas!")
            break
        else:
            print("\n❌ ¡ERROR! Opción inválida. Ingrese un número del 1 al 6.")

if __name__ == "__main__":
    menu_principal()