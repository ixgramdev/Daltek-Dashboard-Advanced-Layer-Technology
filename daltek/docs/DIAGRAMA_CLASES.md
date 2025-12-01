# 📐 Diagrama de Clases - Sistema ECharts

## UML Simplificado

```
┌─────────────────────────────────────────────────────────────────────┐
│                      BaseEChartBuilder (Abstract)                    │
├─────────────────────────────────────────────────────────────────────┤
│ - chart_type: str                                                    │
│ - data: Dict[str, Any]                                               │
│ - config: Dict[str, Any]                                             │
│ - errors: List[str]                                                  │
├─────────────────────────────────────────────────────────────────────┤
│ + build(data, config) → Dict                    [Template Method]    │
│ + get_chart_type() → str                        [Abstract]           │
│ # _validate_data() → bool                       [Abstract]           │
│ # _build_series() → List                        [Abstract]           │
│ # _build_base_config() → Dict                                        │
│ # _build_options() → Dict                                            │
│ # _build_xaxis() → Dict                                              │
│ # _build_yaxis() → Dict                                              │
│ # _should_have_xaxis() → bool                                        │
│ # _should_have_yaxis() → bool                                        │
│ # _get_legend_data() → List                                          │
│ # _normalize_series_name(name) → str                                 │
│ + validate_numeric_data(value) → bool           [Static]            │
│ + ensure_numeric(value, default) → float        [Static]            │
└─────────────────────────────────────────────────────────────────────┘
                    △                   △                   △
                    │                   │                   │
         ┌──────────┴──────────┐  ┌─────┴────────┐  ┌─────┴────────┐
         │                     │  │              │  │              │
         │                     │  │              │  │              │
    ┌────┴────────┐   ┌───────┴──┴──┐  ┌───────┴──┴──┐  ┌────────┴─────┐
    │LineChart    │   │BarChart     │  │PieChart     │  │ScatterChart   │
    │Builder      │   │Builder       │  │Builder      │  │Builder        │
    ├─────────────┤   ├─────────────┤  ├─────────────┤  ├───────────────┤
    │_validate_   │   │_validate_   │  │_validate_   │  │_validate_     │
    │  data()     │   │  data()     │  │  data()     │  │  data()       │
    │             │   │             │  │             │  │               │
    │_build_      │   │_build_      │  │_build_      │  │_build_        │
    │  series()   │   │  series()   │  │  series()   │  │  series()     │
    │             │   │             │  │             │  │               │
    │_build_      │   │_build_      │  │No axes      │  │_build_xaxis() │
    │  xaxis()    │   │  xaxis()    │  │             │  │               │
    │             │   │             │  │_build_base_ │  │_build_yaxis() │
    │_build_      │   │_build_yaxis │  │  config()   │  │               │
    │  yaxis()    │   │             │  │(override)   │  │[x,y] points]  │
    └─────────────┘   └─────────────┘  └─────────────┘  └───────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                    EChartFactory (Static)                        │
├──────────────────────────────────────────────────────────────────┤
│ - _builders: Dict[str, Type[BaseEChartBuilder]]                  │
├──────────────────────────────────────────────────────────────────┤
│ + register(chart_type, builder_class)                           │
│ + create(chart_type) → BaseEChartBuilder                        │
│ + get_available_types() → List[str]                             │
│ + is_registered(chart_type) → bool                              │
│ + unregister(chart_type) → bool                                 │
│ + reset()                                                        │
│ + get_registry() → Dict                                          │
└──────────────────────────────────────────────────────────────────┘
          │
          │ <<creates>>
          │
          ├──→ LineChartBuilder
          ├──→ BarChartBuilder
          ├──→ PieChartBuilder
          └──→ ScatterChartBuilder


┌──────────────────────────────────────────────────────────────────┐
│                EChartTransformer                                 │
├──────────────────────────────────────────────────────────────────┤
│ - optimizations_enabled: bool                                    │
│ - cache_enabled: bool                                            │
│ - _cache: Dict                                                   │
├──────────────────────────────────────────────────────────────────┤
│ + transform_widget(widget) → Dict                                │
│ + transform_config(config) → Dict                                │
│ + transform_data_for_export(widget) → Dict                       │
│ + transform_batch(widgets) → List                                │
│ # _optimize_large_data(config) → Dict                            │
│ # _normalize_colors(colors) → List                               │
│ # _optimize_tooltip(tooltip) → Dict                              │
│ # _get_responsive_config() → Dict                                │
│ # _transform_for_export_axis_chart(data) → Dict                  │
│ # _transform_for_export_pie_chart(data) → Dict                   │
│ # _transform_for_export_scatter(data) → Dict                     │
│ + clear_cache()                                                  │
└──────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│                WidgetService                                     │
├──────────────────────────────────────────────────────────────────┤
│ - validator: WidgetValidator                                     │
│ - echart_factory: EChartFactory                                  │
│ - echart_transformer: EChartTransformer                          │
├──────────────────────────────────────────────────────────────────┤
│                    CRUD Methods                                  │
│ + add(doc_name, widget) → Dict                                   │
│ + edit(doc_name, widget_id, widget_data) → Dict                 │
│ + delete(doc_name, widget_id) → Dict                             │
│ + get_layout(doc_name) → List                                    │
│ + render_layout(doc_name) → Dict                                 │
│                                                                  │
│              EChart Specialized Methods                          │
│ + add_echart(doc_name, chart_type, chart_data,                  │
│              chart_config, widget_props) → Dict                 │
│ + build_echart(doc_name, widget_id) → Dict                      │
│ + update_echart_data(doc_name, widget_id,                       │
│                      chart_data) → Dict                         │
│ + transform_echart_for_render(doc_name,                         │
│                               widget_id) → Dict                 │
│                                                                  │
│               Helper Methods                                     │
│ # _build_echart(widget_data) → Dict                              │
│ # _parse_layout(layout_data) → List                              │
│ # _generate_widget_id(layout) → str                              │
│ # _process_widgets_for_render(layout) → List                     │
└──────────────────────────────────────────────────────────────────┘
      │                    │                     │
      │ uses               │ creates             │ transforms
      │                    │                     │
      ▼                    ▼                     ▼
  ┌─────────┐      ┌──────────────┐    ┌─────────────────┐
  │Validator│      │ Factory      │    │ Transformer     │
  └─────────┘      └──────────────┘    └─────────────────┘


┌──────────────────────────────────────────────────────────────────┐
│              Widget (Stored in Daltek.layout)                    │
├──────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "id": "widget_1_1701234567890",                               │
│   "type": "line",                      ← Tipo de chart          │
│   "echart_data": {                     ← Datos originales       │
│     "series": [...],                                            │
│     "categories": [...]                                         │
│   },                                                             │
│   "echart_config": {                   ← Config construida      │
│     "series": [...],                                            │
│     "xAxis": {...},                                             │
│     "yAxis": {...},                                             │
│     "color": [...],                                             │
│     "tooltip": {...},                                           │
│     "legend": {...}                                             │
│   },                                                             │
│   "properties": {                      ← Props del widget       │
│     "title": "Sales Chart"                                      │
│   },                                                             │
│   "created_at": "2024-11-30T10:30:00",                         │
│   "modified_at": "2024-11-30T10:30:00"                         │
│ }                                                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Relaciones entre Componentes

```
┌────────────────────────────────────────────────────────┐
│                    WidgetService                        │
└────────────────────────────────────────────────────────┘
              │         │           │
              │         │           └─ Usa WidgetValidator
              │         │
              │         └─ Crea builders mediante ↓
              │
              ▼
        ┌──────────────┐
        │ EChartFactory│ ──→ [LineChartBuilder]
        ├──────────────┤     [BarChartBuilder]
        │   Registry   │     [PieChartBuilder]
        │   (4 tipos)  │     [ScatterChartBuilder]
        └──────────────┘
              
        Cada builder hereda de BaseEChartBuilder
        y define su propia validación y construcción


