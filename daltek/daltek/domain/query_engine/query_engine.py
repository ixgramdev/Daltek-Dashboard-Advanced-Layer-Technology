class QueryEngine:
    def __init__(self):
        self._select = []
        self._from = None
        self._joins = []
        self._where = []
        self._group_by = []
        self._having = []
        self._order_by = []
        self._limit = None
        self._offset = None

    def select(self, *columns):
        for col in columns:
            if isinstance(col, SQLFunction):
                self._select.append(str(col))
            else:
                self._select.append(str(col))
        return self

    def from_table(self, table_name, alias=None):
        if alias:
            self._from = f"{table_name} AS {alias}"
        else:
            self._from = table_name
        return self

    def join(self, table, on_condition, join_type="INNER", alias=None):
        table_expr = f"{table} AS {alias}" if alias else table
        self._joins.append(f"{join_type} JOIN {table_expr} ON {on_condition}")
        return self

    def inner_join(self, table, on_condition, alias=None):
        return self.join(table, on_condition, "INNER", alias)

    def left_join(self, table, on_condition, alias=None):
        return self.join(table, on_condition, "LEFT", alias)

    def right_join(self, table, on_condition, alias=None):
        return self.join(table, on_condition, "RIGHT", alias)

    def where(self, condition):
        if isinstance(condition, Condition):
            self._where.append(str(condition))
        else:
            self._where.append(str(condition))
        return self

    def and_where(self, condition):
        return self.where(condition)

    def group_by(self, *columns):
        self._group_by.extend(columns)
        return self

    def having(self, condition):
        self._having.append(str(condition))
        return self

    def order_by(self, column, direction="ASC"):
        direction = direction.upper()
        if direction not in ("ASC", "DESC"):
            raise ValueError("direction debe ser 'ASC' o 'DESC'")
        self._order_by.append(f"{column} {direction}")
        return self

    def limit(self, count):
        self._limit = int(count)
        return self

    def offset(self, count):
        self._offset = int(count)
        return self

    def build(self):
        if not self._select:
            raise ValueError("Debe especificar al menos una columna con select()")
        if not self._from:
            raise ValueError("Debe especificar una tabla con from_table()")

        query_parts = []

        select_clause = "SELECT " + ", ".join(self._select)
        query_parts.append(select_clause)

        query_parts.append(f"FROM {self._from}")

        if self._joins:
            query_parts.extend(self._joins)

        if self._where:
            where_clause = "WHERE " + " AND ".join(self._where)
            query_parts.append(where_clause)

        if self._group_by:
            group_clause = "GROUP BY " + ", ".join(self._group_by)
            query_parts.append(group_clause)

        if self._having:
            having_clause = "HAVING " + " AND ".join(self._having)
            query_parts.append(having_clause)

        if self._order_by:
            order_clause = "ORDER BY " + ", ".join(self._order_by)
            query_parts.append(order_clause)

        if self._limit is not None:
            query_parts.append(f"LIMIT {self._limit}")

        if self._offset is not None:
            query_parts.append(f"OFFSET {self._offset}")

        return "\n".join(query_parts)

    def __str__(self):
        return self.build()


class SQLFunction:
    def __init__(self, expression, alias=None):
        self.expression = expression
        self.alias = alias

    def __str__(self):
        if self.alias:
            return f"{self.expression} AS {self.alias}"
        return self.expression


class Count(SQLFunction):
    def __init__(self, column="*", alias=None):
        expression = f"COUNT({column})"
        super().__init__(expression, alias)


class Sum(SQLFunction):
    def __init__(self, column, alias=None):
        expression = f"SUM({column})"
        super().__init__(expression, alias)


class Avg(SQLFunction):
    def __init__(self, column, alias=None):
        expression = f"AVG({column})"
        super().__init__(expression, alias)


class Min(SQLFunction):
    def __init__(self, column, alias=None):
        expression = f"MIN({column})"
        super().__init__(expression, alias)


class Max(SQLFunction):
    def __init__(self, column, alias=None):
        expression = f"MAX({column})"
        super().__init__(expression, alias)


class Distinct(SQLFunction):
    def __init__(self, column, alias=None):
        expression = f"DISTINCT({column})"
        super().__init__(expression, alias)


class Round(SQLFunction):
    def __init__(self, column, decimals=2, alias=None):
        expression = f"ROUND({column}, {decimals})"
        super().__init__(expression, alias)


class Coalesce(SQLFunction):
    def __init__(self, *columns, alias=None):
        expression = f"COALESCE({', '.join(columns)})"
        super().__init__(expression, alias)


class Condition:
    @staticmethod
    def equals(column, value):
        if isinstance(value, str):
            return f"{column} = '{value}'"
        return f"{column} = {value}"

    @staticmethod
    def not_equals(column, value):
        if isinstance(value, str):
            return f"{column} != '{value}'"
        return f"{column} != {value}"

    @staticmethod
    def greater_than(column, value):
        return f"{column} > {value}"

    @staticmethod
    def less_than(column, value):
        return f"{column} < {value}"

    @staticmethod
    def in_list(column, values):
        values_str = ", ".join(
            [f"'{v}'" if isinstance(v, str) else str(v) for v in values]
        )
        return f"{column} IN ({values_str})"

    @staticmethod
    def like(column, pattern):
        return f"{column} LIKE '{pattern}'"

    @staticmethod
    def between(column, start, end):
        return f"{column} BETWEEN {start} AND {end}"

    @staticmethod
    def is_null(column):
        return f"{column} IS NULL"

    @staticmethod
    def is_not_null(column):
        return f"{column} IS NOT NULL"
