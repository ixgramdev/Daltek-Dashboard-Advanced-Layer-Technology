# Quick Reference - EChart Widget Service

## 🚀 Inicio Rápido (Copy-Paste)

### Crear Line Chart
```python
from daltek.domain.widget_service import WidgetService

service = WidgetService()

result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="line",
    chart_data={
        "series": [
            {"name": "Ventas", "data": [100, 150, 120, 200]},
            {"name": "Ganancias", "data": [30, 50, 40, 70]}
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr"]
    },
    chart_config={
        "smooth": True,
        "fill_area": True,
        "colors": ["#2196F3", "#4CAF50"]
    },
    widget_properties={"title": "Sales Chart"}
)

print(result['widget']['id'])  # widget_1_1234567890
```

### Crear Pie Chart
```python
result = service.add_echart(
    doc_name="Dashboard1",
    chart_type="pie",
    chart_data={
        "data": [
            {"name": "Chrome", "value": 450},
            {"name": "Firefox", "value": 300},
            {"name": "Safari", "value": 200}
        ]
    },
    chart_config={"show_labels": True}
)
```

### Actualizar Datos
```python
service.update_echart_data(
    doc_name="Dashboard1",
    widget_id="widget_1_1234567890",
    chart_data={
        "series": [{"name": "Ventas", "data": [110, 160, 130, 210]}],
        "categories": ["Ene", "Feb", "Mar", "Abr"]
    }
)
```

### Renderizar para Frontend
```python
result = service.transform_echart_for_render(
    doc_name="Dashboard1",
    widget_id="widget_1_1234567890"
)

# Enviar result['widget'] al cliente
# Cliente hace: echarts.setOption(widget.echart_config)
```

---

## 📊 Estructura de Datos por Tipo

### LINE CHART
```python
{
    "series": [
        {"name": "Nombre", "data": [números...]}
    ],
    "categories": ["Etiqueta1", "Etiqueta2", ...]
}
```

### BAR CHART
```python
{
    "series": [
        {"name": "Nombre", "data": [números...]}
    ],
    "categories": ["Etiqueta1", "Etiqueta2", ...]
}
```

### PIE CHART
```python
{
    "data": [
        {"name": "Nombre", "value": número},
        {"name": "Nombre", "value": número}
    ]
}
```

### SCATTER CHART
```python
{
    "series": [
        {"name": "Nombre", "data": [[x,y], [x,y], ...]}
    ]
}
```

---

## ⚙️ Opciones de Configuración

### Colors
```python
"colors": ["#FF0000", "#00FF00", "#0000FF"]
```

### Titles
```python
"title": "Mi Gráfico"
"xaxis_name": "Eje X"
"yaxis_name": "Eje Y"
```

### Line Chart Específicos
```python
"smooth": True/False              # Suavizar líneas
"fill_area": True/False           # Area bajo línea
"symbol": "circle"                # Tipo de marca
"symbolSize": 6                   # Tamaño de marca
```

### Bar Chart Específicos
```python
"barWidth": "60%"                 # Ancho de barras
```

### Pie Chart Específicos
```python
"radius": "50%"                   # Radio del círculo
"show_labels": True/False         # Mostrar etiquetas
"name": "Distribution"            # Nombre de serie
```

---

## 🔍 Tipos Disponibles

| Tipo | Descripción | Datos |
|------|-------------|-------|
| `line` | Gráfico de línea | series + categories |
| `bar` | Gráfico de barras | series + categories |
| `pie` | Gráfico circular | data (name + value) |
| `scatter` | Dispersión | series con [x,y] |

---

## ✅ Validaciones Automáticas

```python
# ❌ ERROR: Falta "categories" en line chart
{"series": [...]}

# ✅ OK
{"series": [...], "categories": [...]}

# ❌ ERROR: Valores no numéricos
{"series": [{"name": "Data", "data": [1, "text", 3]}]}

# ✅ OK
{"series": [{"name": "Data", "data": [1, 2, 3]}]}

# ❌ ERROR: Cantidad no coincide
{
    "series": [{"data": [1, 2, 3]}],
    "categories": ["A", "B"]  # Solo 2, necesita 3
}

# ✅ OK
{
    "series": [{"data": [1, 2, 3]}],
    "categories": ["A", "B", "C"]
}
```

