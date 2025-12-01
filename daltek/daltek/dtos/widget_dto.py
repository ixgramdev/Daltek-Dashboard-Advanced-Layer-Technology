"""
DTO base para widgets genéricos.

Define la estructura de datos para transferir información de widgets genéricos
entre capas de la aplicación.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class WidgetDTO:
    """
    DTO base para widgets genéricos.

    Contiene las propiedades comunes a todos los tipos de widgets.

    Attributes:
        id: Identificador único del widget
        type: Tipo de widget (e.g., 'card', 'echart', 'table')
        properties: Propiedades genéricas del widget
        created_at: Fecha de creación (ISO format)
        modified_at: Fecha de última modificación (ISO format)git st
        position: Posición del widget en el dashboard {'x': int, 'y': int}
    """

    id: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: str | None = None
    modified_at: str | None = None
    position: dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el DTO a diccionario.

        Returns:
            Representación en diccionario del DTO
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WidgetDTO":
        """
        Crea una instancia del DTO desde un diccionario.

        Args:
            data: Diccionario con los datos del widget

        Returns:
            Instancia de WidgetDTO

        Raises:
            KeyError: Si faltan campos requeridos
        """
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            properties=data.get("properties", {}),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            position=data.get("position", {"x": 0, "y": 0}),
        )

    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida el DTO.

        Returns:
            Tupla (es_válido, lista_de_errores)
        """
        errors = []

        if not self.id or not isinstance(self.id, str):
            errors.append("ID debe ser un string no vacío")

        if not self.type or not isinstance(self.type, str):
            errors.append("Type debe ser un string no vacío")

        if not isinstance(self.properties, dict):
            errors.append("Properties debe ser un diccionario")

        if not isinstance(self.position, dict):
            errors.append("Position debe ser un diccionario")

        if "x" not in self.position or "y" not in self.position:
            errors.append("Position debe contener las claves 'x' e 'y'")

        return len(errors) == 0, errors
