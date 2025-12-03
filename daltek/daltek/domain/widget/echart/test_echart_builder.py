"""
Tests para EChartBuilder y sus subclases.

Valida:
- Creación de builders correctos
- Validación de datos
- Construcción de configuración
- Manejo de errores
"""

import unittest

from .base_echart_builder import BaseEChartBuilder
from .echart_builder import (
    BarChartBuilder,
    LineChartBuilder,
    PieChartBuilder,
    ScatterChartBuilder,
)
from .echart_factory import EChartFactory


class TestLineChartBuilder(unittest.TestCase):
    """Tests para LineChartBuilder"""

    def setUp(self):
        self.builder = LineChartBuilder()
        self.valid_data = {
            "series": [
                {"name": "Sales", "data": [100, 200, 150, 300, 250]},
                {"name": "Profit", "data": [30, 50, 45, 80, 70]},
            ],
            "categories": ["Jan", "Feb", "Mar", "Apr", "May"],
        }
        self.valid_config = {"smooth": True, "fill_area": True}

    def test_valid_line_chart(self):
        """Debe construir un line chart válido"""
        result = self.builder.build(self.valid_data, self.valid_config)

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("chart_type"), "line")
        self.assertIn("series", result.get("config", {}))
        self.assertIn("xAxis", result.get("config", {}))
        self.assertIn("yAxis", result.get("config", {}))

    def test_missing_series(self):
        """Debe rechazar si falta 'series'"""
        data = {"categories": ["Jan", "Feb"]}
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))
        self.assertIn("series", result.get("error", "").lower())

    def test_empty_series(self):
        """Debe rechazar si 'series' está vacía"""
        data = {"series": [], "categories": ["Jan"]}
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))

    def test_invalid_data_points(self):
        """Debe rechazar si los datos no son numéricos"""
        data = {
            "series": [{"name": "Sales", "data": [100, "invalid", 150]}],
            "categories": ["A", "B", "C"],
        }
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))

    def test_mismatched_categories_and_data(self):
        """Debe rechazar si categorías no coinciden con datos"""
        data = {
            "series": [{"name": "Sales", "data": [100, 200, 150]}],
            "categories": ["Jan", "Feb"],  # Solo 2, pero hay 3 datos
        }
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))

    def test_series_structure(self):
        """Debe construir series con estructura correcta"""
        result = self.builder.build(self.valid_data, self.valid_config)

        series = result.get("config", {}).get("series", [])
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0].get("type"), "line")
        self.assertEqual(series[0].get("name"), "Sales")
        self.assertIn("areaStyle", series[0])  # Por fill_area=True


class TestBarChartBuilder(unittest.TestCase):
    """Tests para BarChartBuilder"""

    def setUp(self):
        self.builder = BarChartBuilder()
        self.valid_data = {
            "series": [{"name": "Revenue", "data": [1000, 2000, 1500, 3000]}],
            "categories": ["Q1", "Q2", "Q3", "Q4"],
        }

    def test_valid_bar_chart(self):
        """Debe construir un bar chart válido"""
        result = self.builder.build(self.valid_data, {})

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("chart_type"), "bar")
        series = result.get("config", {}).get("series", [])
        self.assertEqual(series[0].get("type"), "bar")

    def test_bar_chart_has_axes(self):
        """El bar chart debe tener ejes X e Y"""
        result = self.builder.build(self.valid_data, {})
        config = result.get("config", {})

        self.assertIn("xAxis", config)
        self.assertIn("yAxis", config)
        self.assertEqual(config["xAxis"]["type"], "category")
        self.assertEqual(config["yAxis"]["type"], "value")


class TestPieChartBuilder(unittest.TestCase):
    """Tests para PieChartBuilder"""

    def setUp(self):
        self.builder = PieChartBuilder()
        self.valid_data = {
            "data": [
                {"name": "Chrome", "value": 450},
                {"name": "Firefox", "value": 300},
                {"name": "Safari", "value": 200},
            ]
        }

    def test_valid_pie_chart(self):
        """Debe construir un pie chart válido"""
        result = self.builder.build(self.valid_data, {})

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("chart_type"), "pie")
        series = result.get("config", {}).get("series", [])
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0].get("type"), "pie")

    def test_pie_chart_no_axes(self):
        """El pie chart NO debe tener ejes"""
        result = self.builder.build(self.valid_data, {})
        config = result.get("config", {})

        self.assertNotIn("xAxis", config)
        self.assertNotIn("yAxis", config)

    def test_missing_data_field(self):
        """Debe rechazar si falta campo 'data'"""
        data = {}
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))

    def test_invalid_value_in_pie(self):
        """Debe rechazar si value no es numérico"""
        data = {
            "data": [
                {"name": "Chrome", "value": "invalid"},
            ]
        }
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))