---

## 🛠️ Métodos Principales

| Método | Uso |
|--------|-----|
| `add_echart()` | Crear nuevo chart |
| `update_echart_data()` | Actualizar datos |
| `edit()` | Editar widget completo |
| `delete()` | Eliminar widget |
| `get_layout()` | Obtener widgets |
| `render_layout()` | Renderizar todos |
| `transform_echart_for_render()` | Preparar para frontend |
| `build_echart()` | Reconstruir config |

---

## 🎯 Flujo Típico

```
1. Cliente prepara datos
   ↓
2. Llama add_echart()
   ↓
3. Validación + Construcción
   ↓
4. Almacenamiento en BD
   ↓
5. Retorna widget con ID
   ↓
6. Cliente solicita renderización
   ↓
7. Llamada transform_echart_for_render()
   ↓
8. Optimización y normalización
   ↓
9. Widget enviado a frontend
   ↓
10. echarts.js renderiza
```

---

## 🐛 Debugging

```python
# Ver tipos disponibles
from daltek.domain.widget_service.echart import EChartFactory
print(EChartFactory.get_available_types())
# ['bar', 'line', 'pie', 'scatter']

# Verificar si tipo está registrado
if EChartFactory.is_registered("line"):
    print("Line chart disponible")

# Ver error específico
result = service.add_echart(...)
if not result.get("success"):
    print(f"Error: {result['error']}")
    # Mensaje descriptivo del error
```

---

## 📈 Ejemplo Completo

```python
from daltek.domain.widget_service import WidgetService

# Inicializar
service = WidgetService()

# 1. CREAR
result = service.add_echart(
    doc_name="SalesDashboard",
    chart_type="line",
    chart_data={
        "series": [
            {"name": "Q1", "data": [100, 200, 150]},
            {"name": "Q2", "data": [150, 250, 200]}
        ],
        "categories": ["Jan", "Feb", "Mar"]
    },
    chart_config={
        "smooth": True,
        "title": "Quarterly Sales"
    },
    widget_properties={"title": "Sales Trend"}
)

widget_id = result['widget']['id']
print(f"Created: {widget_id}")

# 2. LEER
layout = service.get_layout("SalesDashboard")
print(f"Total widgets: {len(layout)}")

# 3. ACTUALIZAR
service.update_echart_data(
    doc_name="SalesDashboard",
    widget_id=widget_id,
    chart_data={
        "series": [
            {"name": "Q1", "data": [120, 220, 170]},
            {"name": "Q2", "data": [170, 270, 220]}
        ],
        "categories": ["Jan", "Feb", "Mar"]
    }
)
print("Data updated")

# 4. TRANSFORMAR
result = service.transform_echart_for_render(
    doc_name="SalesDashboard",
    widget_id=widget_id
)

# Enviar al cliente
return result['widget']

# 5. ELIMINAR (opcional)
service.delete("SalesDashboard", widget_id)
print("Deleted")
```

---

## 📚 Recursos

- Documentación completa: `ARQUITECTURA_ECHART.md`
- Diagramas de flujo: `DIAGRAMAS_ECHART.md`
- Guía detallada: `README_ECHART_SERVICE.md`
- Tests: `echart/test_*.py`
- ECharts docs: https://echarts.apache.org/

---

## 🚨 Errores Comunes

| Error | Solución |
|-------|----------|
| "Type not registered" | Usa tipo válido: line, bar, pie, scatter |
| "Document doesn't exist" | Verifica que doc_name exista |
| "Falta field 'X'" | Revisa estructura de datos |
| "Value not numeric" | Usa números, no strings |
| "Mismatch cantidad" | categories != series data length |

---

## 💡 Tips

✅ Siempre validar `result.get("success")` antes de usar datos

✅ Usar `update_echart_data()` para actualizar solo datos

✅ El transformer optimiza automáticamente

✅ Los colores se normalizan automáticamente

✅ Verificar tipos con `EChartFactory.get_available_types()`

✅ Usar nombres descriptivos en series

✅ Agregar títulos descriptivos en widget_properties

---

**Última actualización**: 30 de noviembre de 2024
