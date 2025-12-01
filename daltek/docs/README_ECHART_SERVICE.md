# EChart Widget Service - Guía de Uso

## Introducción

El **EChart Widget Service** es un sistema centralizado para crear, validar, almacenar y renderizar gráficos interactivos basados en ECharts dentro del dashboard Daltek.

Utiliza patrones de diseño avanzados (Factory + Strategy + Template Method) para proporcionar:
- ✅ Extensibilidad: Agregar nuevos tipos de charts sin modificar código existente
- ✅ Validación robusta: Garantizar integridad de datos antes de almacenar
- ✅ Renderización optimizada: Transformaciones inteligentes para mejor rendimiento
- ✅ Separación de responsabilidades: Cada componente tiene un rol claro

---

## Instalación y Setup

### 1. Archivos Necesarios

Los archivos están ubicados en:

```
widget_service/
├── widget_service.py          # Orquestación principal
├── widget_validator.py        # Validación genérica
└── echart/
    ├── base_echart_builder.py     # Clase abstracta
    ├── echart_builders.py         # Implementaciones (Line, Bar, Pie, Scatter)
    ├── echart_factory.py          # Factory
    ├── echart_transforrmer.py     # Transformer
    ├── test_echart_builder.py     # Tests
    └── test_echart_transformer.py # Tests
```

### 2. Imports Requeridos

```python
from daltek.domain.widget_service import WidgetService
from daltek.domain.widget_service.echart import EChartFactory

# Inicializar servicio
service = WidgetService()
```

---

## Ejemplos de Uso

### Crear un Line Chart (Gráfico de Líneas)

```python
# Datos del chart
chart_data = {
    "series": [
        {
            "name": "Ventas 2024",
            "data": [100, 150, 120, 200, 180, 220, 250]
        },
        {
            "name": "Ventas 2023",
            "data": [80, 110, 95, 160, 140, 180, 200]
        }
    ],
    "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"]
}

# Configuración visual
chart_config = {
    "smooth": True,              # Líneas suavizadas
    "fill_area": True,           # Área bajo la línea
    "colors": ["#2196F3", "#4CAF50"],
    "title": "Comparativa de Ventas",
    "yaxis_name": "Monto ($)"
}

# Propiedades del widget
widget_props = {
    "title": "Análisis de Ventas",
    "size": "medium"
}

# Crear el widget
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data=chart_data,
    chart_config=chart_config,
    widget_properties=widget_props
)

if result.get("success"):
    print(f"✓ Widget creado: {result['widget']['id']}")
    # Widget está almacenado en la BD
else:
    print(f"✗ Error: {result['error']}")
```

**Estructura almacenada en BD:**
```json
{
  "id": "widget_1_1701234567890",
  "type": "line",
  "echart_data": {...datos originales...},
  "echart_config": {
    "series": [
      {
        "name": "Ventas 2024",
        "data": [100, 150, 120, 200, 180, 220, 250],
        "type": "line",
        "smooth": true,
        "areaStyle": {"opacity": 0.3}
      },
      ...
    ],
    "xAxis": {"type": "category", "data": ["Ene", "Feb", ...]},
    "yAxis": {"type": "value", "name": "Monto ($)"},
    "color": ["#2196F3", "#4CAF50"],
    "tooltip": {...},
    "legend": {...}
  },
  "created_at": "2024-11-30T10:30:00",
  "modified_at": "2024-11-30T10:30:00"
}
```

---

### Crear un Bar Chart (Gráfico de Barras)

```python
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="bar",
    chart_data={
        "series": [
            {
                "name": "Q1",
                "data": [1000, 1500, 1200, 1800]
            },
            {
                "name": "Q2",
                "data": [1200, 1800, 1500, 2000]
            }
        ],
        "categories": ["Enero", "Febrero", "Marzo", "Abril"]
    },
    chart_config={
        "barWidth": "60%",
        "colors": ["#FF9800", "#F44336"]
    }
)
```

---

### Crear un Pie Chart (Gráfico Circular)

