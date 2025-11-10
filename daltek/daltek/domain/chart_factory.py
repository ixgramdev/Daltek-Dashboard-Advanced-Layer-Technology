# daltek/domain/chart_factory.py

# Clases base de charts
class ChartBase:
    def __init__(self, dataset, x, y, title=None, color=None, style=None):
        self.dataset = dataset
        self.x = x
        self.y = y
        self.title = title or ""
        self.color = color or "blue"
        self.style = style or {}

    def render(self):
        raise NotImplementedError("Render debe implementarse en subclases")


# Subclases específicas
class BarChart(ChartBase):
    def render(self):
        return {
            "type": "bar",
            "x": self.dataset.df[self.x].tolist(),
            "y": self.dataset.df[self.y].tolist(),
            "name": self.title,
            "marker": {
                "color": self.color,
                **self.style,
            },
        }


class PieChart(ChartBase):
    def render(self):
        colors = self.color
        if not isinstance(colors, list):
            colors = [colors] * len(self.dataset.df)
        return {
            "type": "pie",
            "labels": self.dataset.df[self.x].tolist(),
            "values": self.dataset.df[self.y].tolist(),
            "name": self.title,
            "marker": {
                "colors": colors,
                **self.style,
            },
        }


# Fábrica
class ChartFactory:
    """
    Fábrica para crear charts. Valida tipo, columnas, colores y estilo.
    """

    CHART_TYPES = {
        "bar": BarChart,
        "pie": PieChart,
        # Se pueden agregar más tipos: "line": LineChart, etc.
    }

    @staticmethod
    def create_chart(chart_type, dataset, x, y, title=None, color=None, style=None):
        # Validar tipo
        ChartCls = ChartFactory.CHART_TYPES.get(chart_type.lower())
        if not ChartCls:
            raise ValueError(f"Tipo de chart '{chart_type}' no soportado")

        # Validar columnas
        for col in [x, y]:
            if col not in dataset.df.columns:
                raise ValueError(f"Columna '{col}' no existe en el dataset")

        # Validar color
        if isinstance(color, list) and len(color) != len(dataset.df):
            raise ValueError(
                "Lista de colores debe coincidir con el número de filas del dataset"
            )

        # Validar estilo
        if style and not isinstance(style, dict):
            raise ValueError("style debe ser un dict con propiedades CSS/Plotly")

        # Crear instancia del chart
        return ChartCls(dataset, x, y, title=title, color=color, style=style)
