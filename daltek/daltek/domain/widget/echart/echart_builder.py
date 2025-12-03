"""
Implementaciones específicas de builders para diferentes tipos de ECharts.

Cada builder maneja la lógica particular de su tipo de gráfico.
"""

from typing import Any

from .base_echart_builder import BaseEChartBuilder
from .echart_factory import EChartFactory


class LineChartBuilder(BaseEChartBuilder):
    """Builder para gráficos de líneas."""

    def __init__(self):
        super().__init__()
        self.chart_type = "line"

    def get_chart_type(self) -> str:
        return "line"

    def _validate_data(self) -> bool:
        """Valida estructura de datos para línea."""
        # Validar que exista 'series'
        if "series" not in self.data:
            self._add_error("Falta campo 'series' en datos")
            return False

        series = self.data["series"]

        # Debe ser una lista
        if not isinstance(series, list) or len(series) == 0:
            self._add_error("'series' debe ser una lista no vacía")
            return False

        # Validar estructura de cada serie
        for i, serie in enumerate(series):
            if not isinstance(serie, dict):
                self._add_error(f"Serie {i} debe ser un diccionario")
                return False

            if "name" not in serie:
                self._add_error(f"Serie {i} sin campo 'name'")
                return False

            if "data" not in serie:
                self._add_error(f"Serie {i} sin campo 'data'")
                return False

            # Validar que 'data' sea una lista de números
            data = serie["data"]
            if not isinstance(data, list) or len(data) == 0:
                self._add_error(
                    f"Serie '{serie['name']}' tiene 'data' vacía o inválida"
                )
                return False

            for j, value in enumerate(data):
                if not self.validate_numeric_data(value):
                    self._add_error(
                        f"Serie '{serie['name']}' posición {j}: valor '{value}' no es numérico"
                    )
                    return False

        # Validar que exista 'categories' (eje X)
        if "categories" not in self.data:
            self._add_error("Falta campo 'categories' en datos")
            return False

        categories = self.data["categories"]
        if not isinstance(categories, list) or len(categories) == 0:
            self._add_error("'categories' debe ser una lista no vacía")
            return False

        # Validar que cantidad de categorías coincida con datos
        if len(categories) != len(series[0]["data"]):
            self._add_error(
                f"Cantidad de categorías ({len(categories)}) no coincide "
                f"con datos en series ({len(series[0]['data'])})"
            )
            return False

        return True

    def _build_series(self) -> list[dict[str, Any]] | None:
        """Construye array de series para línea."""
        try:
            series_list = []
            for serie in self.data["series"]:
                echart_serie = {
                    "name": self._normalize_series_name(serie["name"]),
                    "data": [self.ensure_numeric(v) for v in serie["data"]],
                    "type": "line",
                    "smooth": self.config.get("smooth", True),
                    "symbol": self.config.get("symbol", "circle"),
                    "symbolSize": self.config.get("symbolSize", 4),
                }

                # Agregar área bajo la línea si está configurado
                if self.config.get("fill_area"):
                    echart_serie["areaStyle"] = {"opacity": 0.3}

                series_list.append(echart_serie)

            return series_list

        except Exception as e:
            self._add_error(f"Error construyendo series: {str(e)}")
            return None

    def _should_have_xaxis(self) -> bool:
        return True

    def _should_have_yaxis(self) -> bool:
        return True

    def _build_xaxis(self) -> dict[str, Any] | None:
        """Construye eje X con categorías."""
        return {
            "type": "category",
            "data": self.data.get("categories", []),
            "boundaryGap": False,
        }

    def _build_yaxis(self) -> dict[str, Any] | None:
        """Construye eje Y."""
        yaxis = {
            "type": "value",
            "name": self.config.get("yaxis_name", ""),
        }

        # Valores mín/máx si están configurados
        if "min" in self.config:
            yaxis["min"] = self.ensure_numeric(self.config["min"])
        if "max" in self.config:
            yaxis["max"] = self.ensure_numeric(self.config["max"])

        return yaxis


