import win32com.client

import os


def create_access_db(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)

    # Dispatch the ADOX Catalog COM object
    catalog = win32com.client.Dispatch("ADOX.Catalog")

    # Use the ACE OLE DB provider to create .accdb
    conn_str = f"Provider=Microsoft.ACE.OLEDB.12.0;Data Source={db_path};"
    catalog.Create(conn_str)
    print(f"Database created at {db_path}")

    # Connect to the database to add content
    conn = win32com.client.Dispatch("ADODB.Connection")
    conn.Open(conn_str)

    # Create tables
    conn.Execute(
        "CREATE TABLE Orders (id TEXT, in_document_name TEXT, out_document_name TEXT);"
    )
    print("Table created.")

    # Add a row
    conn.Execute(
        "INSERT INTO Orders (id, in_document_name, out_document_name) VALUES ('0', 'in_document_name', 'out_document_name');"
    )
    print("Row added to table.")

    # Close the connection
    conn.Close()


if __name__ == "__main__":

    create_access_db(
        r"C:\CAF\CAFRepository\my_projects\iot_bind\backend\.gitignores\db.accdb"
    )
