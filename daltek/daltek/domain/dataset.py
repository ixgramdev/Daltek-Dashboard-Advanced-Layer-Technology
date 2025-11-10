# daltek/domain/dataset.py

import pandas as pd


class Dataset:
    """
    Clase base para manejar datos de un dashboard.
    Puede inicializarse desde listas de dicts, pandas DataFrame, o resultados de consultas.
    """

    def __init__(self, data):
        """
        data: lista de dicts o DataFrame
        """
        if isinstance(data, pd.DataFrame):
            self.df = data.copy()
        elif isinstance(data, list):
            self.df = pd.DataFrame(data)
        else:
            raise ValueError("Dataset: data debe ser una lista de dicts o DataFrame")

    def head(self, n=5):
        """Primeras n filas"""
        return self.df.head(n)

    def columns(self):
        """Lista de columnas"""
        return self.df.columns.tolist()

    def filter_rows(self, **conditions):
        """
        Filtra filas según condiciones.
        Ejemplo: ds.filter_rows(status='active', type='premium')
        """
        df_filtered = self.df.copy()
        for col, val in conditions.items():
            df_filtered = df_filtered[df_filtered[col] == val]
        return Dataset(df_filtered)

    def select_columns(self, *cols):
        """Selecciona columnas específicas"""
        return Dataset(self.df[list(cols)])

    def group_by(self, by, agg=None):
        """
        Agrupa por una columna o lista de columnas.
        agg: dict {'col': 'sum'} o lista de funciones
        """
        grouped = self.df.groupby(by).agg(agg or {})
        grouped = grouped.reset_index()
        return Dataset(grouped)

    def pivot(self, index, columns, values, aggfunc="sum"):
        """Crea tabla pivote"""
        pivoted = pd.pivot_table(
            self.df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0,
        ).reset_index()
        return Dataset(pivoted)

    def describe(self):
        """Estadísticas básicas de columnas numéricas"""
        return self.df.describe()

    def to_dict(self, orient="records"):
        """Devuelve los datos en formato lista de dicts"""
        return self.df.to_dict(orient=orient)

    def sort_by(self, column, ascending=True):
        """Ordena por columna"""
        return Dataset(self.df.sort_values(by=column, ascending=ascending))