```python
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="pie",
    chart_data={
        "data": [
            {"name": "Chrome", "value": 450},
            {"name": "Firefox", "value": 300},
            {"name": "Safari", "value": 200},
            {"name": "Edge", "value": 150},
        ]
    },
    chart_config={
        "show_labels": True,
        "radius": "50%",
        "colors": ["#2196F3", "#4CAF50", "#FF9800", "#F44336"]
    },
    widget_properties={"title": "Browser Distribution"}
)
```

---

### Crear un Scatter Chart (Gráfico de Dispersión)

```python
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="scatter",
    chart_data={
        "series": [
            {
                "name": "Producto A",
                "data": [
                    [10, 20], [15, 25], [20, 30],
                    [25, 35], [30, 40], [35, 38]
                ]
            },
            {
                "name": "Producto B",
                "data": [
                    [12, 18], [18, 28], [22, 32],
                    [28, 38], [32, 42], [38, 40]
                ]
            }
        ]
    },
    chart_config={
        "symbolSize": 10,
        "xaxis_name": "Cantidad",
        "yaxis_name": "Precio"
    }
)
```

---

## Operaciones CRUD

### Leer Layout

```python
# Obtener todos los widgets
layout = service.get_layout("Dashboard1")

for widget in layout:
    print(f"ID: {widget['id']}")
    print(f"Tipo: {widget['type']}")
    print(f"Creado: {widget['created_at']}")
```

### Actualizar Datos de un Chart

```python
# Actualizar solo los datos (mantiene configuración visual)
result = service.update_echart_data(
    doc_name="Dashboard1",
    widget_id="widget_1_1701234567890",
    chart_data={
        "series": [
            {
                "name": "Ventas 2024",
                "data": [110, 160, 130, 210, 190, 230, 260]  # Nuevos valores
            }
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"]
    }
)

print(result['message'])  # "Datos del EChart actualizados"
```

### Editar Widget Completo

```python
# Reemplazar widget completo (mantiene ID y timestamps)
result = service.edit(
    doc_name="Dashboard1",
    widget_id="widget_1_1701234567890",
    widget_data={
        "type": "line",
        "echart_data": {...},
        "echart_config": {...},
        "properties": {"title": "Nuevo Título"}
    }
)
```

### Eliminar Widget

```python
result = service.delete(
    doc_name="Dashboard1",
    widget_id="widget_1_1701234567890"
)

if result.get("success"):
    print("Widget eliminado")
```

---

## Renderización

### Transformar para Renderización en Cliente

```python
# Preparar widget para enviar a frontend
result = service.transform_echart_for_render(
    doc_name="Dashboard1",
    widget_id="widget_1_1701234567890"
)

if result.get("success"):
    widget = result['widget']
    
    # El widget está optimizado y listo para echarts.js
    # Características aplicadas:
    # - Sampling si hay > 1000 puntos
    # - Colores normalizados
    # - Responsive media queries
    # - Animaciones configuradas
    
    return widget  # Enviar al cliente
```

### Renderizar Layout Completo

```python
# Renderizar todos los widgets del dashboard
result = service.render_layout("Dashboard1")

if result.get("success"):
    widgets = result['widgets']
    layout = result['layout']
    count = result['count']
    
    print(f"Dashboard con {count} widgets lista para renderizar")
```

---

## Validación de Datos

### Validación Automática en Builders

Cada builder valida automáticamente los datos:

```python
# Esto fallará - falta "categories"
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data={
        "series": [{"name": "Data", "data": [1, 2, 3]}]
        # Falta "categories"
    }
)
# result['success'] = False
# result['error'] = "Falta campo 'categories' en datos"
```

```python
# Esto fallará - valores no numéricos
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data={
        "series": [{"name": "Data", "data": [1, "texto", 3]}],
        "categories": ["A", "B", "C"]
    }
)
# result['success'] = False
# result['error'] = "Serie 'Data' posición 1: valor 'texto' no es numérico"
```

---

## Exportación de Datos

### Exportar a Formato Tabular

