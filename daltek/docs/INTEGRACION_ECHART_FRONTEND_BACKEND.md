# 🔄 Integración Backend-Frontend: EChart Widget Service

## ✅ CAMBIOS APLICADOS

### 1️⃣ hooks.py
**Archivo**: `daltek/hooks.py`

**Cambios**:
- ✅ Agregada librería ECharts.js a `app_include_js`
- ✅ Agregado CSS de widgets EChart a `app_include_css`

```python
app_include_css = [
    "/assets/daltek/css/gridstack.min.css",
    "/assets/daltek/css/echarts-widgets.css",  # ← NUEVO
]
app_include_js = [
    "/assets/daltek/js/libs/gridstack-all.js",
    "/assets/daltek/js/libs/echarts.min.js",  # ← NUEVO
]
```

**Acción requerida**: 
```bash
# Descargar echarts.min.js a la carpeta correcta
cd ~/Documentos/Avangenio/ERP\ Cuba/frappe_docker/development/frappe-bench/apps/daltek/daltek/public/js/libs/
wget https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js
```

---

### 2️⃣ widgets.js (Definición de widgets)
**Archivo**: `daltek/public/js/widgets.js`

**Cambios**:
- ✅ Restructurados widgets con propiedades generales y específicas
- ✅ Agregados 3 tipos de ECharts: Line, Bar, Pie
- ✅ Widget Card mantiene estructura tradicional

**Estructura nueva**:
```javascript
{
  // Propiedades generales
  id: "line_chart_widget",
  name: "Line Chart",
  label: "Gráfico de Líneas - Muestra tendencias temporales",
  type: "echart", // ← Tipo principal
  
  // Propiedades específicas
  chart_type: "line", // Subtipo para backend
  default_data: { ... },
  default_config: { ... },
  previewHtml: "...",
  grid_config: { w: 6, h: 4 }
}
```

---

### 3️⃣ drag_and_drop/widgets.js (Lógica de drag & drop)
**Archivo**: `daltek/public/js/drag_and_drop/widgets.js`

**Cambios**:
- ✅ Modificado `handleDrop()` para detectar `type === "echart"`
- ✅ Agregada función `createEChartWidget()` que llama al backend
- ✅ Agregada función `renderEChartWidget()` que inicializa echarts.js

**Flujo**:
```
Usuario arrastra widget
  ↓
handleDrop() detecta type
  ↓
Si type === "echart" → createEChartWidget()
  ↓
Backend crea chart → Retorna config
  ↓
renderEChartWidget() renderiza en canvas
```

---

### 4️⃣ daltek.py (Backend wrappers)
**Archivo**: `daltek/daltek/doctype/daltek/daltek.py`

**Cambios**:
- ✅ Agregado `@frappe.whitelist() add_widget_echart()`
- ✅ Agregado `@frappe.whitelist() add_widget()`

**Métodos nuevos**:
```python
add_widget_echart(doc_name, chart_type, chart_data, chart_config, widget_properties)
  → Llama a WidgetService.add_echart()
  → Retorna widget creado con echart_config

add_widget(doc_name, widget)
  → Llama a WidgetService.add() para widgets tradicionales
  → Retorna widget guardado
```

---

### 5️⃣ echarts-widgets.css (Estilos)
**Archivo**: `daltek/public/css/echarts-widgets.css`

**Cambios**:
- ✅ Creado archivo nuevo con estilos para widgets EChart
- ✅ Estilos para `.echart-widget`, `.echart-container`
- ✅ Estilos para preview en sidebar con gradientes
- ✅ Estilos responsive

**Clases principales**:
- `.echart-widget` - Contenedor principal
- `.echart-container` - Contenedor del chart (100% ancho/alto)
- `.dd-widget-preview.echart-preview` - Preview en sidebar

---

### 6️⃣ main.js (Inicialización)
**Archivo**: `daltek/public/js/drag_and_drop/main.js`

**Cambios**:
- ✅ Modificado `initDragDropSystem()` para cargar layout desde backend
- ✅ Agregada lógica para renderizar ECharts y widgets tradicionales
- ✅ Guardado `docName` en el estado

**Flujo de inicialización**:
```
initDragDropSystem(frm)
  ↓
Cargar layout desde backend (frappe.call)
  ↓
Para cada widget en layout:
  Si type === "echart" → renderEChartWidget()
  Si no → renderWidget() tradicional
  ↓
Renderizar sidebar con widgets disponibles
```

---

## 🎯 PATRONES DE DISEÑO APLICADOS

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Strategy** | `handleDrop()` | Diferentes estrategias según `type` del widget |
| **Factory** | Backend (`EChartFactory`) | Crear builders según `chart_type` |
| **Template Method** | Backend (`BaseEChartBuilder.build()`) | Esqueleto común de construcción |
| **Observer** | `frappe.call() callback` | Reaccionar a respuesta del backend |
| **Facade** | `add_widget_echart()` | Simplificar acceso a `WidgetService` |

