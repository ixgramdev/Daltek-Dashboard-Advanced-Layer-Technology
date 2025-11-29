"""
Test suite para QueryEngine, QueryBuilder y QueryTransform
"""

import unittest

from daltek.domain.query_service.query_service import (
    QueryBuilder,
    QueryEngine,
    QueryTransform,
)


class TestQueryTransform(unittest.TestCase):
    """Pruebas para la clase QueryTransform"""

    def test_transform_simple_json(self):
        """Debe transformar JSON simple correctamente"""
        json_data = {"select": ["id", "nombre"], "from": "usuarios"}

        transformer = QueryTransform(json_data)
        result = transformer.transform()

        self.assertEqual(result["select"], ["id", "nombre"])
        self.assertEqual(result["from"], "usuarios")

    def test_transform_json_string(self):
        """Debe parsear JSON como string"""
        json_string = '{"select": ["id"], "from": "usuarios"}'

        transformer = QueryTransform(json_string)
        result = transformer.transform()

        self.assertEqual(result["select"], ["id"])
        self.assertEqual(result["from"], "usuarios")

    def test_invalid_json_string(self):
        """Debe lanzar excepción con JSON string inválido"""
        with self.assertRaises(ValueError):
            QueryTransform("JSON INVÁLIDO")

    def test_missing_from_field(self):
        """Debe validar que 'from' es obligatorio"""
        json_data = {"select": ["id"]}

        transformer = QueryTransform(json_data)
        with self.assertRaises(ValueError):
            transformer.transform()

    def test_extract_select_default(self):
        """Debe usar * como select por defecto"""
        json_data = {"from": "usuarios"}

        transformer = QueryTransform(json_data)
        result = transformer.transform()

        self.assertEqual(result["select"], ["*"])

    def test_extract_from_with_alias(self):
        """Debe manejar alias en FROM"""
        json_data = {"from": {"table": "usuarios", "alias": "u"}, "select": ["*"]}

        transformer = QueryTransform(json_data)
        result = transformer.transform()

        self.assertEqual(result["from"], "usuarios AS u")

    def test_extract_where_conditions(self):
        """Debe extraer condiciones WHERE"""
        json_data = {
            "from": "usuarios",
            "where": [
                {"field": "edad", "operator": ">", "value": 18},
                {"field": "activo", "operator": "=", "value": 1},
            ],
        }

        transformer = QueryTransform(json_data)
        result = transformer.transform()

        self.assertEqual(len(result["where"]), 2)
        self.assertEqual(result["where"][0]["field"], "edad")

    def test_extract_order_by(self):
        """Debe extraer ORDER BY"""
        json_data = {
            "from": "usuarios",
            "order_by": [
                {"column": "nombre", "direction": "ASC"},
                {"column": "fecha", "direction": "DESC"},
            ],
        }

        transformer = QueryTransform(json_data)
        result = transformer.transform()

        self.assertEqual(len(result["order_by"]), 2)
        self.assertEqual(result["order_by"][0]["direction"], "ASC")

    def test_extract_joins(self):
        """Debe extraer configuración de JOINs"""
        json_data = {
            "from": "usuarios",
            "joins": [
                {
                    "type": "INNER",
                    "table": "posts",
                    "alias": "p",
                    "on": "usuarios.id = posts.usuario_id",
                }
            ],
        }

        transformer = QueryTransform(json_data)
        result = transformer.transform()

        self.assertEqual(len(result["joins"]), 1)
        self.assertEqual(result["joins"][0]["type"], "INNER")


