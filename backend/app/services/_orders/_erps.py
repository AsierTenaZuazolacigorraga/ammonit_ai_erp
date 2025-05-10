import pyodbc


class AccessDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn_str = (
            f"Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};Dbq={db_path};"
        )
        self.conn = pyodbc.connect(self.conn_str)
        self.cursor = self.conn.cursor()

    def read_orders(self, limit=100):
        self.cursor.execute(f"SELECT TOP {limit} * FROM Orders")
        return self.cursor.fetchall()

    def write_order(self, order_data):
        columns = ", ".join(order_data.keys())
        placeholders = ", ".join(["?"] * len(order_data))
        sql = f"INSERT INTO Orders ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, list(order_data.values()))
        self.conn.commit()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
