import os
import time


directory = "data_slices"


def cleanup_old_files():
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if (
            os.path.isfile(file_path)
            and (current_time - os.path.getmtime(file_path)) > 3600
        ):
            os.remove(file_path)
            print(f"Удалён файл: {file_path}")


if __name__ == "__main__":
    while True:
        cleanup_old_files()
        time.sleep(3600)  # Каждые 1 час