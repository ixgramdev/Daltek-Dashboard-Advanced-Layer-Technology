import json
from typing import Any

class QueryBuilder:

    # Estructura del JSON
    # {
    # "id": null,
    # "name": "Consulta de ventas",
    # "doctype": "Sales Invoice",
    # "columns": ["customer", "amount", "date"],
    # "filters": [{"field": "status", "operator": "=", "value": "Paid"}],
    # "description": "Consulta sobre Sales Invoice",
    # "created_by": "juan.perez@example.com",
    # "created_at": "2025-11-29T04:30:00.000Z"
    # }

    def __init__(self, query_data: str | dict[str, Any]):

        self.raw_data = query_data
        self.query_dict = self._parse_input(query_data)
        self.sql_parts = []
        self._validate_input()

    def _parse_input(self, data: str | dict[str, Any]) -> dict[str, Any]:
        """
        Parsea el input si es string JSON o lo usa si es diccionario.

        Args:
            data: String JSON o diccionario

        Returns:
            Diccionario con la configuración de consulta

        Raises:
            ValueError: Si no se puede parsear el JSON
        """
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON inválido: {str(e)}")
        elif isinstance(data, dict):
            return data
        else:
            raise ValueError("query_data debe ser un string JSON o un diccionario")

    def _validate_input(self) -> None:
        """Valida que el diccionario tenga los campos necesarios."""
        if not isinstance(self.query_dict, dict):
            raise ValueError("query_dict debe ser un diccionario")

        # Validar campos obligatorios
        if "from" not in self.query_dict or not self.query_dict["from"]:
            raise ValueError("Campo 'from' es obligatorio")

        # Si no hay SELECT, asumir todas las columnas
        if "select" not in self.query_dict or not self.query_dict["select"]:
            self.query_dict["select"] = ["*"]

    def build(self) -> str:
        """
        Construye la sentencia SQL completa.

        Returns:
            str: La sentencia SQL lista para ejecutarse
        """
        self._build_select()
        self._build_from()
        self._build_joins()
        self._build_where()
        self._build_group_by()
        self._build_having()
        self._build_order_by()
        self._build_limit_offset()

        return self._compile_query()

    def _build_select(self) -> None:
        """Construye la cláusula SELECT."""
        select_cols = self.query_dict.get("select", ["*"])

        # Validar que sea lista
        if not isinstance(select_cols, list):
            select_cols = [select_cols]

        # Si está vacía, usar *
        if not select_cols or select_cols == []:
            select_cols = ["*"]

        select_clause = "SELECT " + ", ".join(str(col) for col in select_cols)
        self.sql_parts.append(select_clause)

    def _build_from(self) -> None:
        """Construye la cláusula FROM."""
        from_clause = self.query_dict.get("from")
        self.sql_parts.append(f"FROM {from_clause}")

    def _build_joins(self) -> None:
        """Construye las cláusulas JOIN."""
        joins = self.query_dict.get("joins", [])

        if not isinstance(joins, list):
            return

        for join in joins:
            if not isinstance(join, dict):
                continue

            join_type = join.get("type", "INNER").upper()
            table = join.get("table")
            alias = join.get("alias")
            on_condition = join.get("on")

            if not table or not on_condition:
                continue

            table_expr = f"{table} AS {alias}" if alias else table
            join_clause = f"{join_type} JOIN {table_expr} ON {on_condition}"
            self.sql_parts.append(join_clause)

    def _build_where(self) -> None:
        """Construye la cláusula WHERE."""
        where_conditions = self.query_dict.get("where", [])

        if not where_conditions:
            return

        where_clauses = []

        for condition in where_conditions:
            if not isinstance(condition, dict):
                continue

            # Si es condición RAW
            if condition.get("type") == "RAW":
                where_clauses.append(condition.get("condition"))
                continue

            # Construir condición normal
            field = condition.get("field")
            operator = condition.get("operator", "=")
            value = condition.get("value")

            if field is None:
                continue

            # Escapar valor si es string
            if isinstance(value, str):
                value_str = f"'{value}'"
            elif value is None:
                value_str = "NULL"
            else:
                value_str = str(value)

            where_clause = f"{field} {operator} {value_str}"
            where_clauses.append(where_clause)

        if where_clauses:
            combined_where = " AND ".join(where_clauses)
            self.sql_parts.append(f"WHERE {combined_where}")

    def _build_group_by(self) -> None:
        """Construye la cláusula GROUP BY."""
        group_by = self.query_dict.get("group_by", [])

        if not group_by:
            return

        if not isinstance(group_by, list):
            group_by = [group_by]

        group_clause = "GROUP BY " + ", ".join(str(col) for col in group_by)
        self.sql_parts.append(group_clause)

    def _build_having(self) -> None:
        """Construye la cláusula HAVING."""
        having_conditions = self.query_dict.get("having", [])

        if not having_conditions:
            return

        having_clauses = []

        for condition in having_conditions:
            if not isinstance(condition, dict):
                continue

            # Si es condición RAW
            if condition.get("type") == "RAW":
                having_clauses.append(condition.get("condition"))
                continue

            # Construir condición normal
            field = condition.get("field")
            operator = condition.get("operator", "=")
            value = condition.get("value")

            if field is None:
                continue

            # Escapar valor
            if isinstance(value, str):
                value_str = f"'{value}'"
            elif value is None:
                value_str = "NULL"
            else:
                value_str = str(value)

            having_clause = f"{field} {operator} {value_str}"
            having_clauses.append(having_clause)

        if having_clauses:
            combined_having = " AND ".join(having_clauses)
            self.sql_parts.append(f"HAVING {combined_having}")

    def _build_order_by(self) -> None:
        """Construye la cláusula ORDER BY."""
        order_by = self.query_dict.get("order_by", [])

        if not order_by:
            return

        if not isinstance(order_by, list):
            order_by = [order_by]

        order_clauses = []
        for item in order_by:
            if isinstance(item, dict):
                field = item.get("field")
                direction = item.get("direction", "ASC").upper()
                if field:
                    order_clauses.append(f"{field} {direction}")
            else:
                order_clauses.append(str(item))

        if order_clauses:
            order_clause = "ORDER BY " + ", ".join(order_clauses)
            self.sql_parts.append(order_clause)

    def _build_limit_offset(self) -> None:
        """Construye las cláusulas LIMIT y OFFSET."""
        limit = self.query_dict.get("limit")
        offset = self.query_dict.get("offset")

        if limit is not None:
            self.sql_parts.append(f"LIMIT {int(limit)}")

        if offset is not None:
            self.sql_parts.append(f"OFFSET {int(offset)}")

    def _compile_query(self) -> str:
        """Compila todas las partes en una sentencia SQL completa."""
        return " ".join(self.sql_parts)

    def get_sql(self) -> str:
        """Alias para build(), retorna la sentencia SQL."""
        return self.build()

# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo 1: Con diccionario
    query_dict = {
        "select": ["name", "email", "status"],
        "from": "User",
        "where": [{"field": "status", "operator": "=", "value": "Active"}],
        "order_by": [{"field": "name", "direction": "ASC"}],
        "limit": 100,
    }

    builder = QueryBuilder(query_dict)
    sql = builder.build()
    print("=== Ejemplo 1: Con diccionario ===")
    print(sql)
    print()

    # Ejemplo 2: Con JSON string
    json_str = """
    {
        "select": ["department", "COUNT(*) as total"],
        "from": "Employee",
        "where": [
            {"field": "company", "operator": "=", "value": "Acme Corp"}
        ],
        "group_by": ["department"],
        "having": [
            {"field": "COUNT(*)", "operator": ">", "value": 5}
        ]
    }
    """

    builder2 = QueryBuilder(json_str)
    sql2 = builder2.build()
    print("=== Ejemplo 2: Con JSON string ===")
    print(sql2)
    print()

    # Ejemplo 3: Con JOIN
    query_with_join = {
        "select": ["u.name", "u.email", "p.role"],
        "from": "User u",
        "joins": [
            {"type": "LEFT", "table": "UserRole", "alias": "p", "on": "u.name = p.user"}
        ],
        "where": [{"field": "u.status", "operator": "=", "value": "Active"}],
    }

    builder3 = QueryBuilder(query_with_join)
    sql3 = builder3.build()
    print("=== Ejemplo 3: Con JOIN ===")
    print(sql3)
