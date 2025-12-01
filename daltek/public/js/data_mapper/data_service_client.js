// DataServiceClient: Cliente JavaScript para comunicación con DataService backend
// Maneja todas las operaciones de datos entre UI y servidor

class DataServiceClient {
    constructor() {
        this.baseMethod = 'daltek.daltek.doctype.daltek.daltek';
    }

    // Obtiene datos de una query
    fetchQueryData(docName, queryId) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.fetch_query_data`,
                args: {
                    doc_name: docName,
                    query_id: queryId
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error fetching data');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Aplica transformaciones a los datos
    applyTransformations(data, config) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.apply_transformations`,
                args: {
                    data: JSON.stringify(data),
                    config: JSON.stringify(config)
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error applying transformations');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Guarda configuración de widget
    saveWidgetConfig(docName, widgetConfig) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.save_widget_config`,
                args: {
                    doc_name: docName,
                    widget_config: JSON.stringify(widgetConfig)
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error saving widget');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Sube datos desde frontend
    uploadData(docName, data, source = 'manual') {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.upload_data`,
                args: {
                    doc_name: docName,
                    data: JSON.stringify(data),
                    source: source
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error uploading data');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Filtra datos
    filterData(data, filters) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.filter_data`,
                args: {
                    data: JSON.stringify(data),
                    filters: JSON.stringify(filters)
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error filtering data');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Agrega datos
    aggregateData(data, groupBy, aggregations) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.aggregate_data`,
                args: {
                    data: JSON.stringify(data),
                    group_by: JSON.stringify(groupBy),
                    aggregations: JSON.stringify(aggregations)
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error aggregating data');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Preview de widget
    previewWidget(data, widgetType, widgetConfig) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.preview_widget`,
                args: {
                    data: JSON.stringify(data),
                    widget_type: widgetType,
                    widget_config: JSON.stringify(widgetConfig)
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error generating preview');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }

    // Valida configuración
    validateConfig(config, dataColumns) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.validate_config`,
                args: {
                    config: JSON.stringify(config),
                    data_columns: JSON.stringify(dataColumns)
                },
                callback: (r) => {
                    resolve(r.message);
                },
                error: (err) => reject(err)
            });
        });
    }

    // Obtiene estadísticas de columna
    getColumnStats(data, column) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: `${this.baseMethod}.get_column_stats`,
                args: {
                    data: JSON.stringify(data),
                    column: column
                },
                callback: (r) => {
                    if (r.message && r.message.success) {
                        resolve(r.message);
                    } else {
                        reject(r.message?.error || 'Error getting stats');
                    }
                },
                error: (err) => reject(err)
            });
        });
    }
}

// Singleton global
window.DataServiceClient = DataServiceClient;
window.dataService = new DataServiceClient();
