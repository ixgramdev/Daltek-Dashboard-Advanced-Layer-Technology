# Arquitectura de ECharts en WidgetService

## Visión General

Sistema centralizado para gestionar la creación, validación, almacenamiento y renderización de gráficos ECharts dentro del dashboard Daltek. Utiliza patrones **Strategy** y **Factory** para mantener código limpio, extensible y mantenible.

---

## Arquitectura en Capas

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Frontend)                       │
│              Renderiza con echarts.js                         │
└──────────────────────┬──────────────────────────────────────┘
                       │ JSON transformado
┌──────────────────────▼──────────────────────────────────────┐
│              EChartTransformer                               │
│    Transforma config → Renderización                        │
│    - Optimización de datos                                  │
│    - Normalización de colores                               │
│    - Adaptación responsive                                  │
│    - Exportación de datos                                   │
└──────────────────────┬──────────────────────────────────────┘
                       │ Config JSON almacenada
┌──────────────────────▼──────────────────────────────────────┐
│                   WidgetService                              │
│           Orquestación de Widgets                            │
│    - CRUD de widgets                                        │
│    - Delegación a EChartFactory                             │
│    - Gestión de layout                                      │
│    - Persistencia en BD                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Demanda crear chart
┌──────────────────────▼──────────────────────────────────────┐
│              EChartFactory (Patrón Factory)                  │
│         Retorna builder según tipo                          │
│    - Registry de types disponibles                          │
│    - Manejo de errores                                      │
│    - Extensible para nuevos tipos                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────┐
        │              │              │              │
    ┌───▼──┐      ┌───▼──┐      ┌───▼──┐      ┌───▼──┐
    │ Line │      │ Bar  │      │ Pie  │      │Scatter
    └──────┘      └──────┘      └──────┘      └──────┘
        │              │              │              │
        └──────────────┼──────────────┴──────────────┘
                       │ (Heredan de)
┌──────────────────────▼──────────────────────────────────────┐
│         BaseEChartBuilder (Clase Abstracta)                 │
│      Define contrato para todos los builders                │
│    - build(): Template Method Pattern                       │
│    - _validate_data()                                       │
│    - _build_series()                                        │
│    - _build_xaxis() / _build_yaxis()                       │
│    - _build_options()                                       │
│    - Métodos helper reutilizables                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Patrones de Diseño Utilizados

### 1. **Strategy Pattern** (BaseEChartBuilder + Subclases)
Cada tipo de chart implementa su propia estrategia de construcción.

```python
# Diferentes estrategias
LineChartBuilder    # Implementa para gráficos de línea
BarChartBuilder     # Implementa para barras
PieChartBuilder     # Implementa para pasteles
ScatterChartBuilder # Implementa para dispersión
```

**Ventaja**: Cambiar comportamiento en tiempo de ejecución según el tipo de chart.

### 2. **Factory Pattern** (EChartFactory)
Centraliza la creación de builders, ocultando la lógica de instanciación.

```python
builder = EChartFactory.create("line")      # Retorna LineChartBuilder
builder = EChartFactory.create("bar")       # Retorna BarChartBuilder
builder = EChartFactory.create("pie")       # Retorna PieChartBuilder
```

**Ventaja**: Agregar nuevos tipos sin modificar código cliente.

### 3. **Template Method Pattern** (BaseEChartBuilder.build())
Define el esqueleto del algoritmo, permitiendo que subclases personalicen pasos específicos.

```python
def build(data, config):
    1. Validar datos         (_validate_data)
    2. Config base           (_build_base_config)
    3. Construir series      (_build_series)      ← Específico de cada builder
    4. Construir ejes        (_build_xaxis/yaxis) ← Específico de cada builder
    5. Opciones visuales     (_build_options)
    6. Retornar resultado
```

---

## Flujo de Datos

### Agregar un nuevo EChart:

