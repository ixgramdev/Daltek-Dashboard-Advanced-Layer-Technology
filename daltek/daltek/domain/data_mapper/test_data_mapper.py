"""
Tests para Data Mapper
"""

import unittest
import pandas as pd
from daltek.daltek.domain.data_mapper.pandas_transformer import PandasTransformer
from daltek.daltek.domain.data_mapper.widget_data_adapter import WidgetDataAdapter
from daltek.daltek.domain.data_mapper.mapping_validator import MappingValidator
from daltek.daltek.domain.data_mapper.data_mapper_service import DataMapperService


class TestPandasTransformer(unittest.TestCase):
    """Tests para PandasTransformer"""

    def setUp(self):
        self.transformer = PandasTransformer()
        self.sample_data = [
            {"fecha": "2024-01-01", "categoria": "A", "ventas": 100, "cantidad": 10},
            {"fecha": "2024-01-01", "categoria": "B", "ventas": 200, "cantidad": 20},
            {"fecha": "2024-02-01", "categoria": "A", "ventas": 150, "cantidad": 15},
            {"fecha": "2024-02-01", "categoria": "B", "ventas": 250, "cantidad": 25},
        ]

    def test_load_data(self):
        """Test cargar datos"""
        df = self.transformer.load_data(self.sample_data)
        self.assertEqual(len(df), 4)
        self.assertEqual(list(df.columns), ["fecha", "categoria", "ventas", "cantidad"])

    def test_aggregate(self):
        """Test agregación"""
        df = self.transformer.load_data(self.sample_data)
        config = {
            "group_by": ["fecha"],
            "aggregations": {
                "ventas_totales": {"column": "ventas", "func": "sum"},
                "cantidad_total": {"column": "cantidad", "func": "sum"},
            },
        }
        result = self.transformer.aggregate(df, config)

        self.assertEqual(len(result), 2)  # 2 fechas
        self.assertIn("ventas_totales", result.columns)
        self.assertIn("cantidad_total", result.columns)
        self.assertEqual(result["ventas_totales"].iloc[0], 300)  # 100 + 200

    def test_filter(self):
        """Test filtros"""
        df = self.transformer.load_data(self.sample_data)
        conditions = [{"column": "ventas", "operator": ">", "value": 150}]
        result = self.transformer.filter(df, conditions)

        self.assertEqual(len(result), 2)  # Solo 200 y 250
        self.assertTrue(all(result["ventas"] > 150))

    def test_sort(self):
        """Test ordenamiento"""
        df = self.transformer.load_data(self.sample_data)
        result = self.transformer.sort(df, "ventas", ascending=False)

        self.assertEqual(result["ventas"].iloc[0], 250)  # Mayor primero
        self.assertEqual(result["ventas"].iloc[-1], 100)  # Menor último

    def test_top_n(self):
        """Test top N"""
        df = self.transformer.load_data(self.sample_data)
        result = self.transformer.top_n(df, "ventas", n=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result["ventas"].max(), 250)


class TestWidgetDataAdapter(unittest.TestCase):
    """Tests para WidgetDataAdapter"""

    def setUp(self):
        self.adapter = WidgetDataAdapter()
        self.sample_df = pd.DataFrame(
            {
                "mes": ["Enero", "Febrero", "Marzo"],
                "ventas": [1000, 1500, 1200],
                "cantidad": [100, 150, 120],
            }
        )

    def test_to_echart_format(self):
        """Test conversión a formato EChart"""
        result = self.adapter.to_echart_format(
            self.sample_df, "line", "mes", ["ventas", "cantidad"]
        )

        self.assertIn("xAxis", result)
        self.assertIn("series", result)
        self.assertEqual(len(result["series"]), 2)
        self.assertEqual(result["xAxis"]["data"], ["Enero", "Febrero", "Marzo"])

    def test_to_table_format(self):
        """Test conversión a formato tabla"""
        result = self.adapter.to_table_format(self.sample_df)

        self.assertIn("columns", result)
        self.assertIn("rows", result)
        self.assertEqual(len(result["columns"]), 3)
        self.assertEqual(len(result["rows"]), 3)

    def test_to_card_format(self):
        """Test conversión a formato card"""
        metric_config = {
            "value_column": "ventas",
            "label": "Ventas Totales",
            "format": "currency",
        }
        result = self.adapter.to_card_format(self.sample_df, metric_config)

        self.assertIn("value", result)
        self.assertIn("label", result)
        self.assertEqual(result["value"], 3700)  # Suma total


class TestMappingValidator(unittest.TestCase):
    """Tests para MappingValidator"""

    def setUp(self):
        self.validator = MappingValidator()
        self.columns = [
            {"name": "fecha", "type": "date"},
            {"name": "ventas", "type": "float"},
            {"name": "categoria", "type": "text"},
        ]

    def test_validate_aggregation_compatibility(self):
        """Test validación de agregaciones"""
        self.assertTrue(self.validator.validate_aggregation_compatibility("float", "sum"))
        self.assertTrue(
            self.validator.validate_aggregation_compatibility("text", "count")
        )
        self.assertFalse(
            self.validator.validate_aggregation_compatibility("text", "sum")
        )

    def test_validate_filter_operator(self):
        """Test validación de operadores"""
        self.assertTrue(self.validator.validate_filter_operator("float", ">"))
        self.assertTrue(self.validator.validate_filter_operator("text", "contains"))
        self.assertFalse(self.validator.validate_filter_operator("text", ">"))

    def test_get_compatible_aggregations(self):
        """Test obtener agregaciones compatibles"""
        numeric_aggs = self.validator.get_compatible_aggregations("float")
        self.assertIn("sum", numeric_aggs)
        self.assertIn("avg", numeric_aggs)

        text_aggs = self.validator.get_compatible_aggregations("text")
        self.assertIn("count", text_aggs)
        self.assertNotIn("sum", text_aggs)


class TestDataMapperService(unittest.TestCase):
    """Tests para DataMapperService"""

    def setUp(self):
        self.service = DataMapperService()
        self.query_result = {
            "success": True,
            "results": [
                {"fecha": "2024-01-01", "categoria": "A", "ventas": 100},
                {"fecha": "2024-01-01", "categoria": "B", "ventas": 200},
                {"fecha": "2024-02-01", "categoria": "A", "ventas": 150},
            ],
            "count": 3,
        }

    def test_transform_basic(self):
        """Test transformación básica"""
        mapper_config = {
            "transformations": {
                "group_by": ["fecha"],
                "aggregations": {
                    "ventas_totales": {"column": "ventas", "func": "sum"}
                },
            },
            "widget_mapping": {
                "type": "table",
            },
        }

        result = self.service.transform(self.query_result, mapper_config)

        self.assertTrue(result["success"])
        self.assertIn("data", result)
        self.assertIn("metadata", result)

    def test_get_column_metadata(self):
        """Test obtención de metadata"""
        data = self.query_result["results"]
        metadata = self.service.get_column_metadata(data)

        self.assertEqual(len(metadata), 3)  # 3 columnas
        self.assertTrue(any(col["name"] == "ventas" for col in metadata))


if __name__ == "__main__":
    unittest.main()