class TestScatterChartBuilder(unittest.TestCase):
    """Tests para ScatterChartBuilder"""

    def setUp(self):
        self.builder = ScatterChartBuilder()
        self.valid_data = {
            "series": [
                {
                    "name": "Dataset 1",
                    "data": [[10, 20], [15, 25], [20, 30], [25, 35]],
                }
            ]
        }

    def test_valid_scatter_chart(self):
        """Debe construir un scatter chart válido"""
        result = self.builder.build(self.valid_data, {})

        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("chart_type"), "scatter")

    def test_scatter_points_format(self):
        """Debe validar formato [x, y] de puntos"""
        data = {
            "series": [
                {"name": "Data", "data": [[10, 20], [15]]}
            ]  # Último punto incompleto
        }
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))

    def test_scatter_non_numeric_values(self):
        """Debe rechazar si puntos contienen no-numéricos"""
        data = {"series": [{"name": "Data", "data": [[10, "invalid"], [15, 25]]}]}
        result = self.builder.build(data, {})

        self.assertFalse(result.get("success"))


class TestEChartFactory(unittest.TestCase):
    """Tests para EChartFactory"""

    def test_create_line_chart(self):
        """Factory debe crear LineChartBuilder"""
        builder = EChartFactory.create("line")

        self.assertIsInstance(builder, LineChartBuilder)
        self.assertEqual(builder.get_chart_type(), "line")

    def test_create_bar_chart(self):
        """Factory debe crear BarChartBuilder"""
        builder = EChartFactory.create("bar")

        self.assertIsInstance(builder, BarChartBuilder)

    def test_create_pie_chart(self):
        """Factory debe crear PieChartBuilder"""
        builder = EChartFactory.create("pie")

        self.assertIsInstance(builder, PieChartBuilder)

    def test_create_scatter_chart(self):
        """Factory debe crear ScatterChartBuilder"""
        builder = EChartFactory.create("scatter")

        self.assertIsInstance(builder, ScatterChartBuilder)

    def test_case_insensitive(self):
        """Factory debe ser case-insensitive"""
        builder1 = EChartFactory.create("LINE")
        builder2 = EChartFactory.create("Line")

        self.assertIsInstance(builder1, LineChartBuilder)
        self.assertIsInstance(builder2, LineChartBuilder)

    def test_invalid_chart_type(self):
        """Factory debe lanzar error para tipo inválido"""
        with self.assertRaises(ValueError):
            EChartFactory.create("invalid_type")

    def test_get_available_types(self):
        """Debe retornar tipos disponibles"""
        types = EChartFactory.get_available_types()

        self.assertIn("line", types)
        self.assertIn("bar", types)
        self.assertIn("pie", types)
        self.assertIn("scatter", types)

    def test_is_registered(self):
        """Debe verificar si tipo está registrado"""
        self.assertTrue(EChartFactory.is_registered("line"))
        self.assertTrue(EChartFactory.is_registered("bar"))
        self.assertFalse(EChartFactory.is_registered("invalid"))


class TestBaseEChartBuilderUtils(unittest.TestCase):
    """Tests para métodos utilitarios del builder base"""

    def setUp(self):
        self.builder = LineChartBuilder()

    def test_validate_numeric_data(self):
        """Debe validar valores numéricos"""
        self.assertTrue(BaseEChartBuilder.validate_numeric_data(10))
        self.assertTrue(BaseEChartBuilder.validate_numeric_data(10.5))
        self.assertTrue(BaseEChartBuilder.validate_numeric_data("20"))
        self.assertFalse(BaseEChartBuilder.validate_numeric_data("abc"))
        self.assertFalse(BaseEChartBuilder.validate_numeric_data(None))

    def test_ensure_numeric(self):
        """Debe convertir a número o retornar default"""
        self.assertEqual(BaseEChartBuilder.ensure_numeric(10), 10.0)
        self.assertEqual(BaseEChartBuilder.ensure_numeric("20"), 20.0)
        self.assertEqual(BaseEChartBuilder.ensure_numeric("invalid"), 0)
        self.assertEqual(BaseEChartBuilder.ensure_numeric("invalid", 99), 99)

    def test_normalize_series_name(self):
        """Debe normalizar nombres de series"""
        self.assertEqual(self.builder._normalize_series_name("  Sales  "), "Sales")
        self.assertEqual(self.builder._normalize_series_name(123), "123")

    def test_get_legend_data_from_series(self):
        """Debe extraer datos de leyenda desde series"""
        self.builder.data = {
            "series": [
                {"name": "Sales", "data": [100, 200]},
                {"name": "Profit", "data": [30, 40]},
            ]
        }
        legend = self.builder._get_legend_data()

        self.assertEqual(legend, ["Sales", "Profit"])

    def test_get_default_colors(self):
        """Debe retornar paleta de colores por defecto"""
        colors = self.builder._get_default_colors()

        self.assertIsInstance(colors, list)
        self.assertGreater(len(colors), 0)
        # Verificar que son colores hex
        for color in colors:
            self.assertTrue(color.startswith("#"))


if __name__ == "__main__":
    unittest.main()