```python
# 1. Cliente envía widget JSON
widget_data = {
    "type": "line",
    "echart_data": {
        "series": [{"name": "Sales", "data": [100, 200, 150]}],
        "categories": ["Jan", "Feb", "Mar"]
    },
    "properties": {"title": "Sales Chart"}
}

# 2. WidgetService.add_echart()
result = widget_service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data=widget_data["echart_data"],
    chart_config=widget_data["properties"]
)

# 3. Internamente:
#    a) Factory crea LineChartBuilder
builder = EChartFactory.create("line")

#    b) Builder valida y construye config
echart_config = builder.build(chart_data, chart_config)

#    c) WidgetService almacena widget con configuración
#       En BD: layout = [{
#           "id": "widget_1_1234567890",
#           "type": "line",
#           "echart_data": {...datos originales...},
#           "echart_config": {...config construida...}
#       }]

# 4. Resultado retorna al cliente
{
    "success": true,
    "widget": {...widget_data...},
    "layout": [...]
}
```

### Renderizar un EChart:

```python
# 1. Cliente solicita renderización
widget = widget_service.transform_echart_for_render(
    doc_name="Dashboard1",
    widget_id="widget_1_1234567890"
)

# 2. EChartTransformer procesa:
#    - Optimiza datos grandes (sampling)
#    - Normaliza colores
#    - Añade configuración responsive
#    - Prepara para echarts.js

# 3. Cliente recibe widget transformado
{
    "id": "widget_1_1234567890",
    "type": "line",
    "echart_config": {
        "series": [...],
        "xAxis": {...},
        "yAxis": {...},
        "animationDuration": 500,
        "responsive": {...},
        ...
    }
}

# 4. Frontend renderiza con echarts.js
var chart = echarts.init(dom);
chart.setOption(widget.echart_config);
```

---

## Estructura de Clases

### BaseEChartBuilder (Abstracta)

```python
class BaseEChartBuilder(ABC):
    
    # Métodos públicos
    build(data: dict, config: dict) -> dict
    
    # Métodos abstractos (implementar en subclases)
    @abstractmethod
    _validate_data() -> bool
    
    @abstractmethod
    _build_series() -> list
    
    @abstractmethod
    get_chart_type() -> str
    
    # Métodos template (personalizar en subclases)
    def _build_xaxis() -> dict
    def _build_yaxis() -> dict
    def _should_have_xaxis() -> bool
    def _should_have_yaxis() -> bool
    
    # Métodos helpers (reutilizables)
    _get_legend_data()
    _get_default_colors()
    _normalize_series_name()
    _add_error()
    @staticmethod
    validate_numeric_data()
    @staticmethod
    ensure_numeric()
```

### LineChartBuilder (Subclase)

```python
class LineChartBuilder(BaseEChartBuilder):
    def __init__(self):
        self.chart_type = "line"
    
    def _validate_data(self) -> bool:
        # Validar: series, categories, datos numéricos
        # Validar cantidad coincida
    
    def _build_series(self) -> list:
        # Construir array con series de tipo "line"
        # Agregar smooth, fill_area si está configurado
    
    def _should_have_xaxis(self) -> bool:
        return True
    
    def _should_have_yaxis(self) -> bool:
        return True
```

### EChartFactory

```python
class EChartFactory:
    _builders: Dict[str, Type[BaseEChartBuilder]] = {}
    
    @classmethod
    def register(chart_type: str, builder_class: Type) -> None
    
    @classmethod
    def create(chart_type: str) -> BaseEChartBuilder
    
    @classmethod
    def get_available_types() -> list[str]
    
    @classmethod
    def is_registered(chart_type: str) -> bool
```

### WidgetService

```python
class WidgetService:
    def add_echart(doc_name, chart_type, chart_data, chart_config) -> dict
    
    def build_echart(doc_name, widget_id) -> dict
    
    def update_echart_data(doc_name, widget_id, chart_data) -> dict
    
    def transform_echart_for_render(doc_name, widget_id) -> dict
    
    def _build_echart(widget_data) -> dict
```

### EChartTransformer

