# Diagramas de Flujo - Sistema ECharts

## 1. Diagrama de Flujo: Crear un Widget EChart

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Frontend)                        │
│  Prepara datos del chart (series, categories, etc)          │
│  JSON: {                                                     │
│    type: "line",                                            │
│    echart_data: {...},                                      │
│    properties: {...}                                        │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ POST /api/method/add_echart
                       │ {doc_name, chart_type, chart_data, config}
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              WidgetService.add_echart()                      │
│                                                              │
│  1. Parsear strings a dicts                                 │
│  2. Validar tipo registrado en Factory                      │
│  3. Crear builder mediante Factory                          │
│  4. Construir config del chart                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│            EChartFactory.create(chart_type)                  │
│                                                              │
│  if type == "line":                                         │
│      return LineChartBuilder()                              │
│  elif type == "bar":                                        │
│      return BarChartBuilder()                               │
│  elif type == "pie":                                        │
│      return PieChartBuilder()                               │
│  else:                                                      │
│      raise ValueError(...)                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│          builder.build(chart_data, chart_config)            │
│                                                              │
│  TEMPLATE METHOD:                                           │
│  1. _validate_data()      ← Subclase implementa            │
│  2. _build_base_config()                                    │
│  3. _build_series()       ← Subclase implementa            │
│  4. _build_xaxis()        ← Subclase (si aplica)           │
│  5. _build_yaxis()        ← Subclase (si aplica)           │
│  6. _build_options()      ← Normaliza colores, etc         │
│  7. Retorna config completo                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ ¿Validación OK?
                       │
        ┌──────────────┴──────────────┐
        │ SÍ                          │ NO
        ▼                             ▼
┌──────────────────────┐      ┌──────────────────┐
│ Crear widget con     │      │ Error: Datos     │
│ config almacenada    │      │ inválidos        │
└──────────┬───────────┘      └────────┬─────────┘
           │                           │
           └──────────┬────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│         WidgetService.add()                                 │
│                                                              │
│  1. Generar ID único                                        │
│  2. Añadir timestamps (created_at, modified_at)             │
│  3. Agregar a layout                                        │
│  4. Guardar en BD (frappe.db.set_value)                     │
└─────────────────────┬──────────────────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────────────────┐
│              Respuesta al Cliente                            │
│  {                                                           │
│    "success": true,                                         │
│    "widget": {...widget_data...},                           │
│    "layout": [...updated_layout...]                         │
│  }                                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama de Validación: LineChartBuilder

```
┌─────────────────────────────────────────────────────────────┐
│              Datos de entrada (chart_data)                   │
│  {                                                           │
│    "series": [...],                                         │
│    "categories": [...]                                      │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ ¿Existe campo "series"?      │
        └──────────┬──────────┬────────┘
                  SÍ          NO
                   │           │
                   │           └──► ERROR: Falta "series"
                   │
                   ▼
        ┌──────────────────────────────┐
        │ ¿"series" es lista no vacía? │
        └──────────┬──────────┬────────┘
                  SÍ          NO
                   │           │
                   │           └──► ERROR: "series" vacía
                   │
                   ▼
     ┌─────────────────────────────────────┐
     │ Para cada serie en series:          │
     │ - ¿Es diccionario?                  │
     │ - ¿Tiene "name"?                    │
     │ - ¿Tiene "data"?                    │
     │ - ¿"data" es lista no vacía?        │
     │ - ¿Todos los valores son números?  │
     └──────────┬──────────┬───────────────┘
               SÍ           NO
                │            │
                │            └──► ERROR: Serie inválida
                │
                ▼
        ┌──────────────────────────────┐
        │ ¿Existe "categories"?        │
        └──────────┬──────────┬────────┘
                  SÍ          NO
                   │           │
                   │           └──► ERROR: Falta "categories"
                   │
                   ▼
        ┌──────────────────────────────┐
        │ ¿Cantidad de categorías ==   │
        │  cantidad de datos en        │
        │  primera serie?              │
        └──────────┬──────────┬────────┘
                  SÍ          NO
                   │           │
                   │           └──► ERROR: Mismatch
                   │
                   ▼
            ✓ VÁLIDO
```

---

## 3. Diagrama de Decisión: EChartFactory.create()

```
┌─────────────────────────────────────────────────────────────┐
│              chart_type (string)                             │
│  ej: "line", "Line", "LINE"                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │ Convertir a lowercase:       │
        │ chart_type = chart_type.    │
        │            lower()           │
        └──────────────────┬───────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │ ¿Existe en registry?                 │
        │ if chart_type in _builders:          │
        └──────────┬──────────┬────────────────┘
                  SÍ           NO
                   │            │
                   │            └──► ValueError
                   │
                   ▼
        ┌──────────────────────────────┐
        │ Obtener clase builder:       │
        │ builder_class =              │
        │  _builders[chart_type]       │
        └──────────────────┬───────────┘
                           │
                           ▼
        ┌──────────────────────────────┐
        │ Instanciar y retornar:       │
        │ return builder_class()       │
        │                              │
        │ ej: LineChartBuilder()       │
        │     BarChartBuilder()        │
        │     PieChartBuilder()        │
        └──────────────────────────────┘
```

---

## 4. Diagrama de Transformación: EChartTransformer

```
┌─────────────────────────────────────────────────────────────┐
│              Widget (con echart_config almacenado)           │
│  {                                                           │
│    "id": "widget_1",                                        │
│    "type": "line",                                          │
│    "echart_config": {...}                                   │
│  }                                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
      ┌────────────────────────────────────┐
      │ transformer.transform_widget()     │
      └─────────────────┬──────────────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
          ▼             ▼             ▼
     ┌────────┐    ┌──────────┐   ┌──────────┐
     │Transform│    │Agregar   │   │Optimizar │
     │config   │    │render_   │   │data      │
     │         │    │info      │   │          │
     └────────┘    └──────────┘   └──────────┘
          │             │             │
          └─────────────┼─────────────┘
                        │
                        ▼
      ┌────────────────────────────────────┐
      │ transform_config(echart_config)    │
      │                                    │
      │ Aplica:                           │
      │ 1. Optimización de datos grandes  │
      │ 2. Normalización de colores       │
      │ 3. Optimización de tooltips       │
      │ 4. Configuración responsive       │
      │ 5. Animación default              │
      └─────────────────┬──────────────────┘
                        │
      ┌─────────────────┼─────────────────┐
      │                 │                 │
      ▼                 ▼                 ▼
   ┌────────┐        ┌────────┐      ┌────────┐
   │Sampling│        │Hex     │      │Media   │
   │si > 1k │        │#RRGGBB │      │queries │
   │puntos  │        │format  │      │        │
   └────────┘        └────────┘      └────────┘
      │                 │                 │
      └─────────────────┼─────────────────┘
                        │
                        ▼
      ┌────────────────────────────────────┐
      │        Widget transformado         │
      │  Listo para enviar al cliente      │
      │  {                                 │
      │    ...widget original...,         │
      │    echart_config: {...optimizado  │
      │    render_info: {...}             │
      │  }                                 │
      └────────────────────────────────────┘
```

---

## 5. Tabla Comparativa de Builders

```
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Propiedad    │ LineChart    │ BarChart     │ PieChart     │ ScatterChart │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Tipo datos   │ series +     │ series +     │ data array   │ series con   │
│              │ categories   │ categories   │ (name,value) │ [x,y] points │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ¿X-Axis?     │ SÍ           │ SÍ           │ NO           │ SÍ           │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ ¿Y-Axis?     │ SÍ           │ SÍ           │ NO           │ SÍ           │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Serie type   │ "line"       │ "bar"        │ "pie"        │ "scatter"    │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Opciones     │ smooth,      │ barWidth     │ radius,      │ symbolSize   │
│ típicas      │ fill_area    │              │ show_labels  │              │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ Validación   │ 1. Series    │ 1. Series    │ 1. Data      │ 1. Series    │
│ clave        │ 2. Categories│ 2. Categories│ 2. name+     │ 2. [x,y]     │
│              │ 3. Match qty │ 3. Match qty │    value     │ 3. Numeric   │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 6. Ciclo de Vida de un Widget EChart

```
┌──────────────────────────────────────────────────────────────┐
│ ESTADO 1: CREACIÓN                                           │
│ - Cliente prepara datos                                      │
│ - Llama a WidgetService.add_echart()                         │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ ESTADO 2: VALIDACIÓN & CONSTRUCCIÓN                          │
│ - Factory crea builder apropiado                             │
│ - Builder valida datos                                       │
│ - Builder construye configuración EChart                     │
│ - Config almacenada en widget                                │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ ESTADO 3: PERSISTENCIA                                       │
│ - WidgetService.add() guarda en BD                           │
│ - Frappe.db.set_value() serializa JSON                       │
│ - Widget con ID único está listo                             │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ ESTADO 4: RECUPERACIÓN                                       │
│ - Cliente solicita renderización                             │
│ - WidgetService.get_layout() recupera widget                 │
│ - JSON parseado a dict                                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ ESTADO 5: TRANSFORMACIÓN                                     │
│ - EChartTransformer.transform_widget()                       │
│ - Optimización de datos                                      │
│ - Normalización de colores                                   │
│ - Configuración responsive                                   │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ ESTADO 6: RENDERIZACIÓN (Cliente)                            │
│ - Frontend recibe widget transformado                         │
│ - echarts.js crea instancia del gráfico                      │
│ - Chart.setOption(echart_config)                             │
│ - Usuario ve visualización interactiva                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
     ┌───────────────┴───────────────┐
     │ (Opcional)                    │
     │                               │
     ▼                               ▼
┌─────────────────┐        ┌──────────────────┐
│ ACTUALIZACIÓN   │        │ EXPORTACIÓN      │
│ update_echart   │        │ transform_data   │
│ _data()         │        │ _for_export()    │
│ - Nuevos datos  │        │ - CSV            │
│ - Recalcular    │        │ - Excel          │
│   config        │        │ - Tabla HTML     │
└────────┬────────┘        └────────┬─────────┘
         │                          │
         └──────────┬───────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │ PERSISTENCIA NUEVOS   │
        │ DATOS / EXPORTACIÓN   │
        └───────────────────────┘
```

---

## 7. Stack de Tecnologías

```
┌─────────────────────────────────────────────────────────────┐
│                   CLIENTE                                    │
│  HTML5 / JavaScript / echarts.js 5.x                        │
└─────────────────────────────────────────────────────────────┘
                              │ JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              API REST (Frappe Routes)                         │
│  /api/method/add_echart                                     │
│  /api/method/build_echart                                   │
│  /api/method/update_echart_data                             │
│  /api/method/transform_echart_for_render                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            BACKEND (Python/Frappe)                           │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ WidgetService                                         │   │
│  │ - CRUD operations                                     │   │
│  │ - Orquestación                                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                          │                                   │
│  ┌──────┬───────────┬────┴────┬──────────┐                  │
│  │      │           │         │          │                  │
│  ▼      ▼           ▼         ▼          ▼                  │
│  ┌──┐ ┌───┐ ┌───┐ ┌───┐ ┌──────────┐ ┌──────┐            │
│  │L │ │B  │ │P  │ │Sc │ │Factory   │ │Trans │            │
│  │in│ │ar │ │ie │ │at │ │          │ │form │            │
│  │e │ │   │ │   │ │ter│ │          │ │      │            │
│  └──┘ └───┘ └───┘ └───┘ └──────────┘ └──────┘            │
│                                                              │
│  Frappe ORM (frappe.db)                                     │
│  Persistencia en BD                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BD (MySQL/MariaDB)                         │
│  Tabla: Daltek (JSON field: layout)                         │
└─────────────────────────────────────────────────────────────┘
```
