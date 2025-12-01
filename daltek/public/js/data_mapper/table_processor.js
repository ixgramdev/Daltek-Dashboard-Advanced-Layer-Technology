// TableProcessor: Procesador de datos con operaciones registradas
// Maneja transformaciones y filtros sobre datos tabulares

class TableProcessor {
    constructor(data, queryName) {
        this.originalData = JSON.parse(JSON.stringify(data)); // Copia profunda
        this.processedData = JSON.parse(JSON.stringify(data));
        this.queryName = queryName;
        this.operations = []; // Historial de operaciones
        this.columns = this.detectColumns();
        this.originalColumns = JSON.parse(JSON.stringify(this.columns)); // Guardar columnas originales
    }

    // Detecta las columnas del dataset
    detectColumns() {
        if (!this.originalData || this.originalData.length === 0) {
            return [];
        }

        const firstRow = this.originalData[0];
        return Object.keys(firstRow).map(key => ({
            name: key,
            type: this.detectColumnType(key),
            visible: true,
            calculated: false
        }));
    }

    // Actualiza las columnas desde los datos procesados (incluye columnas calculadas)
    updateColumns() {
        if (!this.processedData || this.processedData.length === 0) {
            return;
        }

        const firstRow = this.processedData[0];
        const currentColumnNames = this.columns.map(c => c.name);
        
        // Agregar columnas nuevas que no existen
        Object.keys(firstRow).forEach(key => {
            if (!currentColumnNames.includes(key)) {
                console.log('Agregando columna nueva detectada:', key);
                this.columns.push({
                    name: key,
                    type: this.detectColumnType(key),
                    visible: true,
                    calculated: true
                });
            }
        });
    }

    // Detecta el tipo de datos de una columna
    detectColumnType(columnName) {
        // Usar processedData para incluir columnas calculadas
        const dataSource = this.processedData.length > 0 ? this.processedData : this.originalData;
        const sample = dataSource.slice(0, 10).map(row => row[columnName]).filter(val => val !== undefined && val !== null);
        
        if (sample.length === 0) {
            return 'text';
        }
        
        // Verificar si es número
        if (sample.every(val => !isNaN(val) && val !== '')) {
            return 'number';
        }
        
        // Verificar si es fecha
        if (sample.every(val => !isNaN(Date.parse(val)))) {
            return 'date';
        }
        
        return 'text';
    }

    // Aplica un filtro a los datos
    applyFilter(column, operator, value) {
        // Check if there's already a filter on the same column with the same operator
        const existingFilterIndex = this.operations.findIndex(
            op => op.type === 'filter' && op.column === column && op.operator === operator
        );
        
        // If exists, remove it before applying the new one
        if (existingFilterIndex !== -1) {
            this.operations.splice(existingFilterIndex, 1);
        }

        const operation = {
            type: 'filter',
            column: column,
            operator: operator,
            value: value,
            timestamp: new Date().toISOString()
        };

        this.processedData = this.processedData.filter(row => {
            const cellValue = row[column];
            
            switch(operator) {
                case 'equals':
                    return cellValue == value;
                case 'not_equals':
                    return cellValue != value;
                case 'contains':
                    return String(cellValue).toLowerCase().includes(String(value).toLowerCase());
                case 'not_contains':
                    return !String(cellValue).toLowerCase().includes(String(value).toLowerCase());
                case 'starts_with':
                    return String(cellValue).toLowerCase().startsWith(String(value).toLowerCase());
                case 'ends_with':
                    return String(cellValue).toLowerCase().endsWith(String(value).toLowerCase());
                case 'greater_than':
                    return parseFloat(cellValue) > parseFloat(value);
                case 'less_than':
                    return parseFloat(cellValue) < parseFloat(value);
                case 'greater_equal':
                    return parseFloat(cellValue) >= parseFloat(value);
                case 'less_equal':
                    return parseFloat(cellValue) <= parseFloat(value);
                case 'is_empty':
                    return !cellValue || cellValue === '';
                case 'is_not_empty':
                    return cellValue && cellValue !== '';
                default:
                    return true;
            }
        });

        this.operations.push(operation);
        return this;
    }

