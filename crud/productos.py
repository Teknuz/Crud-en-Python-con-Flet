import flet as ft
from product_manager import ProductManager
from fpdf import FPDF
import pandas as pd
import datetime

# Clase para generar el PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Tabla de Productos', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

class FormUi(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.data = ProductManager()
        self.selected_row = None

        # Definición de los campos de entrada
        self.name = ft.TextField(label="Nombre del Producto", border_color="green")
        self.price = ft.TextField(label="Precio", border_color="green",
                                  input_filter=ft.NumbersOnlyInputFilter(),
                                  max_length=10)
        self.quantity = ft.TextField(label="Cantidad", border_color="green",
                                     input_filter=ft.NumbersOnlyInputFilter(),
                                     max_length=5)

        self.search_field = ft.TextField(
            suffix_icon=ft.icons.SEARCH,
            label="Buscar por nombre del producto",
            border=ft.InputBorder.UNDERLINE,
            border_color="white",
            label_style=ft.TextStyle(color="white"),
            on_change=self.search_data,
        )

        self.data_table = ft.DataTable(
            expand=True,
            border=ft.border.all(2, "green"),
            data_row_color={
                ft.ControlState.SELECTED: "green",
                ft.ControlState.PRESSED: "black"
            },
            border_radius=10,
            show_checkbox_column=True,
            columns=[
                ft.DataColumn(ft.Text("Nombre del Producto", color="green", weight="bold")),
                ft.DataColumn(ft.Text("Precio", color="green", weight="bold")),
                ft.DataColumn(ft.Text("Cantidad", color="green", weight="bold")),
            ],
        )

        self.show_data()

        # Mensaje para mostrar información al usuario
        self.info_message = ft.Text("", color="white", size=14)

        # Contenedor del formulario
        self.form = ft.Container(
            bgcolor="#222222",
            border_radius=10,
            col=4,
            padding=10,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_AROUND,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Ingrese los Datos del Producto", size=40, text_align="center", font_family="vivaldi"),
                    self.name,
                    self.price,
                    self.quantity,
                    ft.Container(
                        content=ft.Row(
                            spacing=5,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.TextButton(
                                    text="Guardar",
                                    icon=ft.icons.SAVE,
                                    icon_color="white",
                                    style=ft.ButtonStyle(color="white", bgcolor="green"),
                                    on_click=self.add_data,
                                ),
                                ft.TextButton(
                                    text="Actualizar",
                                    icon=ft.icons.UPDATE,
                                    icon_color="white",
                                    style=ft.ButtonStyle(color="white", bgcolor="green"),
                                    on_click=self.update_data,
                                ),
                                ft.TextButton(
                                    text="Borrar",
                                    icon=ft.icons.DELETE,
                                    icon_color="white",
                                    style=ft.ButtonStyle(color="white", bgcolor="green"),
                                    on_click=self.delete_data,
                                ),
                                ft.TextButton(
                                    text="Limpiar",
                                    icon=ft.icons.CLEAR,
                                    icon_color="white",
                                    style=ft.ButtonStyle(color="white", bgcolor="red"),
                                    on_click=self.clean_fields,
                                ),
                                ft.TextButton(
                                    text="Volver al Menú Principal",
                                    icon=ft.icons.HOME,
                                    icon_color="white",
                                    style=ft.ButtonStyle(color="white", bgcolor="blue"),
                                    on_click=self.back_to_menu,
                                )
                            ]
                        )
                    ),
                    self.info_message
                ]
            )
        )

        # Contenedor para la tabla de datos
        self.table = ft.Container(
            bgcolor="#222222",
            border_radius=10,
            padding=10,
            col=8,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.Container(
                        padding=10,
                        content=ft.Row(
                            controls=[
                                self.search_field,
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    on_click=self.edit_field_text,
                                    icon_color="white",
                                ),
                                ft.IconButton(
                                    tooltip="Descargar en PDF",
                                    icon=ft.icons.PICTURE_AS_PDF,
                                    icon_color="white",
                                    on_click=self.save_pdf,
                                ),
                                ft.IconButton(
                                    tooltip="Descargar en EXCEL",
                                    icon=ft.icons.SAVE_ALT,
                                    icon_color="white",
                                    on_click=self.save_excel,
                                ),
                            ]
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        scroll="auto",
                        controls=[
                            ft.ResponsiveRow([self.data_table]),
                        ]
                    )
                ]
            )
        )

        self.content = ft.ResponsiveRow(
            controls=[
                self.form,
                self.table
            ]
        )

    def show_data(self):
        """Muestra los datos de productos en la tabla."""
        self.data_table.rows = []
        for x in self.data.get_products():
            self.data_table.rows.append(
                ft.DataRow(
                    on_select_changed=self.get_index,
                    cells=[
                        ft.DataCell(ft.Text(x[1])),
                        ft.DataCell(ft.Text(str(x[2]))),
                        ft.DataCell(ft.Text(str(x[3]))),
                    ]
                )
            )
        self.update()

    def add_data(self, e):
        """Agrega un nuevo producto a la base de datos."""
        name = self.name.value
        price = str(self.price.value)
        quantity = str(self.quantity.value)

        if len(name) and len(price) and len(quantity) > 0:
            product_exists = False
            for row in self.data.get_products():
                if row[1] == name:
                    product_exists = True
                    break

            if not product_exists:
                self.clean_fields()
                self.data.add_product(name, price, quantity)
                self.show_data()
                self.info_message.value = f"Producto '{name}' agregado correctamente."
            else:
                self.info_message.value = "El producto ya existe en la base de datos."
        else:
            self.info_message.value = "Por favor, complete todos los campos."

        self.update()

    def get_index(self, e):
        """Obtiene el índice de la fila seleccionada en la tabla."""
        if e.control.selected:
            e.control.selected = False
        else:
            e.control.selected = True

        name = e.control.cells[0].content.value
        for row in self.data.get_products():
            if row[1] == name:
                self.selected_row = row
                print(f"Producto seleccionado: {self.selected_row}")  # Para depuración
                break
        self.update()

    def edit_field_text(self, e):
        """Rellena los campos de texto con la información del producto seleccionado."""
        try:
            if self.selected_row:
                self.name.value = self.selected_row[1]
                self.price.value = self.selected_row[2]
                self.quantity.value = self.selected_row[3]
            self.update()
        except TypeError:
            self.info_message.value = "Error al intentar editar el producto."

    def update_data(self, e):
        """Actualiza la información del producto seleccionado."""
        name = self.name.value
        price = str(self.price.value)
        quantity = str(self.quantity.value)

        if len(name) and len(price) and len(quantity) > 0:
            if self.selected_row is not None:  # Verifica que se haya seleccionado una fila
                self.data.update_product(self.selected_row[0], name, price, quantity)
                self.clean_fields()  # Limpia los campos después de actualizar
                self.show_data()
                self.info_message.value = f"Producto '{name}' actualizado correctamente."
            else:
                self.info_message.value = "No se ha seleccionado ningún producto para actualizar."
        else:
            self.info_message.value = "Por favor, complete todos los campos."

        self.update()

    def delete_data(self, e):
        """Elimina el producto seleccionado."""
        if self.selected_row:
            self.data.delete_product(self.selected_row[0])
            self.show_data()
            self.info_message.value = f"Producto '{self.selected_row[0]}' eliminado."
            self.clean_fields()
        else:
            self.info_message.value = "No se ha seleccionado ningún producto para eliminar."

        self.update()

    def search_data(self, e):
        """Busca un producto por nombre y muestra el resultado."""
        search_term = self.search_field.value
        self.data_table.rows = []

        if search_term:
            results = self.data.search_product(search_term)
            if results:
                for x in results:
                    self.data_table.rows.append(
                        ft.DataRow(
                            on_select_changed=self.get_index,
                            cells=[
                                ft.DataCell(ft.Text(x[1])),
                                ft.DataCell(ft.Text(str(x[2]))),
                                ft.DataCell(ft.Text(str(x[3]))),
                            ]
                        )
                    )
            else:
                self.info_message.value = "No se encontró ningún producto."
        else:
            self.show_data()

        self.update()

    def clean_fields(self, e=None):
        """Limpia los campos de texto."""
        self.name.value = ""
        self.price.value = ""
        self.quantity.value = ""
        self.selected_row = None  # Restablece la fila seleccionada
        self.info_message.value = ""
        self.update()

    def save_pdf(self, e):
        """Guarda los productos en un archivo PDF."""
        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)

        for product in self.data.get_products():
            pdf.cell(0, 10, f"Nombre: {product[1]}, Precio: {product[2]}, Cantidad: {product[3]}", ln=True)

        now = datetime.datetime.now()
        filename = f"productos_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf.output(filename)

        self.info_message.value = f"Productos guardados en PDF como '{filename}'."
        self.update()

    def save_excel(self, e):
        """Guarda los productos en un archivo Excel."""
        products = self.data.get_products()
        df = pd.DataFrame(products, columns=["ID", "Nombre", "Precio", "Cantidad"])
        now = datetime.datetime.now()
        filename = f"productos_{now.strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)

        self.info_message.value = f"Productos guardados en Excel como '{filename}'."
        self.update()

    def back_to_menu(self, e):
        """Vuelve al menú principal."""
        self.page.controls.clear()
        main(self.page)

    def build(self):
        return self.content

# Asegúrate de que este bloque esté presente para iniciar la aplicación
def main(page: ft.Page):
    page.title = "Gestor de Productos"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Instancia de FormUi
    form = FormUi(page)
    page.add(form)

# Inicia la aplicación
ft.app(target=main)
