# Copyright (c) 2025, GSI and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.model.document import Document

from ...domain.query.query_service import QueryService
from ...domain.widget.widget_service import WidgetService


class Daltek(Document):
    def before_save(self):
        current_datetime = frappe.utils.now()

        if not self.dashboard_owner:
            self.dashboard_owner = frappe.session.user

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
# Los métodos CRUD de los services se encuentran en sus respectivas carpetas
# Solo mantener aquí métodos relacionados con el UI del DocType


@frappe.whitelist()
def get_query_builder_html():
    """
    Retorna el HTML completo del Query Builder para renderizar en un campo HTML.
    Combina el HTML base con todos los archivos JS necesarios de forma modular.
    """
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
    """
    Retorna el HTML completo del sistema Drag and Drop para renderizar en un campo HTML.
    Combina el HTML base con todos los archivos JS necesarios de forma modular.
    """
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
            ("drag_drop_handlers.js", "js"),
            ("widget_config.js", "js"),
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
            "drag_drop_handlers.js": "dd-drag-drop-handlers-js",
            "widget_config.js": "dd-widget-config-js",
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


# --- QUERY SERVICE ---


@frappe.whitelist()
def save_query(doc_name, query_data):
    """
    Guarda una nueva consulta o actualiza una existente en el campo JSON.

    Args:
        doc_name: Nombre del documento Daltek
        query_data: JSON string o dict con los datos de la consulta

    Returns:
        Dict con success, message, queries y saved_query
    """
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
    """
    Edita una consulta existente.

    Args:
        doc_name: Nombre del documento Daltek
        query_id: ID de la consulta a editar
        query_data: JSON string o dict con los nuevos datos

    Returns:
        Dict con success, message, queries y saved_query
    """
    try:
        service = QueryService()
        result = service.edit(doc_name, query_id, query_data)
        return result

    except Exception as e:
        frappe.log_error(f"Error en edit_query: {str(e)}", "QueryService Wrapper Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def delete_query(doc_name, query_id):
    """
    Elimina una consulta del documento.

    Args:
        doc_name: Nombre del documento Daltek
        query_id: ID de la consulta a eliminar

    Returns:
        Dict con success, message y queries actualizadas
    """
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


# Obtener solo los tipos de campos específicos a seleccionar para la query
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


# --- WIDGET SERVICE ---


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


# ==================== WIDGET ENDPOINTS ====================


@frappe.whitelist()
def add_widget(doc_name, widget):
    """
    Endpoint único para agregar cualquier tipo de widget.
    Delega la lógica específica a WidgetService.add()
    """
    service = WidgetService()
    result = service.add(doc_name, widget)
    return result
