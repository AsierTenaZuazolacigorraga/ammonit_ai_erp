import requests
import time
import pyodbc

# from backend.app.logger import get_logger

import argparse

import os

API_URL = "https://api.ammonit.es/api/v1/"
ACCESS_TOKEN_POST_URL = f"{API_URL}login/access-token/"
ORDERS_GET_URL = f"{API_URL}orders/"

# logger = get_logger(__name__)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    while True:

        try:
            time.sleep(2)

            # Get input arguments
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
            access_db = AccessDB(args.db_path)

            # Get token
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

                                logger.info(f"Id: {order['id']}")
                                logger.info(f"In document: {order['in_document_name']}")
                                logger.info(
                                    f"Out document: {order['out_document_name']}"
                                )

                                # Write it into access
                                access_db.write_order(
                                    {
                                        "id": order["id"],
                                        "in_document_name": order["in_document_name"],
                                        "out_document_name": order["out_document_name"],
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
