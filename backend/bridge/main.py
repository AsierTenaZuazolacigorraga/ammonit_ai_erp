import requests
import time
import pyodbc
import pandas as pd  # Import pandas for CSV handling
import io
import base64  # For decoding base64 encoded strings

from backend.app.logger import get_logger

import argparse

import os

API_URL = "https://api.ammonit.es/api/v1/"
ACCESS_TOKEN_POST_URL = f"{API_URL}login/access-token/"
ORDERS_GET_URL = f"{API_URL}orders/"

logger = get_logger(__name__)


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


def main() -> None:

    logger.info(f"Getting into the loop")

    while True:

        try:
            time.sleep(2)

            # Get input arguments
            logger.info(f"Getting input arguments")
            parser = argparse.ArgumentParser(description="Process some integers.")
            parser.add_argument("--db_path", type=str, help="Path to the database file")
            parser.add_argument("--username", type=str, help="Username for API access")
            parser.add_argument("--password", type=str, help="Password for API access")
            args = parser.parse_args()

            if args.username == "":
                args.username = os.getenv("FIRST_SUPERUSER")
            if args.password == "":
                args.password = os.getenv("FIRST_SUPERUSER_PASSWORD")

            # Get access db class
            logger.info(f"Getting access db class")
            access_db = AccessDB(args.db_path)

            # Get token
            logger.info(f"Getting token")
            logger.info(f"  - Username: {args.username}")
            response = requests.post(
                ACCESS_TOKEN_POST_URL,
                data={
                    "grant_type": "password",
                    "username": args.username,
                    "password": args.password,
                    "scope": "",
                    "client_id": "string",
                    "client_secret": "string",
                },
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            if response.status_code == 200:
                access_token = response.json().get("access_token")

                while True:
                    time.sleep(2)

                    # Get orders
                    logger.info(f"Getting orders")
                    response = requests.get(
                        ORDERS_GET_URL,
                        params={"skip": 0, "limit": 100},
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Accept": "application/json",
                        },
                    )
                    if response.status_code == 200:
                        orders = response.json().get("data")
                        db_orders = access_db.read_orders()

                        # Identify new emails
                        for order in orders:
                            if order["id"] not in [o[0] for o in db_orders]:

                                # Read the CSV data from the out_document string
                                csv_data_str = order["out_document"]

                                # Decode if it's base64 encoded
                                decoded_data = base64.b64decode(csv_data_str).decode(
                                    "utf-8"
                                )

                                # Use StringIO to create a file-like object from the string
                                csv_file = io.StringIO(decoded_data)

                                # Read the CSV data, iterate and write it into access
                                csv_data = pd.read_csv(csv_file, sep=";")
                                for _, row in csv_data.iterrows():
                                    logger.info(f"Order ID: {order['id']}")
                                    logger.info(
                                        f"  - Número de Pedido: {row['Número de Pedido']}"
                                    )
                                    logger.info(f"  - Código: {row['Código']}")
                                    logger.info(
                                        f"  - Descripción: {row['Descripción']}"
                                    )
                                    logger.info(f"  - Cantidad: {row['Cantidad']}")
                                    logger.info(
                                        f"  - Precio Unitario: {row['Precio Unitario']}"
                                    )
                                    logger.info(f"  - Plazo: {row['Plazo']}")

                                    # Write it into access
                                    access_db.write_order(
                                        {
                                            "id": str(order["id"]),
                                            "NUMERO_PEDIDO": str(
                                                row["Número de Pedido"]
                                            ),
                                            "CODIGO": str(row["Código"]),
                                            "DESCRIPCION": str(row["Descripción"]),
                                            "CANTIDAD": str(row["Cantidad"]),
                                            "PRECIO_UNITARIO": str(
                                                row["Precio Unitario"]
                                            ),
                                            "PLAZO": str(row["Plazo"]),
                                        }
                                    )

        except Exception as e:
            print(f"An error occurred: {e}")

            try:
                access_db.close_connection()
            except Exception as e:
                pass


if __name__ == "__main__":
    main()
