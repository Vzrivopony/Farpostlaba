import sqlite3
import os
from collections.abc import Collection
from typing import Iterator, Optional, Tuple, Any


class TableData(Collection):
    #Класс для работы с таблицей SQLite как с коллекцией.

    def __init__(self, database_name: str, table_name: str):

        #Инициализирует объект для работы с таблицей.
        if not os.path.exists(database_name):
            raise FileNotFoundError(f"Файл базы данных '{database_name}' не найден.")
        self.database_name = database_name
        self.table_name = table_name

    def _execute_query(self, query: str, params: Optional[dict] = None) -> sqlite3.Cursor:
        #Выполняет SQL-запрос к базе данных.
        with sqlite3.connect(self.database_name) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or {})
            return cursor

    def __len__(self) -> int:
        #Возвращает количество строк в таблице.
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        return self._execute_query(query).fetchone()[0]

    def __getitem__(self, name: str) -> Tuple[Any, ...]:
        #Возвращает запись из таблицы по имени.
        query = f"SELECT * FROM {self.table_name} WHERE name = :name"
        row = self._execute_query(query, {"name": name}).fetchone()
        if row is None:
            raise KeyError(f"Запись с именем '{name}' не найдена.")
        return row

    def __contains__(self, name: str) -> bool:
        #Наличие записи по селекту 
        query = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE name = :name)"
        return bool(self._execute_query(query, {"name": name}).fetchone()[0])

    def __iter__(self) -> Iterator[Tuple[Any, ...]]:
        query = f"SELECT * FROM {self.table_name}"
        cursor = self._execute_query(query)
        while row := cursor.fetchone():
            yield row