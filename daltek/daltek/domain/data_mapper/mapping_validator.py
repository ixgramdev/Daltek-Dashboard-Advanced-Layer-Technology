# MappingValidator: Validador de configuraciones de mapeo

from typing import Dict, List, Any


class MappingValidator:
    # Valida que las configuraciones de mapeo sean correctas
    
    # Tipos de datos soportados
    NUMERIC_TYPES = ["int", "float", "currency", "number", "decimal"]
    TEXT_TYPES = ["text", "string", "varchar", "char"]
    DATE_TYPES = ["date", "datetime", "timestamp"]

    # Agregaciones válidas por tipo
    NUMERIC_AGGREGATIONS = [
        "sum",
        "avg",
        "mean",
        "min",
        "max",
        "count",
        "median",
        "std",
        "var",
        "percentile_25",
        "percentile_50",
        "percentile_75",
        "percentile_90",
        "percentile_95",
        "percentile_99",
    ]

    TEXT_AGGREGATIONS = ["count", "count_unique", "first", "last", "concat"]

    DATE_AGGREGATIONS = ["count", "min", "max", "first", "last"]

    # Operadores válidos por tipo
    NUMERIC_OPERATORS = ["=", "!=", ">", ">=", "<", "<=", "between"]

    TEXT_OPERATORS = [
        "=",
        "!=",
        "contains",
        "not_contains",
        "starts_with",
        "ends_with",
        "in",
        "not_in",
    ]

    DATE_OPERATORS = [
        "=",
        "!=",
        ">",
        ">=",
        "<",
        "<=",
        "between",
        "date_equals",
        "date_before",
        "date_after",
        "date_between",
    ]

    def validate_mapping(self, config: Dict, available_columns: List[Dict]) -> Dict:
        # Valida configuración completa de mapeo
        errors = []
        warnings = []

        # Crear mapa de columnas
        columns_map = {col["name"]: col for col in available_columns}

        # Validar group_by
        if "group_by" in config:
            for col in config["group_by"]:
                if col not in columns_map:
                    errors.append(f"Columna '{col}' en group_by no existe")

        # Validar aggregations
        if "aggregations" in config:
            for alias, agg_config in config["aggregations"].items():
                col = agg_config.get("column")
                func = agg_config.get("func")

                if col not in columns_map:
                    errors.append(
                        f"Columna '{col}' en agregación '{alias}' no existe"
                    )
                    continue

                col_type = columns_map[col].get("type", "text").lower()

                if not self.validate_aggregation_compatibility(col_type, func):
                    errors.append(
                        f"Agregación '{func}' no es compatible con tipo '{col_type}' para columna '{col}'"
                    )

        # Validar filters
        if "filters" in config:
            for i, filter_config in enumerate(config["filters"]):
                col = filter_config.get("column")
                operator = filter_config.get("operator")

                if col not in columns_map:
                    errors.append(f"Columna '{col}' en filtro #{i + 1} no existe")
                    continue

                col_type = columns_map[col].get("type", "text").lower()

                if not self.validate_filter_operator(col_type, operator):
                    errors.append(
                        f"Operador '{operator}' no es compatible con tipo '{col_type}' para columna '{col}'"
                    )

        # Validar sort
        if "sort" in config:
            sort_config = config["sort"]
            if isinstance(sort_config, dict):
                col = sort_config.get("column")
                if col and col not in columns_map:
                    errors.append(f"Columna '{col}' en sort no existe")
            elif isinstance(sort_config, str):
                if sort_config not in columns_map:
                    errors.append(f"Columna '{sort_config}' en sort no existe")

        # Validar widget_mapping
        if "widget_mapping" in config:
            mapping = config["widget_mapping"]

            if "x_axis" in mapping:
                x_col = mapping["x_axis"]
                if x_col not in columns_map:
                    # Podría ser una columna calculada
                    if "aggregations" not in config or x_col not in config[
                        "aggregations"
                    ]:
                        warnings.append(
                            f"Columna '{x_col}' en x_axis no existe (¿columna calculada?)"
                        )

            if "y_axes" in mapping:
                for y_col in mapping["y_axes"]:
                    if y_col not in columns_map:
                        if "aggregations" not in config or y_col not in config[
                            "aggregations"
                        ]:
                            warnings.append(
                                f"Columna '{y_col}' en y_axes no existe (¿columna calculada?)"
                            )

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def validate_columns_exist(
        self, config: Dict, available_columns: List[str]
    ) -> Dict:
        # Verifica que las columnas especificadas existan
        errors = []

        # Verificar columnas en diferentes partes de la config
        all_columns = set()

        if "group_by" in config:
            all_columns.update(config["group_by"])

        if "aggregations" in config:
            for agg_config in config["aggregations"].values():
                all_columns.add(agg_config.get("column"))

        if "filters" in config:
            for filter_config in config["filters"]:
                all_columns.add(filter_config.get("column"))

        # Verificar existencia
        for col in all_columns:
            if col and col not in available_columns:
                errors.append(f"Columna '{col}' no existe en los datos")

        return {"is_valid": len(errors) == 0, "errors": errors}

    def validate_aggregation_compatibility(self, column_type: str, aggfunc: str) -> bool:
        # Verifica que la agregación sea válida para el tipo de columna
        column_type = column_type.lower()

        if any(t in column_type for t in self.NUMERIC_TYPES):
            return aggfunc in self.NUMERIC_AGGREGATIONS
        elif any(t in column_type for t in self.TEXT_TYPES):
            return aggfunc in self.TEXT_AGGREGATIONS
        elif any(t in column_type for t in self.DATE_TYPES):
            return aggfunc in self.DATE_AGGREGATIONS
        else:
            # Si no se conoce el tipo, permitir count
            return aggfunc in ["count", "count_unique"]

    def validate_filter_operator(self, column_type: str, operator: str) -> bool:
        # Verifica que el operador sea válido para el tipo de columna
        column_type = column_type.lower()

        # Operadores universales
        if operator in ["is_null", "is_not_null"]:
            return True

        if any(t in column_type for t in self.NUMERIC_TYPES):
            return operator in self.NUMERIC_OPERATORS
        elif any(t in column_type for t in self.TEXT_TYPES):
            return operator in self.TEXT_OPERATORS
        elif any(t in column_type for t in self.DATE_TYPES):
            return operator in self.DATE_OPERATORS
        else:
            # Operadores básicos permitidos para tipos desconocidos
            return operator in ["=", "!=", "in", "not_in"]

    def validate_chart_compatibility(self, chart_type: str, data_shape: Dict) -> Dict:
        # Verifica que los datos sean compatibles con el tipo de gráfico
        errors = []
        warnings = []

        num_columns = data_shape.get("num_columns", 0)
        num_rows = data_shape.get("num_rows", 0)
        has_numeric = data_shape.get("has_numeric", False)

        if chart_type in ["line", "bar", "area"]:
            if num_columns < 2:
                errors.append(
                    f"Gráfico {chart_type} requiere al menos 2 columnas (X e Y)"
                )
            if not has_numeric:
                errors.append(f"Gráfico {chart_type} requiere al menos una columna numérica")

        elif chart_type == "pie":
            if num_columns < 2:
                errors.append("Gráfico pie requiere 2 columnas (label y value)")
            if num_columns > 2:
                warnings.append(
                    "Gráfico pie solo usa 2 columnas, columnas adicionales serán ignoradas"
                )

        elif chart_type == "scatter":
            if num_columns < 2:
                errors.append("Gráfico scatter requiere al menos 2 columnas numéricas")

        elif chart_type == "heatmap":
            if num_columns < 3:
                errors.append("Heatmap requiere al menos 3 columnas (X, Y, valor)")

        # Validar cantidad de datos
        if num_rows == 0:
            errors.append("No hay datos para visualizar")
        elif num_rows > 10000:
            warnings.append(
                f"Dataset grande ({num_rows} filas), podría afectar el rendimiento"
            )

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def get_compatible_aggregations(self, column_type: str) -> List[str]:
        # Retorna lista de agregaciones compatibles con el tipo de columna
        column_type = column_type.lower()

        if any(t in column_type for t in self.NUMERIC_TYPES):
            return self.NUMERIC_AGGREGATIONS
        elif any(t in column_type for t in self.TEXT_TYPES):
            return self.TEXT_AGGREGATIONS
        elif any(t in column_type for t in self.DATE_TYPES):
            return self.DATE_AGGREGATIONS
        else:
            return ["count", "count_unique"]

    def get_compatible_operators(self, column_type: str) -> List[str]:
        # Retorna lista de operadores compatibles con el tipo de columna
        column_type = column_type.lower()

        if any(t in column_type for t in self.NUMERIC_TYPES):
            return self.NUMERIC_OPERATORS + ["is_null", "is_not_null"]
        elif any(t in column_type for t in self.TEXT_TYPES):
            return self.TEXT_OPERATORS + ["is_null", "is_not_null"]
        elif any(t in column_type for t in self.DATE_TYPES):
            return self.DATE_OPERATORS + ["is_null", "is_not_null"]
        else:
            return ["=", "!=", "in", "not_in", "is_null", "is_not_null"]
