import sqlite3

class ProductManager:
    def __init__(self):
        self.connection = sqlite3.connect("products.db", check_same_thread=False)

    def add_product(self, name, price, quantity):
        # """Agrega un nuevo producto a la base de datos."""
        query = """
                INSERT INTO products (name, price, quantity)
                VALUES (?, ?, ?)"""
        self.connection.execute(query, (name, price, quantity))
        self.connection.commit()

    def get_products(self):
        # """Obtiene todos los productos de la base de datos."""
        cursor = self.connection.cursor()
        query = "SELECT * FROM products"
        cursor.execute(query)
        products = cursor.fetchall()
        return products

    def delete_product(self, product_id):
        query = "DELETE FROM products WHERE id = ?"
        self.connection.execute(query, (product_id,))
        self.connection.commit()

    def update_product(self, product_id, name, price, quantity):
        # """Actualiza un producto existente en la base de datos."""
        query = """
                UPDATE products
                SET name = ?, price = ?, quantity = ?
                WHERE id = ?
                """
        self.connection.execute(query, (name, price, quantity, product_id))
        self.connection.commit()

    def close_connection(self):
        self.connection.close()
        print("cerrar")
