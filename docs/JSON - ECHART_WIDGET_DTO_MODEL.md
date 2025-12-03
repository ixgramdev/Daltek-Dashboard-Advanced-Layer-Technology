# EChart Widget DTO Model - Modelo Especializado para Gráficos

## Descripción General

El `EChartWidgetDTO` es una clase especializada que extiende `WidgetDTO` para la transferencia de datos de widgets que usan gráficos EChart. Hereda toda la estructura base y añade campos específicos para la configuración y datos de gráficos.

## Herencia

```
WidgetDTO (clase base)
    ↓
EChartWidgetDTO (clase especializada)
```

## Estructura JSON

```json
{
  "id": "widget_1_xxx",
  "type": "echart",
  "label": "Mi Gráfico",
  "metadata": {
    "created_at": "2025-12-03T10:30:00.000000",
    "modified_at": "2025-12-03T10:30:00.000000",
    "version": 1
  },
  "layout": {
    "x": 0,
    "y": 0,
    "width": 6,
    "height": 4,
    "min_width": 4,
    "min_height": 3
  },
  "properties": {
    "title": "Ventas",
    "other_properties": "..."
  },
  "content": {
    "type": "echart",
    "chart_type": "line",
    "data": {
      "series": [
        {
          "name": "Ventas",
          "data": [120, 250, 180, 320, 450]
        }
      ],
      "categories": ["Ene", "Feb", "Mar", "Abr", "May"]
    },
    "config": {
      "xAxis": {
        "type": "category",
        "data": ["Ene", "Feb", "Mar", "Abr", "May"]
      },
      "yAxis": {
        "type": "value"
      },
      "series": [
        {
          "data": [120, 250, 180, 320, 450],
          "type": "line"
        }
      ]
    }
  }
}
```

## Atributos del Modelo

### Atributos Heredados de WidgetDTO

| Atributo | Tipo | Descripción |
|----------|------|-------------|
| `type` | `str` | Siempre debe ser `"echart"` |
| `properties` | `dict[str, Any]` | Propiedades genéricas del widget |
| `id` | `str \| None` | Identificador único |
| `created_at` | `str \| None` | Fecha de creación |
| `modified_at` | `str \| None` | Fecha de última modificación |
| `position` | `dict[str, int]` | Posición y tamaño del widget |
| `label` | `str` | Etiqueta legible del widget |

### Atributos Específicos de EChart

| Atributo | Tipo | Descripción | Requerido |
|----------|------|-------------|-----------|
| `chart_type` | `str` | Tipo de gráfico (`line`, `bar`, `pie`, `scatter`, `gauge`, etc.) | ✓ Sí |
| `echart_data` | `dict[str, Any]` | Datos del gráfico (series, categorías, etc.) | No (default: `{}`) |
| `echart_config` | `dict[str, Any]` | Configuración de EChart (axes, series, etc.) | No (default: `{}`) |

## Sub-objeto: content.data

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `series` | `list` | Datos de las series del gráfico |
| `categories` | `list` | Categorías del eje X |

**Ejemplo de series:**
```json
{
  "series": [
    {
      "name": "Ventas",
      "data": [120, 250, 180, 320, 450]
    },
    {
      "name": "Costos",
      "data": [80, 150, 120, 200, 300]
    }
  ]
}
```

## Sub-objeto: content.config

Configuración específica de EChart que define la apariencia y comportamiento del gráfico.

**Campos principales:**
- `xAxis`: Configuración del eje X
- `yAxis`: Configuración del eje Y
- `series`: Definición de las series a graficar
- `legend`: Configuración de la leyenda
- `tooltip`: Configuración de tooltips
- `grid`: Configuración del área de gráfico

## Tipos de Gráfico Soportados

| Tipo | Descripción | Uso |
|------|-------------|-----|
| `line` | Gráfico de líneas | Tendencias en el tiempo |
| `bar` | Gráfico de barras | Comparación de valores |
| `pie` | Gráfico de pastel | Distribución porcentual |
| `scatter` | Gráfico de dispersión | Correlación entre variables |
| `gauge` | Indicador de velocímetro | Medidores de progreso |
| `candlestick` | Gráfico de velas | Datos financieros |
| `heatmap` | Mapa de calor | Densidad de datos |
| `funnel` | Gráfico de embudo | Flujos de conversión |

## Métodos

### `to_dict() -> dict[str, Any]`

Convierte la instancia del DTO a diccionario en formato normalizado.

**Retorna:**
- `dict`: Estructura JSON normalizada con toda la información de EChart

**Nota:** Este método extiende el de la clase base para incluir los campos específicos de EChart en el sub-objeto `content`.

**Ejemplo:**
```python
echart = EChartWidgetDTO(
    chart_type="line",
    label="Ventas Mensuales",
    properties={"title": "Ventas"},
    echart_data={
        "series": [{"name": "Ventas", "data": [100, 200, 150]}],
        "categories": ["Ene", "Feb", "Mar"]
    }
)
echart_dict = echart.to_dict()
```

### `from_dict(data: dict[str, Any]) -> EChartWidgetDTO`

Crea una instancia del DTO desde un diccionario en formato normalizado.