```python
class EChartTransformer:
    def transform_widget(widget: dict) -> dict
    
    def transform_config(config: dict) -> dict
    
    def transform_data_for_export(widget: dict) -> dict
    
    def transform_batch(widgets: list) -> list
    
    # Métodos privados
    _optimize_large_data()
    _normalize_colors()
    _optimize_tooltip()
    _get_responsive_config()
    _transform_for_export_axis_chart()
    _transform_for_export_pie_chart()
    _transform_for_export_scatter()
```

---

## Ejemplos de Uso

### Crear un Line Chart

```python
service = WidgetService()

result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data={
        "series": [
            {"name": "Ventas", "data": [100, 150, 120, 200, 180]},
            {"name": "Ganancias", "data": [30, 50, 40, 70, 60]},
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr", "May"]
    },
    chart_config={
        "smooth": True,
        "fill_area": True,
        "colors": ["#2196F3", "#4CAF50"],
        "title": "Ventas vs Ganancias"
    },
    widget_properties={"title": "Monthly Performance"}
)
```

### Crear un Pie Chart

```python
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="pie",
    chart_data={
        "data": [
            {"name": "Chrome", "value": 450},
            {"name": "Firefox", "value": 300},
            {"name": "Safari", "value": 200},
        ]
    },
    chart_config={
        "show_labels": True,
        "radius": "50%"
    },
    widget_properties={"title": "Browser Usage"}
)
```

### Actualizar datos de un Chart

```python
result = service.update_echart_data(
    doc_name="Dashboard1",
    widget_id="widget_1_1234567890",
    chart_data={
        "series": [
            {"name": "Ventas", "data": [120, 160, 130, 210, 190]},
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr", "May"]
    }
)
```

### Renderizar un Chart

```python
result = service.transform_echart_for_render(
    doc_name="Dashboard1",
    widget_id="widget_1_1234567890"
)

# El widget está listo para echarts.js en el cliente
```

---

## Extensibilidad

### Agregar un nuevo tipo de Chart

1. **Crear nueva subclase** en `echart_builders.py`:

```python
class GaugeChartBuilder(BaseEChartBuilder):
    def __init__(self):
        self.chart_type = "gauge"
    
    def _validate_data(self) -> bool:
        # Validaciones específicas del gauge
        pass
    
    def _build_series(self) -> list:
        # Construcción específica del gauge
        pass
    
    def get_chart_type(self) -> str:
        return "gauge"
```

2. **Registrar en Factory**:

```python
EChartFactory.register("gauge", GaugeChartBuilder)
```

3. **Usar inmediatamente**:

```python
service.add_echart(
    doc_name="Dashboard1",
    chart_type="gauge",
    chart_data={...},
    chart_config={...}
)
```

---

## Ventajas de esta Arquitectura

✅ **Separation of Concerns**: Cada clase tiene una responsabilidad única
✅ **Extensibilidad**: Agregar nuevos tipos sin tocar código existente
✅ **Reutilización**: Métodos comunes en base abstracta
✅ **Validación**: Validación centralizada antes de construir
✅ **Mantenibilidad**: Código limpio y fácil de entender
✅ **Testabilidad**: Cada componente puede testearse aisladamente
✅ **Flexibilidad**: Estrategias intercambiables en tiempo de ejecución

---

## Archivos del Sistema

```
widget_service/
├── __init__.py
├── widget_service.py           # Servicio principal (CRUD + orquestación)
├── widget_validator.py         # Validación de widgets genéricos
└── echart/
    ├── __init__.py
    ├── base_echart_builder.py   # Clase abstracta base
    ├── echart_builders.py       # Implementaciones: Line, Bar, Pie, Scatter
    ├── echart_factory.py        # Factory para crear builders
    ├── echart_transforrmer.py   # Transforma para renderización
    ├── test_echart_builder.py   # Tests de builders y factory
    └── test_echart_transformer.py # Tests del transformer
```

---

## Próximos Pasos

1. ✅ Completar implementación de builders adicionales (Radar, Gauge)
2. ⬜ Integración con datos en tiempo real (WebSocket)
3. ⬜ Caché de configuraciones frecuentes
4. ⬜ Análisis y optimización de rendimiento
5. ⬜ Documentación de API REST
6. ⬜ Panel de administración de widgets
