from typing import Any


class WidgetValidator:
    """
    Valida la estructura y datos de widgets antes de guardarlos.
    """

    REQUIRED_FIELDS = ["type", "properties"]
    SUPPORTED_TYPES = [
        "card",
        "line_chart",
        "bar_chart",
        "pie_chart",
        "table",
        "metric",
        "echart",  # ← Nuevo tipo para widgets EChart dinámicos
    ]

    def validate_widget(self, widget: dict[str, Any]) -> dict[str, Any]:
        """
        Valida que un widget tenga la estructura correcta.

        Args:
            widget: Dict con datos del widget

        Returns:
            Dict con {valid: bool, error: str}
        """
        # Verificar campos requeridos
        for field in self.REQUIRED_FIELDS:
            if field not in widget or not widget[field]:
                return {
                    "valid": False,
                    "error": f"Campo requerido faltante: '{field}'",
                }

        # Validar tipo
        widget_type = widget.get("type")
        if widget_type not in self.SUPPORTED_TYPES:
            return {
                "valid": False,
                "error": f"Tipo de widget no soportado: '{widget_type}'. "
                f"Tipos válidos: {', '.join(self.SUPPORTED_TYPES)}",
            }

        # Validar propiedades
        properties = widget.get("properties", {})
        if not isinstance(properties, dict):
            return {
                "valid": False,
                "error": "Las propiedades deben ser un diccionario",
            }

        # Validar posición si existe
        if "position" in widget:
            position = widget.get("position", {})
            if not isinstance(position, dict):
                return {
                    "valid": False,
                    "error": "La posición debe ser un diccionario",
                }

            # Validar campos de posición
            position_fields = ["x", "y", "width", "height"]
            for field in position_fields:
                if field in position:
                    try:
                        int(position[field])
                    except (ValueError, TypeError):
                        return {
                            "valid": False,
                            "error": f"Posición '{field}' debe ser un número",
                        }

        return {"valid": True}

    def validate_batch(self, widgets: list[dict]) -> dict[str, Any]:
        """
        Valida múltiples widgets.

        Args:
            widgets: Lista de widgets

        Returns:
            Dict con {valid: bool, errors: list, valid_widgets: list}
        """
        errors = []
        valid_widgets = []

        for i, widget in enumerate(widgets):
            result = self.validate_widget(widget)
            if not result.get("valid"):
                errors.append(
                    {
                        "index": i,
                        "widget_id": widget.get("id"),
                        "error": result.get("error"),
                    }
                )
            else:
                valid_widgets.append(widget)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "valid_widgets": valid_widgets,
            "total": len(widgets),
            "valid_count": len(valid_widgets),
        }
