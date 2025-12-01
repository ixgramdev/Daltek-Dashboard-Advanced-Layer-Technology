// TableProcessor: Procesador de datos con operaciones registradas
// Maneja transformaciones y filtros sobre datos tabulares

class TableProcessor {
    constructor(data, queryName) {
        this.originalData = JSON.parse(JSON.stringify(data)); // Copia profunda
        this.processedData = JSON.parse(JSON.stringify(data));
        this.queryName = queryName;
        this.operations = []; // Historial de operaciones
        this.columns = this.detectColumns();
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
            visible: true
        }));
    }

    // Detecta el tipo de datos de una columna
    detectColumnType(columnName) {
        const sample = this.originalData.slice(0, 10).map(row => row[columnName]);
        
        // Verificar si es número
        if (sample.every(val => !isNaN(val) && val !== null && val !== '')) {
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
                        result[`${aggColumn}_sum`] = values.reduce((a, b) => a + b, 0);
                        break;
                    case 'avg':
                        result[`${aggColumn}_avg`] = values.reduce((a, b) => a + b, 0) / values.length;
                        break;
                    case 'count':
                        result[`${aggColumn}_count`] = group.length;
                        break;
                    case 'min':
                        result[`${aggColumn}_min`] = Math.min(...values);
                        break;
                    case 'max':
                        result[`${aggColumn}_max`] = Math.max(...values);
                        break;
                }
            });

            return result;
        });

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
                // Evaluar fórmula simple (ej: "column1 + column2")
                const result = this.evaluateFormula(formula, row);
                row[newColumn] = result;
            } catch(e) {
                row[newColumn] = null;
            }
            return row;
        });

        this.operations.push(operation);
        return this;
    }

    // Evalúa una fórmula simple
    evaluateFormula(formula, row) {
        // Reemplazar nombres de columnas por valores
        let expression = formula;
        Object.keys(row).forEach(col => {
            const value = parseFloat(row[col]) || 0;
            expression = expression.replace(new RegExp(`\\b${col}\\b`, 'g'), value);
        });

        // Evaluar expresión matemática simple
        return Function('"use strict"; return (' + expression + ')')();
    }

    // Resetea a datos originales
    reset() {
        this.processedData = JSON.parse(JSON.stringify(this.originalData));
        this.operations = [];
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