class TestQueryBuilder(unittest.TestCase):
    """Pruebas para la clase QueryBuilder"""

    def test_build_simple_select(self):
        """Debe construir SELECT simple"""
        query_dict = {"select": ["id", "nombre"], "from": "usuarios"}

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("SELECT id, nombre", sql)
        self.assertIn("FROM usuarios", sql)

    def test_build_select_with_where(self):
        """Debe construir SELECT con WHERE"""
        query_dict = {
            "select": ["*"],
            "from": "usuarios",
            "where": [{"field": "edad", "operator": ">", "value": 18}],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("WHERE", sql)
        self.assertIn("edad > 18", sql)

    def test_build_select_with_where_string(self):
        """Debe construir SELECT con WHERE string"""
        query_dict = {
            "select": ["*"],
            "from": "usuarios",
            "where": [{"condition": "edad > 18", "type": "RAW"}],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("WHERE edad > 18", sql)

    def test_build_select_with_limit(self):
        """Debe agregar LIMIT"""
        query_dict = {"select": ["*"], "from": "usuarios", "limit": 10}

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("LIMIT 10", sql)

    def test_build_select_with_limit_offset(self):
        """Debe agregar LIMIT y OFFSET"""
        query_dict = {"select": ["*"], "from": "usuarios", "limit": 10, "offset": 5}

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("LIMIT 10", sql)
        self.assertIn("OFFSET 5", sql)

    def test_build_select_with_order_by(self):
        """Debe agregar ORDER BY"""
        query_dict = {
            "select": ["*"],
            "from": "usuarios",
            "order_by": [{"column": "nombre", "direction": "ASC"}],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("ORDER BY nombre ASC", sql)

    def test_build_select_with_join(self):
        """Debe construir SELECT con JOIN"""
        query_dict = {
            "select": ["u.id", "p.titulo"],
            "from": "usuarios AS u",
            "joins": [
                {
                    "type": "INNER",
                    "table": "posts",
                    "alias": "p",
                    "on": "u.id = p.usuario_id",
                }
            ],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("INNER JOIN posts AS p", sql)
        self.assertIn("ON u.id = p.usuario_id", sql)

    def test_build_select_with_group_by(self):
        """Debe construir SELECT con GROUP BY"""
        query_dict = {
            "select": ["departamento", "COUNT(id)"],
            "from": "empleados",
            "group_by": ["departamento"],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("GROUP BY departamento", sql)

    def test_build_select_with_having(self):
        """Debe construir SELECT con HAVING"""
        query_dict = {
            "select": ["departamento", "COUNT(id) AS total"],
            "from": "empleados",
            "group_by": ["departamento"],
            "having": [{"field": "COUNT(id)", "operator": ">", "value": 5}],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("HAVING", sql)
        self.assertIn("COUNT(id) > 5", sql)

    def test_invalid_missing_from(self):
        """Debe fallar si falta 'from'"""
        query_dict = {"select": ["*"]}

        with self.assertRaises(ValueError):
            QueryBuilder(query_dict)

    def test_string_escaping(self):
        """Debe escapar strings en WHERE"""
        query_dict = {
            "select": ["*"],
            "from": "usuarios",
            "where": [{"field": "nombre", "operator": "=", "value": "Juan"}],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("nombre = 'Juan'", sql)

    def test_null_handling(self):
        """Debe manejar NULL en WHERE"""
        query_dict = {
            "select": ["*"],
            "from": "usuarios",
            "where": [{"field": "telefono", "operator": "=", "value": None}],
        }

        builder = QueryBuilder(query_dict)
        sql = builder.build()

        self.assertIn("telefono = NULL", sql)


class TestQueryEngine(unittest.TestCase):
    """Pruebas para la clase QueryEngine"""

    def test_execute_from_json_dict(self):
        """Debe ejecutar pipeline con diccionario"""
        engine = QueryEngine()

        json_data = {"select": ["id", "nombre"], "from": "usuarios"}

        sql = engine.execute_from_json(json_data)

        self.assertIn("SELECT id, nombre", sql)
        self.assertIn("FROM usuarios", sql)

    def test_execute_from_json_string(self):
        """Debe ejecutar pipeline con JSON string"""
        engine = QueryEngine()

        json_string = '{"select": ["id"], "from": "usuarios"}'

        sql = engine.execute_from_json(json_string)

        self.assertIn("SELECT id", sql)

    def test_get_sql(self):
        """Debe retornar SQL generado"""
        engine = QueryEngine()

        json_data = {"select": ["*"], "from": "usuarios"}
        engine.execute_from_json(json_data)

        sql = engine.get_sql()

        self.assertIsNotNone(sql)
        self.assertIn("SELECT", sql)

    def test_get_query_dict(self):
        """Debe retornar diccionario transformado"""
        engine = QueryEngine()

        json_data = {"select": ["id"], "from": "usuarios", "limit": 10}
        engine.execute_from_json(json_data)

        query_dict = engine.get_query_dict()

        self.assertEqual(query_dict["limit"], 10)

    def test_validate_json_valid(self):
        """Debe validar JSON válido"""
        engine = QueryEngine()

        json_data = {"select": ["*"], "from": "usuarios"}

        result = engine.validate_json(json_data)

        self.assertTrue(result)

    def test_validate_json_invalid(self):
        """Debe rechazar JSON inválido"""
        engine = QueryEngine()

        json_data = {"select": ["*"]}  # Falta 'from'

        result = engine.validate_json(json_data)

        self.assertFalse(result)
        self.assertGreater(len(engine.get_errors()), 0)

    def test_reset(self):
        """Debe reiniciar el estado"""
        engine = QueryEngine()

        json_data = {"select": ["*"], "from": "usuarios"}
        engine.execute_from_json(json_data)

        engine.reset()

        self.assertIsNone(engine.get_sql())
        self.assertIsNone(engine.get_query_dict())

    def test_error_tracking(self):
        """Debe rastrear errores"""
        engine = QueryEngine()

        engine.validate_json({"select": ["*"]})
        errors = engine.get_errors()

        self.assertGreater(len(errors), 0)

    def test_clear_errors(self):
        """Debe limpiar lista de errores"""
        engine = QueryEngine()

        engine.validate_json({"select": ["*"]})
        engine.clear_errors()

        self.assertEqual(len(engine.get_errors()), 0)

    def test_legacy_fluent_api(self):
        """Debe soportar API legacy fluent"""
        engine = QueryEngine()

        sql = engine.select("id", "nombre").from_table("usuarios").limit(10).build()

        self.assertIn("SELECT id, nombre", sql)
        self.assertIn("LIMIT 10", sql)

    def test_legacy_join(self):
        """Debe soportar joins en API legacy"""
        engine = QueryEngine()

        sql = (
            engine.select("u.id", "p.titulo")
            .from_table("usuarios", "u")
            .inner_join("posts", "u.id = p.usuario_id", "p")
            .build()
        )

        self.assertIn("INNER JOIN", sql)

    def test_complex_query(self):
        """Debe manejar consultas complejas"""
        engine = QueryEngine()

        json_data = {
            "select": ["u.id", "u.nombre", "COUNT(p.id) AS total_posts"],
            "from": {"table": "usuarios", "alias": "u"},
            "joins": [
                {
                    "type": "LEFT",
                    "table": "posts",
                    "alias": "p",
                    "on": "u.id = p.usuario_id",
                }
            ],
            "where": [{"field": "u.activo", "operator": "=", "value": 1}],
            "group_by": ["u.id", "u.nombre"],
            "having": [{"field": "COUNT(p.id)", "operator": ">", "value": 0}],
            "order_by": [{"column": "total_posts", "direction": "DESC"}],
            "limit": 50,
        }

        sql = engine.execute_from_json(json_data)

        self.assertIn("SELECT", sql)
        self.assertIn("LEFT JOIN", sql)
        self.assertIn("WHERE", sql)
        self.assertIn("GROUP BY", sql)
        self.assertIn("HAVING", sql)
        self.assertIn("ORDER BY", sql)
        self.assertIn("LIMIT 50", sql)


if __name__ == "__main__":
    unittest.main()
