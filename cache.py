
class PrecomputationCache:
    """
    Кэш таблиц предвычисленных степеней
    """

    def __init__(self):
        self._cache = {}

        self.cache_hits = 0
        self.cache_misses = 0

    @property
    def size(self) -> int:
        """Количество сохранённых таблиц"""
        return len(self._cache)

    def get(self, key):
        """
        Получение таблицы по ключу
        Возвращает None, если таблица отсутствует
        """

        if key not in self._cache:
            self.cache_misses += 1
            return None

        self.cache_hits += 1

        table = self._cache[key]

        # Возвращаем копию, чтобы алгоритм
        # не изменил сохранённую таблицу
        if isinstance(table, dict):
            return table.copy()

        if isinstance(table, list):
            return table.copy()

        return table

    def put(self, key, table):
        """Сохранение таблицы"""

        if isinstance(table, dict):
            table = table.copy()
        elif isinstance(table, list):
            table = table.copy()

        self._cache[key] = table

    def clear(self):
        """Полная очистка кэша и статистики"""

        self._cache.clear()

        self.cache_hits = 0
        self.cache_misses = 0

    def __len__(self):
        return self.size
