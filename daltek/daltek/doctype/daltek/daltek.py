# Copyright (c) 2025, GSI and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.model.document import Document

from ...domain.query_service.query_service import QueryService
from ...domain.widget_service.widget_service import WidgetService


class Daltek(Document):
    def before_save(self):
        current_datetime = frappe.utils.now()

        if not self.date_created:
            self.date_created = current_datetime

        self.last_modified = current_datetime

    def validate(self):
        # Validar que los datos sean fechas y el usuario exista dentro del sistema
        pass

    @frappe.whitelist()
    def get_name(self):
        return self.name


# --- MÉTODOS DEL DOCTYPE ---
# Los métodos CRUD de queries se encuentran en QueryService
# Solo mantener aquí métodos relacionados con el UI del DocType


@frappe.whitelist()
def get_doctype_fields(doctype_name):
    try:
        if not doctype_name:
            frappe.throw("El nombre del DocType es requerido")

        # Verificar que el DocType existe
        if not frappe.db.exists("DocType", doctype_name):
            frappe.throw(f"El DocType '{doctype_name}' no existe")

        # Obtener metadatos del DocType
        meta = frappe.get_meta(doctype_name)

        doctype_doc = frappe.get_doc("DocType", doctype_name)
        is_custom = getattr(doctype_doc, "custom", 0) == 1

        standard_fields = [
            {"fieldname": "name", "label": "ID", "fieldtype": "Data"},
            {
                "fieldname": "creation",
                "label": "Fecha Creación",
                "fieldtype": "Datetime",
            },
            {
                "fieldname": "modified",
                "label": "Fecha Modificación",
                "fieldtype": "Datetime",
            },
            {
                "fieldname": "modified_by",
                "label": "Modificado Por",
                "fieldtype": "Data",
            },
            {"fieldname": "owner", "label": "Propietario", "fieldtype": "Data"},
        ]

        custom_fields = []
        for field in meta.fields:
            if (
                field.fieldname
                and not field.hidden
                and field.fieldtype
                in [
                    "Data",
                    "Select",
                    "Link",
                    "Int",
                    "Float",
                    "Currency",
                    "Date",
                    "Datetime",
                    "Check",
                    "Text",
                    "Small Text",
                    "Long Text",
                    "MultiSelect",
                    "Child Table",
                ]
            ):
                custom_fields.append(
                    {
                        "fieldname": field.fieldname,
                        "label": field.label or field.fieldname,
                        "fieldtype": field.fieldtype,
                        "options": field.options or "",
                    }
                )

        return {
            "success": True,
            "doctype": doctype_name,
            "table_name": f"tab{doctype_name.replace(' ', '')}",
            "is_custom": is_custom,
            "standard_fields": standard_fields,
            "custom_fields": custom_fields,
            "all_fields": standard_fields + custom_fields,
        }

    except Exception as e:
        frappe.log_error(
            f"Error obteniendo campos del DocType {doctype_name}: {str(e)}",
            "QueryBuilder Error",
        )
        return {
            "success": False,
            "error": str(e),
            "doctype": doctype_name,
            "message": f"Error obteniendo campos del DocType: {str(e)}",
        }


@frappe.whitelist()
def get_query_builder_html():
    # Retorna el HTML completo del Query Builder
    try:
        app_path = frappe.get_app_path("daltek")
        query_builder_path = os.path.join(app_path, "public", "js", "query_builder")

        # Leer archivos en el orden correcto
        files_to_load = [
            ("index.html", "html"),
            ("state.js", "js"),
            ("ui.js", "js"),
            ("views.js", "js"),
            ("steps.js", "js"),
            ("executor.js", "js"),
            ("main.js", "js"),
        ]

        html_content = ""
        js_contents = {}

        for filename, file_type in files_to_load:
            file_path = os.path.join(query_builder_path, filename)

            if not os.path.exists(file_path):
                frappe.log_error(f"Archivo no encontrado: {file_path}")
                continue

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

                if file_type == "html":
                    html_content = content
                else:
                    js_contents[filename] = content

        # Inyectar los JS en los placeholders del HTML
        placeholder_map = {
            "state.js": "qb-state-js",
            "ui.js": "qb-ui-js",
            "views.js": "qb-views-js",
            "steps.js": "qb-steps-js",
            "executor.js": "qb-executor-js",
            "main.js": "qb-main-js",
        }

        for js_file, placeholder_id in placeholder_map.items():
            if js_file in js_contents:
                html_content = html_content.replace(
                    f'<script id="{placeholder_id}">\n// ============ {js_file} ============\n</script>',
                    f'<script id="{placeholder_id}">\n{js_contents[js_file]}\n</script>',
                )

        return html_content

    except FileNotFoundError as e:
        error_msg = f"Error: No se encontró el archivo del Query Builder: {str(e)}"
        frappe.log_error(error_msg)
        error_style = "padding: 20px" + "; " + "color: red"
        return f"<div style='{error_style}'>{error_msg}</div>"
    except Exception as e:
        error_msg = f"Error cargando Query Builder: {str(e)}"
        frappe.log_error(error_msg)
        error_style = "padding: 20px" + "; " + "color: red"
        return f"<div style='{error_style}'>{error_msg}</div>"


