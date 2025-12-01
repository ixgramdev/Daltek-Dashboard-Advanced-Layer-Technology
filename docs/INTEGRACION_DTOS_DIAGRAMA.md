# 🗺️ Mapa de Integración de DTOs - Diagrama Visual

**Última actualización:** 1 de diciembre de 2025

---

## 📊 Arquitectura con DTOs Integrados

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENTE - Frontend                                  │
│                                                                               │
│  Browser: echarts.js + Drag & Drop                                          │
│  Envía: JSON {type, chart_type, echart_data, echart_config, properties}    │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ HTTP POST/GET
                              │ /api/method/...
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CAPA 1: ENDPOINTS (WidgetService)                        │
│                                                                               │
│  ┌─ add_echart(doc_name, chart_type, chart_data, config)                   │
│  │  ✅ EChartWidgetDTO.from_dict() → Create DTO                            │
│  │  ✅ dto.validate() → Check integrity                                     │
│  │  └─ Retorna: {"success": true, "widget": dto.to_dict()}                 │
│  │                                                                            │
│  ├─ add(doc_name, widget)                                                   │
│  │  ✅ WidgetDTO / EChartWidgetDTO.from_dict()                             │
│  │  ✅ dto.validate()                                                       │
│  │  └─ Retorna: {"success": true, "widget": dto.to_dict()}                 │
│  │                                                                            │
│  ├─ edit(doc_name, widget_id, widget_data)                                  │
│  │  ✅ Load existing DTO from DB                                            │
│  │  ✅ Update properties                                                    │
│  │  ✅ dto.validate()                                                       │
│  │  └─ Retorna: {"success": true, "widget": dto.to_dict()}                 │
│  │                                                                            │
│  ├─ render_layout(doc_name)                                                  │
│  │  ✅ Load DTOs from DB                                                    │
│  │  ✅ dto.get_chart_config_for_render() for each                          │
│  │  └─ Retorna: {widgets: [transformed...]}                                 │
│  │                                                                            │
│  └─ get_layout(doc_name)                                                     │
│     ✅ Load Layout JSON from DB                                             │
│     └─ Retorna: [{id, type, ...}, ...]                                      │
│                                                                               │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              CAPA 2: BUILDERS & TRANSFORMERS                                │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │ EChartFactory.create(chart_type) → BaseEChartBuilder          │         │
│  │                                                                 │         │
│  │  ├─ LineChartBuilder.build(data, config)                      │         │
│  │  │  ✅ Validate using DTO                                     │         │
│  │  │  ✅ Return dto.get_chart_config_for_render()              │         │
│  │  │                                                             │         │
│  │  ├─ BarChartBuilder.build(data, config)                       │         │
│  │  │  ✅ Similar flow...                                        │         │
│  │  │                                                             │         │
│  │  ├─ PieChartBuilder.build(data, config)                       │         │
│  │  │  ✅ Similar flow...                                        │         │
│  │  │                                                             │         │
│  │  └─ ScatterChartBuilder.build(data, config)                   │         │
│  │     ✅ Similar flow...                                        │         │
│  │                                                                 │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │ EChartTransformer                                              │         │
│  │                                                                 │         │
│  │  ├─ transform_widget(widget)                                   │         │
│  │  │  ✅ EChartWidgetDTO.from_dict(widget)                      │         │
│  │  │  ✅ dto.get_chart_config_for_render()                      │         │
│  │  │  ✅ Apply optimizations                                     │         │
│  │  │  └─ Return: {id, type, config, data, render_info}         │         │
│  │  │                                                             │         │
│  │  └─ transform_batch(widgets)                                   │         │
│  │     ✅ For each widget: create DTO, validate, transform      │         │
│  │     └─ Return: [transformed_widgets]                          │         │
│  │                                                                 │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                               │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│           CAPA 3: DTO LAYER (Type-Safe Data Transfer)                      │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │  WidgetDTO (@dataclass)                                      │           │
│  │  ├─ id: str                                                  │           │
│  │  ├─ type: str                                                │           │
│  │  ├─ properties: dict[str, Any]                              │           │
│  │  ├─ created_at: str | None                                  │           │
│  │  ├─ modified_at: str | None                                 │           │
│  │  ├─ position: dict[str, int]                                │           │
│  │  │                                                           │           │
│  │  ├─ Methods:                                                 │           │
│  │  │ ├─ to_dict() → dict                                       │           │
│  │  │ ├─ from_dict(data) → WidgetDTO                           │           │
│  │  │ └─ validate() → (bool, list[str])                        │           │
│  │  │                                                           │           │
│  │  └─ Inherits: EChartWidgetDTO                               │           │
│  │                                                           │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────┐           │
│  │  EChartWidgetDTO(WidgetDTO)  [HEREDA]                       │           │
│  │  ├─ chart_type: str                                          │           │
│  │  ├─ echart_data: dict[str, Any]                             │           │
│  │  ├─ echart_config: dict[str, Any]                           │           │
│  │  │                                                           │           │
│  │  ├─ Methods:                                                 │           │
│  │  │ ├─ to_dict() → dict                                       │           │
│  │  │ ├─ from_dict(data) → EChartWidgetDTO                     │           │
│  │  │ ├─ validate() → (bool, list[str])  [Overrides]          │           │
│  │  │ ├─ get_chart_config_for_render() → dict                 │           │
│  │  │ ├─ update_chart_data(new_data) → None                   │           │
│  │  │ └─ update_chart_config(new_config) → None               │           │
│  │  │                                                           │           │
│  │  └─ Ubicación: daltek/daltek/dtos/                          │           │
│  │                                                           │           │
│  └──────────────────────────────────────────────────────────────┘           │
│                                                                               │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  CAPA 4: DATA PERSISTENCE (Frappe DB)                       │
│                                                                               │
│  Frappe Framework                                                            │
│  └─ DocType: Daltek                                                         │
│     ├─ Field: name (string)                                                 │
│     ├─ Field: layout (JSON) ← Almacena widgets como dicts                   │
│     └─ Field: modified_at (datetime)                                        │
│                                                                               │
│  Layout JSON Structure:                                                      │
│  [                                                                           │
│    {                                                                         │
│      "id": "widget_1_1704114000000",                                        │
│      "type": "echart",                                                      │
│      "chart_type": "line",                                                  │
│      "echart_data": {                                                       │
│        "series": [{name, data}, ...],                                       │
│        "categories": [...]                                                  │
│      },                                                                      │
│      "echart_config": {                                                     │
│        "series": [{type, data, ...}, ...],                                  │
│        "xAxis": {...},                                                      │
│        "yAxis": {...}                                                       │
│      },                                                                      │
│      "properties": {                                                        │
│        "title": "Chart Title",                                              │
│        "size": "medium"                                                     │
│      },                                                                      │
│      "position": {"x": 0, "y": 0},                                          │
│      "created_at": "2025-12-01T10:00:00",                                   │
│      "modified_at": "2025-12-01T10:30:00"                                   │
│    },                                                                        │
│    ... más widgets                                                          │
│  ]                                                                           │
│                                                                               │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │
                              ▼ JSON to DTO conversion