class BarChartBuilder(BaseEChartBuilder):
    """Builder para gráficos de barras."""

    def __init__(self):
        super().__init__()
        self.chart_type = "bar"

    def get_chart_type(self) -> str:
        return "bar"

    def _validate_data(self) -> bool:
        """Valida estructura de datos para barras."""
        # Similar a LineChart
        if "series" not in self.data:
            self._add_error("Falta campo 'series' en datos")
            return False

        series = self.data["series"]

        if not isinstance(series, list) or len(series) == 0:
            self._add_error("'series' debe ser una lista no vacía")
            return False

        for i, serie in enumerate(series):
            if not isinstance(serie, dict):
                self._add_error(f"Serie {i} debe ser un diccionario")
                return False

            if "name" not in serie or "data" not in serie:
                self._add_error(f"Serie {i} incompleta (name y data requeridos)")
                return False

            data = serie["data"]
            if not isinstance(data, list) or len(data) == 0:
                self._add_error(f"Serie '{serie['name']}' tiene 'data' vacía")
                return False

            for j, value in enumerate(data):
                if not self.validate_numeric_data(value):
                    self._add_error(
                        f"Serie '{serie['name']}' posición {j}: valor no numérico"
                    )
                    return False

        if "categories" not in self.data:
            self._add_error("Falta campo 'categories'")
            return False

        return True

    def _build_series(self) -> list[dict[str, Any]] | None:
        """Construye array de series para barras."""
        try:
            series_list = []
            for serie in self.data["series"]:
                echart_serie = {
                    "name": self._normalize_series_name(serie["name"]),
                    "data": [self.ensure_numeric(v) for v in serie["data"]],
                    "type": "bar",
                    "barWidth": self.config.get("barWidth", "60%"),
                }

                series_list.append(echart_serie)

            return series_list

        except Exception as e:
            self._add_error(f"Error construyendo series: {str(e)}")
            return None

    def _should_have_xaxis(self) -> bool:
        return True

    def _should_have_yaxis(self) -> bool:
        return True

    def _build_xaxis(self) -> dict[str, Any] | None:
        """Construye eje X."""
        return {
            "type": "category",
            "data": self.data.get("categories", []),
        }

    def _build_yaxis(self) -> dict[str, Any] | None:
        """Construye eje Y."""
        return {"type": "value"}


class PieChartBuilder(BaseEChartBuilder):
    """Builder para gráficos circulares (pie)."""

    def __init__(self):
        super().__init__()
        self.chart_type = "pie"

    def get_chart_type(self) -> str:
        return "pie"

    def _validate_data(self) -> bool:
        """Valida estructura de datos para pie."""
        if "data" not in self.data:
            self._add_error("Falta campo 'data'")
            return False

        data = self.data["data"]

        if not isinstance(data, list) or len(data) == 0:
            self._add_error("'data' debe ser una lista no vacía")
            return False

        # Cada elemento debe tener 'name' y 'value'
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                self._add_error(f"Elemento {i} debe ser un diccionario")
                return False

            if "name" not in item or "value" not in item:
                self._add_error(f"Elemento {i} incompleto (name y value requeridos)")
                return False

            if not self.validate_numeric_data(item["value"]):
                self._add_error(f"Elemento '{item['name']}': value no es numérico")
                return False

        return True

    def _build_series(self) -> list[dict[str, Any]] | None:
        """Construye array de series para pie."""
        try:
            data = []
            for item in self.data["data"]:
                data.append(
                    {
                        "name": item["name"],
                        "value": self.ensure_numeric(item["value"]),
                    }
                )

            serie = {
                "name": self.config.get("name", "Distribution"),
                "type": "pie",
                "radius": self.config.get("radius", "50%"),
                "data": data,
                "emphasis": {"itemStyle": {"shadowBlur": 10, "shadowOffsetX": 0}},
            }

            # Mostrar etiquetas
            if self.config.get("show_labels"):
                serie["label"] = {
                    "formatter": "{b}: {c} ({d}%)",
                    "position": "outside",
                }

            return [serie]

        except Exception as e:
            self._add_error(f"Error construyendo series: {str(e)}")
            return None

    def _should_have_xaxis(self) -> bool:
        return False

    def _should_have_yaxis(self) -> bool:
        return False

    def _build_base_config(self) -> dict[str, Any]:
        """Sobreescribe config base para pie (sin grid)."""
        return {
            "tooltip": {"trigger": "item"},
            "legend": {
                "data": self._get_legend_data(),
                "orient": "vertical",
                "left": "left",
            },
        }

    def _get_legend_data(self) -> list[str]:
        """Extrae nombres para leyenda desde data."""
        return [item.get("name", "") for item in self.data.get("data", [])]


