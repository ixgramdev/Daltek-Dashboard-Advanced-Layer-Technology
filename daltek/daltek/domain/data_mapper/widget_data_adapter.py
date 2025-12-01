# WidgetDataAdapter: Adapta datos transformados al formato específico de cada widget

import pandas as pd
from typing import Dict, List, Any


class WidgetDataAdapter:
    # Convierte DataFrames a formato específico de cada tipo de widget
    
    def to_echart_format(
        self,
        df: pd.DataFrame,
        chart_type: str,
        x_column: str,
        y_columns: List[str],
        chart_config: Dict = None,
    ) -> Dict:
        # Convierte a formato EChart
        if chart_config is None:
            chart_config = {}

        # Extraer datos del eje X
        x_data = df[x_column].tolist()

        # Crear series para cada columna Y
        series = []
        for y_col in y_columns:
            if y_col not in df.columns:
                continue

            y_data = df[y_col].tolist()

            serie = {
                "name": y_col,
                "type": chart_type,
                "data": y_data,
            }

            # Opciones adicionales según tipo de gráfico
            if chart_type == "line":
                serie["smooth"] = chart_config.get("smooth", True)
                serie["symbol"] = chart_config.get("symbol", "circle")
                serie["symbolSize"] = chart_config.get("symbolSize", 6)
            elif chart_type == "bar":
                serie["barWidth"] = chart_config.get("barWidth", "60%")
            elif chart_type == "pie":
                # Para pie, usar formato diferente
                serie = {
                    "name": y_col,
                    "type": "pie",
                    "radius": chart_config.get("radius", "50%"),
                    "data": [
                        {"value": y_data[i], "name": x_data[i]}
                        for i in range(len(x_data))
                    ],
                }
                return {
                    "series": [serie],
                    "tooltip": {"trigger": "item"},
                    "legend": {"orient": "vertical", "left": "left"},
                }

            series.append(serie)

        # Configuración del gráfico
        result = {
            "xAxis": {"type": "category", "data": x_data},
            "yAxis": {"type": "value"},
            "series": series,
            "tooltip": {"trigger": "axis"},
            "legend": {"data": y_columns},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        }

        # Agregar configuraciones adicionales
        if "color" in chart_config:
            result["color"] = chart_config["color"]

        if "title" in chart_config:
            result["title"] = {"text": chart_config["title"], "left": "center"}

        return result

    def to_table_format(self, df: pd.DataFrame, columns: List[str] = None) -> Dict:
        # Formato para widget de tabla
        if columns is None:
            columns = df.columns.tolist()

        # Detectar tipos de columnas
        column_defs = []
        for col in columns:
            if col not in df.columns:
                continue

            col_type = "text"
            dtype = df[col].dtype

            if pd.api.types.is_numeric_dtype(dtype):
                col_type = "number"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                col_type = "date"
            elif pd.api.types.is_bool_dtype(dtype):
                col_type = "boolean"

            column_defs.append({"field": col, "label": col.replace("_", " ").title(), "type": col_type})

        # Convertir filas a dict
        rows = df[columns].to_dict(orient="records")

        return {"columns": column_defs, "rows": rows, "count": len(rows)}

    def to_card_format(self, df: pd.DataFrame, metric_config: Dict) -> Dict:
        # Formato para widget de tarjeta/KPI
        value_col = metric_config.get("value_column")
        label = metric_config.get("label", value_col)
        compare_col = metric_config.get("compare_column")
        fmt = metric_config.get("format", "number")

        # Obtener valor principal (última fila o suma)
        if len(df) == 1:
            value = df[value_col].iloc[0]
        else:
            value = df[value_col].sum()

        result = {"value": value, "label": label, "format": fmt}

        # Calcular cambio si hay columna de comparación
        if compare_col and compare_col in df.columns:
            if len(df) == 1:
                compare_value = df[compare_col].iloc[0]
            else:
                compare_value = df[compare_col].sum()

            if compare_value != 0:
                change_pct = ((value - compare_value) / compare_value) * 100
                result["change"] = f"{change_pct:+.1f}%"
                result["trend"] = "up" if change_pct > 0 else "down" if change_pct < 0 else "neutral"
                result["subtitle"] = "vs período anterior"

        return result

    def to_heatmap_format(
        self, df: pd.DataFrame, x: str, y: str, value: str
    ) -> Dict:
        # Formato para heatmap
        # Obtener valores únicos de X e Y
        x_categories = df[x].unique().tolist()
        y_categories = df[y].unique().tolist()

        # Crear matriz de datos
        data = []
        for i, y_val in enumerate(y_categories):
            for j, x_val in enumerate(x_categories):
                mask = (df[x] == x_val) & (df[y] == y_val)
                if mask.any():
                    val = df.loc[mask, value].values[0]
                    data.append([j, i, val])

        return {
            "xAxis": {"type": "category", "data": x_categories},
            "yAxis": {"type": "category", "data": y_categories},
            "visualMap": {
                "min": df[value].min(),
                "max": df[value].max(),
                "calculable": True,
                "orient": "horizontal",
                "left": "center",
                "bottom": "15%",
            },
            "series": [
                {
                    "type": "heatmap",
                    "data": data,
                    "label": {"show": True},
                }
            ],
            "tooltip": {"position": "top"},
        }

    def to_treemap_format(
        self, df: pd.DataFrame, hierarchy: List[str], value: str
    ) -> Dict:
        # Formato para treemap (jerarquías)
        
        def build_tree(df_subset, level):
            if level >= len(hierarchy):
                return []

            col = hierarchy[level]
            groups = df_subset.groupby(col)[value].sum()

            children = []
            for name, val in groups.items():
                node = {"name": name, "value": float(val)}

                # Recursivamente construir hijos
                if level + 1 < len(hierarchy):
                    df_children = df_subset[df_subset[col] == name]
                    child_nodes = build_tree(df_children, level + 1)
                    if child_nodes:
                        node["children"] = child_nodes

                children.append(node)

            return children

        tree_data = build_tree(df, 0)

        return {
            "series": [
                {
                    "type": "treemap",
                    "data": tree_data,
                    "leafDepth": 1,
                    "label": {"show": True, "formatter": "{b}"},
                    "upperLabel": {"show": True, "height": 30},
                }
            ],
            "tooltip": {"formatter": "{b}: {c}"},
        }

    def to_gauge_format(
        self, df: pd.DataFrame, value_column: str, max_value: float = None
    ) -> Dict:
        # Formato para gauge (medidor)
        value = df[value_column].iloc[0] if len(df) > 0 else 0

        if max_value is None:
            max_value = df[value_column].max() * 1.2

        return {
            "series": [
                {
                    "type": "gauge",
                    "detail": {"formatter": "{value}"},
                    "data": [{"value": float(value), "name": value_column}],
                    "max": max_value,
                }
            ]
        }

    def to_funnel_format(
        self, df: pd.DataFrame, label_column: str, value_column: str
    ) -> Dict:
        # Formato para funnel (embudo)
        data = [
            {"value": row[value_column], "name": row[label_column]}
            for _, row in df.iterrows()
        ]

        return {
            "series": [
                {
                    "type": "funnel",
                    "data": data,
                    "label": {"show": True, "position": "inside"},
                }
            ],
            "tooltip": {"trigger": "item", "formatter": "{b}: {c}"},
        }

    def to_sankey_format(
        self, df: pd.DataFrame, source: str, target: str, value: str
    ) -> Dict:
        # Formato para sankey (flujo)
        # Obtener nodos únicos
        nodes = set(df[source].tolist() + df[target].tolist())
        nodes_list = [{"name": node} for node in nodes]

        # Crear links
        links = [
            {"source": row[source], "target": row[target], "value": row[value]}
            for _, row in df.iterrows()
        ]

        return {
            "series": [
                {"type": "sankey", "data": nodes_list, "links": links, "layout": "none"}
            ],
            "tooltip": {"trigger": "item"},
        }