```

---

## 🔄 Flujos de Datos Detallados

### Flujo 1: CREATE (add_echart)

```
Input (dict)
    │
    ▼
WidgetService.add_echart()
    │
    ├─ Parse JSON strings → dicts
    │
    ├─ EChartWidgetDTO.from_dict()  ← DTO Created
    │   └─ Set all properties
    │
    ├─ echart_dto.validate()  ← Validation
    │   └─ Check id, type, chart_type, echart_data, echart_config
    │
    ├─ builder = EChartFactory.create(chart_type)
    │
    ├─ builder.build(data, config)
    │   ├─ Temp DTO for validation
    │   ├─ Build configuration
    │   └─ Return: {success, config}
    │
    ├─ widget = {
    │     type: "echart",
    │     chart_type,
    │     echart_data,
    │     echart_config,
    │     properties
    │   }
    │
    ├─ self.add(doc_name, widget)
    │   └─ EChartWidgetDTO.from_dict(widget)
    │   └─ dto.validate()
    │   └─ Save to DB
    │
    ▼
Output: {"success": true, "widget": {...}}
```

### Flujo 2: READ (get_all)

```
Database Layout JSON
    │
    ▼
WidgetService.get_all()
    │
    ├─ Load layout from DB
    │
    ├─ For each widget_dict in layout:
    │   │
    │   ├─ if type == "echart":
    │   │   └─ EChartWidgetDTO.from_dict(widget_dict)  ← DTO Created
    │   └─ else:
    │       └─ WidgetDTO.from_dict(widget_dict)       ← DTO Created
    │
    ├─ dto.validate()  ← Validation
    │
    ├─ dtos_list = [all valid DTOs]
    │
    ▼
