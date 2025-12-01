# 🔴 Diagnóstico: Widgets No Se Renderizan

## Problema Identificado

Los widgets no aparecen en el menú lateral de la pestaña drag and drop porque **los scripts JavaScript no están siendo cargados**.

## Raiz del Problema

En el archivo `index.html` hay placeholder vacíos para los scripts:

```html
<script id="dd-state-js">
// ============ state.js ============
</script>

<script id="dd-ui-js">
// ============ ui.js ============
</script>

<script id="dd-grid-js">
// ============ grid.js ============
</script>

<script id="dd-widgets-js">
// ============ widgets.js ============
</script>

<script id="dd-main-js">
// ============ main.js ============
</script>
```

❌ **Los scripts NO contienen el código actual**, solo comentarios.

## Diagrama del Flujo Roto

```
┌─────────────────────────────────────────┐
│  daltek.js (load_drag_drop_system)      │
│  - Llama a get_drag_drop_html()         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Backend Python devuelve HTML           │
│  - index.html se inserta en el DOM      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  HTML cargado con scripts VACÍOS        │ ❌
│  - state.js → comentario                │
│  - ui.js → comentario                   │
│  - grid.js → comentario                 │
│  - widgets.js → comentario              │
│  - main.js → comentario                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  window.initDragDropSystem NO EXISTE    │ ❌
│  window.DragDropState NO EXISTE         │ ❌
│  window.DragDropUI NO EXISTE            │ ❌
│  window.DragDropGrid NO EXISTE          │ ❌
│  window.DragDropWidgets NO EXISTE       │ ❌
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Resultado: Consola muestra error       │ ❌
│  "Módulos no cargados correctamente"    │
└─────────────────────────────────────────┘
```

## Archivos vs Contenido

| Archivo | Existe | Contenido | En HTML |
|---------|--------|-----------|---------|
| state.js | ✅ | 82 líneas de código | ❌ Solo comentario |
| ui.js | ✅ | 130+ líneas de código | ❌ Solo comentario |
| grid.js | ✅ | 150+ líneas de código | ❌ Solo comentario |
| widgets.js | ✅ | 80+ líneas de código | ❌ Solo comentario |
| main.js | ✅ | 80+ líneas de código | ❌ Solo comentario |

## ¿Cómo se Debería Hacer?

### Opción 1: Scripts Externos (Recomendado)

```html
<script src="/assets/daltek/js/drag_and_drop/state.js"></script>
<script src="/assets/daltek/js/drag_and_drop/ui.js"></script>
<script src="/assets/daltek/js/drag_and_drop/grid.js"></script>
<script src="/assets/daltek/js/drag_and_drop/widgets.js"></script>
<script src="/assets/daltek/js/drag_and_drop/main.js"></script>
```

### Opción 2: Inlining Scripts (Para desarrollo)

```html
<script>
<!-- Contenido completo de state.js -->
(function (window) {
  ...
})();
</script>

<script>
<!-- Contenido completo de ui.js -->
(function (window) {
  ...
})();
</script>

<!-- ... etc -->
```

### Opción 3: Cargar Dinámicamente (Backend Python)

En `get_drag_drop_html()`:
```python
def get_drag_drop_html():
    html = render_template("drag_and_drop/index.html")
    
    # Inyectar scripts directamente
    state_content = read_file("state.js")
    ui_content = read_file("ui.js")
    # ... etc
    
    html = html.replace(
        "<!-- ============ state.js ============ -->",
        f"<script>{state_content}</script>"
    )
    
    return html
```

## Impacto

### ¿Por qué los widgets no se renderizan?

1. **main.js no está cargado**
   - `window.initDragDropSystem` NO existe
   - El código en `daltek.js` línea 83-90 recibe error

2. **state.js no está cargado**
   - `window.DragDropState` NO existe
   - Los demás scripts dependen de esto

3. **ui.js no está cargado**
   - `window.DragDropUI` NO existe
   - `renderWidgetList()` no puede ejecutarse

4. **widgets.js no está cargado**
   - `window.DragDropWidgets` NO existe
   - El drag and drop no funciona

5. **grid.js no está cargado**
   - `window.DragDropGrid` NO existe
   - GridStack no se inicializa

## Errores en la Consola

```
Error: Drag and Drop: Módulos no cargados correctamente
Error: Sistema Drag and Drop no disponible o widgets no cargados
```

## Solución Recomendada

✅ **Opción 1 (Mejor)**: Usar Frappe's `frappe.require()` en el backend

En `hooks.py`:
```python
"js": [
    "public/js/drag_and_drop/state.js",
    "public/js/drag_and_drop/ui.js",
    "public/js/drag_and_drop/grid.js",
    "public/js/drag_and_drop/widgets.js",
    "public/js/drag_and_drop/main.js",
]
```

O en `daltek.js` antes de llamar `load_drag_drop_system()`:
```javascript
frappe.require([
    "/assets/daltek/js/drag_and_drop/state.js",
    "/assets/daltek/js/drag_and_drop/ui.js",
    "/assets/daltek/js/drag_and_drop/grid.js",
    "/assets/daltek/js/drag_and_drop/widgets.js",
    "/assets/daltek/js/drag_and_drop/main.js"
], function() {
    load_drag_drop_system(frm);
});
```

## Checklist de Verificación

- [ ] ¿Los scripts JS están siendo importados?
- [ ] ¿`window.DragDropState` existe en consola?
- [ ] ¿`window.DragDropUI` existe en consola?
- [ ] ¿`window.DragDropGrid` existe en consola?
- [ ] ¿`window.DragDropWidgets` existe en consola?
- [ ] ¿`window.initDragDropSystem` existe en consola?
- [ ] ¿`window.availableWidgets` tiene contenido?
- [ ] ¿El HTML tiene `ddCanvas`, `ddSidebar`, `ddWidgetList`?

## Próximos Pasos

1. **Importar los scripts correctamente**
2. **Validar en consola** que los objetos globales existen
3. **Verificar que `availableWidgets`** tiene el contenido de `/js/widgets.js`
4. **Debug**: Revisar mensajes en consola (F12)