```python
# Convertir chart a formato tabular (para CSV, Excel)
export_data = service.echart_transformer.transform_data_for_export(widget)

# Para line/bar chart:
# {
#     "type": "tabular",
#     "headers": ["Categoría", "Ventas 2024", "Ventas 2023"],
#     "rows": [
#         ["Ene", 100, 80],
#         ["Feb", 150, 110],
#         ...
#     ]
# }

# Para pie chart:
# {
#     "type": "tabular",
#     "headers": ["Nombre", "Valor", "Porcentaje"],
#     "rows": [
#         ["Chrome", 450, "45.00%"],
#         ["Firefox", 300, "30.00%"],
#         ...
#     ]
# }
```

---

## Tipos de Charts Disponibles

### 1. **Line Chart** - Gráficos de Línea

**Datos requeridos:**
```python
{
    "series": [
        {"name": "Serie1", "data": [num, num, ...]},
        {"name": "Serie2", "data": [num, num, ...]}
    ],
    "categories": ["Cat1", "Cat2", ...]
}
```

**Opciones:**
- `smooth`: Boolean, suavizar líneas
- `fill_area`: Boolean, área bajo la línea
- `yaxis_name`: String, nombre del eje Y
- `min` / `max`: Números, rango del eje Y

**Validaciones:**
- Todas las series deben tener igual cantidad de datos
- Cantidad de datos = cantidad de categorías
- Todos los valores deben ser numéricos

---

### 2. **Bar Chart** - Gráficos de Barras

**Datos requeridos:**
```python
{
    "series": [
        {"name": "Serie1", "data": [num, num, ...]},
        {"name": "Serie2", "data": [num, num, ...]}
    ],
    "categories": ["Cat1", "Cat2", ...]
}
```

**Opciones:**
- `barWidth`: String, ancho de barras (ej: "60%")

---

### 3. **Pie Chart** - Gráficos Circulares

**Datos requeridos:**
```python
{
    "data": [
        {"name": "Nombre1", "value": numero},
        {"name": "Nombre2", "value": numero}
    ]
}
```

**Opciones:**
- `radius`: String, radio del círculo (ej: "50%")
- `show_labels`: Boolean, mostrar etiquetas
- `name`: String, nombre de la serie

**Validaciones:**
- Cada elemento debe tener `name` y `value`
- `value` debe ser numérico

---

### 4. **Scatter Chart** - Gráficos de Dispersión

**Datos requeridos:**
```python
{
    "series": [
        {"name": "Serie1", "data": [[x, y], [x, y], ...]},
        {"name": "Serie2", "data": [[x, y], [x, y], ...]}
    ]
}
```

**Opciones:**
- `symbolSize`: Número, tamaño de símbolos
- `xaxis_name`: String, nombre eje X
- `yaxis_name`: String, nombre eje Y

**Validaciones:**
- Cada punto debe ser [x, y]
- x e y deben ser numéricos

---

## Manejo de Errores

### Errores Comunes y Soluciones

```python
# Error 1: Tipo de chart no existe
try:
    result = service.add_echart(
        doc_name="Dashboard1",
        chart_type="radar",  # No implementado aún
        chart_data={...}
    )
except ValueError as e:
    print(f"Tipos disponibles: {EChartFactory.get_available_types()}")
    # Salida: ['bar', 'line', 'pie', 'scatter']


# Error 2: Documento Daltek no existe
result = service.add_echart(
    doc_name="NoExiste",
    chart_type="line",
    chart_data={...}
)
if not result.get("success"):
    print(result['error'])
    # "Documento Daltek 'NoExiste' no existe"


# Error 3: Datos inválidos
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data={
        "series": [{"name": "Bad", "data": [1, "invalid", 3]}],
        "categories": ["A", "B", "C"]
    }
)
# result['error'] contiene descripción del error


# Error 4: Estructura incompleta
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data={...}  # Falta "categories"
)
# Automáticamente rechazado en validación
```

---

## Extender con Nuevos Charts

### Crear un Nuevo Builder

1. **Heredar de BaseEChartBuilder:**

