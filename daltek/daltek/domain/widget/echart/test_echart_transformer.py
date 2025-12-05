"""
Tests para EChartTransformer.

Valida:
- Transformación de widgets
- Optimización de datos
- Normalización de colores
- Exportación de datos
"""

import unittest

from .echart_transforrmer import EChartTransformer

class TestEChartTransformer(unittest.TestCase):
    """Tests para EChartTransformer"""

    def setUp(self):
        self.transformer = EChartTransformer()
        self.sample_widget = {
            "id": "widget_1",
            "type": "line",
            "echart_data": {
                "series": [{"name": "Sales", "data": [100, 200, 150]}],
                "categories": ["Jan", "Feb", "Mar"],
            },
            "echart_config": {
                "series": [
                    {
                        "name": "Sales",
                        "type": "line",
                        "data": [100, 200, 150],
                    }
                ],
                "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar"]},
                "yAxis": {"type": "value"},
                "tooltip": {"trigger": "axis"},
                "legend": {"data": ["Sales"]},
            },
            "properties": {"title": "Sales Chart"},
        }

    def test_transform_widget(self):
        """Debe transformar un widget completo"""
        result = self.transformer.transform_widget(self.sample_widget.copy())

        self.assertIn("render_info", result)
        self.assertTrue(result["render_info"]["is_echart"])
        self.assertEqual(result["render_info"]["type"], "line")

    def test_transform_config_basic(self):
        """Debe transformar configuración básica"""
        config = self.sample_widget["echart_config"].copy()
        transformed = self.transformer.transform_config(config)

        # Debe tener propiedades de animación
        self.assertIn("animationDuration", transformed)
        self.assertIn("animationEasing", transformed)
        self.assertIn("responsive", transformed)

    def test_transform_config_with_colors(self):
        """Debe normalizar colores en configuración"""
        config = {
            "color": ["#FF0000", "#00FF00", "0000FF"], # El tercero sin #
            "series": [],
        }
        transformed = self.transformer.transform_config(config)

        colors = transformed.get("color", [])
        # Todos deben estar normalizados
        for color in colors:
            self.assertTrue(color.startswith("#"))

    def test_normalize_colors(self):
        """Debe normalizar colores correctamente"""
        colors = ["#FF0000", "00FF00", "#0000FF"]
        normalized = self.transformer._normalize_colors(colors)

        self.assertEqual(len(normalized), 3)
        for color in normalized:
            self.assertTrue(color.startswith("#"))

    def test_normalize_single_color(self):
        """Debe normalizar color único"""
        color = "#FF0000"
        normalized = self.transformer._normalize_colors(color)

        self.assertIsInstance(normalized, list)
        self.assertEqual(normalized[0], "#FF0000")

    def test_optimize_large_data(self):
        """Debe aplicar sampling a datos grandes"""
        # Crear serie con muchos puntos
        large_data = list(range(1500))
        config = {"series": [{"name": "Data", "data": large_data}]}

        optimized = self.transformer._optimize_large_data(config)
        optimized_data = optimized["series"][0]["data"]

        # Debe haber reducido el tamaño
        self.assertLess(len(optimized_data), len(large_data))
        self.assertGreater(len(optimized_data), 0)

    def test_optimize_tooltip(self):
        """Debe optimizar configuración de tooltip"""
        tooltip = {}
        optimized = self.transformer._optimize_tooltip(tooltip)

        self.assertTrue(optimized.get("confine"))
        self.assertIn("textStyle", optimized)
        self.assertEqual(optimized["textStyle"].get("fontSize"), 12)

    def test_transform_data_for_export_line_chart(self):
        """Debe transformar datos de line chart para exportación"""
        export_data = self.transformer.transform_data_for_export(self.sample_widget)

        self.assertEqual(export_data["type"], "tabular")
        self.assertIn("headers", export_data)
        self.assertIn("rows", export_data)
        self.assertIn("Categoría", export_data["headers"])
        self.assertIn("Sales", export_data["headers"])

    def test_transform_data_for_export_pie_chart(self):
        """Debe transformar datos de pie chart para exportación"""
        pie_widget = {
            "type": "pie",
            "echart_data": {
                "data": [
                    {"name": "Chrome", "value": 450},
                    {"name": "Firefox", "value": 300},
                ]
            },
        }

        export_data = self.transformer.transform_data_for_export(pie_widget)

        self.assertEqual(export_data["type"], "tabular")
        self.assertEqual(len(export_data["rows"]), 2)
        self.assertIn("Porcentaje", export_data["headers"])

    def test_transform_data_for_export_scatter(self):
        """Debe transformar datos de scatter plot para exportación"""
        scatter_widget = {
            "type": "scatter",
            "echart_data": {
                "series": [
                    {
                        "name": "Points",
                        "data": [[10, 20], [15, 25], [20, 30]],
                    }
                ]
            },
        }

        export_data = self.transformer.transform_data_for_export(scatter_widget)

        self.assertEqual(len(export_data["rows"]), 3)
        self.assertEqual(export_data["rows"][0][1], 10) # X del primer punto
        self.assertEqual(export_data["rows"][0][2], 20) # Y del primer punto

    def test_transform_batch(self):
        """Debe transformar múltiples widgets"""
        widgets = [self.sample_widget.copy(), self.sample_widget.copy()]
        results = self.transformer.transform_batch(widgets)

        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIn("render_info", result)

    def test_get_responsive_config(self):
        """Debe retornar configuración responsive"""
        responsive = self.transformer._get_responsive_config()

        self.assertIn("media", responsive)
        self.assertGreater(len(responsive["media"]), 0)
        for breakpoint in responsive["media"]:
            self.assertIn("query", breakpoint)
            self.assertIn("option", breakpoint)

    def test_clear_cache(self):
        """Debe limpiar caché"""
        self.transformer._cache["test"] = "value"
        self.transformer.clear_cache()

        self.assertEqual(len(self.transformer._cache), 0)

    def test_transform_widget_without_echart_config(self):
        """Debe manejar widgets sin configuración EChart"""
        widget = {
            "id": "widget_1",
            "type": "card",
            "properties": {"title": "Simple Card"},
        }

        result = self.transformer.transform_widget(widget)

        self.assertIn("render_info", result)
        self.assertFalse(result["render_info"]["is_echart"])

    def test_error_handling_in_transform_config(self):
        """Debe manejar errores en transformación de config"""
        # Config inválida
        invalid_config = {"series": None, "color": 123}

        result = self.transformer.transform_config(invalid_config)

        # Debe retornar algo sin lanzar excepción
        self.assertIsInstance(result, dict)

    def test_animation_defaults(self):
        """Debe aplicar valores por defecto para animación"""
        config = {"series": []}
        transformed = self.transformer.transform_config(config)

        self.assertEqual(transformed.get("animationDuration"), 500)
        self.assertEqual(transformed.get("animationEasing"), "cubicOut")

    def test_preserve_original_config(self):
        """No debe modificar el config original"""
        config = {"series": [], "color": ["#FF0000"]}
        original = config.copy()

        self.transformer.transform_config(config)

        self.assertEqual(config, original)

if __name__ == "__main__":
    unittest.main()
