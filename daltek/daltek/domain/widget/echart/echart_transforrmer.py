"""
EChartTransformer: Transforma configuraciones de ECharts para renderización en cliente.

Responsabilidades:
- Procesar configuraciones JSON almacenadas
- Aplicar transformaciones finales
- Preparar datos para envío al navegador
- Optimizar para rendimiento
"""

from typing import Any

import frappe


class EChartTransformer:
    """
    Transforma la configuración almacenada de ECharts en datos listos para renderizar.
    Aplica optimizaciones y adaptaciones antes de enviar al cliente.
    """

    def __init__(self):
        """Inicializa el transformer."""
        self.optimizations_enabled = True
        self.cache_enabled = True
        self._cache = {}

    # --- MÉTODOS PÚBLICOS ---

    def transform_widget(self, widget: dict[str, Any]) -> dict[str, Any]:
        """
        Transforma un widget completo para renderización.

        Args:
            widget: Dict con estructura del widget

        Returns:
            Widget transformado listo para renderizar
        """
        try:
            chart_type = widget.get("type")

            # Si tiene configuración de EChart, transformarla
            if widget.get("echart_config"):
                widget["echart_config"] = self.transform_config(
                    widget.get("echart_config")
                )

            # Añadir información de renderización
            widget["render_info"] = {
                "transformed_at": frappe.utils.now_datetime().isoformat(),
                "type": chart_type,
                "is_echart": chart_type
                in [
                    "line",
                    "bar",
                    "pie",
                    "scatter",
                    "radar",
                    "gauge",
                ],
            }

            return widget

        except Exception as e:
            frappe.log_error(
                f"Error en transform_widget(): {str(e)}", "EChartTransformer"
            )
            return widget

    def transform_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Transforma la configuración de un EChart.
        Aplica optimizaciones y preparaciones finales.

        Args:
            config: Configuración del chart

        Returns:
            Configuración transformada
        """
        try:
            transformed = config.copy()

            # 1. Optimizar datos grandes
            if self.optimizations_enabled:
                transformed = self._optimize_large_data(transformed)

            # 2. Normalizar colores
            if "color" in transformed:
                transformed["color"] = self._normalize_colors(transformed["color"])

            # 3. Optimizar tooltips
            if "tooltip" in transformed:
                transformed["tooltip"] = self._optimize_tooltip(transformed["tooltip"])

            # 4. Preparar animaciones
            transformed["animationDuration"] = transformed.get("animationDuration", 500)
            transformed["animationEasing"] = transformed.get(
                "animationEasing", "cubicOut"
            )

            # 5. Añadir configuración responsive
            transformed["responsive"] = self._get_responsive_config()

            return transformed

        except Exception as e:
            frappe.log_error(
                f"Error en transform_config(): {str(e)}", "EChartTransformer"
            )
            return config

    def transform_data_for_export(self, widget: dict[str, Any]) -> dict[str, Any]:
        """
        Transforma datos para exportación (CSV, Excel, etc).

        Args:
            widget: Widget a exportar

        Returns:
            Datos en formato exportable
        """
        try:
            chart_type = widget.get("type")
            data = widget.get("echart_data", {})

            if chart_type == "line" or chart_type == "bar":
                return self._transform_for_export_axis_chart(data)
            elif chart_type == "pie":
                return self._transform_for_export_pie_chart(data)
            elif chart_type == "scatter":
                return self._transform_for_export_scatter(data)
            else:
                return data

        except Exception as e:
            frappe.log_error(
                f"Error en transform_data_for_export(): {str(e)}",
                "EChartTransformer",
            )
            return widget.get("echart_data", {})

    def transform_batch(self, widgets: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Transforma múltiples widgets a la vez.

        Args:
            widgets: Lista de widgets

        Returns:
            Lista de widgets transformados
        """
        return [self.transform_widget(w) for w in widgets]

    # --- MÉTODOS PRIVADOS DE TRANSFORMACIÓN ---

    def _optimize_large_data(self, config: dict[str, Any]) -> dict[str, Any]:
        """
        Optimiza datos grandes aplicando sampling o agregación.

        Args:
            config: Configuración del chart

        Returns:
            Configuración optimizada
        """
        # Si las series tienen muchos puntos, aplicar sampling
        if "series" in config:
            for serie in config["series"]:
                if isinstance(serie.get("data"), list):
                    data_length = len(serie["data"])
                    if data_length > 1000:
                        # Aplicar sampling: tomar cada N-ésimo punto
                        step = max(1, data_length // 500)
                        serie["data"] = serie["data"][::step]

        return config

    def _normalize_colors(self, colors: list[str] | str) -> list[str]:
        """
        Normaliza colores a formato válido.

        Args:
            colors: Color(es) a normalizar

        Returns:
            Lista de colores normalizados
        """
        if isinstance(colors, str):
            colors = [colors]

        normalized = []
        for color in colors:
            # Validar formato hex
            if isinstance(color, str):
                color = color.strip()
                # Si no tiene #, agregarlo
                if not color.startswith("#") and len(color) == 6:
                    color = "#" + color
                normalized.append(color)

        return normalized if normalized else self._get_default_colors()

    def _optimize_tooltip(self, tooltip: dict[str, Any]) -> dict[str, Any]:
        """
        Optimiza configuración de tooltip.

        Args:
            tooltip: Configuración del tooltip

        Returns:
            Tooltip optimizado
        """
        optimized = tooltip.copy()

        # Mejorar renderización
        optimized["confine"] = optimized.get("confine", True)
        optimized["textStyle"] = optimized.get("textStyle", {})
        optimized["textStyle"]["fontSize"] = optimized["textStyle"].get("fontSize", 12)

        return optimized

    def _get_responsive_config(self) -> dict[str, Any]:
        """
        Retorna configuración responsive para diferentes resoluciones.

        Returns:
            Dict con breakpoints y ajustes
        """
        return {
            "media": [
                {
                    "query": "(max-width: 768px)",
                    "option": {
                        "grid": {"left": "5%", "right": "5%", "bottom": "10%"},
                        "legend": {"orient": "horizontal", "bottom": "0%"},
                    },
                },
                {
                    "query": "(min-width: 768px)",
                    "option": {
                        "grid": {"left": "3%", "right": "4%", "bottom": "3%"},
                    },
                },
            ]
        }

    # --- EXPORTACIÓN DE DATOS ---

    def _transform_for_export_axis_chart(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Transforma datos de chart con ejes (line, bar) para exportación.

        Args:
            data: Datos del chart

        Returns:
            Datos en formato tabular
        """
        categories = data.get("categories", [])
        series = data.get("series", [])

        # Convertir a formato tabular
        rows = []
        headers = ["Categoría"] + [
            s.get("name", f"Serie {i}") for i, s in enumerate(series)
        ]

        for cat_idx, category in enumerate(categories):
            row = [category]
            for serie in series:
                serie_data = serie.get("data", [])
                row.append(serie_data[cat_idx] if cat_idx < len(serie_data) else None)
            rows.append(row)

        return {
            "headers": headers,
            "rows": rows,
            "type": "tabular",
        }

    def _transform_for_export_pie_chart(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Transforma datos de pie chart para exportación.

        Args:
            data: Datos del chart

        Returns:
            Datos en formato tabular
        """
        pie_data = data.get("data", [])

        headers = ["Nombre", "Valor", "Porcentaje"]
        total = sum(item.get("value", 0) for item in pie_data)

        rows = []
        for item in pie_data:
            value = item.get("value", 0)
            percentage = (value / total * 100) if total > 0 else 0
            percentage_str = f"{percentage:.2f}%"  # noqa: E231
            rows.append([item.get("name", ""), value, percentage_str])

        return {
            "headers": headers,
            "rows": rows,
            "type": "tabular",
        }

    def _transform_for_export_scatter(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Transforma datos de scatter plot para exportación.

        Args:
            data: Datos del chart

        Returns:
            Datos en formato tabular
        """
        series = data.get("series", [])

        headers = ["Serie", "X", "Y"]
        rows = []

        for serie in series:
            serie_name = serie.get("name", "")
            serie_data = serie.get("data", [])
            for point in serie_data:
                if isinstance(point, (list, tuple)) and len(point) >= 2:
                    rows.append([serie_name, point[0], point[1]])

        return {
            "headers": headers,
            "rows": rows,
            "type": "tabular",
        }

    # --- UTILIDADES ---

    def _get_default_colors(self) -> list[str]:
        """Retorna paleta de colores por defecto."""
        return [
            "#2196F3",
            "#4CAF50",
            "#FF9800",
            "#F44336",
            "#9C27B0",
            "#00BCD4",
            "#FFEB3B",
            "#795548",
        ]

    def clear_cache(self) -> None:
        """Limpia el caché interno."""
        self._cache.clear()
