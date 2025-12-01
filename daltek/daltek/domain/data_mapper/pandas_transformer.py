# PandasTransformer: Motor de transformaciones usando Pandas

import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union
from datetime import datetime


class PandasTransformer:
    # Utiliza Pandas para transformaciones avanzadas de datos

    def __init__(self):
        self.df = None

    def load_data(self, data: List[Dict]) -> pd.DataFrame:
        # Carga datos en DataFrame
        self.df = pd.DataFrame(data)
        return self.df

    def aggregate(self, df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        # Agregación: SUM, AVG, COUNT, MIN, MAX, etc.
        group_by = config.get("group_by", [])
        aggregations = config.get("aggregations", {})

        if not group_by:
            # Agregación sin agrupar (totales globales)
            agg_dict = {}
            for alias, agg_config in aggregations.items():
                col = agg_config["column"]
                func = agg_config["func"]
                agg_dict[alias] = df[col].agg(func)

            result = pd.DataFrame([agg_dict])
            return result

        # Agrupar y agregar
        agg_dict = {}
        for alias, agg_config in aggregations.items():
            col = agg_config["column"]
            func = agg_config["func"]
            agg_dict[col] = func

        result = df.groupby(group_by, as_index=False).agg(agg_dict)

        # Renombrar columnas según alias
        rename_map = {}
        for alias, agg_config in aggregations.items():
            col = agg_config["column"]
            rename_map[col] = alias

        result = result.rename(columns=rename_map)

        return result

    def filter(self, df: pd.DataFrame, conditions: List[Dict]) -> pd.DataFrame:
        # Filtros dinámicos (>, <, in, between, contains, etc.)
        if not conditions:
            return df

        result = df.copy()

        for condition in conditions:
            col = condition["column"]
            operator = condition["operator"]
            value = condition["value"]

            if operator == "=":
                result = result[result[col] == value]
            elif operator == "!=":
                result = result[result[col] != value]
            elif operator == ">":
                result = result[result[col] > value]
            elif operator == ">=":
                result = result[result[col] >= value]
            elif operator == "<":
                result = result[result[col] < value]
            elif operator == "<=":
                result = result[result[col] <= value]
            elif operator == "between":
                result = result[
                    (result[col] >= value[0]) & (result[col] <= value[1])
                ]
            elif operator == "in":
                result = result[result[col].isin(value)]
            elif operator == "not_in":
                result = result[~result[col].isin(value)]
            elif operator == "contains":
                result = result[result[col].str.contains(value, na=False)]
            elif operator == "not_contains":
                result = result[~result[col].str.contains(value, na=False)]
            elif operator == "starts_with":
                result = result[result[col].str.startswith(value, na=False)]
            elif operator == "ends_with":
                result = result[result[col].str.endswith(value, na=False)]
            elif operator == "is_null":
                result = result[result[col].isna()]
            elif operator == "is_not_null":
                result = result[result[col].notna()]

        return result

    def pivot(
        self,
        df: pd.DataFrame,
        index: str,
        columns: str,
        values: str,
        aggfunc: str = "sum",
    ) -> pd.DataFrame:
        # Tabla pivote
        result = pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0,
        ).reset_index()

        # Aplanar nombres de columnas multi-nivel
        result.columns = [str(col) for col in result.columns]

        return result

    def sort(
        self, df: pd.DataFrame, columns: Union[str, List[str]], ascending: bool = True
    ) -> pd.DataFrame:
        # Ordenamiento (ascendente o descendente)
        if isinstance(columns, str):
            columns = [columns]

        return df.sort_values(by=columns, ascending=ascending).reset_index(drop=True)

    def calculate(self, df: pd.DataFrame, calculations: Dict) -> pd.DataFrame:
        # Columnas calculadas con fórmulas
        result = df.copy()

        for col_name, calc_config in calculations.items():
            formula = calc_config.get("formula")

            if not formula:
                continue

            try:
                # Evaluar fórmula en contexto del DataFrame
                result[col_name] = eval(
                    formula, {"__builtins__": {}}, {"df": result, **result.to_dict()}
                )
            except Exception as e:
                print(f"Error calculando columna {col_name}: {str(e)}")
                continue

        return result

    def format_values(self, df: pd.DataFrame, formats: Dict) -> pd.DataFrame:
        # Formateo de valores (currency, date, percentage, number)
        result = df.copy()

        for col, fmt in formats.items():
            if col not in result.columns:
                continue

            fmt_type = fmt.get("type")

            if fmt_type == "currency":
                decimals = fmt.get("decimals", 2)
                result[col] = result[col].apply(
                    lambda x: f"${x:,.{decimals}f}" if pd.notna(x) else ""
                )
            elif fmt_type == "percentage":
                decimals = fmt.get("decimals", 1)
                result[col] = result[col].apply(
                    lambda x: f"{x:.{decimals}f}%" if pd.notna(x) else ""
                )
            elif fmt_type == "date":
                date_format = fmt.get("format", "%Y-%m-%d")
                result[col] = pd.to_datetime(result[col]).dt.strftime(date_format)
            elif fmt_type == "number":
                decimals = fmt.get("decimals", 0)
                result[col] = result[col].apply(
                    lambda x: f"{x:,.{decimals}f}" if pd.notna(x) else ""
                )

        return result

    def resample_time_series(
        self, df: pd.DataFrame, date_column: str, freq: str, agg: str = "sum"
    ) -> pd.DataFrame:
        # Resampleo de series temporales (D, W, M, Q, Y)
        result = df.copy()
        result[date_column] = pd.to_datetime(result[date_column])
        result = result.set_index(date_column)

        # Resamplear
        numeric_cols = result.select_dtypes(include=[np.number]).columns
        result = result[numeric_cols].resample(freq).agg(agg).reset_index()

        return result

    def rolling_window(
        self, df: pd.DataFrame, column: str, window: int, func: str = "mean"
    ) -> pd.DataFrame:
        # Ventanas deslizantes (media móvil)
        result = df.copy()
        col_name = f"{column}_{func}_{window}"

        if func == "mean":
            result[col_name] = result[column].rolling(window=window).mean()
        elif func == "sum":
            result[col_name] = result[column].rolling(window=window).sum()
        elif func == "min":
            result[col_name] = result[column].rolling(window=window).min()
        elif func == "max":
            result[col_name] = result[column].rolling(window=window).max()
        elif func == "std":
            result[col_name] = result[column].rolling(window=window).std()

        return result

    def top_n(
        self, df: pd.DataFrame, column: str, n: int = 10, ascending: bool = False
    ) -> pd.DataFrame:
        # Top N registros
        return df.nlargest(n, column) if not ascending else df.nsmallest(n, column)

    def merge_queries(
        self, df1: pd.DataFrame, df2: pd.DataFrame, on: str, how: str = "inner"
    ) -> pd.DataFrame:
        # Combinar resultados de múltiples queries
        return pd.merge(df1, df2, on=on, how=how)

    def add_cumulative(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        # Suma acumulada
        result = df.copy()
        result[f"{column}_cumsum"] = result[column].cumsum()
        return result

    def add_percentage_change(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        # Cambio porcentual entre filas consecutivas
        result = df.copy()
        result[f"{column}_pct_change"] = result[column].pct_change() * 100
        return result

    def add_rank(self, df: pd.DataFrame, column: str, ascending: bool = False) -> pd.DataFrame:
        # Añadir ranking
        result = df.copy()
        result[f"{column}_rank"] = result[column].rank(ascending=ascending, method="dense")
        return result

    def bin_values(
        self, df: pd.DataFrame, column: str, bins: int = 5, labels: List = None
    ) -> pd.DataFrame:
        # Agrupar valores en bins (categorías)
        result = df.copy()
        result[f"{column}_bin"] = pd.cut(result[column], bins=bins, labels=labels)
        return result
