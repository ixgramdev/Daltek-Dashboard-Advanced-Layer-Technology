# 📊 Data Mapper - Procesador de Tablas Interactivo

## 🎯 Descripción

Interfaz de usuario completa para visualizar, filtrar, transformar y procesar datos de consultas SQL. Permite aplicar operaciones sobre los datos y exportar la configuración en formato JSON.

## 🚀 Componentes

### 1. **TableProcessor** (`table_processor.js`)
Motor de procesamiento de datos que maneja todas las transformaciones:

- **Filtros**: equals, not_equals, contains, greater_than, less_than, etc.
- **Ordenamiento**: Ascendente/descendente por cualquier columna
- **Agrupación**: GROUP BY con agregaciones (sum, avg, count, min, max)
- **Cálculos**: Crear columnas calculadas con fórmulas
- **Límites**: Limitar número de filas
- **Selección**: Seleccionar columnas específicas

### 2. **DataTableUI** (`data_table_ui.js`)
Interfaz visual con Bootstrap:

- Tabla interactiva con paginación
- Ordenamiento por columnas (click en header)
- Diálogos para filtros, agrupación y cálculos
- Historial de operaciones aplicadas
- Exportación a JSON
- Deshacer operaciones

## 📦 Archivos

```
/public/js/data_mapper/
├── table_processor.js     # Motor de procesamiento
├── data_table_ui.js       # Interfaz de usuario
├── demo.html              # Demo standalone
└── README_TABLE_UI.md     # Esta documentación
```

## 🎨 Uso Básico

### Standalone (Demo)

```bash
# Abrir demo.html en el navegador
open demo.html
```

### En Frappe

```javascript
// 1. Incluir scripts en tu página
frappe.require([
    '/assets/daltek/js/data_mapper/table_processor.js',
    '/assets/daltek/js/data_mapper/data_table_ui.js'
], function() {
    // 2. Obtener datos de una query
    frappe.call({
        method: 'daltek.daltek.doctype.daltek.daltek.execute_query',
        args: {
            doc_name: 'DALTEK-001',
            query_id: 'query_123'
        },
        callback: function(r) {
            if (r.message.success) {
                // 3. Inicializar UI
                const ui = new DataTableUI('container-id');
                ui.init(r.message.results, 'Nombre de Consulta');
            }
        }
    });
});
```

## 🔧 API del TableProcessor

### Cargar Datos
```javascript
const processor = new TableProcessor(data, 'Query Name');
```

### Aplicar Filtro
```javascript
processor.applyFilter('columna', 'equals', 'valor');
processor.applyFilter('precio', 'greater_than', 100);
processor.applyFilter('nombre', 'contains', 'laptop');
```

### Ordenar
```javascript
processor.sort('columna', 'asc');  // Ascendente
processor.sort('columna', 'desc'); // Descendente
```

### Agrupar
```javascript
processor.groupBy('categoria', {
    'ventas': 'sum',
    'cantidad': 'avg'
});
```

### Calcular Columna
```javascript
processor.calculate('margen', 'ventas - costo');
processor.calculate('total_con_iva', 'total * 1.16');
```

### Limitar Filas
```javascript
processor.limit(10); // Top 10
```

### Obtener Datos Procesados
```javascript
const datos = processor.getData();
console.log(datos);
```

### Exportar Configuración
```javascript
const config = processor.exportConfig();
console.log(JSON.stringify(config, null, 2));
```

**Ejemplo de JSON exportado:**
```json
{
  "query_name": "Reporte de Ventas",
  "original_count": 100,
  "processed_count": 15,
  "columns": [
    {"name": "mes", "type": "text", "visible": true},
    {"name": "ventas", "type": "number", "visible": true}
  ],
  "operations": [
    {
      "type": "filter",
      "column": "ventas",
      "operator": "greater_than",
      "value": 1000,
      "timestamp": "2024-12-01T10:30:00Z"
    },
    {
      "type": "sort",
      "column": "ventas",
      "order": "desc",
      "timestamp": "2024-12-01T10:31:00Z"
    }
  ],
  "timestamp": "2024-12-01T10:32:00Z"
}
```

### Importar Configuración
```javascript
processor.importConfig(config);
```

### Deshacer/Reset
```javascript
processor.undo();  // Deshace última operación
processor.reset(); // Resetea todo
```

## 🎯 Operadores de Filtro

