# 📊 Integración de DTOs en la Arquitectura Daltek

**Fecha:** 1 de diciembre de 2025  
**Estado:** Propuesta de Integración  
**Autor:** ixgram

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Puntos de Integración](#puntos-de-integración)
3. [DTOs Disponibles](#dtos-disponibles)
4. [Detalles de Integración por Sección](#detalles-de-integración-por-sección)
5. [Ejemplos de Implementación](#ejemplos-de-implementación)
6. [Flujo de Datos con DTOs](#flujo-de-datos-con-dtos)

---

## 🎯 Visión General

Los DTOs (`WidgetDTO` y `EChartWidgetDTO`) proporcionan una capa de transferencia de datos **fuertemente tipada** y **validada** entre capas de la aplicación. Reemplazan el uso de diccionarios genéricos con estructura predefinida.

### Beneficios

✅ **Type Safety**: Type hints completos en toda la arquitectura  
✅ **Validación integrada**: Método `validate()` en cada DTO  
✅ **Serialización estándar**: `to_dict()` y `from_dict()` consistentes  
✅ **Documentación clara**: Propiedades bien documentadas  
✅ **Mantenibilidad**: Cambios centralizados en DTOs  

---

## 🔗 Puntos de Integración

| # | Archivo | Método | Tipo de DTO | Sección |
|---|---------|--------|------------|---------|
| 1 | `widget_service.py` | `add_echart()` | `EChartWidgetDTO` | Recepción y validación |
| 2 | `widget_service.py` | `add()` | `WidgetDTO` | CRUD genérico |
| 3 | `widget_service.py` | `edit()` | `WidgetDTO / EChartWidgetDTO` | Actualización |
| 4 | `widget_service.py` | `get_all()` | `List[WidgetDTO]` | Lectura |
| 5 | `widget_service.py` | `render_layout()` | `List[EChartWidgetDTO]` | Transformación |
| 6 | `echart_transformer.py` | `transform_widget()` | `EChartWidgetDTO` | Transformación |
| 7 | `echart_transformer.py` | `transform_batch()` | `List[EChartWidgetDTO]` | Batch processing |
| 8 | `base_echart_builder.py` | `build()` | `EChartWidgetDTO` | Construcción |
| 9 | `query_service.py` | `get_all()` | `List[WidgetDTO]` | Query builder |
| 10 | `dataset.py` | Dataset data | `WidgetDTO` | Datos del dominio |

---

## 📦 DTOs Disponibles

### WidgetDTO
```python
@dataclass
class WidgetDTO:
    id: str
    type: str
    properties: dict[str, Any]
    created_at: str | None
    modified_at: str | None
    position: dict[str, int]
```

**Métodos:**
- `to_dict()`: Convierte a diccionario
- `from_dict(data)`: Crea desde diccionario
- `validate()`: Retorna (bool, list[str]) - validación

### EChartWidgetDTO (hereda de WidgetDTO)
```python
@dataclass
class EChartWidgetDTO(WidgetDTO):
    chart_type: str
    echart_data: dict[str, Any]
    echart_config: dict[str, Any]
```

**Métodos adicionales:**
- `get_chart_config_for_render()`: Config lista para renderizar
- `update_chart_data(new_data)`: Actualiza datos
- `update_chart_config(new_config)`: Actualiza configuración

---

## 🔍 Detalles de Integración por Sección

### 1️⃣ **WidgetService.add_echart() - Recepción**

**Ubicación:** `daltek/domain/widget_service/widget_service.py:242-288`

**Cambio propuesto:**

```python
from daltek.dtos import EChartWidgetDTO

@frappe.whitelist()
def add_echart(
    self,
    doc_name: str,
    chart_type: str,
    chart_data: str | dict,
    chart_config: str | dict = None,
    widget_properties: dict = None,
) -> dict[str, Any]:
    """Crear EChart con validación mediante DTO."""
    try:
        # Parsear inputs
        if isinstance(chart_data, str):
            chart_data = json.loads(chart_data)
        if isinstance(chart_config, str):
            chart_config = json.loads(chart_config)
        
        # ✅ CREAR DTO AQUÍ
        echart_dto = EChartWidgetDTO(
            id=f"widget_{int(time.time() * 1000)}",
            type="echart",
            chart_type=chart_type,
            echart_data=chart_data,
            echart_config=chart_config or {},
            properties=widget_properties or {},
            position={"x": 0, "y": 0}
        )
        
        # ✅ VALIDAR ANTES DE PROCESAR
        is_valid, errors = echart_dto.validate()
        if not is_valid:
            return {
                "success": False,
                "error": f"Validación fallida: {'; '.join(errors)}"
            }
        
        # Continuar con lógica existente pero usando DTO
        builder = self.echart_factory.create(chart_type)
        # ... resto del código
```

**Cambios:**
- Importar `EChartWidgetDTO`
- Crear instancia del DTO con los parámetros
- Llamar `validate()` inmediatamente
- Usar propiedades del DTO en lugar de diccionarios

---

### 2️⃣ **WidgetService.add() - CRUD Genérico**

**Ubicación:** `daltek/domain/widget_service/widget_service.py:51-94`

**Cambio propuesto:**

```python
from daltek.dtos import WidgetDTO, EChartWidgetDTO

@frappe.whitelist()
def add(self, doc_name: str, widget: dict[str, Any]) -> dict[str, Any]:
    """
    Añade un widget al layout.
    
    ✅ INTEGRACIÓN DTO:
    - Convertir diccionario a DTO según tipo
    - Validar DTO
    - Usar propiedades del DTO
    """
    try:
        if not frappe.db.exists("Daltek", doc_name):
            return {
                "success": False,
                "error": f"Documento '{doc_name}' no existe",
            }
        
        # ✅ CREAR DTO SEGÚN TIPO
        if widget.get("type") == "echart":
            dto = EChartWidgetDTO.from_dict(widget)
        else:
            dto = WidgetDTO.from_dict(widget)
        
        # ✅ VALIDAR
        is_valid, errors = dto.validate()
        if not is_valid:
            return {"success": False, "error": "; ".join(errors)}
        
        # ✅ USAR DTO PARA ALMACENAR
        layout = self.get_layout(doc_name)
        layout.append(dto.to_dict())
        
        # Guardar en BD
        doc = frappe.get_doc("Daltek", doc_name)
        doc.layout = json.dumps(layout)
        doc.save()
        
        return {
            "success": True,
            "widget": dto.to_dict(),
            "layout": layout
        }
```

---

### 3️⃣ **WidgetService.edit() - Actualización**

**Ubicación:** `daltek/domain/widget_service/widget_service.py:96-140`

**Cambio propuesto:**

```python
@frappe.whitelist()
def edit(
    self, doc_name: str, widget_id: str, widget_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Edita un widget.
    
    ✅ INTEGRACIÓN DTO:
    - Cargar DTO existente
    - Actualizar campos
    - Validar cambios
    """
    try:
        layout = self.get_layout(doc_name)
        widget = None
        widget_index = -1
        
        for i, w in enumerate(layout):
            if w.get("id") == widget_id:
                widget = w
                widget_index = i
                break
        
        if not widget:
            return {"success": False, "error": "Widget no encontrado"}
        
        # ✅ CARGAR DTO EXISTENTE
        if widget.get("type") == "echart":
            dto = EChartWidgetDTO.from_dict(widget)
        else:
            dto = WidgetDTO.from_dict(widget)
        
        # ✅ ACTUALIZAR DESDE DATA
        for key, value in widget_data.items():
            if hasattr(dto, key):
                setattr(dto, key, value)
        
        # ✅ VALIDAR CAMBIOS
        is_valid, errors = dto.validate()
        if not is_valid:
            return {"success": False, "error": "; ".join(errors)}
        
        # ✅ GUARDAR USANDO DTO
        layout[widget_index] = dto.to_dict()
        doc = frappe.get_doc("Daltek", doc_name)
        doc.layout = json.dumps(layout)
        doc.save()
        
        return {"success": True, "widget": dto.to_dict()}
```

---

### 4️⃣ **WidgetService.get_all() - Lectura**

**Ubicación:** `daltek/domain/query_service/query_service.py:233-244`

**Cambio propuesto:**

```python
@frappe.whitelist()
def get_all(self, doc_name: str) -> dict[str, Any]:
    """
    Obtiene todos los widgets.
    
    ✅ INTEGRACIÓN DTO:
    - Convertir cada widget a DTO
    - Retornar DTOs en lugar de dicts
    """
    try:
        doc = frappe.get_doc("Daltek", doc_name)
        layout = json.loads(doc.layout or "[]")
        
        # ✅ CONVERTIR A DTOs
        widgets_dtos = []
        for widget_data in layout:
            if widget_data.get("type") == "echart":
                dto = EChartWidgetDTO.from_dict(widget_data)
            else:
                dto = WidgetDTO.from_dict(widget_data)
            
            # Validar antes de retornar
            is_valid, _ = dto.validate()
            if is_valid:
                widgets_dtos.append(dto)
        
        return {
            "success": True,
            "widgets": [dto.to_dict() for dto in widgets_dtos],
            "count": len(widgets_dtos)
        }
    except Exception as e:
        frappe.log_error(str(e), "QueryService.get_all")
        return {"success": False, "error": str(e)}
```

---

### 5️⃣ **WidgetService.render_layout() - Transformación**

**Ubicación:** `daltek/domain/widget_service/widget_service.py:25-49`

**Cambio propuesto:**

```python
@frappe.whitelist()
def render_layout(self, doc_name: str) -> dict[str, Any]:
    """
    Renderiza layout con DTOs.
    
    ✅ INTEGRACIÓN DTO:
    - Cargar DTOs desde layout
    - Transformar usando DTOs
    - Retornar DTOs preparados
    """
    try:
        if not frappe.db.exists("Daltek", doc_name):
            return {
                "success": False,
                "error": f"Documento '{doc_name}' no existe",
            }
        
        layout = self.get_layout(doc_name)
        
        # ✅ CARGAR COMO DTOs
        echart_dtos = []
        for widget_data in layout:
            if widget_data.get("type") == "echart":
                dto = EChartWidgetDTO.from_dict(widget_data)
                echart_dtos.append(dto)
        
        # ✅ TRANSFORMAR CON DTOs
        transformed_widgets = []
        for echart_dto in echart_dtos:
            # Usar método del DTO para obtener config renderizable
            render_config = echart_dto.get_chart_config_for_render()
            transformed_widgets.append(render_config)
        
        return {
            "success": True,
            "layout": layout,
            "widgets": transformed_widgets,
            "count": len(transformed_widgets),
        }
    except Exception as e:
        frappe.log_error(str(e), "WidgetService.render_layout")
        return {"success": False, "error": str(e)}
```

---

### 6️⃣ **EChartTransformer.transform_widget() - Transformación**

**Ubicación:** `daltek/domain/widget_service/echart/echart_transforrmer.py:32-52`

**Cambio propuesto:**

```python
from daltek.dtos import EChartWidgetDTO

def transform_widget(self, widget: dict[str, Any]) -> dict[str, Any]:
    """
    Transforma un widget para renderización.
    
    ✅ INTEGRACIÓN DTO:
    - Recibir dict, crear DTO
    - Usar métodos del DTO
    - Retornar dict transformado
    """
    try:
        # ✅ CREAR DTO DESDE DICT
        if widget.get("type") == "echart":
            echart_dto = EChartWidgetDTO.from_dict(widget)
            
            # ✅ USAR MÉTODO DEL DTO
            render_config = echart_dto.get_chart_config_for_render()
            
            # Aplicar transformaciones adicionales
            if self.optimizations_enabled:
                render_config["config"] = self._optimize_config(
                    render_config["config"]
                )
            
            # Añadir metadata
            render_config["render_info"] = {
                "transformed_at": frappe.utils.now_datetime().isoformat(),
                "type": echart_dto.chart_type,
                "is_optimized": self.optimizations_enabled,
            }
            
            return render_config
        else:
            # Widgets genéricos
            return widget
            
    except Exception as e:
        frappe.log_error(str(e), "EChartTransformer.transform_widget")
        return {"success": False, "error": str(e)}
```

---

### 7️⃣ **EChartTransformer.transform_batch() - Batch Processing**

**Ubicación:** `daltek/domain/widget_service/echart/echart_transforrmer.py:83-96`

**Cambio propuesto:**

```python
def transform_batch(self, widgets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Transforma múltiples widgets.
    
    ✅ INTEGRACIÓN DTO:
    - Crear lista de DTOs
    - Procesar en batch
    - Retornar transformados
    """
    transformed = []
    
    for widget_data in widgets:
        # ✅ CREAR DTO
        if widget_data.get("type") == "echart":
            try:
                echart_dto = EChartWidgetDTO.from_dict(widget_data)
                
                # Validar
                is_valid, errors = echart_dto.validate()
                if not is_valid:
                    frappe.log_error(
                        f"DTO inválido: {'; '.join(errors)}",
                        "TransformBatch"
                    )
                    continue
                
                # Transformar usando DTO
                transformed_widget = self.transform_widget(
                    echart_dto.to_dict()
                )
                transformed.append(transformed_widget)
                
            except Exception as e:
                frappe.log_error(str(e), "TransformBatch")
                continue
    
    return transformed
```

---

### 8️⃣ **BaseEChartBuilder.build() - Construcción**

**Ubicación:** `daltek/domain/widget_service/echart/base_echart_builder.py:33-85`

**Cambio propuesto:**

```python
from daltek.dtos import EChartWidgetDTO

def build(self, data: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    """
    Construye configuración del EChart.
    
    ✅ INTEGRACIÓN DTO:
    - Validar input usando DTO
    - Construir retornando DTO
    """
    try:
        # ✅ VALIDAR USANDO DTO (antes de procesar)
        temp_dto = EChartWidgetDTO(
            id="temp",
            type="echart",
            chart_type=self.chart_type,
            echart_data=data,
            echart_config=config,
        )
        
        is_valid, errors = temp_dto.validate()
        if not is_valid:
            return {
                "success": False,
                "error": f"Datos inválidos: {'; '.join(errors)}",
                "chart_type": self.chart_type,
            }
        
        # Lógica de construcción original
        self.data = data
        self.config = config
        self.errors = []
        
        if not self._validate_data():
            return {
                "success": False,
                "error": f"Validación fallida: {'; '.join(self.errors)}",
                "chart_type": self.chart_type,
            }
        
        # Construcción...
        echart_config = self._build_base_config()
        # ... resto del código
        
        # ✅ RETORNAR USANDO DTO
        result_dto = EChartWidgetDTO(
            id="temp",
            type="echart",
            chart_type=self.chart_type,
            echart_data=data,
            echart_config=echart_config,
        )
        
        return {
            "success": True,
            "chart_type": self.chart_type,
            "config": result_dto.get_chart_config_for_render(),
            "data": data,
        }
```

---

### 9️⃣ **QueryService.get_all() - Query Builder**

**Ubicación:** `daltek/domain/query_service/query_service.py:233-244`

**Cambio propuesto:**

```python
from daltek.dtos import WidgetDTO, EChartWidgetDTO

@frappe.whitelist()
def get_all(self, doc_name: str) -> dict[str, Any]:
    """
    Obtiene todas las queries con DTOs.
    
    ✅ INTEGRACIÓN DTO:
    - Retornar widgets como DTOs tipados
    - Permitir downstream type-safe processing
    """
    try:
        doc = frappe.get_doc("Daltek", doc_name)
        queries = self._get_queries_list(doc)
        
        # ✅ CONVERTIR A DTOs
        query_dtos = []
        for query_data in queries:
            if query_data.get("type") == "echart":
                dto = EChartWidgetDTO.from_dict(query_data)
            else:
                dto = WidgetDTO.from_dict(query_data)
            
            query_dtos.append(dto)
        
        return {
            "success": True,
            "queries": [dto.to_dict() for dto in query_dtos],
            "count": len(query_dtos),
            "dtos": query_dtos  # Retornar DTOs para processing
        }
    except Exception as e:
        frappe.log_error(str(e), "QueryService.get_all")
        return {"success": False, "error": str(e)}
```

---

### 🔟 **Dataset.py - Domain Data**

**Ubicación:** `daltek/domain/dataset.py`

**Cambio propuesto:**

```python
from daltek.dtos import WidgetDTO, EChartWidgetDTO

class Dataset:
    """
    Gestión de datos del dominio.
    
    ✅ INTEGRACIÓN DTO:
    - Modelar widgets como DTOs
    - Usar DTOs en transformaciones de datos
    """
    
    def process_widget_data(
        self, 
        widget_data: dict[str, Any]
    ) -> WidgetDTO | EChartWidgetDTO:
        """
        Procesa datos de widget a DTO.
        
        Args:
            widget_data: Dict con datos del widget
            
        Returns:
            DTO del widget (WidgetDTO o EChartWidgetDTO)
        """
        # ✅ CREAR DTO SEGÚN TIPO
        if widget_data.get("type") == "echart":
            dto = EChartWidgetDTO.from_dict(widget_data)
        else:
            dto = WidgetDTO.from_dict(widget_data)
        
        # ✅ VALIDAR
        is_valid, errors = dto.validate()
        if not is_valid:
            raise ValueError(f"Datos inválidos: {'; '.join(errors)}")
        
        return dto
    
    def transform_widgets_batch(
        self,
        widgets: list[dict[str, Any]]
    ) -> list[WidgetDTO | EChartWidgetDTO]:
        """
        Transforma múltiples widgets a DTOs.
        
        Args:
            widgets: Lista de dicts de widgets
            
        Returns:
            Lista de DTOs validados
        """
        dtos = []
        for widget_data in widgets:
            try:
                dto = self.process_widget_data(widget_data)
                dtos.append(dto)
            except Exception as e:
                frappe.log_error(str(e), "Dataset.transform_widgets_batch")
                continue
        
        return dtos
```

---

## 📝 Ejemplos de Implementación

### Ejemplo 1: Crear Widget EChart Completo

```python
from daltek.dtos import EChartWidgetDTO
import time

# Crear DTO
echart_dto = EChartWidgetDTO(
    id=f"widget_{int(time.time() * 1000)}",
    type="echart",
    chart_type="line",
    echart_data={
        "series": [
            {"name": "Ventas", "data": [100, 150, 120, 200]},
            {"name": "Ganancias", "data": [30, 50, 40, 70]},
        ],
        "categories": ["Ene", "Feb", "Mar", "Abr"]
    },
    echart_config={
        "smooth": True,
        "fill_area": True,
        "colors": ["#2196F3", "#4CAF50"],
    },
    properties={"title": "Monthly Performance"},
    position={"x": 0, "y": 0},
    created_at="2025-12-01T10:00:00",
    modified_at="2025-12-01T10:00:00",
)

# Validar
is_valid, errors = echart_dto.validate()
if is_valid:
    print("✓ DTO válido")
    
    # Usar DTO
    render_config = echart_dto.get_chart_config_for_render()
    # Renderizar...
else:
    print(f"✗ Errores: {errors}")
```

### Ejemplo 2: Cargar y Actualizar Widget

```python
from daltek.dtos import EChartWidgetDTO

# Cargar desde dict (DB)
widget_dict = {
    "id": "widget_1_123456",
    "type": "echart",
    "chart_type": "bar",
    "echart_data": {...},
    "echart_config": {...},
    "properties": {"title": "Sales"},
    "position": {"x": 0, "y": 1},
}

# ✅ Crear DTO desde dict
echart_dto = EChartWidgetDTO.from_dict(widget_dict)

# ✅ Actualizar datos
new_data = {"series": [...], "categories": [...]}
echart_dto.update_chart_data(new_data)

# ✅ Validar cambios
is_valid, errors = echart_dto.validate()

# ✅ Convertir a dict para guardar
updated_dict = echart_dto.to_dict()
# Guardar en BD...
```

### Ejemplo 3: Procesar Batch de Widgets

```python
from daltek.dtos import WidgetDTO, EChartWidgetDTO

def process_widgets_batch(widgets_list):
    """Procesa múltiples widgets usando DTOs."""
    
    dtos = []
    
    for widget_data in widgets_list:
        try:
            # ✅ Crear DTO según tipo
            if widget_data.get("type") == "echart":
                dto = EChartWidgetDTO.from_dict(widget_data)
            else:
                dto = WidgetDTO.from_dict(widget_data)
            
            # ✅ Validar
            is_valid, errors = dto.validate()
            if not is_valid:
                print(f"Widget {widget_data.get('id')} inválido: {errors}")
                continue
            
            # ✅ Procesar
            dtos.append(dto)
            
        except Exception as e:
            print(f"Error procesando widget: {e}")
            continue
    
    return dtos
```

---

## 🔄 Flujo de Datos con DTOs

### Flujo Completo: Crear → Validar → Guardar → Renderizar

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. CLIENTE - Frontend                         │
│   Envía: {type: "echart", chart_type: "line", data: {...}}     │
└──────────────────────┬──────────────────────────────────────────┘
                       │ POST /api/method/add_echart
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│              2. WidgetService.add_echart()                       │
│                                                                  │
│  • Parsear JSON                                                  │
│  ✅ EChartWidgetDTO.from_dict(data)  ← DTO creado              │
│  ✅ echart_dto.validate()             ← Validación             │
│  ✅ builder.build(echart_dto.to_dict())                         │
│                                                                  │
│  Return: {"success": true, "widget": dto.to_dict()}            │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Guardar en BD
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│              3. Almacenamiento (Frappe DB)                       │
│                                                                  │
│  layout = [                                                      │
│    {                                                             │
│      "id": "widget_1_12345",                                    │
│      "type": "echart",                                          │
│      "chart_type": "line",                                      │
│      "echart_data": {...},                                      │
│      "echart_config": {...},                                    │
│      "properties": {...}                                        │
│    }                                                             │
│  ]                                                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │ GET /api/method/render_layout
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│         4. WidgetService.render_layout() - Lectura              │
│                                                                  │
│  • Obtener layout de BD                                         │
│  ✅ EChartWidgetDTO.from_dict(widget)  ← DTO creado            │
│  ✅ echart_dto.validate()               ← Validación           │
│  ✅ echart_dto.get_chart_config_for_render()                    │
│                                                                  │
│  Return: [transformed_configs...]                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Transformación
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│    5. EChartTransformer.transform_widget() - Transformación     │
│                                                                  │
│  ✅ EChartWidgetDTO.from_dict(widget) ← DTO creado             │
│  ✅ echart_dto.get_chart_config_for_render()                    │
│  • Aplicar optimizaciones                                       │
│  • Normalizar colores                                           │
│  • Adaptación responsive                                        │
│                                                                  │
│  Return: {id, type, config, data, properties, render_info}    │
└──────────────────────┬──────────────────────────────────────────┘
                       │ JSON optimizado
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│              6. CLIENTE - Renderización                          │
│                                                                  │
│  var chart = echarts.init(dom);                                │
│  chart.setOption(response.config);                             │
│                                                                  │
│  ✅ Widget renderizado con datos optimizados                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Resumen de Beneficios

| Aspecto | Sin DTOs | Con DTOs |
|--------|----------|----------|
| **Tipado** | Dicts sin tipo | Type hints completos |
| **Validación** | Manual en cada método | Integrada en DTO |
| **Documentación** | En comentarios | En docstrings y type hints |
| **Reutilización** | Código duplicado | Métodos centralizados |
| **Mantenibilidad** | Cambios dispersos | Cambios centralizados |
| **IDE Support** | Limitado | Autocompletar + errors |
| **Testing** | Complejidad alta | Tests enfocados en DTO |

---

## ✅ Checklist de Implementación

- [ ] Importar DTOs en `widget_service.py`
- [ ] Importar DTOs en `echart_transformer.py`
- [ ] Importar DTOs en `base_echart_builder.py`
- [ ] Importar DTOs en `query_service.py`
- [ ] Actualizar `add_echart()` para usar DTOs
- [ ] Actualizar `add()` para usar DTOs
- [ ] Actualizar `edit()` para usar DTOs
- [ ] Actualizar `get_all()` para retornar DTOs
- [ ] Actualizar `render_layout()` para usar DTOs
- [ ] Actualizar `transform_widget()` para usar DTOs
- [ ] Actualizar `transform_batch()` para usar DTOs
- [ ] Actualizar `build()` en builders para validar con DTOs
- [ ] Crear tests para validación de DTOs
- [ ] Actualizar documentación de API
- [ ] Migrar datos existentes (si aplica)

---

**Próximos pasos:** Implementar cambios gradualmente comenzando por `WidgetService.add_echart()`
