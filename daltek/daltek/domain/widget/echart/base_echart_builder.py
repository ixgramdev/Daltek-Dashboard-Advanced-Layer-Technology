"""
Base abstracta para construcción de ECharts.

Define la interfaz común que todos los builders de EChart deben implementar.
Utiliza el patrón Strategy para permitir diferentes estrategias de construcción.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseEChartBuilder(ABC):
    """
    Clase abstracta que define el contrato para todos los builders de EChart.

    Responsabilidades:
    - Validar datos de entrada
    - Construir configuración específica del tipo de chart
    - Normalizar datos para echarts.js
    - Generar opciones de renderización
    """

    def __init__(self):
        """Inicializa el builder base."""
        self.chart_type: str = ""
        self.data: dict[str, Any] = {}
        self.config: dict[str, Any] = {}
        self.errors: list[str] = []

    # --- MÉTODOS PÚBLICOS (Template Method Pattern) ---

    def build(self, data: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        """
        Método principal que orquesta el proceso de construcción.
        Implementa el Template Method Pattern.

        Args:
            data: Datos del chart (series, categories, etc)
            config: Configuración visual (colors, legend, tooltips, etc)

        Returns:
            Dict con la configuración completa del EChart listo para renderizar
        """
        self.data = data
        self.config = config
        self.errors = []

        # 1. Validar datos
        if not self._validate_data():
            return {
                "success": False,
                "error": f"Validación fallida: {'; '.join(self.errors)}",
                "chart_type": self.chart_type,
            }

        # 2. Construir configuración base
        echart_config = self._build_base_config()

        # 3. Construir series (datos)
        series = self._build_series()
        if series is None:
            return {
                "success": False,
                "error": f"Error construyendo series: {'; '.join(self.errors)}",
                "chart_type": self.chart_type,
            }
        echart_config["series"] = series

        # 4. Construir X-Axis (si aplica)
        if self._should_have_xaxis():
            xaxis = self._build_xaxis()
            if xaxis:
                echart_config["xAxis"] = xaxis

        # 5. Construir Y-Axis (si aplica)
        if self._should_have_yaxis():
            yaxis = self._build_yaxis()
            if yaxis:
                echart_config["yAxis"] = yaxis

        # 6. Construir opciones visuales (tooltip, legend, color, etc)
        echart_config.update(self._build_options())

        return {
            "success": True,
            "chart_type": self.chart_type,
            "data": data,
            "config": echart_config,
        }

    # --- MÉTODOS ABSTRACTOS (deben implementarse en subclases) ---

    @abstractmethod
    def _validate_data(self) -> bool:
        """
        Valida que los datos cumplan con los requisitos del chart.
        Debe llenar self.errors con mensajes descriptivos.

        Returns:
            True si validación pasa, False si falla
        """
        pass

    @abstractmethod
    def _build_series(self) -> list[dict[str, Any]] | None:
        """
        Construye el array de series para echarts.

        Returns:
            List de series o None si hay error
        """
        pass

    @abstractmethod
    def get_chart_type(self) -> str:
        """
        Retorna el tipo de chart (line, bar, pie, scatter, etc).

        Returns:
            String con el tipo de chart
        """
        pass

    # --- MÉTODOS TEMPLATE (pueden ser sobrescritos en subclases) ---

    def _build_base_config(self) -> dict[str, Any]:
        """
        Construye la configuración base común a todos los charts.

        Returns:
            Dict con config base
        """
        return {
            "tooltip": {"trigger": "axis"},
            "legend": {"data": self._get_legend_data()},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        }

    def _build_options(self) -> dict[str, Any]:
        """
        Construye opciones visuales (colores, fondos, etc).

        Returns:
            Dict con opciones visuales
        """
        options = {}

        # Colores
        if "colors" in self.config:
            options["color"] = self.config["colors"]
        else:
            options["color"] = self._get_default_colors()

        # Title
        if "title" in self.config:
            options["title"] = {
                "text": self.config["title"],
                "left": "center",
            }

        # Legend
        if "legend_position" in self.config:
            options["legend"] = options.get("legend", {})
            options["legend"]["orient"] = self.config["legend_position"]

        return options

    def _build_xaxis(self) -> dict[str, Any] | None:
        """
        Construye el eje X. Por defecto retorna None.
        Sobrescribir en subclases que necesiten X-Axis.

        Returns:
            Dict con config del xAxis o None
        """
        return None

    def _build_yaxis(self) -> dict[str, Any] | None:
        """
        Construye el eje Y. Por defecto retorna None.
        Sobrescribir en subclases que necesiten Y-Axis.

        Returns:
            Dict con config del yAxis o None
        """
        return None

    def _should_have_xaxis(self) -> bool:
        """Retorna True si el chart debe tener eje X."""
        return False

    def _should_have_yaxis(self) -> bool:
        """Retorna True si el chart debe tener eje Y."""
        return False

    # --- MÉTODOS HELPERS ---

    def _get_legend_data(self) -> list[str]:
        """
        Extrae las series para mostrar en la leyenda.

        Returns:
            Lista de nombres de series
        """
        series_names = self.data.get("series", [])

        if isinstance(series_names, list):
            # Si es lista de dicts {name: "", data: []}
            if series_names and isinstance(series_names[0], dict):
                return [s.get("name", "") for s in series_names]
            # Si es lista simple de nombres
            else:
                return series_names

        return []

    def _get_default_colors(self) -> list[str]:
        """
        Retorna paleta de colores por defecto.

        Returns:
            Lista de colores en formato hex
        """
        return [
            "#2196F3",  # Blue
            "#4CAF50",  # Green
            "#FF9800",  # Orange
            "#F44336",  # Red
            "#9C27B0",  # Purple
            "#00BCD4",  # Cyan
            "#FFEB3B",  # Yellow
            "#795548",  # Brown
        ]

    def _normalize_series_name(self, name: str) -> str:
        """
        Normaliza nombre de serie (elimina espacios, caracteres especiales).

        Args:
            name: Nombre original

        Returns:
            Nombre normalizado
        """
        return name.strip() if isinstance(name, str) else str(name)

    def _add_error(self, message: str) -> None:
        """
        Añade un mensaje de error a la lista de errores.

        Args:
            message: Mensaje de error
        """
        if message not in self.errors:
            self.errors.append(message)

    def _has_errors(self) -> bool:
        """Retorna True si hay errores."""
        return len(self.errors) > 0

    # --- MÉTODOS DE UTILIDAD ---

    @staticmethod
    def validate_numeric_data(value: Any) -> bool:
        """
        Valida que un valor sea numérico.

        Args:
            value: Valor a validar

        Returns:
            True si es numérico
        """
        try:
            float(value)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def ensure_numeric(value: Any, default: float = 0) -> float:
        """
        Convierte un valor a número o retorna default.

        Args:
            value: Valor a convertir
            default: Valor por defecto

        Returns:
            Valor numérico
        """
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