Output: {"success": true, "widgets": [dto.to_dict() for dto in dtos_list]}
```

### Flujo 3: UPDATE (edit)

```
Existing widget_dict from DB
    │
    ▼
WidgetService.edit(doc_name, widget_id, widget_data)
    │
    ├─ Load existing widget from DB
    │
    ├─ Create DTO from existing:
    │   └─ EChartWidgetDTO.from_dict(existing_widget)  ← DTO Created
    │
    ├─ Update DTO properties:
    │   │
    │   └─ For each key, value in widget_data:
    │       └─ setattr(dto, key, value)
    │
    ├─ dto.validate()  ← Validation
    │
    ├─ Updated dict = dto.to_dict()
    │
    ├─ Save to DB
    │
    ▼
Output: {"success": true, "widget": dto.to_dict()}
```

### Flujo 4: RENDER (render_layout)

```
Database Layout JSON
    │
    ▼
WidgetService.render_layout()
    │
    ├─ Load layout from DB
    │
    ├─ For each widget_dict in layout:
    │   │
    │   ├─ EChartWidgetDTO.from_dict(widget_dict)  ← DTO Created
    │   │
    │   └─ dto.get_chart_config_for_render()
    │       └─ Return: {id, type, config, data, properties}
    │
    ├─ EChartTransformer.transform_widget(render_config)
    │   │
    │   ├─ Create DTO from render_config
    │   ├─ Optimize data
    │   ├─ Normalize colors
    │   ├─ Add responsive config
    │   └─ Return: optimized config
    │
    ├─ transformed_widgets = [all transformed configs]
    │
    ▼
Output: {
    "success": true,
    "layout": [...],
    "widgets": [optimized configs ready for echarts.js],
    "count": n
}
    │
    ▼
Frontend: echarts.init(dom).setOption(widget.config)
```

### Flujo 5: BUILD (builder.build)

```
chart_data, chart_config (dicts)
    │
    ▼
BaseEChartBuilder.build()
    │
    ├─ Create temp DTO for validation:
    │   └─ EChartWidgetDTO(
    │       id="temp",
    │       type="echart",
    │       chart_type=self.chart_type,
    │       echart_data=data,
    │       echart_config=config
    │   )
    │
    ├─ dto.validate()  ← Early validation
    │   └─ Check chart_type, data, config formats
    │
    ├─ Build configuration:
    │   ├─ _validate_data()
    │   ├─ _build_base_config()
    │   ├─ _build_series()
    │   ├─ _build_axis()
    │   └─ _build_options()
    │
    ├─ Create result DTO:
    │   └─ EChartWidgetDTO(
    │       id="temp",
    │       type="echart",
    │       chart_type=self.chart_type,
    │       echart_data=data,
    │       echart_config=built_config
    │   )
    │
    ├─ Return:
    │   └─ dto.get_chart_config_for_render()
    │
    ▼
