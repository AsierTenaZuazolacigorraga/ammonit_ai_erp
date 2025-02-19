import pyodbc


def show_access_data(db_path):
    # Be sure this matches your driver name and bitness
    conn_str = r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};" f"Dbq={db_path};"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Query your table
    cursor.execute("SELECT * FROM Example")
    for row in cursor:
        print(row)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    show_access_data(
        r"C:\CAF\CAFRepository\my_projects\iot_bind\backend\.gitignores\db.accdb"
    )
