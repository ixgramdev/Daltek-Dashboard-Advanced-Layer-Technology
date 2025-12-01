# ⚡ DTO Quick Reference - Guía Rápida de Uso

**Última actualización:** 1 de diciembre de 2025  
**Ubicación:** `daltek/daltek/dtos/`

---

## 📦 Importaciones

```python
# Opción 1: Importar desde módulo dtos
from daltek.dtos import WidgetDTO, EChartWidgetDTO

# Opción 2: Importar directo de archivos
from daltek.dtos.widget_dto import WidgetDTO
from daltek.dtos.echart_widget_dto import EChartWidgetDTO
```

---

## 🚀 Uso Rápido

### ✅ Crear WidgetDTO

```python
from daltek.dtos import WidgetDTO

# Método 1: Constructor directo
widget = WidgetDTO(
    id="widget_1_123456",
    type="card",
    properties={"title": "Mi Tarjeta"},
    created_at="2025-12-01T10:00:00",
    position={"x": 0, "y": 0}
)

# Método 2: Desde diccionario
widget_dict = {
    "id": "widget_1_123456",
    "type": "card",
    "properties": {"title": "Mi Tarjeta"},
    "position": {"x": 0, "y": 0}
}
widget = WidgetDTO.from_dict(widget_dict)
```

### ✅ Crear EChartWidgetDTO

```python
from daltek.dtos import EChartWidgetDTO

# Constructor directo
echart = EChartWidgetDTO(
    id="widget_2_123456",
    type="echart",
    chart_type="line",
    echart_data={
        "series": [{"name": "Ventas", "data": [100, 150, 120]}],
        "categories": ["Ene", "Feb", "Mar"]
    },
    echart_config={
        "series": [{"type": "line", "data": [100, 150, 120]}],
        "xAxis": {"type": "category", "data": ["Ene", "Feb", "Mar"]},
        "yAxis": {"type": "value"}
    },
    properties={"title": "Gráfico de Ventas"},
    position={"x": 0, "y": 1}
)
```

---

## 🔍 Validación

```python
# Validar DTO
is_valid, errors = echart.validate()

if is_valid:
    print("✓ DTO válido")
else:
    print(f"✗ Errores: {errors}")
    # Output: ['chart_type debe ser un string no vacío', 'Position debe...']
```

---

## 🔄 Conversión

```python
# DTO → Diccionario
widget_dict = echart.to_dict()
# Output: {id, type, chart_type, echart_data, echart_config, properties, position, ...}

# Diccionario → DTO
echart = EChartWidgetDTO.from_dict(widget_dict)
```

---

## 📊 Métodos EChartWidgetDTO

### get_chart_config_for_render()

```python
# Obtiene configuración lista para renderizar en echarts.js
render_config = echart.get_chart_config_for_render()

# Output:
# {
#     "id": "widget_2_123456",
#     "type": "line",
#     "config": {...echart_config...},
#     "data": {...echart_data...},
#     "properties": {"title": "Gráfico de Ventas"}
# }
```

### update_chart_data()

```python
# Actualizar datos del gráfico
new_data = {
    "series": [{"name": "Ventas", "data": [200, 250, 220]}],
    "categories": ["Abr", "May", "Jun"]
}
echart.update_chart_data(new_data)
```

### update_chart_config()

```python
# Actualizar configuración del gráfico
new_config = {
    "smooth": True,
    "fill_area": True,
    "colors": ["#FF0000"]
}
echart.update_chart_config(new_config)
```

---

## 💾 Integración con WidgetService

### Crear Widget

```python
from daltek.dtos import EChartWidgetDTO

# Crear DTO en add_echart()
echart_dto = EChartWidgetDTO(
    id=f"widget_{int(time.time() * 1000)}",
    type="echart",
    chart_type="line",
    echart_data={...},
    echart_config={...},
    properties={"title": "Mi Gráfico"}
)

# Validar
is_valid, errors = echart_dto.validate()
if not is_valid:
    return {"success": False, "error": "; ".join(errors)}

# Usar en builder
builder = self.echart_factory.create(chart_type)
build_result = builder.build(
    echart_dto.echart_data,
    echart_dto.echart_config
)
```