---

## 📊 FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUARIO arrastra "Line Chart" al canvas                 │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. handleDrop() detecta type === "echart"                  │
│    → Prepara payload con chart_type, chart_data, etc       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼ frappe.call()
┌─────────────────────────────────────────────────────────────┐
│ 3. BACKEND: add_widget_echart()                             │
│    → Llama a WidgetService.add_echart()                     │
│    → Factory crea LineChartBuilder                          │
│    → Builder construye echart_config                        │
│    → Guarda en BD (layout JSON)                            │
│    → Retorna widget completo                                │
└────────────────┬────────────────────────────────────────────┘
                 │ response.message.widget
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. FRONTEND: createEChartWidget() recibe widget            │
│    → Llama a renderEChartWidget()                           │
│    → Crea <div id="echart_{id}">                           │
│    → Inicializa echarts.init()                              │
│    → Ejecuta chart.setOption(echart_config)                 │
│    → Gráfico renderizado ✅                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 PRUEBAS

### Paso 1: Verificar que ECharts.js está cargado

1. Abre la consola del navegador (F12)
2. Ejecuta:
   ```javascript
   console.log(echarts ? `✅ ECharts ${echarts.version}` : "❌ ECharts no cargado");
   ```

### Paso 2: Verificar widgets disponibles

```javascript
console.log("Widgets disponibles:", window.availableWidgets);
// Deberías ver 4 widgets: Line Chart, Bar Chart, Pie Chart, KPI Card
```

### Paso 3: Probar arrastrar un widget EChart

1. Abre un documento Daltek
2. Arrastra "Line Chart" al canvas
3. Observa la consola:
   ```
   🎨 Widget EChart detectado: line
   ✅ EChart creado en backend: line_chart_widget_1234567890
   📊 EChart renderizado: line_chart_widget_1234567890
   ```
4. El gráfico debería aparecer en el canvas

### Paso 4: Verificar persistencia

1. Guarda el documento
2. Recarga la página
3. Los widgets deberían cargarse automáticamente

---

## 🐛 TROUBLESHOOTING

### Problema: "echarts is not defined"

**Causa**: ECharts.js no se descargó

**Solución**:
```bash
cd ~/Documentos/Avangenio/ERP\ Cuba/frappe_docker/development/frappe-bench/apps/daltek/daltek/public/js/libs/
wget https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js
bench build --app daltek
```

### Problema: "add_widget_echart method not found"

**Causa**: Backend no reconoce el método

**Solución**:
```bash
bench restart
```

### Problema: El widget se arrastra pero no aparece

**Causa**: Error en el backend o frontend

**Solución**:
1. Abre la consola del navegador
2. Busca errores en rojo
3. Revisa los logs del backend:
   ```bash
   bench console
   >>> frappe.get_doc("Error Log").get_list(limit=5)
   ```

### Problema: El gráfico aparece vacío

**Causa**: `echart_config` inválido

**Solución**:
1. Verifica que `default_data` en `widgets.js` sea válido
2. Ejecuta en consola:
   ```javascript
   window.DragDropState.state.widgets.forEach(w => {
     if (w.type === "echart") {
       console.log("Widget:", w.id, "Config:", w.echart_config);
     }
   });
   ```

---

## 📚 ARCHIVOS MODIFICADOS

| Archivo | Líneas | Cambios |
|---------|--------|---------|
| `hooks.py` | +4 | Agregados ECharts.js y CSS |
| `widgets.js` | ~160 | Restructurado con nuevos widgets |
| `drag_and_drop/widgets.js` | +120 | Funciones crear y renderizar ECharts |
| `daltek.py` | +75 | Wrappers backend |
| `echarts-widgets.css` | +160 | Estilos para ECharts (NUEVO) |
| `main.js` | +40 | Cargar layout desde backend |

**Total**: ~560 líneas de código nuevo/modificado

---

## 🚀 PRÓXIMOS PASOS

1. **Probar flujo completo**: Arrastrar → Backend → Renderizar ✅
2. **Implementar edición**: Hacer click en configuración para editar datos
3. **Agregar más tipos**: Scatter, Radar, Gauge charts
4. **Exportar datos**: Descargar chart como imagen o CSV
5. **Tiempo real**: Actualizar datos automáticamente

---

## 📞 SOPORTE

Si encuentras problemas:

1. Revisa la consola del navegador (F12)
2. Revisa logs del backend: `bench console` → `frappe.get_list("Error Log")`
3. Verifica que todos los archivos se guardaron correctamente
4. Ejecuta `bench build --app daltek` y `bench restart`

---

**Estado**: ✅ COMPLETADO
**Fecha**: 30 de noviembre de 2025
**Versión**: v1.0.0
