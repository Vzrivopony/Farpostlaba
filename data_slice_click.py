import mysql.connector
import clickhouse_connect
from datetime import datetime
import time


mysql_config = {
    "user": "root",
    "password": "root",
    "host": "localhost",
    "database": "mydatabase",
}


ch_client = clickhouse_connect.get_client(
    host="localhost",
    port=8123,
    username="default",
    password="mypassword",
    database="mydatabase",
)


def fetch_data_from_mysql():
    """Извлечение данных из MySQL"""
    conn = mysql.connector.connect(**mysql_config)
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, message FROM messages")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def insert_into_clickhouse(data):
    """Вставка данных в ClickHouse"""
    if not data:
        print("Нет данных для вставки.")
        return

    rows = []
    for row in data:
        id_, timestamp, message = row
        if isinstance(timestamp, str):
            export_timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        rows.append((id_, timestamp, message))

    ch_client.insert(
        "messages", rows, column_names=["id", "export_timestamp", "message"]
    )
    print(f"Вставлено {len(rows)} строк в ClickHouse.")


if __name__ == "__main__":
    while True:
        data = fetch_data_from_mysql()
        insert_into_clickhouse(data)
        time.sleep(300)  # Каждые 5 минут