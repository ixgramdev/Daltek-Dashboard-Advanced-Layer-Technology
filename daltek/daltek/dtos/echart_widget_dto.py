"""
DTO especializado para widgets EChart en formato normalizado ÚNICO.

Estructura:
{
    "id": "widget_1_xxx",
    "type": "echart",
    "label": "Mi Gráfico",
    "metadata": { "created_at": "...", "modified_at": "...", "version": 1 },
    "layout": { "x": 0, "y": 0, "width": 6, "height": 4 },
    "properties": { "title": "Ventas", ... },
    "content": {
        "type": "echart",
        "chart_type": "line",
        "data": { "series": [...], "categories": [...] },
        "config": { "xAxis": {...}, "yAxis": {...}, "series": [...] }
    }
}
"""

from dataclasses import dataclass, field
from typing import Any

from .widget_dto import WidgetDTO


@dataclass
class EChartWidgetDTO(WidgetDTO):
    """
    DTO para widgets EChart en formato normalizado único.

    Attributes:
        chart_type: Tipo de gráfico ('line', 'bar', 'pie', 'scatter', 'gauge', etc)
        echart_data: Datos del gráfico
        echart_config: Configuración del gráfico
    """

    chart_type: str = ""
    echart_data: dict[str, Any] = field(default_factory=dict)
    echart_config: dict[str, Any] = field(default_factory=dict)

    # Dimensiones mínimas específicas para EChart
    MIN_DIMENSIONS = {
        "echart": {
            "min_width": 6,
            "min_height": 4,
            "default_width": 8,
            "default_height": 6,
        },
        "line": {
            "min_width": 6,
            "min_height": 4,
            "default_width": 8,
            "default_height": 6,
        },
        "bar": {
            "min_width": 6,
            "min_height": 4,
            "default_width": 8,
            "default_height": 6,
        },
        "pie": {
            "min_width": 5,
            "min_height": 5,
            "default_width": 6,
            "default_height": 6,
        },
        "scatter": {
            "min_width": 6,
            "min_height": 4,
            "default_width": 8,
            "default_height": 6,
        },
        "gauge": {
            "min_width": 4,
            "min_height": 4,
            "default_width": 5,
            "default_height": 5,
        },
        "candlestick": {
            "min_width": 6,
            "min_height": 4,
            "default_width": 10,
            "default_height": 6,
        },
        "heatmap": {
            "min_width": 6,
            "min_height": 5,
            "default_width": 8,
            "default_height": 6,
        },
    }

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte a diccionario en formato normalizado (ÚNICO formato).

        Returns:
            Dict con estructura normalizada, content incluye EChart-specific data
        """
        base_dict = super().to_dict()

        # Aplicar dimensiones mínimas específicas para EChart según chart_type
        min_dims = self.MIN_DIMENSIONS.get(
            self.chart_type,
            self.MIN_DIMENSIONS.get(
                "echart",
                {
                    "min_width": 6,
                    "min_height": 4,
                    "default_width": 8,
                    "default_height": 6,
                },
            ),
        )

        # Asegurar que width y height cumplan con mínimos del chart_type
        width = max(self.position.get("width", 8), min_dims.get("default_width", 8))
        height = max(self.position.get("height", 6), min_dims.get("default_height", 6))

        base_dict["layout"]["width"] = width
        base_dict["layout"]["height"] = height
        base_dict["layout"]["min_width"] = min_dims.get("min_width", 6)
        base_dict["layout"]["min_height"] = min_dims.get("min_height", 4)

        base_dict["content"].update(
            {
                "type": "echart",
                "chart_type": self.chart_type,
                "data": self.echart_data,
                "config": self.echart_config,
            }
        )

        return base_dict

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EChartWidgetDTO":
        """
        Crea instancia desde diccionario en formato normalizado.

        Args:
            data: Dict con estructura normalizado o formato DTO del frontend

        Returns:
            Instancia de EChartWidgetDTO
        """
        metadata = data.get("metadata", {})
        layout = data.get("layout", {})
        content = data.get("content", {})

        # chart_type puede estar en el nivel raíz (del frontend) o en content (normalizado)
        chart_type = data.get("chart_type") or content.get("chart_type", "")

        # echart_data puede estar en el nivel raíz (del frontend) o en content.data (normalizado)
        echart_data = data.get("echart_data") or content.get("data", {})

        # echart_config puede estar en el nivel raíz (del frontend) o en content.config (normalizado)
        echart_config = data.get("echart_config") or content.get("config", {})

        return cls(
            id=data.get("id"),
            type=data.get("type", "echart"),
            properties=data.get("properties", {}),
            created_at=metadata.get("created_at") or data.get("created_at"),
            modified_at=metadata.get("modified_at") or data.get("modified_at"),
            position=data.get("position")
            or {
                "x": layout.get("x", 0),
                "y": layout.get("y", 0),
                "width": layout.get("width", 6),
                "height": layout.get("height", 4),
                "min_width": layout.get("min_width", 4),
                "min_height": layout.get("min_height", 3),
            },
            label=data.get("label", ""),
            chart_type=chart_type,
            echart_data=echart_data,
            echart_config=echart_config,
        )

    def get_chart_config_for_render(self) -> dict[str, Any]:
        """
        Obtiene la configuración del EChart para renderizar.

        Returns:
            Dict con estructura normalizada lista para renderizar
        """
        return self.to_dict()

    def update_chart_data(self, new_data: dict[str, Any]) -> None:
        """Actualiza los datos del gráfico."""
        self.echart_data.update(new_data)

    def update_chart_config(self, new_config: dict[str, Any]) -> None:
        """Actualiza la configuración del gráfico."""
        self.echart_config.update(new_config)