┌────────────────────────────────────────────────────────┐
│         Data Flow: Create → Store → Render             │
└────────────────────────────────────────────────────────┘

1. Cliente envía datos
         │
         ▼
2. WidgetService.add_echart()
         │
         ├─→ Valida con Validator
         │
         ├─→ Crea builder con Factory
         │
         ├─→ Builder.build() construye config
         │
         └─→ Almacena widget en BD (JSON)
         │
         ▼
3. Widget guardado en Daltek.layout
         │
         ▼
4. Cliente solicita renderización
         │
         ▼
5. WidgetService.transform_echart_for_render()
         │
         ├─→ Obtiene widget de BD
         │
         ├─→ Usa Transformer para optimizar
         │
         │   ├─ Sampling
         │   ├─ Colores
         │   ├─ Responsive
         │   └─ Animación
         │
         └─→ Retorna widget transformado
         │
         ▼
6. Frontend recibe widget
         │
         ▼
7. echarts.js.setOption(widget.echart_config)
         │
         ▼
8. Gráfico renderizado en pantalla
```

---

## 📋 Tabla de Responsabilidades

| Componente | Responsabilidad |
|-----------|-----------------|
| **BaseEChartBuilder** | Definir estructura común, Template Method |
| **LineChartBuilder** | Validar y construir line charts |
| **BarChartBuilder** | Validar y construir bar charts |
| **PieChartBuilder** | Validar y construir pie charts |
| **ScatterChartBuilder** | Validar y construir scatter charts |
| **EChartFactory** | Crear builders, Registry de tipos |
| **WidgetService** | Orquestar CRUD, gestionar widgets |
| **EChartTransformer** | Optimizar para renderización |
| **WidgetValidator** | Validar widgets genéricos |

---

## 🎯 Métodos Clave y Su Flujo

### BaseEChartBuilder.build()

```python
def build(data, config):
    # Template Method - Orden fijo
    1. _validate_data()          # Abstracto - Subclase implementa
    2. _build_base_config()      # Común a todos
    3. _build_series()           # Abstracto - Subclase implementa
    4. _build_xaxis()            # Template - Personalizable
    5. _build_yaxis()            # Template - Personalizable
    6. _build_options()          # Común a todos
    
    return {
        "success": True/False,
        "config": {...},
        "error": "..." (si falla)
    }
