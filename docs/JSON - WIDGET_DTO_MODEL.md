# Widget DTO Model - Modelo Base de Widgets

## Descripción General

El `WidgetDTO` es la clase base para la transferencia de datos de widgets entre capas de la aplicación. Define una estructura normalizada única para todos los widgets genéricos.

## Estructura JSON

```json
{
  "id": "widget_1_xxx",
  "type": "card",
  "label": "Mi Widget",
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
    "title": "...",
    "color": "...",
    "other_properties": "..."
  },
  "content": {
    "type": "card"
  }
}
```

## Atributos del Modelo

### Atributos Principales

| Atributo | Tipo | Descripción | Requerido |
|----------|------|-------------|-----------|
| `type` | `str` | Tipo de widget (`card`, `echart`, `table`, etc.) | ✓ Sí |
| `properties` | `dict[str, Any]` | Propiedades genéricas del widget | No (default: `{}`) |
| `id` | `str \| None` | Identificador único (generado por backend) | No |
| `created_at` | `str \| None` | Fecha de creación en formato ISO | No |
| `modified_at` | `str \| None` | Fecha de última modificación en formato ISO | No |
| `position` | `dict[str, int]` | Posición y tamaño del widget | No (default: `{"x": 0, "y": 0, "width": 6, "height": 4}`) |
| `label` | `str` | Etiqueta legible del widget | No (default: `""`) |

### Sub-objeto: metadata

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `created_at` | `str` | Fecha de creación (ISO format) |
| `modified_at` | `str` | Fecha de última modificación (ISO format) |
| `version` | `int` | Número de versión (actualmente 1) |

### Sub-objeto: layout

| Campo | Tipo | Descripción | Default |
|-------|------|-------------|---------|
| `x` | `int` | Posición horizontal en la grilla | 0 |
| `y` | `int` | Posición vertical en la grilla | 0 |
| `width` | `int` | Ancho del widget en unidades de grilla | 6 |
| `height` | `int` | Alto del widget en unidades de grilla | 4 |
| `min_width` | `int` | Ancho mínimo permitido | 4 |
| `min_height` | `int` | Alto mínimo permitido | 3 |

## Métodos

### `to_dict() -> dict[str, Any]`

Convierte la instancia del DTO a diccionario en formato normalizado.

**Retorna:**
- `dict`: Estructura JSON normalizada lista para enviar al servidor

**Ejemplo:**
```python
widget = WidgetDTO(
    type="card",
    label="Mi Tarjeta",
    properties={"title": "Ventas Total"}
)
widget_dict = widget.to_dict()
```

### `from_dict(data: dict[str, Any]) -> WidgetDTO`

Crea una instancia del DTO desde un diccionario en formato normalizado.

**Parámetros:**
- `data` (`dict`): Diccionario con estructura normalizada

**Retorna:**
- `WidgetDTO`: Instancia del modelo

**Ejemplo:**
```python
data = {
    "id": "widget_1",
    "type": "card",
    "label": "Mi Tarjeta",
    "metadata": {...},
    "layout": {...},
    "properties": {...},
    "content": {...}
}
widget = WidgetDTO.from_dict(data)
```

## Tipos de Widget Soportados

- `card`: Tarjeta con información resumida
- `echart`: Gráfico EChart
- `table`: Tabla de datos
- (Extensibles según necesidad)

## Ejemplo de Uso

### Crear un nuevo widget

```python
from daltek.dtos.widget_dto import WidgetDTO

# Crear instancia
widget = WidgetDTO(
    type="card",
    label="Total de Ventas",
    properties={
        "title": "Ventas",
        "color": "blue",
        "icon": "shopping-cart"
    },
    position={
        "x": 0,
        "y": 0,
        "width": 6,
        "height": 4
    }
)

# Convertir a JSON para enviar al servidor
widget_json = widget.to_dict()
```

### Recibir y parsear widget

```python
# Datos recibidos del frontend
received_data = {
    "id": "widget_1_abc123",
    "type": "card",
    "label": "Total de Ventas",
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
        "color": "blue"
    },
    "content": {
        "type": "card"
    }
}

# Parsear a instancia
widget = WidgetDTO.from_dict(received_data)
print(widget.label)  # "Total de Ventas"
print(widget.type)   # "card"
```

## Nota Importante

Este DTO define un **formato normalizado único** para toda la transferencia de datos de widgets. Se recomienda siempre utilizar los métodos `to_dict()` y `from_dict()` para asegurar consistencia en la estructura de datos entre el frontend y backend.
