import flet as ft
import sqlite3
import os
import subprocess

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correo TEXT UNIQUE NOT NULL,
        contraseña TEXT NOT NULL
    )
    """)
    conn.commit()

    # Insertar un usuario de ejemplo (solo para pruebas)
    try:
        cursor.execute("INSERT INTO usuarios (correo, contraseña) VALUES (?, ?)", ("usuario@example.com", "1234"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # El usuario ya existe, no hacemos nada

    conn.close()

# Inicializar la base de datos
init_db()

def main(page: ft.Page):
    
    page.title = "Iniciar Sesión"
    page.bgcolor = ft.Colors.BLACK
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    

    # Crear entradas de texto globales para capturar valores
    correo_input = ft.TextField(
        width=280,
        height=40,
        hint_text="Correo Electrónico",
        prefix_icon=ft.Icons.EMAIL,
    )
    contraseña_input = ft.TextField(
        width=280,
        height=40,
        hint_text="Contraseña",
        prefix_icon=ft.Icons.LOCK,
        password=True,
    )
    recordar_checkbox = ft.Checkbox(
        label="Recordar Contraseña",
        check_color="black",
    )

    # Definir cargar_formulario antes de usarlo en otras funciones
    def cargar_formulario():
        page.controls.clear()
        page.add(
            ft.Container(
                ft.Column(
                    [
                        ft.Text(
                            "Iniciar Sesión",
                            size=30,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.W_900,
                            color=ft.Colors.WHITE,
                        ),
                        correo_input,
                        contraseña_input,
                        recordar_checkbox,
                        ft.ElevatedButton("Iniciar", on_click=iniciar_sesion),
                        ft.Row(
                            [
                                ft.Text("¿No tiene una cuenta?", color=ft.Colors.WHITE),
                                ft.TextButton("Crear cuenta", on_click=lambda e: mostrar_formulario_crear_cuenta()),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                border_radius=20,
                width=320,
                height=500,
                gradient=ft.LinearGradient(
                    [
                        ft.Colors.PURPLE,
                        ft.Colors.PINK,
                        ft.Colors.RED,
                    ]
                ),
            )
        )
        page.update()

    # Reiniciar el formulario de inicio de sesión
    def reiniciar_formulario():
        if not recordar_checkbox.value:
            correo_input.value = ""
            contraseña_input.value = ""
        page.appbar = None  # Restablece el AppBar
        page.update()  # Actualiza la página para reflejar el cambio en el AppBar
        cargar_formulario()

    # Función para manejar el inicio de sesión
    def iniciar_sesion(e):
        correo = correo_input.value
        contraseña = contraseña_input.value

        conn = sqlite3.connect("usuarios.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = ? AND contraseña = ?", (correo, contraseña))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            mostrar_menu_principal()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Correo o contraseña incorrectos"))
            page.snack_bar.open = True
            page.update()

    # Mostrar menú principal
    def mostrar_menu_principal():
        page.controls.clear()
        page.update()

        def abrir_archivo(nombre_archivo):
            # Construye la ruta completa al archivo en la carpeta 'crud'
            ruta_archivo = os.path.join(os.getcwd(), "./", "crud", nombre_archivo)

            # Verifica si el archivo existe
            if os.path.exists(ruta_archivo):
                try:
                    # Ejecuta el archivo con subprocess
                    subprocess.run(["python", ruta_archivo], check=True)
                except subprocess.CalledProcessError as e:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error al ejecutar el archivo: {e}"))
                    page.snack_bar.open = True
                    page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"El archivo {ruta_archivo} no existe."))
                page.snack_bar.open = True
                page.update()

        navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.CODE, label="Clientes"),
                ft.NavigationRailDestination(icon=ft.Icons.CODE, label="Productos"),
            ],
            on_change=lambda e: abrir_archivo("main.py") if e.control.selected_index == 0 else abrir_archivo("productos.py"),
        )

        page.appbar = ft.AppBar(
            title=ft.Text("Menú Principal // SISTEMA JG"),
            center_title=True,
            bgcolor=ft.Colors.BLUE,
        )
        page.add(
            ft.Row(
                [
                    navigation_rail,
                    ft.VerticalDivider(),
                    ft.Column(
                        [
                            ft.Text("Bienvenido al Menú principal // SISTEMA JG", size=30, color=ft.Colors.WHITE),
                            ft.ElevatedButton("Cerrar sesión", on_click=lambda e: reiniciar_formulario()),
                        ],
                        expand=True,
                    ),
                ],
                expand=True,
            )
        )
        page.update()

    # Mostrar formulario de registro de nueva cuenta
    def mostrar_formulario_crear_cuenta():
        page.appbar = None  # Restablece el AppBar
        page.update()  # Actualiza la página para reflejar el cambio en el AppBar
        page.controls.clear()  # Limpia los controles de la página
        nuevo_correo = ft.TextField(
            width=280,
            height=40,
            hint_text="Nuevo correo electrónico",
            prefix_icon=ft.Icons.EMAIL,
        )
        nueva_contraseña = ft.TextField(
            width=280,
            height=40,
            hint_text="Nueva contraseña",
            prefix_icon=ft.Icons.LOCK,
            password=True,
        )
        confirmar_contraseña = ft.TextField(
            width=280,
            height=40,
            hint_text="Confirmar contraseña",
            prefix_icon=ft.Icons.LOCK,
            password=True,
        )

        def crear_cuenta(e):
            correo = nuevo_correo.value
            contraseña = nueva_contraseña.value
            confirmacion = confirmar_contraseña.value

            if not correo or not contraseña or not confirmacion:
                page.snack_bar = ft.SnackBar(ft.Text("Todos los campos son obligatorios"))
                page.snack_bar.open = True
                page.update()
                return

            if contraseña != confirmacion:
                page.snack_bar = ft.SnackBar(ft.Text("Las contraseñas no coinciden"))
                page.snack_bar.open = True
                page.update()
                return

            try:
                conn = sqlite3.connect("usuarios.db")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (correo, contraseña) VALUES (?, ?)", (correo, contraseña))
                conn.commit()
                conn.close()

                page.snack_bar = ft.SnackBar(ft.Text("Cuenta creada exitosamente. Inicia sesión."))
                page.snack_bar.open = True
                reiniciar_formulario()
            except sqlite3.IntegrityError:
                page.snack_bar = ft.SnackBar(ft.Text("El correo ya está registrado."))
                page.snack_bar.open = True
            page.update()

        page.add(
            ft.Container(
                ft.Column(
                    [
                        ft.Text(
                            "Crear una nueva cuenta",
                            size=30,
                            text_align=ft.TextAlign.CENTER,
                            weight=ft.FontWeight.W_900,
                            color=ft.Colors.WHITE,
                        ),
                        nuevo_correo,
                        nueva_contraseña,
                        confirmar_contraseña,
                        ft.ElevatedButton("Crear cuenta", on_click=crear_cuenta),
                        ft.TextButton("Volver al inicio de sesión", on_click=lambda e: reiniciar_formulario()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
                border_radius=20,
                width=320,
                height=500,
                gradient=ft.LinearGradient(
                    [
                        ft.Colors.PURPLE,
                        ft.Colors.PINK,
                        ft.Colors.RED,
                    ]
                ),
            )
        )
        page.update()

    cargar_formulario()  # Cargar el formulario inicialmente

ft.app(target=main)
