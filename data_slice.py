import mysql.connector
import time
import os
from datetime import datetime

# Настройки подключения к базе данных
config = {
    "user": "root",
    "password": "root",
    "host": "localhost",
    "database": "mydatabase",
}


def fetch_data():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def save_to_file(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data_slices/data_slice_{timestamp}.txt"
    os.makedirs("data_slices", exist_ok=True)
    with open(filename, "w") as f:
        for row in data:
            f.write(",".join(map(str, row)) + "\n")
    print(f"Сохранён файл: {filename}")


if __name__ == "__main__":
    while True:
        data = fetch_data()
        save_to_file(data)
        time.sleep(300)  # 5 минут
