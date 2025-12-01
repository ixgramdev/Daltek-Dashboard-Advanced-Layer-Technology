# Test manual del Data Mapper con datos mockeados
# Ejecutar con: python test_manual.py

import sys
import json
from pandas_transformer import PandasTransformer
from widget_data_adapter import WidgetDataAdapter
from mapping_validator import MappingValidator
from data_mapper_service import DataMapperService


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_pandas_transformer():
    print_section("TEST 1: PandasTransformer")
    
    # Datos mockeados de ventas
    mock_data = [
        {"fecha": "2024-01", "categoria": "Electronica", "producto": "Laptop", "ventas": 1500, "cantidad": 5},
        {"fecha": "2024-01", "categoria": "Electronica", "producto": "Mouse", "ventas": 200, "cantidad": 20},
        {"fecha": "2024-01", "categoria": "Ropa", "producto": "Camisa", "ventas": 300, "cantidad": 15},
        {"fecha": "2024-02", "categoria": "Electronica", "producto": "Laptop", "ventas": 2000, "cantidad": 8},
        {"fecha": "2024-02", "categoria": "Electronica", "producto": "Mouse", "ventas": 180, "cantidad": 18},
        {"fecha": "2024-02", "categoria": "Ropa", "producto": "Camisa", "ventas": 450, "cantidad": 20},
        {"fecha": "2024-03", "categoria": "Electronica", "producto": "Laptop", "ventas": 1800, "cantidad": 6},
        {"fecha": "2024-03", "categoria": "Ropa", "producto": "Camisa", "ventas": 500, "cantidad": 25},
    ]
    
    transformer = PandasTransformer()
    df = transformer.load_data(mock_data)
    
    print(f"✓ Datos cargados: {len(df)} registros")
    print(f"  Columnas: {df.columns.tolist()}")
    print(f"\nPrimeras 3 filas:")
    print(df.head(3).to_string())
    
    # Test agregación por mes
    print("\n--- Test Agregación por Mes ---")
    config = {
        "group_by": ["fecha"],
        "aggregations": {
            "total_ventas": {"column": "ventas", "func": "sum"},
            "total_cantidad": {"column": "cantidad", "func": "sum"},
            "promedio_ventas": {"column": "ventas", "func": "mean"}
        }
    }
    
    result = transformer.aggregate(df, config)
    print(f"✓ Agregación exitosa: {len(result)} grupos")
    print(result.to_string())
    
    # Test filtros
    print("\n--- Test Filtros ---")
    filters = [
        {"column": "ventas", "operator": ">", "value": 300}
    ]
    filtered = transformer.filter(df, filters)
    print(f"✓ Filtro aplicado: {len(filtered)} registros (ventas > 300)")
    print(filtered[["fecha", "producto", "ventas"]].to_string())
    
    # Test ordenamiento
    print("\n--- Test Ordenamiento ---")
    sorted_df = transformer.sort(df, "ventas", ascending=False)
    print(f"✓ Ordenado por ventas descendente (Top 5):")
    print(sorted_df[["fecha", "producto", "ventas"]].head(5).to_string())
    
    # Test Top N
    print("\n--- Test Top 3 Productos ---")
    top_products = transformer.top_n(df, "ventas", n=3)
    print(f"✓ Top 3 productos por ventas:")
    print(top_products[["producto", "ventas"]].to_string())
    
    return True


def test_widget_adapter():
    print_section("TEST 2: WidgetDataAdapter")
    
    # Datos agregados para gráficos
    mock_data = [
        {"mes": "Enero", "ventas": 2000, "gastos": 1500},
        {"mes": "Febrero", "ventas": 2630, "gastos": 1800},
        {"mes": "Marzo", "ventas": 2300, "gastos": 1600},
        {"mes": "Abril", "ventas": 2800, "gastos": 2000},
    ]
    
    transformer = PandasTransformer()
    df = transformer.load_data(mock_data)
    
    adapter = WidgetDataAdapter()
    
    # Test formato EChart
    print("--- Test Formato EChart (Line) ---")
    echart_data = adapter.to_echart_format(
        df, 
        chart_type="line",
        x_column="mes",
        y_columns=["ventas", "gastos"]
    )
    print(f"✓ Formato EChart generado:")
    print(f"  X-Axis: {echart_data['xAxis']['data']}")
    print(f"  Series: {len(echart_data['series'])} series")
    for serie in echart_data['series']:
        print(f"    - {serie['name']}: {serie['data']}")
    
    # Test formato Tabla
    print("\n--- Test Formato Tabla ---")
    table_data = adapter.to_table_format(df)
    print(f"✓ Formato Tabla generado:")
    print(f"  Columnas: {len(table_data['columns'])}")
    for col in table_data['columns']:
        print(f"    - {col['field']} ({col['type']})")
    print(f"  Filas: {table_data['count']}")
    
    # Test formato Card/KPI
    print("\n--- Test Formato Card/KPI ---")
    card_config = {
        "value_column": "ventas",
        "label": "Ventas Totales",
        "format": "currency"
    }
    card_data = adapter.to_card_format(df, card_config)
    print(f"✓ Formato Card generado:")
    print(f"  Label: {card_data['label']}")
    print(f"  Value: {card_data['value']}")
    print(f"  Format: {card_data['format']}")
    
    return True


