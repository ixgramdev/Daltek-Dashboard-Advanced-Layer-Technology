"""
DTO especializado para widgets EChart.

Define la estructura de datos para transferir información de gráficos EChart
entre capas de la aplicación. Hereda de WidgetDTO.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

from .widget_dto import WidgetDTO


@dataclass
class EChartWidgetDTO(WidgetDTO):
    """
    DTO especializado para widgets EChart.

    Hereda de WidgetDTO y añade propiedades específicas para gráficos EChart.

    Attributes:
        chart_type: Tipo de gráfico (e.g., 'line', 'bar', 'pie', 'scatter')
        echart_data: Datos del gráfico en formato EChart
        echart_config: Configuración del gráfico en formato EChart
    """

    chart_type: str = ""
    echart_data: dict[str, Any] = field(default_factory=dict)
    echart_config: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el DTO a diccionario.

        Returns:
            Representación en diccionario del DTO
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EChartWidgetDTO":
        """
        Crea una instancia del DTO desde un diccionario.

        Args:
            data: Diccionario con los datos del widget EChart

        Returns:
            Instancia de EChartWidgetDTO

        Raises:
            KeyError: Si faltan campos requeridos
        """
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "echart"),
            properties=data.get("properties", {}),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            position=data.get("position", {"x": 0, "y": 0}),
            chart_type=data.get("chart_type", ""),
            echart_data=data.get("echart_data", {}),
            echart_config=data.get("echart_config", {}),
        )

    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida el DTO de EChart.

        Valida tanto las propiedades base como las específicas de EChart.

        Returns:
            Tupla (es_válido, lista_de_errores)
        """
        # Validar propiedades base
        is_valid, errors = super().validate()

        # Validaciones específicas de EChart
        if not self.chart_type or not isinstance(self.chart_type, str):
            errors.append("chart_type debe ser un string no vacío")

        if not isinstance(self.echart_data, dict):
            errors.append("echart_data debe ser un diccionario")

        if not isinstance(self.echart_config, dict):
            errors.append("echart_config debe ser un diccionario")

        if self.type != "echart":
            errors.append(f"Type debe ser 'echart', recibió '{self.type}'")

        return len(errors) == 0, errors

    def get_chart_config_for_render(self) -> dict[str, Any]:
        """
        Obtiene la configuración del chart lista para renderizar.

        Prepara la configuración en el formato esperado por echarts.js.

        Returns:
            Configuración del EChart para echarts.js
        """
        return {
            "id": self.id,
            "type": self.chart_type,
            "config": self.echart_config,
            "data": self.echart_data,
            "properties": self.properties,
        }

    def update_chart_data(self, new_data: dict[str, Any]) -> None:
        """
        Actualiza los datos del gráfico.

        Args:
            new_data: Nuevos datos en formato EChart
        """
        self.echart_data.update(new_data)

    def update_chart_config(self, new_config: dict[str, Any]) -> None:
        """
        Actualiza la configuración del gráfico.

        Args:
            new_config: Nueva configuración en formato EChart
        """
        self.echart_config.update(new_config)