### Leer Widget

```python
from daltek.dtos import EChartWidgetDTO

# Cargar DTOs en get_all()
layout = self.get_layout(doc_name)
dtos = []

for widget_dict in layout:
    if widget_dict.get("type") == "echart":
        dto = EChartWidgetDTO.from_dict(widget_dict)
        is_valid, _ = dto.validate()
        if is_valid:
            dtos.append(dto)

return {"widgets": [dto.to_dict() for dto in dtos]}
```

### Actualizar Widget

```python
from daltek.dtos import EChartWidgetDTO

# Cargar DTO existente
existing_widget = layout[widget_index]
dto = EChartWidgetDTO.from_dict(existing_widget)

# Actualizar campos
dto.properties["title"] = new_title
dto.update_chart_data(new_data)

# Validar y guardar
is_valid, errors = dto.validate()
if is_valid:
    layout[widget_index] = dto.to_dict()
    doc.layout = json.dumps(layout)
    doc.save()
```

---

## 📋 Estructura de Datos

### WidgetDTO (Base)

```
{
    "id": "widget_1_1704114000000",           # str: Identificador único
    "type": "card|echart|table",             # str: Tipo de widget
    "properties": {                           # dict: Propiedades genéricas
        "title": "Mi Widget",
        "size": "medium",
        "color": "#FF0000"
    },
    "created_at": "2025-12-01T10:00:00",    # str | None: ISO format
    "modified_at": "2025-12-01T10:30:00",   # str | None: ISO format
    "position": {"x": 0, "y": 1}             # dict: Posición en grid
}
```

### EChartWidgetDTO (Extends WidgetDTO)

```
{
    // ... Campos heredados de WidgetDTO ...
    
    "chart_type": "line|bar|pie|scatter",    # str: Tipo de gráfico
    "echart_data": {                          # dict: Datos del gráfico
        "series": [
            {
                "name": "Ventas",
                "data": [100, 150, 120, 200]
            }
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr"]
    },
    "echart_config": {                        # dict: Config de echarts.js
        "series": [
            {
                "type": "line",
                "data": [100, 150, 120, 200],
                "smooth": true,
                "fill_area": true
            }
        ],
        "xAxis": {
            "type": "category",
            "data": ["Ene", "Feb", "Mar", "Abr"]
        },
        "yAxis": {
            "type": "value"
        },
        "tooltip": {
            "trigger": "axis"
        },
        "legend": {
            "data": ["Ventas"]
        }
    }
}
```

---

## ⚙️ Validación de DTOs

### WidgetDTO.validate()

Valida:
- ✅ `id` es string no vacío
- ✅ `type` es string no vacío
- ✅ `properties` es diccionario
- ✅ `position` contiene 'x' e 'y'

### EChartWidgetDTO.validate()

Valida todo de WidgetDTO + :
- ✅ `chart_type` es string no vacío
- ✅ `echart_data` es diccionario
- ✅ `echart_config` es diccionario
- ✅ `type` = 'echart'

---

## 🔗 Flujos Típicos

### Flujo 1: Crear → Validar → Guardar

```python
# 1. Crear DTO
dto = EChartWidgetDTO.from_dict(input_data)

# 2. Validar
is_valid, errors = dto.validate()
if not is_valid:
    return {"success": False, "error": "; ".join(errors)}

# 3. Guardar
widget_dict = dto.to_dict()
layout.append(widget_dict)
doc.layout = json.dumps(layout)
doc.save()

# 4. Retornar
return {"success": True, "widget": widget_dict}
```

### Flujo 2: Cargar → Actualizar → Guardar

```python
# 1. Cargar
existing_dict = layout[index]
dto = EChartWidgetDTO.from_dict(existing_dict)

# 2. Actualizar
dto.properties["title"] = new_title
dto.update_chart_data(new_data)

# 3. Validar
is_valid, _ = dto.validate()

# 4. Guardar
layout[index] = dto.to_dict()
doc.layout = json.dumps(layout)
doc.save()
```

