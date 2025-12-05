from typing import Any

class WidgetValidator:
    """
    Valida la estructura y datos de widgets en formato DTO.
    Validación basada en la estructura de los DTOs (WidgetDTO, EChartWidgetDTO).
    """

    SUPPORTED_TYPES = ["card", "echart", "table", "metric"]
    SUPPORTED_ECHART_TYPES = [
        "line",
        "bar",
        "pie",
        "scatter",
        "gauge",
        "candlestick",
        "heatmap",
    ]

    def validate_widget(self, dto: Any) -> dict[str, Any]:
        """
        Validación centralizada para DTOs de widgets.

        Args:
            dto: Instancia de WidgetDTO o EChartWidgetDTO (pasada desde widget_service)

        Returns:
            Dict con {valid: bool, error: str} o {valid: True}
        """
        errors = []

        # 1⃣ Validar campos base requeridos del DTO
        if not dto.id or not isinstance(dto.id, str):
            errors.append("Campo requerido: 'id' (debe ser string no vacío)")

        if not dto.type or not isinstance(dto.type, str):
            errors.append("Campo requerido: 'type' (debe ser string no vacío)")

        if errors:
            return {"valid": False, "error": "; ".join(errors)}

        # 2⃣ Validar tipo
        if dto.type not in self.SUPPORTED_TYPES:
            return {
                "valid": False,
                "error": f"Tipo no soportado: '{dto.type}'. Válidos: {', '.join(self.SUPPORTED_TYPES)}",
            }

        # 3⃣ Validar timestamps (created_at, modified_at)
        errors.extend(self._validate_timestamps(dto))

        # 4⃣ Validar posición/layout
        errors.extend(self._validate_position(dto.position))

        # 5⃣ Validar properties
        if dto.properties is not None and not isinstance(dto.properties, dict):
            errors.append("Properties debe ser un diccionario")

        # 6⃣ Validar label
        if dto.label is not None and not isinstance(dto.label, str):
            errors.append("Label debe ser string")

        # 7⃣ Validar según tipo específico
        if dto.type == "echart":
            errors.extend(self._validate_echart_dto(dto))

        if errors:
            return {"valid": False, "error": "; ".join(errors)}

        return {"valid": True}

    def _validate_timestamps(self, dto: Any) -> list[str]:
        """Valida timestamps created_at y modified_at del DTO."""
        errors = []

        for field, value in [
            ("created_at", dto.created_at),
            ("modified_at", dto.modified_at),
        ]:
            if value is not None:
                if not isinstance(value, str):
                    errors.append(f"{field} debe ser string (ISO 8601)")
                elif not ("T" in value and ("-" in value or "+" in value)):
                    # Concatenate to avoid format spec interpretation or lint
                    # issues related to colons in f-strings.
                    errors.append(
                        field + " debe ser ISO 8601 (ej: 2025-12-03T10:30:45)"
                    )

        return errors

    def _validate_position(self, position: dict) -> list[str]:
        """Valida sección position del DTO."""
        errors = []

        if not isinstance(position, dict):
            errors.append("Position debe ser un diccionario")
            return errors

        # Campos requeridos
        required_fields = ["x", "y", "width", "height"]
        for field in required_fields:
            if field not in position:
                errors.append(f"Position.{field} es requerido")
            else:
                try:
                    value = int(position[field])
                    if field in ["width", "height"] and value <= 0:
                        errors.append(f"Position.{field} debe ser > 0")
                    elif field in ["x", "y"] and value < 0:
                        errors.append(f"Position.{field} debe ser >= 0")
                except (ValueError, TypeError):
                    errors.append(f"Position.{field} debe ser número")

        # Campos opcionales
        for field in ["min_width", "min_height"]:
            if field in position:
                try:
                    value = int(position[field])
                    if value <= 0:
                        errors.append(f"Position.{field} debe ser > 0")
                except (ValueError, TypeError):
                    errors.append(f"Position.{field} debe ser número")

        return errors

    def _validate_echart_dto(self, dto: Any) -> list[str]:
        """Valida campos específicos de EChartWidgetDTO."""
        errors = []

        # Validar chart_type
        if not dto.chart_type or not isinstance(dto.chart_type, str):
            errors.append("chart_type requerido para widgets EChart")
        elif dto.chart_type not in self.SUPPORTED_ECHART_TYPES:
            errors.append(
                f"chart_type no soportado: '{dto.chart_type}'. "
                f"Válidos: {', '.join(self.SUPPORTED_ECHART_TYPES)}"
            )

        # Validar echart_data
        if dto.echart_data is not None and not isinstance(dto.echart_data, dict):
            errors.append("echart_data debe ser un diccionario")

        # Validar echart_config
        if dto.echart_config is not None and not isinstance(dto.echart_config, dict):
            errors.append("echart_config debe ser un diccionario")

        return errors

    def validate_batch(self, dtos: list[Any]) -> dict[str, Any]:
        """Valida múltiples widgets."""
        errors = []
        valid_dtos = []

        for i, dto in enumerate(dtos):
            result = self.validate_widget(dto)
            if not result.get("valid"):
                errors.append(
                    {
                        "index": i,
                        "widget_id": dto.id,
                        "widget_type": dto.type,
                        "error": result.get("error"),
                    }
                )
            else:
                valid_dtos.append(dto)

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "valid_dtos": valid_dtos,
            "total": len(dtos),
            "valid_count": len(valid_dtos),
        }

    def is_echart_widget(self, dto: Any) -> bool:
        """Determina si un widget es EChart."""
        return dto.type == "echart"

    def get_supported_types(self) -> list[str]:
        """Retorna tipos soportados."""
        return self.SUPPORTED_TYPES

    def get_supported_echart_types(self) -> list[str]:
        """Retorna tipos de EChart soportados."""
        return self.SUPPORTED_ECHART_TYPES