| Operador | Descripción | Ejemplo |
|----------|-------------|---------|
| `equals` | Igual a | columna = "valor" |
| `not_equals` | Diferente de | columna != "valor" |
| `contains` | Contiene texto | nombre contiene "laptop" |
| `not_contains` | No contiene | nombre no contiene "usado" |
| `starts_with` | Empieza con | codigo empieza con "PRD" |
| `ends_with` | Termina con | email termina con "@gmail.com" |
| `greater_than` | Mayor que | precio > 100 |
| `less_than` | Menor que | stock < 10 |
| `greater_equal` | Mayor o igual | cantidad >= 5 |
| `less_equal` | Menor o igual | descuento <= 0.2 |
| `is_empty` | Está vacío | campo es nulo |
| `is_not_empty` | No está vacío | campo tiene valor |

## 📊 Funciones de Agregación

| Función | Descripción |
|---------|-------------|
| `sum` | Suma de valores |
| `avg` | Promedio |
| `count` | Contar registros |
| `min` | Valor mínimo |
| `max` | Valor máximo |

## 💡 Ejemplos de Uso

### Ejemplo 1: Top 10 Productos Más Vendidos
```javascript
const processor = new TableProcessor(data, 'Productos');
processor
    .sort('ventas', 'desc')
    .limit(10);

console.log(processor.getData());
```

### Ejemplo 2: Ventas por Categoría
```javascript
processor
    .groupBy('categoria', {
        'ventas': 'sum',
        'cantidad': 'count'
    });
```

### Ejemplo 3: Productos con Stock Bajo
```javascript
processor
    .applyFilter('stock', 'less_than', 10)
    .sort('stock', 'asc');
```

### Ejemplo 4: Calcular Margen de Ganancia
```javascript
processor
    .calculate('margen', 'ventas - costo')
    .calculate('porcentaje_margen', '(margen / ventas) * 100')
    .sort('porcentaje_margen', 'desc');
```

### Ejemplo 5: Filtros Múltiples
```javascript
processor
    .applyFilter('categoria', 'equals', 'Electrónica')
    .applyFilter('ventas', 'greater_than', 1000)
    .applyFilter('producto', 'contains', 'laptop')
    .sort('ventas', 'desc');
```

## 🎨 Integración con Frappe

### Endpoint para guardar configuración
```python
@frappe.whitelist()
def save_table_config(doc_name, config):
    # Guardar configuración del procesador
    doc = frappe.get_doc('Daltek', doc_name)
    doc.table_config = json.dumps(config)
    doc.save()
    return {"success": True}
```

### Endpoint para aplicar configuración
```python
@frappe.whitelist()
def apply_table_config(doc_name, query_id, config):
    # 1. Ejecutar query
    query_result = execute_query(doc_name, query_id)
    
    # 2. Aquí podrías aplicar las transformaciones en backend
    # o simplemente retornar los datos para procesarlos en frontend
    
    return query_result
```

## 📱 Características de la UI

- ✅ **Responsiva**: Funciona en desktop y mobile
- ✅ **Paginación**: Maneja grandes datasets
- ✅ **Ordenamiento**: Click en headers para ordenar
- ✅ **Historial**: Visualiza todas las operaciones aplicadas
- ✅ **Export/Import**: Guarda y carga configuraciones
- ✅ **Undo**: Deshace operaciones paso a paso
- ✅ **Reset**: Vuelve a datos originales
- ✅ **Estadísticas**: Stats por columna (count, min, max, avg)

## 🔗 Integración con Data Mapper Backend

```javascript
// Usar con el DataMapperService
frappe.call({
    method: 'daltek.daltek.doctype.daltek.daltek.get_mapper_preview_by_id',
    args: {
        doc_name: 'DALTEK-001',
        query_id: 'query_123',
        mapper_config: JSON.stringify(processor.exportConfig())
    },
    callback: function(r) {
        // Datos transformados desde backend con Pandas
        console.log(r.message.data);
    }
});
```

## 🎓 Casos de Uso

1. **Análisis exploratorio de datos**: Filtrar y explorar resultados de queries
2. **Reportes personalizados**: Aplicar filtros y agrupaciones específicas
3. **Dashboards interactivos**: Configurar transformaciones visuales
4. **Data cleaning**: Filtrar registros incompletos o erróneos
5. **Agregaciones rápidas**: Calcular totales y promedios sin SQL

## 🚀 Próximas Mejoras

- [ ] Filtros avanzados (AND/OR lógico)
- [ ] Búsqueda global en tabla
- [ ] Export a CSV/Excel
- [ ] Gráficos inline en columnas
- [ ] Fórmulas avanzadas con funciones
- [ ] Drag & drop de columnas
- [ ] Guardado de vistas personalizadas

---

**Versión**: 1.0  
**Última actualización**: Diciembre 2025