```python
# En echart_builders.py
from .base_echart_builder import BaseEChartBuilder

class RadarChartBuilder(BaseEChartBuilder):
    def __init__(self):
        self.chart_type = "radar"
    
    def get_chart_type(self) -> str:
        return "radar"
    
    def _validate_data(self) -> bool:
        # Implementar validación específica
        if "series" not in self.data:
            self._add_error("Falta campo 'series'")
            return False
        # ... más validaciones
        return True
    
    def _build_series(self):
        # Implementar construcción específica
        series_list = []
        for serie in self.data["series"]:
            echart_serie = {
                "name": serie.get("name"),
                "data": serie.get("data"),
                "type": "radar",
            }
            series_list.append(echart_serie)
        return series_list
    
    # Otros métodos según necesidad...
```

2. **Registrar en Factory:**

```python
# Al final de echart_builders.py
EChartFactory.register("radar", RadarChartBuilder)
```

3. **Usar inmediatamente:**

```python
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="radar",
    chart_data={...},
    chart_config={...}
)
```

---

## Performance y Optimizaciones

### Optimizaciones Automáticas

El `EChartTransformer` aplica automáticamente:

1. **Sampling de datos grandes**: Si > 1000 puntos, reduce a ~500
2. **Normalización de colores**: Convierte a formato hex válido
3. **Configuración responsive**: Media queries para diferentes dispositivos
4. **Animaciones**: Configuradas para suavidad sin lentitud

### Tips de Performance

```python
# ❌ MAL: Muchos puntos sin necesidad
chart_data = {
    "series": [
        {"name": "Data", "data": list(range(5000))}  # 5000 puntos
    ],
    "categories": list(range(5000))
}

# ✓ BIEN: Datos agregados o resumidos
chart_data = {
    "series": [
        {"name": "Data", "data": [100, 150, 120, ...]}  # ~100-500 puntos
    ],
    "categories": ["Día 1", "Día 2", ...]
}

# El transformer hará sampling automático si es necesario
```

---

## Testing

### Ejecutar Tests

```bash
# Tests de builders y factory
python -m pytest echart/test_echart_builder.py -v

# Tests de transformer
python -m pytest echart/test_echart_transformer.py -v

# Todos los tests
python -m pytest echart/ -v
```

### Escribir Tests Propios

```python
import unittest
from daltek.domain.widget_service import WidgetService

class TestMyDashboard(unittest.TestCase):
    def setUp(self):
        self.service = WidgetService()
    
    def test_create_sales_chart(self):
        """Test crear chart de ventas"""
        result = self.service.add_echart(
            doc_name="Dashboard1",
            chart_type="line",
            chart_data={...},
            chart_config={...}
        )
        
        self.assertTrue(result.get("success"))
        self.assertIn("widget", result)
        self.assertEqual(result['widget']['type'], "line")

if __name__ == "__main__":
    unittest.main()
```

---

## Resumen de Métodos

```python
# WidgetService
service.add_echart(doc_name, chart_type, chart_data, chart_config, widget_props)
service.build_echart(doc_name, widget_id)
service.update_echart_data(doc_name, widget_id, chart_data)
service.transform_echart_for_render(doc_name, widget_id)
service.add(doc_name, widget)
service.edit(doc_name, widget_id, widget_data)
service.delete(doc_name, widget_id)
service.get_layout(doc_name)
service.render_layout(doc_name)

# EChartFactory
EChartFactory.create(chart_type)
EChartFactory.get_available_types()
EChartFactory.is_registered(chart_type)

# EChartTransformer
transformer.transform_widget(widget)
transformer.transform_config(config)
transformer.transform_data_for_export(widget)
transformer.transform_batch(widgets)
```

---

## Referencias

- **Arquitectura**: Ver `ARQUITECTURA_ECHART.md`
- **Diagramas**: Ver `DIAGRAMAS_ECHART.md`
- **Tests**: Ver `echart/test_*.py`
- **Documentación ECharts**: https://echarts.apache.org/en/

---

**¡Listo para usar!** 🚀
