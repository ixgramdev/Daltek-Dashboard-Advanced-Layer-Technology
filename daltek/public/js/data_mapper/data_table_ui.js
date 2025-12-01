// DataTableUI: Interfaz de usuario para visualización y procesamiento de datos
// Muestra tabla interactiva con filtros, ordenamiento y operaciones

class DataTableUI {
    constructor(containerId) {
        this.containerId = containerId;
        this.processor = null;
        this.currentPage = 1;
        this.rowsPerPage = 50;
        this.sortColumn = null;
        this.sortOrder = 'asc';
    }

    // Inicializa la UI con datos
    init(data, queryName) {
        this.processor = new TableProcessor(data, queryName);
        this.render();
    }

    // Renderiza la interfaz completa
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} no encontrado`);
            return;
        }

        container.innerHTML = `
            <div class="data-table-wrapper">
                <!-- Header con nombre de consulta y controles -->
                <div class="data-table-header">
                    <div class="query-info">
                        <h3><i class="fa fa-database"></i> ${this.processor.queryName}</h3>
                        <span class="badge badge-info">${this.processor.processedData.length} registros</span>
                    </div>
                    <div class="header-controls">
                        <button class="btn btn-sm btn-default" id="btn-add-filter">
                            <i class="fa fa-filter"></i> Añadir Filtro
                        </button>
                        <button class="btn btn-sm btn-default" id="btn-group-by">
                            <i class="fa fa-object-group"></i> Agrupar
                        </button>
                        <button class="btn btn-sm btn-default" id="btn-calculate">
                            <i class="fa fa-calculator"></i> Calcular
                        </button>
                        <button class="btn btn-sm btn-warning" id="btn-undo">
                            <i class="fa fa-undo"></i> Deshacer
                        </button>
                        <button class="btn btn-sm btn-danger" id="btn-reset">
                            <i class="fa fa-refresh"></i> Reset
                        </button>
                        <button class="btn btn-sm btn-success" id="btn-export">
                            <i class="fa fa-download"></i> Exportar JSON
                        </button>
                    </div>
                </div>

                <!-- Historial de operaciones -->
                <div class="operations-history" id="operations-history"></div>

                <!-- Filtros activos -->
                <div class="active-filters" id="active-filters"></div>

                <!-- Tabla de datos -->
                <div class="table-container">
                    <table class="table table-bordered table-hover" id="data-table">
                        <thead id="table-head"></thead>
                        <tbody id="table-body"></tbody>
                    </table>
                </div>

                <!-- Paginación -->
                <div class="pagination-container" id="pagination"></div>
            </div>
        `;

        this.attachStyles();
        this.renderTable();
        this.renderOperations();
        this.attachEvents();
    }

    // Agrega estilos CSS
    attachStyles() {
        if (document.getElementById('data-table-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'data-table-styles';
        styles.textContent = `
            .data-table-wrapper {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }

            .data-table-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                padding-bottom: 15px;
                border-bottom: 2px solid #e0e0e0;
            }

            .query-info h3 {
                margin: 0;
                color: #333;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .query-info .badge {
                margin-left: 10px;
                font-size: 12px;
            }

            .header-controls {
                display: flex;
                gap: 8px;
            }

            .operations-history {
                margin-bottom: 15px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
                min-height: 40px;
            }

            .operation-tag {
                display: inline-block;
                padding: 4px 8px;
                margin: 2px;
                background: #007bff;
                color: white;
                border-radius: 3px;
                font-size: 12px;
            }

            .operation-tag.filter { background: #28a745; }
            .operation-tag.sort { background: #17a2b8; }
            .operation-tag.group_by { background: #ffc107; color: #333; }
            .operation-tag.calculate { background: #6f42c1; }

            .active-filters {
                margin-bottom: 15px;
            }

            .filter-chip {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 12px;
                margin: 4px;
                background: #e3f2fd;
                border: 1px solid #2196f3;
                border-radius: 20px;
                font-size: 13px;
            }

            .filter-chip .remove-filter {
                cursor: pointer;
                color: #f44336;
                font-weight: bold;
            }

            .table-container {
                overflow-x: auto;
                max-height: 600px;
                overflow-y: auto;
                margin-bottom: 15px;
            }

            #data-table {
                margin: 0;
                font-size: 13px;
            }

            #data-table thead {
                position: sticky;
                top: 0;
                background: #f5f5f5;
                z-index: 10;
            }

            #data-table th {
                cursor: pointer;
                user-select: none;
                white-space: nowrap;
                padding: 12px 8px;
                background: #f5f5f5;
                font-weight: 600;
            }

            #data-table th:hover {
                background: #e0e0e0;
            }

            #data-table th .sort-icon {
                margin-left: 5px;
                opacity: 0.3;
            }

            #data-table th.sorted .sort-icon {
                opacity: 1;
            }

            #data-table td {
                padding: 8px;
                white-space: nowrap;
            }

            #data-table tbody tr:hover {
                background: #f9f9f9;
            }

            .pagination-container {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-top: 15px;
                border-top: 1px solid #e0e0e0;
            }

            .pagination-info {
                color: #666;
                font-size: 13px;
            }

            .pagination-buttons {
                display: flex;
                gap: 5px;
            }
        `;
        document.head.appendChild(styles);
    }

    // Renderiza la tabla de datos
    renderTable() {
        const data = this.processor.getData();
        const columns = this.processor.columns;

        // Renderizar encabezados
        const thead = document.getElementById('table-head');
        const headerRow = document.createElement('tr');
        
        columns.forEach(col => {
            if (!col.visible) return;
            
            const th = document.createElement('th');
            th.innerHTML = `
                ${col.name} 
                <span class="sort-icon ${this.sortColumn === col.name ? 'sorted' : ''}">
                    ${this.sortColumn === col.name 
                        ? (this.sortOrder === 'asc' ? '▲' : '▼') 
                        : '⇅'}
                </span>
            `;
            th.dataset.column = col.name;
            th.addEventListener('click', () => this.handleSort(col.name));
            headerRow.appendChild(th);
        });
        
        thead.innerHTML = '';
        thead.appendChild(headerRow);

        // Renderizar datos paginados
        const tbody = document.getElementById('table-body');
        tbody.innerHTML = '';

        const startIdx = (this.currentPage - 1) * this.rowsPerPage;
        const endIdx = Math.min(startIdx + this.rowsPerPage, data.length);
        const pageData = data.slice(startIdx, endIdx);

        pageData.forEach(row => {
            const tr = document.createElement('tr');
            columns.forEach(col => {
                if (!col.visible) return;
                const td = document.createElement('td');
                td.textContent = row[col.name] !== undefined ? row[col.name] : '';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });

        this.renderPagination();
    }

    // Renderiza controles de paginación
    renderPagination() {
        const data = this.processor.getData();
        const totalPages = Math.ceil(data.length / this.rowsPerPage);
        const container = document.getElementById('pagination');

        container.innerHTML = `
            <div class="pagination-info">
                Mostrando ${((this.currentPage - 1) * this.rowsPerPage) + 1} - 
                ${Math.min(this.currentPage * this.rowsPerPage, data.length)} 
                de ${data.length} registros
            </div>
            <div class="pagination-buttons">
                <button class="btn btn-sm btn-default" ${this.currentPage === 1 ? 'disabled' : ''} 
                        onclick="dataTableUI.goToPage(1)">
                    <i class="fa fa-angle-double-left"></i>
                </button>
                <button class="btn btn-sm btn-default" ${this.currentPage === 1 ? 'disabled' : ''} 
                        onclick="dataTableUI.goToPage(${this.currentPage - 1})">
                    <i class="fa fa-angle-left"></i> Anterior
                </button>
                <span class="btn btn-sm btn-default" style="cursor: default;">
                    Página ${this.currentPage} de ${totalPages}
                </span>
                <button class="btn btn-sm btn-default" ${this.currentPage === totalPages ? 'disabled' : ''} 
                        onclick="dataTableUI.goToPage(${this.currentPage + 1})">
                    Siguiente <i class="fa fa-angle-right"></i>
                </button>
                <button class="btn btn-sm btn-default" ${this.currentPage === totalPages ? 'disabled' : ''} 
                        onclick="dataTableUI.goToPage(${totalPages})">
                    <i class="fa fa-angle-double-right"></i>
                </button>
            </div>
        `;
    }

    // Renderiza el historial de operaciones
    renderOperations() {
        const container = document.getElementById('operations-history');
        const operations = this.processor.operations;

        if (operations.length === 0) {
            container.innerHTML = '<span style="color: #999;">No hay operaciones aplicadas</span>';
            return;
        }

        container.innerHTML = operations.map(op => {
            let text = '';
            switch(op.type) {
                case 'filter':
                    text = `Filtro: ${op.column} ${op.operator} ${op.value}`;
                    break;
                case 'sort':
                    text = `Ordenar: ${op.column} (${op.order})`;
                    break;
                case 'group_by':
                    text = `Agrupar por: ${op.column}`;
                    break;
                case 'calculate':
                    text = `Calcular: ${op.column}`;
                    break;
                case 'limit':
                    text = `Limitar: ${op.count} filas`;
                    break;
                default:
                    text = op.type;
            }
            return `<span class="operation-tag ${op.type}">${text}</span>`;
        }).join('');
    }

    // Maneja el ordenamiento de columnas
    handleSort(column) {
        if (this.sortColumn === column) {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = column;
            this.sortOrder = 'asc';
        }

        this.processor.sort(column, this.sortOrder);
        this.renderTable();
        this.renderOperations();
    }

    // Navega a una página específica
    goToPage(page) {
        this.currentPage = page;
        this.renderTable();
    }

    // Adjunta event listeners
    attachEvents() {
        // Botón añadir filtro
        document.getElementById('btn-add-filter').addEventListener('click', () => {
            this.showFilterDialog();
        });

        // Botón agrupar
        document.getElementById('btn-group-by').addEventListener('click', () => {
            this.showGroupByDialog();
        });

        // Botón calcular
        document.getElementById('btn-calculate').addEventListener('click', () => {
            this.showCalculateDialog();
        });

        // Botón deshacer
        document.getElementById('btn-undo').addEventListener('click', () => {
            this.processor.undo();
            this.renderTable();
            this.renderOperations();
        });

        // Botón reset
        document.getElementById('btn-reset').addEventListener('click', () => {
            if (confirm('¿Resetear todos los cambios?')) {
                this.processor.reset();
                this.currentPage = 1;
                this.renderTable();
                this.renderOperations();
            }
        });

        // Botón exportar
        document.getElementById('btn-export').addEventListener('click', () => {
            this.exportJSON();
        });
    }

    // Muestra diálogo para añadir filtro
    showFilterDialog() {
        const columns = this.processor.columns.map(c => c.name);
        
        const dialog = new frappe.ui.Dialog({
            title: 'Añadir Filtro',
            fields: [
                {
                    fieldtype: 'Select',
                    fieldname: 'column',
                    label: 'Columna',
                    options: columns,
                    reqd: 1
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'operator',
                    label: 'Operador',
                    options: [
                        'equals',
                        'not_equals',
                        'contains',
                        'not_contains',
                        'starts_with',
                        'ends_with',
                        'greater_than',
                        'less_than',
                        'greater_equal',
                        'less_equal',
                        'is_empty',
                        'is_not_empty'
                    ],
                    reqd: 1
                },
                {
                    fieldtype: 'Data',
                    fieldname: 'value',
                    label: 'Valor',
                    depends_on: 'eval:!["is_empty", "is_not_empty"].includes(doc.operator)'
                }
            ],
            primary_action_label: 'Aplicar Filtro',
            primary_action: (values) => {
                this.processor.applyFilter(values.column, values.operator, values.value || '');
                this.currentPage = 1;
                this.renderTable();
                this.renderOperations();
                dialog.hide();
                frappe.show_alert({message: 'Filtro aplicado', indicator: 'green'});
            }
        });

        dialog.show();
    }

    // Muestra diálogo para agrupar datos
    showGroupByDialog() {
        const columns = this.processor.columns;
        const numericColumns = columns.filter(c => c.type === 'number').map(c => c.name);
        
        const dialog = new frappe.ui.Dialog({
            title: 'Agrupar Datos',
            fields: [
                {
                    fieldtype: 'Select',
                    fieldname: 'group_column',
                    label: 'Agrupar por',
                    options: columns.map(c => c.name),
                    reqd: 1
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'agg_column',
                    label: 'Columna a agregar',
                    options: numericColumns,
                    reqd: 1
                },
                {
                    fieldtype: 'Select',
                    fieldname: 'agg_function',
                    label: 'Función',
                    options: ['sum', 'avg', 'count', 'min', 'max'],
                    reqd: 1
                }
            ],
            primary_action_label: 'Agrupar',
            primary_action: (values) => {
                const aggregations = {};
                aggregations[values.agg_column] = values.agg_function;
                
                this.processor.groupBy(values.group_column, aggregations);
                this.currentPage = 1;
                this.renderTable();
                this.renderOperations();
                dialog.hide();
                frappe.show_alert({message: 'Datos agrupados', indicator: 'green'});
            }
        });

        dialog.show();
    }

    // Muestra diálogo para calcular columna
    showCalculateDialog() {
        const columns = this.processor.columns.map(c => c.name);
        
        const dialog = new frappe.ui.Dialog({
            title: 'Calcular Columna',
            fields: [
                {
                    fieldtype: 'Data',
                    fieldname: 'column_name',
                    label: 'Nombre nueva columna',
                    reqd: 1
                },
                {
                    fieldtype: 'Small Text',
                    fieldname: 'formula',
                    label: 'Fórmula',
                    description: `Ejemplo: columna1 + columna2 * 0.16<br>Columnas disponibles: ${columns.join(', ')}`,
                    reqd: 1
                }
            ],
            primary_action_label: 'Calcular',
            primary_action: (values) => {
                try {
                    this.processor.calculate(values.column_name, values.formula);
                    this.renderTable();
                    this.renderOperations();
                    dialog.hide();
                    frappe.show_alert({message: 'Columna calculada', indicator: 'green'});
                } catch(e) {
                    frappe.msgprint({
                        title: 'Error',
                        message: 'Fórmula inválida: ' + e.message,
                        indicator: 'red'
                    });
                }
            }
        });

        dialog.show();
    }

    // Exporta la configuración como JSON
    exportJSON() {
        const config = this.processor.exportConfig();
        const json = JSON.stringify(config, null, 2);

        // Crear diálogo con JSON
        const dialog = new frappe.ui.Dialog({
            title: 'Exportar Configuración',
            fields: [
                {
                    fieldtype: 'Code',
                    fieldname: 'json',
                    label: 'Configuración JSON',
                    options: 'JSON',
                    default: json
                },
                {
                    fieldtype: 'HTML',
                    fieldname: 'buttons',
                    options: `
                        <div style="margin-top: 10px;">
                            <button class="btn btn-primary btn-sm" id="copy-json-btn">
                                <i class="fa fa-copy"></i> Copiar al Portapapeles
                            </button>
                            <button class="btn btn-default btn-sm" id="download-json-btn">
                                <i class="fa fa-download"></i> Descargar Archivo
                            </button>
                        </div>
                    `
                }
            ]
        });

        dialog.show();

        // Botón copiar
        dialog.$wrapper.find('#copy-json-btn').on('click', () => {
            navigator.clipboard.writeText(json);
            frappe.show_alert({message: 'Copiado al portapapeles', indicator: 'green'});
        });

        // Botón descargar
        dialog.$wrapper.find('#download-json-btn').on('click', () => {
            const blob = new Blob([json], {type: 'application/json'});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.processor.queryName}_config.json`;
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    // Obtiene el procesador actual
    getProcessor() {
        return this.processor;
    }
}

// Instancia global
window.DataTableUI = DataTableUI;
window.dataTableUI = null; // Se inicializará cuando se carguen datos