def test_mapping_validator():
    print_section("TEST 3: MappingValidator")
    
    validator = MappingValidator()
    
    # Columnas disponibles
    available_columns = [
        {"name": "fecha", "type": "date"},
        {"name": "categoria", "type": "text"},
        {"name": "ventas", "type": "float"},
        {"name": "cantidad", "type": "int"}
    ]
    
    # Configuración válida
    print("--- Test Configuración Válida ---")
    valid_config = {
        "group_by": ["fecha"],
        "aggregations": {
            "total_ventas": {"column": "ventas", "func": "sum"}
        },
        "filters": [
            {"column": "ventas", "operator": ">", "value": 100}
        ]
    }
    
    result = validator.validate_mapping(valid_config, available_columns)
    print(f"✓ Validación exitosa: {result['is_valid']}")
    if result['errors']:
        print(f"  Errores: {result['errors']}")
    if result['warnings']:
        print(f"  Warnings: {result['warnings']}")
    
    # Configuración inválida
    print("\n--- Test Configuración Inválida ---")
    invalid_config = {
        "group_by": ["columna_inexistente"],
        "aggregations": {
            "total": {"column": "categoria", "func": "sum"}  # SUM en texto = error
        }
    }
    
    result = validator.validate_mapping(invalid_config, available_columns)
    print(f"✓ Validación detectó errores: {not result['is_valid']}")
    print(f"  Errores encontrados: {len(result['errors'])}")
    for error in result['errors']:
        print(f"    - {error}")
    
    # Test operaciones compatibles
    print("\n--- Test Operaciones Compatibles ---")
    numeric_ops = validator.get_compatible_aggregations("float")
    print(f"✓ Agregaciones para float: {', '.join(numeric_ops[:5])}...")
    
    text_ops = validator.get_compatible_aggregations("text")
    print(f"✓ Agregaciones para text: {', '.join(text_ops)}")
    
    operators = validator.get_compatible_operators("float")
    print(f"✓ Operadores para float: {', '.join(operators)}")
    
    return True


def test_data_mapper_service():
    print_section("TEST 4: DataMapperService (Integración)")
    
    # Simular resultado de query
    mock_query_result = {
        "success": True,
        "results": [
            {"mes": "Enero", "categoria": "A", "ventas": 1000, "cantidad": 10},
            {"mes": "Enero", "categoria": "B", "ventas": 1500, "cantidad": 15},
            {"mes": "Febrero", "categoria": "A", "ventas": 1200, "cantidad": 12},
            {"mes": "Febrero", "categoria": "B", "ventas": 1800, "cantidad": 18},
            {"mes": "Marzo", "categoria": "A", "ventas": 1100, "cantidad": 11},
            {"mes": "Marzo", "categoria": "B", "ventas": 2000, "cantidad": 20},
        ],
        "count": 6
    }
    
    # Configuración del mapper
    mapper_config = {
        "transformations": {
            "group_by": ["mes"],
            "aggregations": {
                "ventas_totales": {"column": "ventas", "func": "sum"},
                "promedio_cantidad": {"column": "cantidad", "func": "mean"}
            },
            "filters": [
                {"column": "ventas", "operator": ">", "value": 1000}
            ],
            "sort": {"column": "mes", "order": "asc"},
            "limit": 10
        },
        "widget_mapping": {
            "type": "echart",
            "chart_type": "bar",
            "x_axis": "mes",
            "y_axes": ["ventas_totales", "promedio_cantidad"]
        }
    }
    
    # Crear servicio y transformar
    service = DataMapperService()
    
    print("--- Test Transformación Completa ---")
    result = service.transform(mock_query_result, mapper_config)
    
    if result['success']:
        print(f"✓ Transformación exitosa!")
        print(f"  Registros originales: {result['metadata']['original_rows']}")
        print(f"  Registros transformados: {result['metadata']['transformed_rows']}")
        print(f"  Columnas: {result['metadata']['columns']}")
        print(f"  Tiempo ejecución: {result['metadata']['execution_time']}")
        
        # Mostrar datos del gráfico
        data = result['data']
        print(f"\n  Datos del gráfico EChart:")
        print(f"    X-Axis: {data['xAxis']['data']}")
        for serie in data['series']:
            print(f"    {serie['name']}: {serie['data']}")
    else:
        print(f"✗ Error: {result['error']}")
        return False
    
    # Test validación
    print("\n--- Test Validación de Mapper ---")
    columns = [
        {"name": "mes", "type": "text"},
        {"name": "categoria", "type": "text"},
        {"name": "ventas", "type": "float"},
        {"name": "cantidad", "type": "int"}
    ]
    
    validation = service.validate_mapping(mapper_config, columns)
    print(f"✓ Validación: {validation['is_valid']}")
    if validation['errors']:
        print(f"  Errores: {validation['errors']}")
    if validation['warnings']:
        print(f"  Warnings: {validation['warnings']}")
    
    # Test metadata de columnas
    print("\n--- Test Metadata de Columnas ---")
    metadata = service.get_column_metadata(mock_query_result['results'])
    print(f"✓ Metadata generada para {len(metadata)} columnas:")
    for col in metadata:
        print(f"  - {col['name']} ({col['type']}): {col['unique_count']} valores únicos")
        print(f"    Sample: {col['sample_values']}")
    
    return True


def run_all_tests():
    print("\n" + "="*60)
    print("  DATA MAPPER - TESTS CON DATOS MOCKEADOS")
    print("="*60)
    
    tests = [
        ("PandasTransformer", test_pandas_transformer),
        ("WidgetDataAdapter", test_widget_adapter),
        ("MappingValidator", test_mapping_validator),
        ("DataMapperService", test_data_mapper_service),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
            print(f"\n✓ {name}: PASSED")
        except Exception as e:
            results[name] = False
            print(f"\n✗ {name}: FAILED")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Resumen final
    print_section("RESUMEN DE TESTS")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\n  Total: {passed}/{total} tests pasados")
    
    if passed == total:
        print(f"\n  🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        return 0
    else:
        print(f"\n  ⚠️  Algunos tests fallaron")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