class ScatterChartBuilder(BaseEChartBuilder):
    """Builder para gráficos de dispersión."""

    def __init__(self):
        super().__init__()
        self.chart_type = "scatter"

    def get_chart_type(self) -> str:
        return "scatter"

    def _validate_data(self) -> bool:
        """Valida estructura de datos para scatter."""
        if "series" not in self.data:
            self._add_error("Falta campo 'series'")
            return False

        series = self.data["series"]

        if not isinstance(series, list) or len(series) == 0:
            self._add_error("'series' debe ser lista no vacía")
            return False

        for i, serie in enumerate(series):
            if not isinstance(serie, dict):
                self._add_error(f"Serie {i} debe ser diccionario")
                return False

            if "name" not in serie or "data" not in serie:
                self._add_error(f"Serie {i} incompleta")
                return False

            data = serie["data"]
            if not isinstance(data, list):
                self._add_error(f"Serie '{serie['name']}' data debe ser lista")
                return False

            # En scatter, cada punto es [x, y]
            for j, point in enumerate(data):
                if not isinstance(point, (list, tuple)) or len(point) < 2:
                    self._add_error(
                        f"Serie '{serie['name']}' punto {j}: debe ser [x, y]"
                    )
                    return False

                if not (
                    self.validate_numeric_data(point[0])
                    and self.validate_numeric_data(point[1])
                ):
                    self._add_error(
                        f"Serie '{serie['name']}' punto {j}: valores no numéricos"
                    )
                    return False

        return True

    def _build_series(self) -> list[dict[str, Any]] | None:
        """Construye array de series para scatter."""
        try:
            series_list = []
            for serie in self.data["series"]:
                echart_serie = {
                    "name": self._normalize_series_name(serie["name"]),
                    "data": [
                        [self.ensure_numeric(p[0]), self.ensure_numeric(p[1])]
                        for p in serie["data"]
                    ],
                    "type": "scatter",
                    "symbolSize": self.config.get("symbolSize", 8),
                }

                series_list.append(echart_serie)

            return series_list

        except Exception as e:
            self._add_error(f"Error construyendo series: {str(e)}")
            return None

    def _should_have_xaxis(self) -> bool:
        return True

    def _should_have_yaxis(self) -> bool:
        return True

    def _build_xaxis(self) -> dict[str, Any] | None:
        """Construye eje X."""
        return {
            "type": "value",
            "name": self.config.get("xaxis_name", "X"),
        }

    def _build_yaxis(self) -> dict[str, Any] | None:
        """Construye eje Y."""
        return {
            "type": "value",
            "name": self.config.get("yaxis_name", "Y"),
        }


# --- REGISTRO AUTOMÁTICO DE BUILDERS ---

# Registrar todos los builders en el factory
EChartFactory.register("line", LineChartBuilder)
EChartFactory.register("bar", BarChartBuilder)
EChartFactory.register("pie", PieChartBuilder)
EChartFactory.register("scatter", ScatterChartBuilder)