    // Ordena los datos por columna
    sort(column, order = 'asc') {
        const operation = {
            type: 'sort',
            column: column,
            order: order,
            timestamp: new Date().toISOString()
        };

        this.processedData.sort((a, b) => {
            let valA = a[column];
            let valB = b[column];

            // Convertir a número si es posible
            if (!isNaN(valA) && !isNaN(valB)) {
                valA = parseFloat(valA);
                valB = parseFloat(valB);
            }

            if (valA < valB) return order === 'asc' ? -1 : 1;
            if (valA > valB) return order === 'asc' ? 1 : -1;
            return 0;
        });

        this.operations.push(operation);
        return this;
    }

    // Agrupa datos por columna
    groupBy(column, aggregations) {
        const operation = {
            type: 'group_by',
            column: column,
            aggregations: aggregations,
            timestamp: new Date().toISOString()
        };

        const groups = {};
        
        // Agrupar datos
        this.processedData.forEach(row => {
            const key = row[column];
            if (!groups[key]) {
                groups[key] = [];
            }
            groups[key].push(row);
        });

        // Aplicar agregaciones
        this.processedData = Object.keys(groups).map(key => {
            const group = groups[key];
            const result = {};
            result[column] = key;

            Object.keys(aggregations).forEach(aggColumn => {
                const aggFunc = aggregations[aggColumn];
                const values = group.map(row => parseFloat(row[aggColumn])).filter(v => !isNaN(v));

                switch(aggFunc) {
                    case 'sum':
                        result[aggColumn] = values.reduce((a, b) => a + b, 0);
                        break;
                    case 'avg':
                        result[aggColumn] = values.reduce((a, b) => a + b, 0) / values.length;
                        break;
                    case 'count':
                        result[aggColumn] = group.length;
                        break;
                    case 'min':
                        result[aggColumn] = Math.min(...values);
                        break;
                    case 'max':
                        result[aggColumn] = Math.max(...values);
                        break;
                }
            });

            return result;
        });

        // Actualizar columnas para mostrar solo las relevantes (columna de agrupación + columnas agregadas)
        const relevantColumns = [column, ...Object.keys(aggregations)];
        this.columns = relevantColumns.map(col => ({
            name: col,
            type: this.detectColumnType(col),
            visible: true,
            calculated: false
        }));

        this.operations.push(operation);
        return this;
    }

    // Selecciona columnas específicas
    selectColumns(columns) {
        const operation = {
            type: 'select',
            columns: columns,
            timestamp: new Date().toISOString()
        };

        this.processedData = this.processedData.map(row => {
            const newRow = {};
            columns.forEach(col => {
                if (row.hasOwnProperty(col)) {
                    newRow[col] = row[col];
                }
            });
            return newRow;
        });

        this.operations.push(operation);
        return this;
    }

    // Limita el número de filas
    limit(count) {
        const operation = {
            type: 'limit',
            count: count,
            timestamp: new Date().toISOString()
        };

        this.processedData = this.processedData.slice(0, count);
        this.operations.push(operation);
        return this;
    }

    // Calcula una nueva columna
    calculate(newColumn, formula) {
        const operation = {
            type: 'calculate',
            column: newColumn,
            formula: formula,
            timestamp: new Date().toISOString()
        };

        this.processedData = this.processedData.map(row => {
            try {
                const result = this.evaluateFormula(formula, row);
                row[newColumn] = result;
            } catch(e) {
                row[newColumn] = null;
            }
            return row;
        });

        // Agregar nueva columna si no existe
        const existingCol = this.columns.find(col => col.name === newColumn);
        if (existingCol) {
            existingCol.calculated = true;
        } else {
            this.columns.push({
                name: newColumn,
                type: 'number',
                visible: true,
                calculated: true
            });
        }

        this.operations.push(operation);
        return this;
    }