**Parámetros:**
- `data` (`dict`): Diccionario con estructura normalizada

**Retorna:**
- `EChartWidgetDTO`: Instancia del modelo

**Ejemplo:**
```python
data = {
    "id": "widget_1",
    "type": "echart",
    "label": "Ventas Mensuales",
    "metadata": {...},
    "layout": {...},
    "properties": {...},
    "content": {
        "type": "echart",
        "chart_type": "line",
        "data": {...},
        "config": {...}
    }
}
echart = EChartWidgetDTO.from_dict(data)
```

### `get_chart_config_for_render() -> dict[str, Any]`

Obtiene la configuración del EChart lista para renderizar en el frontend.

**Retorna:**
- `dict`: Configuración normalizada preparada para EChart

## Ejemplo de Uso

### Crear un gráfico de líneas

```python
from daltek.dtos.echart_widget_dto import EChartWidgetDTO

echart = EChartWidgetDTO(
    type="echart",
    chart_type="line",
    label="Ventas Mensuales 2025",
    properties={
        "title": "Ventas",
        "color": "blue"
    },
    position={
        "x": 0,
        "y": 0,
        "width": 12,
        "height": 6
    },
    echart_data={
        "series": [
            {
                "name": "Ventas",
                "data": [120, 250, 180, 320, 450, 380, 410]
            }
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"]
    },
    echart_config={
        "xAxis": {
            "type": "category",
            "data": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"]
        },
        "yAxis": {
            "type": "value"
        },
        "series": [
            {
                "data": [120, 250, 180, 320, 450, 380, 410],
                "type": "line",
                "smooth": True
            }
        ]
    }
)

# Convertir a JSON
chart_json = echart.to_dict()
```

### Crear un gráfico de barras

```python
echart = EChartWidgetDTO(
    type="echart",
    chart_type="bar",
    label="Comparación de Productos",
    properties={"title": "Ventas por Producto"},
    echart_data={
        "series": [
            {"name": "Producto A", "data": [100, 150, 200]},
            {"name": "Producto B", "data": [120, 180, 220]}
        ],
        "categories": ["Q1", "Q2", "Q3"]
    },
    echart_config={
        "xAxis": {
            "type": "category",
            "data": ["Q1", "Q2", "Q3"]
        },
        "yAxis": {"type": "value"},
        "series": [
            {"name": "Producto A", "data": [100, 150, 200], "type": "bar"},
            {"name": "Producto B", "data": [120, 180, 220], "type": "bar"}
        ]
    }
)
```

### Crear un gráfico de pastel

```python
echart = EChartWidgetDTO(
    type="echart",
    chart_type="pie",
    label="Distribución de Ventas",
    properties={"title": "Participación por Región"},
    echart_data={
        "series": [
            {"name": "Región", "data": [
                {"value": 335, "name": "Norte"},
                {"value": 310, "name": "Sur"},
                {"value": 234, "name": "Este"},
                {"value": 135, "name": "Oeste"}
            ]}
        ]
    },
    echart_config={
        "series": [
            {
                "name": "Región",
                "type": "pie",
                "data": [
                    {"value": 335, "name": "Norte"},
                    {"value": 310, "name": "Sur"},
                    {"value": 234, "name": "Este"},
                    {"value": 135, "name": "Oeste"}
                ]
            }
        ]
    }
)
```

### Recibir y parsear desde frontend

```python
# Datos recibidos del frontend con gráfico
received_data = {
    "id": "widget_1_chart001",
    "type": "echart",
    "label": "Ventas Mensuales",
    "metadata": {
        "created_at": "2025-12-03T10:30:00.000000",
        "modified_at": "2025-12-03T10:30:00.000000",
        "version": 1
    },
    "layout": {
        "x": 0,
        "y": 0,
        "width": 12,
        "height": 6,
        "min_width": 8,
        "min_height": 4
    },
    "properties": {
        "title": "Ventas"
    },
    "content": {
        "type": "echart",
        "chart_type": "line",
        "data": {
            "series": [{"name": "Ventas", "data": [120, 250, 180]}],
            "categories": ["Ene", "Feb", "Mar"]
        },
        "config": {
            "xAxis": {"type": "category", "data": ["Ene", "Feb", "Mar"]},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [120, 250, 180]}]
        }
    }
}

# Parsear a instancia
echart = EChartWidgetDTO.from_dict(received_data)
print(echart.chart_type)  # "line"
print(echart.label)       # "Ventas Mensuales"
```

## Notas Importantes

1. **Tipo de Widget:** El `type` siempre debe ser `"echart"` para este DTO especializado.

2. **Formato Normalizado:** Al igual que `WidgetDTO`, este modelo mantiene un formato normalizado único para toda la transferencia de datos.

3. **Configuración de EChart:** Los datos en `echart_config` deben seguir la documentación oficial de ECharts (https://echarts.apache.org/en/option.html).

4. **Escalabilidad:** El modelo está diseñado para soportar todos los tipos de gráficos que ofrece ECharts.

5. **Método de Renderizado:** Utiliza `get_chart_config_for_render()` para obtener la configuración lista para pasar directamente a las funciones de renderizado del frontend.
