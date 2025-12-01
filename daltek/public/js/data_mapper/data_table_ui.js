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

            .operation-tag .remove-operation {
                margin-left: 8px;
                cursor: pointer;
                font-weight: bold;
                font-size: 18px;
                opacity: 0.7;
                transition: opacity 0.2s;
            }

            .operation-tag .remove-operation:hover {
                opacity: 1;
            }

            .operation-tag.group_by .remove-operation {
                color: #333;
            }

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
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
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
                max-width: 200px;
                overflow: hidden;
                text-overflow: ellipsis;
            }

            #data-table tbody tr:hover {
                background: #f9f9f9;
            }

            /* Columnas calculadas */
            #data-table th.calculated-column {
                background: #e3f2fd;
                color: #1976d2;
                font-weight: 700;
            }

            #data-table th.calculated-column:hover {
                background: #bbdefb;
            }

            #data-table td.calculated-column {
                background: #f1f8ff;
                color: #0d47a1;
                font-weight: 500;
            }

            #data-table tbody tr:hover td.calculated-column {
                background: #e3f2fd;
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
        console.log('renderTable() called');
        const data = this.processor.getData();
        const columns = this.processor.columns;
        console.log('Rendering table with', data.length, 'rows and', columns.length, 'columns');

        // Renderizar encabezados
        const thead = document.getElementById('table-head');
        const headerRow = document.createElement('tr');
        
        columns.forEach(col => {
            if (!col.visible) return;
            
            const th = document.createElement('th');
            // Marcar columnas calculadas
            if (col.calculated) {
                th.classList.add('calculated-column');
            }
            th.style.position = 'relative';
            
            const headerDiv = document.createElement('div');
            headerDiv.style.cssText = 'display: flex; align-items: center; justify-content: space-between;';
            
            const colName = document.createElement('span');
            colName.textContent = col.name + (col.calculated ? ' 🧮' : '');
            
            const menuBtn = document.createElement('button');
            menuBtn.className = 'btn btn-xs btn-default';
            menuBtn.style.cssText = 'padding: 2px 5px; margin-left: 5px;';
            menuBtn.textContent = '⋮';
            menuBtn.onclick = (e) => {
                e.stopPropagation();
                this.showColumnMenu(col.name, menuBtn);
            };
            
            headerDiv.appendChild(colName);
            headerDiv.appendChild(menuBtn);
            th.appendChild(headerDiv);
            th.dataset.column = col.name;
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
                // Marcar celdas de columnas calculadas
                if (col.calculated) {
                    td.classList.add('calculated-column');
                }
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

        container.innerHTML = operations.map((op, index) => {
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
            return `
                <span class="operation-tag ${op.type}">
                    ${text}
                    <span class="remove-operation" data-index="${index}" title="Eliminar operación">
                        ×
                    </span>
                </span>`;
        }).join('');

        // Agregar event listeners a los botones de eliminar
        container.querySelectorAll('.remove-operation').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                this.removeOperation(index);
            });
        });
    }

    // Elimina una operación específica y re-aplica las restantes
    removeOperation(index) {
        if (index < 0 || index >= this.processor.operations.length) return;

        // Guardar operaciones excepto la eliminada
        const operations = [...this.processor.operations];
        operations.splice(index, 1);

        // Reset y re-aplicar operaciones
        this.processor.reset();
        operations.forEach(op => {
            switch(op.type) {
                case 'filter':
                    this.processor.applyFilter(op.column, op.operator, op.value);
                    break;
                case 'sort':
                    this.processor.sort(op.column, op.order);
                    break;
                case 'group_by':
                    this.processor.groupBy(op.columns, op.aggregations);
                    break;
                case 'calculate':
                    this.processor.calculate(op.column, op.formula);
                    break;
                case 'limit':
                    this.processor.limit(op.count);
                    break;
            }
        });

        // Re-renderizar
        this.currentPage = 1;
        this.renderTable();
        this.renderOperations();
        frappe.show_alert({message: 'Operación eliminada', indicator: 'orange'});
    }

    // Maneja el ordenamiento de columnas
    handleSort(column, order = null) {
        // Si se proporciona un orden específico, usarlo
        if (order) {
            this.sortColumn = column;
            this.sortOrder = order;
        } else {
            // Determinar nuevo orden (comportamiento de toggle)
            if (this.sortColumn === column) {
                this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                this.sortColumn = column;
                this.sortOrder = 'asc';
            }
        }

        // Buscar si ya existe un sort en las operaciones
        const existingSortIndex = this.processor.operations.findIndex(
            op => op.type === 'sort' && op.column === column
        );

        // Si existe, eliminarlo primero
        if (existingSortIndex !== -1) {
            this.processor.operations.splice(existingSortIndex, 1);
        }

        // Aplicar el nuevo sort
        this.processor.sort(column, this.sortOrder);
        this.renderTable();
        this.renderOperations();
    }

    // Muestra menú contextual para columna
    showColumnMenu(columnName, buttonElement) {
        // Remover menú anterior si existe
        const existingMenu = document.querySelector('.column-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        // Verificar si la columna es numérica
        const column = this.processor.columns.find(c => c.name === columnName);
        const isNumeric = column && column.type === 'number';

        const menu = document.createElement('div');
        menu.className = 'column-context-menu';
        menu.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 1000;
            min-width: 180px;
            padding: 5px 0;
        `;

        menu.innerHTML = `
            <div style="padding: 5px 15px; font-weight: bold; color: #888; font-size: 11px; text-transform: uppercase;">Ordenar</div>
            <a href="#" class="menu-item" data-action="sort-asc" style="display: block; padding: 8px 15px; text-decoration: none; color: #333;">
                <i class="fa fa-sort-amount-asc"></i> Ascendente
            </a>
            <a href="#" class="menu-item" data-action="sort-desc" style="display: block; padding: 8px 15px; text-decoration: none; color: #333;">
                <i class="fa fa-sort-amount-desc"></i> Descendente
            </a>
            <div style="border-top: 1px solid #eee; margin: 5px 0;"></div>
            <div style="padding: 5px 15px; font-weight: bold; color: #888; font-size: 11px; text-transform: uppercase;">Filtrar</div>
            <a href="#" class="menu-item" data-action="filter" style="display: block; padding: 8px 15px; text-decoration: none; color: #333;">
                <i class="fa fa-filter"></i> Agregar filtro
            </a>
            <div style="border-top: 1px solid #eee; margin: 5px 0;"></div>
            <div style="padding: 5px 15px; font-weight: bold; color: #888; font-size: 11px; text-transform: uppercase;">Agrupar</div>
            <a href="#" class="menu-item" data-action="group" style="display: block; padding: 8px 15px; text-decoration: none; color: #333;">
                <i class="fa fa-object-group"></i> Agrupar por esta columna
            </a>
            ${
                isNumeric ? `
                <div style="border-top: 1px solid #eee; margin: 5px 0;"></div>
                <div style="padding: 5px 15px; font-weight: bold; color: #888; font-size: 11px; text-transform: uppercase;">Calcular</div>
                <a href="#" class="menu-item" data-action="calculate" style="display: block; padding: 8px 15px; text-decoration: none; color: #333;">
                    <i class="fa fa-calculator"></i> Calcular con esta columna
                </a>
                ` : ''
            }
        `;

        // Posicionar el menú
        const rect = buttonElement.getBoundingClientRect();
        menu.style.top = `${rect.bottom + window.scrollY}px`;
        menu.style.left = `${rect.left + window.scrollX}px`;

        // Agregar event listeners
        menu.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('mouseenter', (e) => {
                e.target.style.backgroundColor = '#f5f5f5';
            });
            item.addEventListener('mouseleave', (e) => {
                e.target.style.backgroundColor = 'white';
            });
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const action = e.currentTarget.getAttribute('data-action');
                
                if (action === 'sort-asc') {
                    this.handleSort(columnName, 'asc');
                } else if (action === 'sort-desc') {
                    this.handleSort(columnName, 'desc');
                } else if (action === 'filter') {
                    this.showFilterDialogForColumn(columnName);
                } else if (action === 'group') {
                    this.showGroupByDialogForColumn(columnName);
                } else if (action === 'calculate') {
                    this.showCalculateDialogForColumn(columnName);
                }
                
                menu.remove();
            });
        });

        document.body.appendChild(menu);

        // Cerrar menú al hacer clic fuera
        const closeMenu = (e) => {
            if (!menu.contains(e.target) && e.target !== buttonElement) {
                menu.remove();
                document.removeEventListener('click', closeMenu);
            }
        };
        setTimeout(() => document.addEventListener('click', closeMenu), 0);
    }

    // Navega a una página específica
    goToPage(page) {
        this.currentPage = page;
        this.renderTable();
    }

    // Adjunta event listeners
    attachEvents() {
        // Botón deshacer
        const btnUndo = document.getElementById('btn-undo');
        if (btnUndo) {
            btnUndo.addEventListener('click', () => {
                this.processor.undo();
                this.renderTable();
                this.renderOperations();
            });
        }

        // Botón reset
        const btnReset = document.getElementById('btn-reset');
        if (btnReset) {
            btnReset.addEventListener('click', () => {
                console.log('Reset button clicked');
                if (confirm('¿Resetear todos los cambios?')) {
                    console.log('User confirmed reset');
                    this.processor.reset();
                    this.currentPage = 1;
                    this.sortColumn = null;
                    this.sortOrder = 'asc';
                    this.renderTable();
                    this.renderOperations();
                    if (typeof frappe !== 'undefined' && frappe.show_alert) {
                        frappe.show_alert({message: 'Datos reseteados correctamente', indicator: 'green'});
                    }
                }
            });
        } else {
            console.error('btn-reset not found!');
        }

        // Botón exportar
        const btnExport = document.getElementById('btn-export');
        if (btnExport) {
            btnExport.addEventListener('click', () => {
                this.exportJSON();
            });
        }
    }

    // Muestra diálogo para añadir filtro
    showFilterDialogForColumn(columnName) {
        this.showFilterDialog(columnName);
    }

    showFilterDialog(preselectedColumn) {
        if (!preselectedColumn) {
            frappe.msgprint('Por favor, selecciona una columna desde el menú de columnas');
            return;
        }
        
        const dialog = new frappe.ui.Dialog({
            title: `Filtrar: ${preselectedColumn}`,
            fields: [
                {
                    fieldtype: 'HTML',
                    fieldname: 'column_info',
                    options: `<div style="padding: 10px; background-color: #f0f4f7; border-radius: 4px; margin-bottom: 10px;">
                        <strong>Columna:</strong> <span style="color: #2490ef;">${preselectedColumn}</span>
                    </div>`
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
                this.processor.applyFilter(preselectedColumn, values.operator, values.value || '');
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
    showGroupByDialogForColumn(columnName) {
        this.showGroupByDialog(columnName);
    }

    showGroupByDialog(preselectedColumn = null) {
        const columns = this.processor.columns;
        const numericColumns = columns.filter(c => c.type === 'number').map(c => c.name);
        
        const dialog = new frappe.ui.Dialog({
            title: preselectedColumn ? `Agrupar por: ${preselectedColumn}` : 'Agrupar Datos',
            fields: [
                preselectedColumn ? {
                    fieldtype: 'HTML',
                    fieldname: 'group_column_info',
                    options: `<div style="padding: 10px; background-color: #f0f4f7; border-radius: 4px; margin-bottom: 10px;">
                        <strong>Agrupar por:</strong> <span style="color: #2490ef;">${preselectedColumn}</span>
                    </div>`
                } : {
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
                
                // Usar columna preseleccionada o la seleccionada en el formulario
                const groupColumn = preselectedColumn || values.group_column;
                
                this.processor.groupBy(groupColumn, aggregations);
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
    showCalculateDialogForColumn(columnName) {
        this.showCalculateDialog(columnName);
    }

    showCalculateDialog(preselectedColumn = null) {
        const columns = this.processor.columns.map(c => c.name);
        const numericColumns = this.processor.columns.filter(c => c.type === 'number').map(c => c.name);
        
        if (numericColumns.length === 0) {
            frappe.msgprint('No hay columnas numéricas disponibles para calcular');
            return;
        }
        
        const dialog = new frappe.ui.Dialog({
            title: 'Calcular Nueva Columna',
            fields: [
                {
                    fieldtype: 'Data',
                    fieldname: 'column_name',
                    label: 'Nombre nueva columna',
                    reqd: 1
                },
                {
                    fieldtype: 'HTML',
                    fieldname: 'formula_builder',
                    options: `
                        <div style="border: 1px solid #ddd; padding: 15px; border-radius: 4px; background: #f9f9f9;">
                            <label style="font-weight: bold; margin-bottom: 10px; display: block;">Constructor de Fórmula</label>
                            
                            <div id="operations-container">
                                <!-- Las operaciones se agregarán aquí dinámicamente -->
                            </div>
                            
                            <button type="button" class="btn btn-sm btn-success" id="add-operation-btn" style="margin-bottom: 15px;">
                                <i class="fa fa-plus"></i> Agregar Operación
                            </button>
                            
                            <div style="background: white; padding: 10px; border-radius: 4px; border: 1px solid #ddd;">
                                <strong>Fórmula:</strong> <span id="formula-preview" style="color: #2490ef; font-family: monospace;">${preselectedColumn || '-'}</span>
                            </div>
                        </div>
                    `
                }
            ],
            primary_action_label: 'Calcular',
            primary_action: (values) => {
                const formula = document.getElementById('formula-preview').textContent;
                
                if (!formula || formula === '-') {
                    frappe.msgprint('Por favor agrega al menos una operación');
                    return;
                }
                
                if (!values.column_name) {
                    frappe.msgprint('Por favor ingresa un nombre para la columna');
                    return;
                }
                
                try {
                    this.processor.calculate(values.column_name, formula);
                    this.renderTable();
                    this.renderOperations();
                    dialog.hide();
                    frappe.show_alert({message: 'Columna calculada correctamente', indicator: 'green'});
                } catch(e) {
                    frappe.msgprint({
                        title: 'Error',
                        message: 'Error al calcular: ' + e.message,
                        indicator: 'red'
                    });
                }
            }
        });

        dialog.show();
        
        // Lógica para operaciones encadenadas
        setTimeout(() => {
            let operationCounter = 0;
            let currentFormula = preselectedColumn || '';
            
            const updatePreview = () => {
                document.getElementById('formula-preview').textContent = currentFormula || '-';
            };
            
            const addOperation = () => {
                operationCounter++;
                const opId = `op-${operationCounter}`;
                
                const operationHTML = `
                    <div class="operation-row" id="${opId}" style="margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; border: 1px solid #ddd;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <strong>Operación ${operationCounter}</strong>
                            <button type="button" class="btn btn-xs btn-danger remove-op-btn" data-id="${opId}">
                                <i class="fa fa-times"></i>
                            </button>
                        </div>
                        
                        <div style="margin-bottom: 10px;">
                            <label style="display: block; margin-bottom: 5px;">Operador:</label>
                            <div style="display: flex; gap: 5px;">
                                <button type="button" class="btn btn-sm btn-default op-btn" data-id="${opId}" data-op="+">+</button>
                                <button type="button" class="btn btn-sm btn-default op-btn" data-id="${opId}" data-op="-">−</button>
                                <button type="button" class="btn btn-sm btn-default op-btn" data-id="${opId}" data-op="*">×</button>
                                <button type="button" class="btn btn-sm btn-default op-btn" data-id="${opId}" data-op="/">/</button>
                            </div>
                        </div>
                        
                        <div>
                            <label style="display: block; margin-bottom: 5px;">Columna / Valor:</label>
                            <select class="form-control op-column" data-id="${opId}" style="margin-bottom: 5px;">
                                <option value="">-- Seleccionar columna --</option>
                                ${numericColumns.map(col => `<option value="${col}">${col}</option>`).join('')}
                            </select>
                            <input type="number" class="form-control op-value" data-id="${opId}" placeholder="O ingresa un valor" step="any">
                        </div>
                        
                        <input type="hidden" class="op-operator" data-id="${opId}">
                        <input type="hidden" class="op-operand" data-id="${opId}">
                    </div>
                `;
                
                document.getElementById('operations-container').insertAdjacentHTML('beforeend', operationHTML);
                attachOperationListeners(opId);
            };
            
            const attachOperationListeners = (opId) => {
                // Botones de operador
                document.querySelectorAll(`.op-btn[data-id="${opId}"]`).forEach(btn => {
                    btn.addEventListener('click', function() {
                        document.querySelectorAll(`.op-btn[data-id="${opId}"]`).forEach(b => b.classList.remove('btn-primary'));
                        this.classList.add('btn-primary');
                        document.querySelector(`.op-operator[data-id="${opId}"]`).value = this.getAttribute('data-op');
                        buildFormula();
                    });
                });
                
                // Select de columna
                document.querySelector(`.op-column[data-id="${opId}"]`).addEventListener('change', function() {
                    document.querySelector(`.op-value[data-id="${opId}"]`).value = '';
                    document.querySelector(`.op-operand[data-id="${opId}"]`).value = this.value;
                    buildFormula();
                });
                
                // Input de valor
                document.querySelector(`.op-value[data-id="${opId}"]`).addEventListener('input', function() {
                    document.querySelector(`.op-column[data-id="${opId}"]`).value = '';
                    document.querySelector(`.op-operand[data-id="${opId}"]`).value = this.value;
                    buildFormula();
                });
                
                // Botón eliminar
                document.querySelector(`.remove-op-btn[data-id="${opId}"]`).addEventListener('click', function() {
                    document.getElementById(opId).remove();
                    buildFormula();
                });
            };
            
            const buildFormula = () => {
                let formula = preselectedColumn || '';
                
                document.querySelectorAll('.operation-row').forEach(opRow => {
                    const opId = opRow.id;
                    const operator = document.querySelector(`.op-operator[data-id="${opId}"]`).value;
                    const operand = document.querySelector(`.op-operand[data-id="${opId}"]`).value;
                    
                    if (operator && operand) {
                        formula += ` ${operator} ${operand}`;
                    }
                });
                
                currentFormula = formula;
                updatePreview();
            };
            
            // Botón agregar operación
            document.getElementById('add-operation-btn').addEventListener('click', addOperation);
            
            // Agregar primera operación automáticamente
            if (preselectedColumn) {
                addOperation();
            }
            
            updatePreview();
        }, 100);
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
