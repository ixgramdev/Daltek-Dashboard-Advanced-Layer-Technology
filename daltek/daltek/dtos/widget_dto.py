"""
DTO base para widgets genéricos.

Define la estructura de datos para transferir información de widgets genéricos
entre capas de la aplicación en formato JSON normalizado ÚNICAMENTE.

Formato:
{
    "id": "widget_1_xxx",
    "type": "card",
    "label": "Mi Widget",
    "metadata": { "created_at": "...", "modified_at": "...", "version": 1 },
    "layout": { "x": 0, "y": 0, "width": 6, "height": 4 },
    "properties": { "title": "...", "color": "..." },
    "content": { "type": "card", "value": 1000, ... }
}
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class WidgetDTO:
    """
    DTO base para widgets genéricos en formato normalizado único.

    Attributes:
        type: Tipo de widget ('card', 'echart', 'table')
        properties: Propiedades genéricas del widget
        id: Identificador único (generado por backend)
        created_at: Fecha de creación (ISO format)
        modified_at: Fecha de última modificación (ISO format)
        position: Posición {'x', 'y', 'width', 'height', 'min_width', 'min_height'}
        label: Etiqueta legible del widget
    """

    type: str
    properties: dict[str, Any] = field(default_factory=dict)
    id: str | None = None
    created_at: str | None = None
    modified_at: str | None = None
    position: dict[str, int] = field(
        default_factory=lambda: {"x": 0, "y": 0, "width": 6, "height": 4}
    )
    label: str = ""

    # Dimensiones mínimas por tipo de widget
    MIN_DIMENSIONS = {
        "card": {
            "min_width": 4,
            "min_height": 3,
            "default_width": 6,
            "default_height": 4,
        },
        "table": {
            "min_width": 6,
            "min_height": 4,
            "default_width": 8,
            "default_height": 6,
        },
        "metric": {
            "min_width": 3,
            "min_height": 3,
            "default_width": 4,
            "default_height": 3,
        },
    }

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte a diccionario en formato normalizado (ÚNICO formato soportado).

        Returns:
            Dict con estructura: id, type, label, metadata, layout, properties, content
        """
        now = datetime.utcnow().isoformat()

        # Obtener dimensiones mínimas según tipo
        min_dims = self.MIN_DIMENSIONS.get(self.type, {"min_width": 4, "min_height": 3})

        # Asegurar que width y height cumplan con mínimos
        width = max(self.position.get("width", 6), min_dims.get("default_width", 6))
        height = max(self.position.get("height", 4), min_dims.get("default_height", 4))

        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "metadata": {
                "created_at": self.created_at or now,
                "modified_at": self.modified_at or now,
                "version": 1,
            },
            "layout": {
                "x": self.position.get("x", 0),
                "y": self.position.get("y", 0),
                "width": width,
                "height": height,
                "min_width": min_dims.get("min_width", 4),
                "min_height": min_dims.get("min_height", 3),
            },
            "properties": self.properties,
            "content": {"type": self.type},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WidgetDTO":
        """
        Crea instancia desde diccionario en formato normalizado.

        Args:
            data: Dict con estructura normalizada

        Returns:
            Instancia de WidgetDTO
        """
        metadata = data.get("metadata", {})
        layout = data.get("layout", {})

        return cls(
            type=data.get("type", ""),
            properties=data.get("properties", {}),
            id=data.get("id"),
            created_at=metadata.get("created_at"),
            modified_at=metadata.get("modified_at"),
            position={
                "x": layout.get("x", 0),
                "y": layout.get("y", 0),
                "width": layout.get("width", 6),
                "height": layout.get("height", 4),
                "min_width": layout.get("min_width", 4),
                "min_height": layout.get("min_height", 3),
            },
            label=data.get("label", ""),
        )