@frappe.whitelist()
def get_drag_drop_html():
    # Retorna el HTML completo del sistema Drag and Drop
    try:
        app_path = frappe.get_app_path("daltek")
        drag_drop_path = os.path.join(app_path, "public", "js", "drag_and_drop")

        # Leer archivos en el orden correcto
        files_to_load = [
            ("index.html", "html"),
            ("state.js", "js"),
            ("ui.js", "js"),
            ("grid.js", "js"),
            ("widgets.js", "js"),
            ("main.js", "js"),
        ]

        html_content = ""
        js_contents = {}

        for filename, file_type in files_to_load:
            file_path = os.path.join(drag_drop_path, filename)

            if not os.path.exists(file_path):
                frappe.log_error(f"Archivo no encontrado: {file_path}")
                continue

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

                if file_type == "html":
                    html_content = content
                else:
                    js_contents[filename] = content

        # Inyectar los JS en los placeholders del HTML
        placeholder_map = {
            "state.js": "dd-state-js",
            "ui.js": "dd-ui-js",
            "grid.js": "dd-grid-js",
            "widgets.js": "dd-widgets-js",
            "main.js": "dd-main-js",
        }

        for js_file, placeholder_id in placeholder_map.items():
            if js_file in js_contents:
                html_content = html_content.replace(
                    f'<script id="{placeholder_id}">\n// ============ {js_file} ============\n</script>',
                    f'<script id="{placeholder_id}">\n{js_contents[js_file]}\n</script>',
                )

        return html_content

    except FileNotFoundError as e:
        error_msg = f"Error: No se encontró el archivo del Drag and Drop: {str(e)}"
        frappe.log_error(error_msg)
        error_style = "padding: 20px" + "; " + "color: red"
        return f"<div style='{error_style}'>{error_msg}</div>"
    except Exception as e:
        error_msg = f"Error cargando Drag and Drop: {str(e)}"
        frappe.log_error(error_msg)
        error_style = "padding: 20px" + "; " + "color: red"
        return f"<div style='{error_style}'>{error_msg}</div>"


# --- MÉTODOS PARA QUERY SERVICE ---
# Métodos wrapper que conectan el cliente con QueryService


