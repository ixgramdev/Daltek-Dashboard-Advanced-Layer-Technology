# DataMapperService: Servicio principal de transformación de datos

import json
import time
from typing import Dict, List, Any
import frappe

from .pandas_transformer import PandasTransformer
from .widget_data_adapter import WidgetDataAdapter
from .mapping_validator import MappingValidator


class DataMapperService:
    # Servicio central para transformar datos de queries a formato de widgets
    
    def __init__(self):
        self.pandas_transformer = PandasTransformer()
        self.widget_adapter = WidgetDataAdapter()
        self.validator = MappingValidator()

    def transform(
        self, query_result: Dict, mapper_config: Dict, limit: int = None
    ) -> Dict:
        # Transforma datos crudos según configuración de mapeo
        start_time = time.time()

        try:
            # Validar que hay datos
            if not query_result.get("success"):
                return {
                    "success": False,
                    "error": query_result.get("error", "Query falló"),
                }

            data = query_result.get("results", [])
            if not data:
                return {
                    "success": False,
                    "error": "No hay datos para transformar",
                    "data": [],
                }

            # Cargar datos en DataFrame
            df = self.pandas_transformer.load_data(data)

            # Obtener configuración de transformaciones
            transformations = mapper_config.get("transformations", {})

            # 1. Aplicar filtros
            if "filters" in transformations and transformations["filters"]:
                df = self.pandas_transformer.filter(df, transformations["filters"])

            # 2. Aplicar agregaciones
            if "aggregations" in transformations and transformations["aggregations"]:
                group_by = transformations.get("group_by", [])
                df = self.pandas_transformer.aggregate(
                    df, {"group_by": group_by, "aggregations": transformations["aggregations"]}
                )

            # 3. Aplicar cálculos (columnas calculadas)
            if "calculations" in transformations and transformations["calculations"]:
                df = self.pandas_transformer.calculate(df, transformations["calculations"])

            # 4. Aplicar ordenamiento
            if "sort" in transformations:
                sort_config = transformations["sort"]
                if isinstance(sort_config, dict):
                    column = sort_config.get("column")
                    order = sort_config.get("order", "asc")
                    ascending = order.lower() == "asc"
                    df = self.pandas_transformer.sort(df, column, ascending)
                elif isinstance(sort_config, str):
                    df = self.pandas_transformer.sort(df, sort_config)

            # 5. Aplicar límite
            transform_limit = transformations.get("limit")
            if limit:
                df = df.head(limit)
            elif transform_limit:
                df = df.head(transform_limit)

            # 6. Aplicar formato (si se especifica)
            if "formats" in transformations and transformations["formats"]:
                df = self.pandas_transformer.format_values(df, transformations["formats"])

            # Convertir a formato del widget
            widget_mapping = mapper_config.get("widget_mapping", {})
            widget_type = widget_mapping.get("type", "table")

            if widget_type == "echart":
                chart_type = widget_mapping.get("chart_type", "line")
                x_axis = widget_mapping.get("x_axis")
                y_axes = widget_mapping.get("y_axes", [])
                chart_config = widget_mapping.get("chart_config", {})

                widget_data = self.widget_adapter.to_echart_format(
                    df, chart_type, x_axis, y_axes, chart_config
                )
            elif widget_type == "table":
                columns = widget_mapping.get("columns")
                widget_data = self.widget_adapter.to_table_format(df, columns)
            elif widget_type == "card":
                metric_config = widget_mapping.get("metric_config", {})
                widget_data = self.widget_adapter.to_card_format(df, metric_config)
            elif widget_type == "heatmap":
                widget_data = self.widget_adapter.to_heatmap_format(
                    df,
                    widget_mapping.get("x"),
                    widget_mapping.get("y"),
                    widget_mapping.get("value"),
                )
            elif widget_type == "treemap":
                widget_data = self.widget_adapter.to_treemap_format(
                    df, widget_mapping.get("hierarchy", []), widget_mapping.get("value")
                )
            else:
                # Por defecto, retornar como tabla
                widget_data = self.widget_adapter.to_table_format(df)

            execution_time = time.time() - start_time

            return {
                "success": True,
                "data": widget_data,
                "metadata": {
                    "original_rows": len(data),
                    "transformed_rows": len(df),
                    "columns": df.columns.tolist(),
                    "execution_time": f"{execution_time:.3f}s",
                },
            }

        except Exception as e:
            frappe.log_error(f"Error en DataMapperService.transform: {str(e)}")
            return {"success": False, "error": str(e)}

    def preview_transformation(
        self, query_result: Dict, mapper_config: Dict, limit: int = 100
    ) -> Dict:
        # Preview de transformación sin guardar (para UI)
        return self.transform(query_result, mapper_config, limit=limit)

    def validate_mapping(self, mapper_config: Dict, query_columns: List[Dict]) -> Dict:
        # Valida que la configuración sea compatible con las columnas
        try:
            transformations = mapper_config.get("transformations", {})

            # Usar el validador
            validation = self.validator.validate_mapping(transformations, query_columns)

            return validation

        except Exception as e:
            frappe.log_error(f"Error en DataMapperService.validate_mapping: {str(e)}")
            return {"is_valid": False, "errors": [str(e)], "warnings": []}

    def get_available_operations(self, column_type: str) -> Dict:
        # Retorna operaciones disponibles según tipo de columna
        try:
            aggregations = self.validator.get_compatible_aggregations(column_type)
            operators = self.validator.get_compatible_operators(column_type)

            # Cálculos disponibles (genéricos)
            calculations = [
                "add",
                "subtract",
                "multiply",
                "divide",
                "percentage",
                "round",
                "abs",
            ]

            if "text" in column_type.lower() or "string" in column_type.lower():
                calculations.extend(["upper", "lower", "trim", "concat"])

            if "date" in column_type.lower():
                calculations.extend(
                    [
                        "date_diff",
                        "extract_year",
                        "extract_month",
                        "extract_day",
                        "format_date",
                    ]
                )

            return {
                "success": True,
                "aggregations": aggregations,
                "operators": operators,
                "calculations": calculations,
            }

        except Exception as e:
            frappe.log_error(
                f"Error en DataMapperService.get_available_operations: {str(e)}"
            )
            return {"success": False, "error": str(e)}

    def get_column_metadata(self, data: List[Dict]) -> List[Dict]:
        # Analiza datos y retorna metadata de columnas
        if not data:
            return []

        df = self.pandas_transformer.load_data(data)
        metadata = []

        for col in df.columns:
            col_type = "text"
            dtype = df[col].dtype

            if "int" in str(dtype):
                col_type = "int"
            elif "float" in str(dtype):
                col_type = "float"
            elif "datetime" in str(dtype):
                col_type = "date"
            elif "bool" in str(dtype):
                col_type = "boolean"

            metadata.append(
                {
                    "name": col,
                    "type": col_type,
                    "nullable": df[col].isna().any(),
                    "unique_count": df[col].nunique(),
                    "sample_values": df[col].head(3).tolist(),
                }
            )

        return metadata