Output: {
    "success": true,
    "chart_type": type,
    "config": {id, type, config, data, properties},
    "data": original data
}
```

---

## 📍 Ubicación de Integraciones

```
daltek/
│
├── daltek/
│   │
│   ├── dtos/  ← DTOs (Nuevos)
│   │   ├── __init__.py
│   │   ├── widget_dto.py           [WidgetDTO base]
│   │   └── echart_widget_dto.py    [EChartWidgetDTO extends]
│   │
│   └── domain/
│       │
│       ├── widget_service/
│       │   ├── widget_service.py          ← INTEGRACIÓN 1,2,3,4,5
│       │   │   ├─ add_echart()     → EChartWidgetDTO
│       │   │   ├─ add()            → WidgetDTO / EChartWidgetDTO
│       │   │   ├─ edit()           → WidgetDTO / EChartWidgetDTO
│       │   │   ├─ get_all()        → List[WidgetDTO]
│       │   │   └─ render_layout()  → List[EChartWidgetDTO]
│       │   │
│       │   └── echart/
│       │       ├── base_echart_builder.py     ← INTEGRACIÓN 8
│       │       │   └─ build()     → EChartWidgetDTO for validation
│       │       │
│       │       ├── echart_factory.py         ← INTEGRACIÓN 8 (indirect)
│       │       │   └─ create(type) → Builder
│       │       │
│       │       └── echart_transforrmer.py    ← INTEGRACIÓN 6,7
│       │           ├─ transform_widget()  → EChartWidgetDTO input
│       │           └─ transform_batch()   → List[EChartWidgetDTO]
│       │
│       └── query_service/
│           └── query_service.py        ← INTEGRACIÓN 9
│               └─ get_all()  → List[WidgetDTO]
│
└── docs/
    ├── INTEGRACION_DTOS.md           ← Guía completa
    └── INTEGRACION_DTOS_DIAGRAMA.md  ← Este archivo
```

---

## ✨ Beneficios Visuales

### Antes (Sin DTOs - Dicts genéricos)

```python
# ❌ Sin seguridad de tipos
widget = {
    "id": "widget_1",
    "type": "echart",  # ¿Y si está mal?
    "chart_type": "line",  # ¿Existe esta clave?
    "echart_data": {...},  # ¿Formato correcto?
    "echart_config": {...},  # ¿Validado?
    "properties": {...},
    "position": {"x": 0}  # ¿Falta "y"?
}

# Acceso sin validación
config = widget["echart_config"]
chart_type = widget.get("chart_type", "line")  # Default silencioso
```

### Después (Con DTOs - Type-Safe)

```python
# ✅ Seguridad de tipos
echart_dto = EChartWidgetDTO(
    id="widget_1",
    type="echart",
    chart_type="line",
    echart_data={...},
    echart_config={...},
    properties={...},
    position={"x": 0, "y": 0}
)

# ✅ Validación automática
is_valid, errors = echart_dto.validate()
if not is_valid:
    # Errores claros y específicos
    # "Position debe contener las claves 'x' e 'y'"

# ✅ Acceso seguro con IDE support
config = echart_dto.get_chart_config_for_render()
chart_type = echart_dto.chart_type  # Type hint disponible
```

---

## 🎯 Plan de Implementación por Fases

### Fase 1: Estabilización (Semana 1)
- [ ] Crear tests para DTOs
- [ ] Documentar casos de uso
- [ ] Revisar con el equipo

### Fase 2: Integración Primaria (Semana 2)
- [ ] Actualizar `WidgetService.add_echart()`
- [ ] Actualizar `WidgetService.add()`
- [ ] Tests de integración

### Fase 3: Integración Secundaria (Semana 3)
- [ ] Actualizar `EChartTransformer`
- [ ] Actualizar `BaseEChartBuilder`
- [ ] Tests de transformación

### Fase 4: Migración de Datos (Semana 4)
- [ ] Script de validación de datos existentes
- [ ] Migración gradual
- [ ] Backups preventivos

---

**Status:** Propuesta completa  
**Next:** Implementación de Fase 1