### Flujo 3: Cargar → Transformar → Renderizar

```python
# 1. Cargar
dto = EChartWidgetDTO.from_dict(widget_dict)

# 2. Transformar
render_config = dto.get_chart_config_for_render()
render_config = transformer.transform_widget(render_config)

# 3. Renderizar (Frontend)
# chart.setOption(render_config.config)
```

---

## 🎯 Casos de Uso Comunes

### Caso 1: Validar widget antes de guardar

```python
dto = EChartWidgetDTO.from_dict(widget_data)
is_valid, errors = dto.validate()

if not is_valid:
    frappe.throw(", ".join(errors))
```

### Caso 2: Actualizar solo datos de gráfico

```python
dto = EChartWidgetDTO.from_dict(existing_widget)
dto.update_chart_data(new_data)
# echart_config se recalcula automáticamente
```

### Caso 3: Procesar batch de widgets

```python
dtos = []
for widget_dict in widgets_list:
    dto = EChartWidgetDTO.from_dict(widget_dict)
    if dto.validate()[0]:  # is_valid
        dtos.append(dto)

# Procesar solo DTOs válidos
for dto in dtos:
    config = dto.get_chart_config_for_render()
    # ...
```

### Caso 4: Copiar widget existente

```python
# Cargar original
original = EChartWidgetDTO.from_dict(original_dict)

# Crear copia con nuevo ID
copy = EChartWidgetDTO(
    id=f"widget_{int(time.time() * 1000)}",
    type=original.type,
    chart_type=original.chart_type,
    echart_data=original.echart_data.copy(),
    echart_config=original.echart_config.copy(),
    properties=original.properties.copy(),
    position={"x": original.position["x"] + 1, "y": original.position["y"]}
)

# Guardar copia
layout.append(copy.to_dict())
```

---

## 🐛 Troubleshooting

### Error: "chart_type debe ser un string no vacío"

```python
# ❌ Incorrecto
dto = EChartWidgetDTO(
    chart_type=""  # Vacío
)

# ✅ Correcto
dto = EChartWidgetDTO(
    chart_type="line"  # Con valor
)
```

### Error: "Position debe contener las claves 'x' e 'y'"

```python
# ❌ Incorrecto
position = {"x": 0}  # Falta 'y'

# ✅ Correcto
position = {"x": 0, "y": 1}
```

### Error: "Type debe ser 'echart'"

```python
# ❌ Incorrecto
dto = EChartWidgetDTO(
    type="card"  # Tipo equivocado
)

# ✅ Correcto
dto = EChartWidgetDTO(
    type="echart"
)
```

---

## 📚 Referencias

| Archivo | Contenido |
|---------|-----------|
| `widget_dto.py` | Clase WidgetDTO |
| `echart_widget_dto.py` | Clase EChartWidgetDTO |
| `INTEGRACION_DTOS.md` | Guía de integración detallada |
| `INTEGRACION_DTOS_DIAGRAMA.md` | Diagramas de arquitectura |

---

## 💡 Tips

✨ **Siempre validar después de `from_dict()`**
```python
dto = EChartWidgetDTO.from_dict(data)
is_valid, errors = dto.validate()  # ← No omitir
```

✨ **Usar `get_chart_config_for_render()` para renderización**
```python
render_config = dto.get_chart_config_for_render()
# Retorna dict con estructura lista para echarts.js
```

✨ **Usar `update_*` methods en lugar de setattr**
```python
# Mejor
dto.update_chart_data(new_data)
dto.update_chart_config(new_config)

# Que
dto.echart_data = new_data
dto.echart_config = new_config
```

✨ **Convertir a dict solo cuando sea necesario guardar/enviar**
```python
# Guardar en BD
widget_dict = dto.to_dict()
db.save(widget_dict)

# Enviar a frontend
return {"widget": dto.to_dict()}
```

---

**Última revisión:** 2025-12-01  
**Autor:** ixgram  
**Status:** Documentado y listo para usar