@frappe.whitelist()
def save_query(doc_name, query_data):
    # Guarda una nueva consulta o actualiza una existente
    try:
        service = QueryService()

        # Parsear query_data si viene como string
        if isinstance(query_data, str):
            import json

            query_dict = json.loads(query_data)
        else:
            query_dict = query_data

        # Si la query tiene ID, es una edición
        if query_dict.get("id"):
            result = service.edit(doc_name, query_dict["id"], query_dict)
        else:
            result = service.save(doc_name, query_dict)

        return result

    except Exception as e:
        frappe.log_error(f"Error en save_query: {str(e)}", "QueryService Wrapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def edit_query(doc_name, query_id, query_data):
    # Edita una consulta existente
    try:
        service = QueryService()
        result = service.edit(doc_name, query_id, query_data)
        return result

    except Exception as e:
        frappe.log_error(f"Error en edit_query: {str(e)}", "QueryService Wrapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def delete_query(doc_name, query_id):
    # Elimina una consulta del documento
    try:
        service = QueryService()
        result = service.delete(doc_name, query_id)
        return result

    except Exception as e:
        frappe.log_error(
            f"Error en delete_query: {str(e)}", "QueryService Wrapper Error"
        )
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_query(doc_name, query_id):
    try:
        service = QueryService()
        result = service.get(doc_name, query_id)
        return result

    except Exception as e:
        frappe.log_error(f"Error en get_query: {str(e)}", "QueryService Wrapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_all_queries(doc_name):

    try:
        service = QueryService()
        result = service.get_all(doc_name)
        return result

    except Exception as e:
        frappe.log_error(
            f"Error en get_all_queries: {str(e)}", "QueryService Wrapper Error"
        )
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def execute_query(doc_name, query_id):
    # Ejecuta una consulta
    try:
        service = QueryService()
        result = service.execute(doc_name, query_id)
        return result

    except Exception as e:
        frappe.log_error(
            f"Error en execute_query: {str(e)}", "QueryService Wrapper Error"
        )
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def update_query_field(doc_name, query_id, field_name, field_value):
    # Actualiza un solo campo de una consuta sin afectar al resto
    try:
        service = QueryService()

        # Obtener la query actual
        get_result = service.get(doc_name, query_id)
        if not get_result.get("success"):
            return get_result

        query = get_result.get("query")

        # Actualizar el campo específico
        query[field_name] = field_value

        # Guardar la query actualizada
        result = service.edit(doc_name, query_id, query)
        return result

    except Exception as e:
        frappe.log_error(
            f"Error en update_query_field: {str(e)}", "QueryService Wrapper Error"
        )
        return {"success": False, "error": str(e)}


# --- Metodos de WidgetService ---


@frappe.whitelist()
def render_layout(doc_name):
    try:
        service = WidgetService()
        result = service.render_layout(doc_name)
        return result

    except Exception as e:
        frappe.log_error(
            f"Error en render_layout: {str(e)}", "WidgetService Wrapper Error"
        )
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_layout(doc_name):
    try:
        service = WidgetService()
        layout = service.get_layout(doc_name)
        return {"success": True, "layout": layout}

    except Exception as e:
        frappe.log_error(
            f"Error en get_layout: {str(e)}", "WidgetService Wrapper Error"
        )
        return {"success": False, "error": str(e)}


# ==================== WRAPPERS PARA ECHARTS ====================


@frappe.whitelist()
def add_widget_echart(
    doc_name, chart_type, chart_data, chart_config=None, widget_properties=None
):
    # Crea widget EChart
    try:
        import json

        # Parsear strings a dicts si es necesario
        if isinstance(chart_data, str):
            chart_data = json.loads(chart_data)
        if isinstance(chart_config, str):
            chart_config = json.loads(chart_config)
        if isinstance(widget_properties, str):
            widget_properties = json.loads(widget_properties)

        # Llamar al servicio
        service = WidgetService()
        result = service.add_echart(
            doc_name=doc_name,
            chart_type=chart_type,
            chart_data=chart_data,
            chart_config=chart_config or {},
            widget_properties=widget_properties or {},
        )

        return result

    except Exception as e:
        frappe.log_error(
            f"Error en add_widget_echart(): {str(e)}", "EChart Widget Wrapper Error"
        )
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def add_widget(doc_name, widget):
    # Añade widget genérico (card, table, etc)
    try:
        import json

        if isinstance(widget, str):
            widget = json.loads(widget)

        service = WidgetService()
        result = service.add(doc_name, widget)
        return result

    except Exception as e:
        frappe.log_error(f"Error en add_widget(): {str(e)}", "Widget Wrapper Error")
        return {"success": False, "error": str(e)}


# --- DATA MAPPER ENDPOINTS ---
# Endpoints para el sistema de transformación de datos


@frappe.whitelist()
def get_mapper_preview(query_name, mapper_config):
    # Retorna preview de datos transformados
    try:
        import json
        from ...domain.data_mapper.data_mapper_service import DataMapperService
        from ...domain.query_service.query_service import QueryService
        
        # Parse config si viene como string
        if isinstance(mapper_config, str):
            mapper_config = json.loads(mapper_config)
        
        # Ejecutar query
        query_service = QueryService()
        
        # Si query_name es el nombre guardado
        if isinstance(query_name, str) and not query_name.startswith("{"):
            # Buscar la query por nombre en algún documento
            # Por ahora ejecutamos directamente
            frappe.throw("Debe proporcionar query_id o doc_name con query_id")
        else:
            # Si viene query_id directo, necesitamos doc_name también
            frappe.throw("Parámetros insuficientes. Use get_mapper_preview_by_id")
        
    except Exception as e:
        frappe.log_error(f"Error en get_mapper_preview: {str(e)}", "DataMapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_mapper_preview_by_id(doc_name, query_id, mapper_config):
    # Retorna preview de datos transformados desde query guardada
    try:
        import json
        from ...domain.data_mapper.data_mapper_service import DataMapperService
        from ...domain.query_service.query_service import QueryService
        
        # Parse config si viene como string
        if isinstance(mapper_config, str):
            mapper_config = json.loads(mapper_config)
        
        # Ejecutar query
        query_service = QueryService()
        query_result = query_service.execute(doc_name, query_id)
        
        if not query_result.get("success"):
            return query_result
        
        # Aplicar transformación
        mapper_service = DataMapperService()
        transformed = mapper_service.preview_transformation(
            query_result,
            mapper_config,
            limit=100  # Límite para preview
        )
        
        return transformed
        
    except Exception as e:
        frappe.log_error(f"Error en get_mapper_preview_by_id: {str(e)}", "DataMapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def validate_mapper_config(mapper_config, query_columns):
    # Valida configuración de mapeo contra columnas disponibles
    try:
        import json
        from ...domain.data_mapper.data_mapper_service import DataMapperService
        
        # Parse inputs
        if isinstance(mapper_config, str):
            mapper_config = json.loads(mapper_config)
        
        if isinstance(query_columns, str):
            query_columns = json.loads(query_columns)
        
        # Validar
        mapper_service = DataMapperService()
        validation = mapper_service.validate_mapping(mapper_config, query_columns)
        
        return validation
        
    except Exception as e:
        frappe.log_error(f"Error en validate_mapper_config: {str(e)}", "DataMapper Error")
        return {"is_valid": False, "errors": [str(e)], "warnings": []}


@frappe.whitelist()
def get_available_operations(column_type):
    # Retorna operaciones disponibles para un tipo de columna
    try:
        from ...domain.data_mapper.data_mapper_service import DataMapperService
        
        mapper_service = DataMapperService()
        operations = mapper_service.get_available_operations(column_type)
        
        return operations
        
    except Exception as e:
        frappe.log_error(f"Error en get_available_operations: {str(e)}", "DataMapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_column_metadata(doc_name, query_id):
    # Obtiene metadata de columnas de una query ejecutada
    try:
        from ...domain.data_mapper.data_mapper_service import DataMapperService
        from ...domain.query_service.query_service import QueryService
        
        # Ejecutar query
        query_service = QueryService()
        query_result = query_service.execute(doc_name, query_id)
        
        if not query_result.get("success"):
            return query_result
        
        # Obtener metadata
        mapper_service = DataMapperService()
        data = query_result.get("results", [])
        columns = mapper_service.get_column_metadata(data)
        
        return {"success": True, "columns": columns}
        
    except Exception as e:
        frappe.log_error(f"Error en get_column_metadata: {str(e)}", "DataMapper Error")
        return {"success": False, "error": str(e)}


# ============================================
# WIDGET SERVICE LAYER - DATA SERVICE ENDPOINTS
# ============================================

@frappe.whitelist()
def fetch_query_data(doc_name, query_id):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.fetch_query_data(doc_name, query_id)


@frappe.whitelist()
def apply_transformations(data, config):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.apply_transformations(data, config)


@frappe.whitelist()
def save_widget_config(doc_name, widget_config):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.save_widget_config(doc_name, widget_config)


@frappe.whitelist()
def upload_data_service(doc_name, data, source="manual"):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.upload_data(doc_name, data, source)


@frappe.whitelist()
def filter_data(data, filters):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.filter_data(data, filters)


@frappe.whitelist()
def aggregate_data(data, group_by, aggregations):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.aggregate_data(data, group_by, aggregations)


@frappe.whitelist()
def preview_widget(data, widget_type, widget_config=None):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.preview_widget(data, widget_type, widget_config)


@frappe.whitelist()
def validate_config(config, data_columns):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.validate_config(config, data_columns)


@frappe.whitelist()
def get_column_stats(data, column):
    from ...domain.widget_service.data_service_endpoints import DataServiceEndpoints
    endpoints = DataServiceEndpoints()
    return endpoints.get_column_stats(data, column)