    // Evalúa una fórmula simple
    evaluateFormula(formula, row) {
        let expression = formula;
        
        // Ordenar columnas por longitud (más largas primero) para evitar reemplazos parciales
        const columns = Object.keys(row).sort((a, b) => b.length - a.length);
        
        columns.forEach(col => {
            const value = parseFloat(row[col]);
            if (!isNaN(value)) {
                const escapedCol = col.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                expression = expression.replace(new RegExp(`\\b${escapedCol}\\b`, 'g'), value);
            }
        });

        return Function('"use strict"; return (' + expression + ')')();
    }

    // Resetea a datos originales
    reset() {
        console.log('TableProcessor.reset() called');
        console.log('Before reset - operations:', this.operations.length);
        console.log('Before reset - columns:', this.columns.length);
        
        this.processedData = JSON.parse(JSON.stringify(this.originalData));
        this.operations = [];
        
        // Restaurar columnas originales (sin columnas calculadas)
        this.columns = JSON.parse(JSON.stringify(this.originalColumns));
        
        console.log('After reset - operations:', this.operations.length);
        console.log('After reset - columns:', this.columns.length);
        console.log('After reset - processedData rows:', this.processedData.length);
        
        return this;
    }

    // Deshace la última operación
    undo() {
        if (this.operations.length === 0) return this;
        
        this.operations.pop();
        this.processedData = JSON.parse(JSON.stringify(this.originalData));
        
        // Reaplicar todas las operaciones excepto la última
        const ops = [...this.operations];
        this.operations = [];
        
        ops.forEach(op => {
            switch(op.type) {
                case 'filter':
                    this.applyFilter(op.column, op.operator, op.value);
                    break;
                case 'sort':
                    this.sort(op.column, op.order);
                    break;
                case 'group_by':
                    this.groupBy(op.column, op.aggregations);
                    break;
                case 'select':
                    this.selectColumns(op.columns);
                    break;
                case 'limit':
                    this.limit(op.count);
                    break;
                case 'calculate':
                    this.calculate(op.column, op.formula);
                    break;
            }
        });
        
        return this;
    }

    // Obtiene los datos procesados
    getData() {
        return this.processedData;
    }

    // Exporta el procesamiento como JSON
    exportConfig() {
        return {
            query_name: this.queryName,
            original_count: this.originalData.length,
            processed_count: this.processedData.length,
            columns: this.columns,
            operations: this.operations,
            timestamp: new Date().toISOString()
        };
    }

    // Importa y aplica configuración
    importConfig(config) {
        this.reset();
        
        config.operations.forEach(op => {
            switch(op.type) {
                case 'filter':
                    this.applyFilter(op.column, op.operator, op.value);
                    break;
                case 'sort':
                    this.sort(op.column, op.order);
                    break;
                case 'group_by':
                    this.groupBy(op.column, op.aggregations);
                    break;
                case 'select':
                    this.selectColumns(op.columns);
                    break;
                case 'limit':
                    this.limit(op.count);
                    break;
                case 'calculate':
                    this.calculate(op.column, op.formula);
                    break;
            }
        });
        
        return this;
    }

    // Obtiene estadísticas de una columna
    getColumnStats(column) {
        const values = this.processedData
            .map(row => row[column])
            .filter(v => v !== null && v !== undefined && v !== '');

        const numericValues = values.filter(v => !isNaN(v)).map(v => parseFloat(v));

        return {
            count: values.length,
            unique: new Set(values).size,
            numeric: numericValues.length > 0,
            min: numericValues.length > 0 ? Math.min(...numericValues) : null,
            max: numericValues.length > 0 ? Math.max(...numericValues) : null,
            avg: numericValues.length > 0 ? numericValues.reduce((a,b) => a+b, 0) / numericValues.length : null
        };
    }
}

// Exportar para uso global
window.TableProcessor = TableProcessor;