```

### EChartFactory.create()

```python
def create(chart_type):
    1. Normalizar tipo (lowercase)
    2. Verificar en registry
    3. Si no existe → ValueError
    4. Si existe → Instanciar builder
    5. Retornar builder
```

### WidgetService.add_echart()

```python
def add_echart(doc_name, chart_type, chart_data, config):
    1. Validar tipo en Factory
    2. Crear builder
    3. Builder.build() → echart_config
    4. Crear widget con config
    5. Guardar en BD
    6. Retornar resultado
```

### EChartTransformer.transform_config()

```python
def transform_config(config):
    1. Optimizar datos grandes
    2. Normalizar colores
    3. Optimizar tooltip
    4. Agregar animaciones
    5. Configuración responsive
    6. Retornar config optimizada
```

---

## 🔍 Jerarquía de Herencia

```
Object (Python)
  │
  └─→ BaseEChartBuilder (Abstract)
      │
      ├─→ LineChartBuilder
      ├─→ BarChartBuilder
      ├─→ PieChartBuilder
      └─→ ScatterChartBuilder

```

---

## 💾 Persistencia

```
Frontend (JSON)
    │
    ▼
WidgetService.add_echart()
    │
    ▼
widget = {
    "id": "...",
    "type": "line",
    "echart_data": {...},
    "echart_config": {...},
    ...
}
    │
    ▼
frappe.db.set_value(
    "Daltek",
    doc_name,
    "layout",
    JSON.dumps(widget)
)
    │
    ▼
MySQL/MariaDB
├─ Daltek table
│  └─ layout column (JSON field)
│     └─ Array de widgets
```

---

## 🚀 Extensión

Para agregar un nuevo chart:

```
1. Crear clase → extends BaseEChartBuilder
2. Implementar métodos abstractos
3. Registrar → EChartFactory.register()
4. ¡Listo!

No tocar:
- EChartFactory (solo registrar)
- WidgetService (funciona automáticamente)
- EChartTransformer (genérico)
```

---

## 📊 Interacciones Clave

```
[Cliente]
   │
   ├─→ POST /api/method/add_echart
   │   └─→ WidgetService.add_echart()
   │
   └─→ GET /api/method/transform_echart_for_render
       └─→ WidgetService.transform_echart_for_render()


[WidgetService]
   │
   ├─→ Llama EChartFactory.create()
   │   └─→ Retorna builder específico
   │
   ├─→ Llama builder.build()
   │   └─→ Retorna echart_config
   │
   ├─→ Llamaa EChartTransformer
   │   └─→ Retorna widget optimizado
   │
   └─→ Llamaa frappe.db para persistencia
       └─→ Almacena en BD


[Frontend]
   │
   └─→ echarts.js.setOption(widget.echart_config)
       └─→ Renderiza gráfico
```

---

**Diagrama generado**: 30 de noviembre de 2024
**Versión**: v1.0.0
