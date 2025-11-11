# Copyright (c) 2025, GSI and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.model.document import Document


class Daltek(Document):
    pass


@frappe.whitelist()
def execute_query_builder_sql(sql_query, limit=100):
    """
    Ejecuta una consulta SQL generada por el Query Builder de forma segura.

    Args:
        sql_query (str): La consulta SQL a ejecutar
        limit (int): Límite máximo de filas a retornar (default: 100)

    Returns:
        dict: Diccionario con los resultados de la consulta
    """
    try:
        # Validaciones de seguridad
        if not sql_query or not sql_query.strip():
            frappe.throw("La consulta SQL no puede estar vacía")

        # Limpiar y normalizar la consulta
        sql_query = sql_query.strip()
        if sql_query.endswith(";"):
            sql_query = sql_query[:-1]

        # Validar que sea solo una consulta SELECT
        sql_upper = sql_query.upper().strip()
        if not sql_upper.startswith("SELECT"):
            frappe.throw("Solo se permiten consultas SELECT")

        # Evitar consultas peligrosas
        dangerous_keywords = [
            "DELETE",
            "INSERT",
            "UPDATE",
            "DROP",
            "CREATE",
            "ALTER",
            "TRUNCATE",
        ]
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                frappe.throw(f"Palabra clave no permitida: {keyword}")

        # Agregar límite si no existe
        if "LIMIT" not in sql_upper:
            sql_query += f" LIMIT {limit}"

        # Ejecutar la consulta
        frappe.log_error(f"Ejecutando consulta: {sql_query}", "QueryBuilder SQL")

        results = frappe.db.sql(sql_query, as_dict=True)

        return {
            "success": True,
            "data": results,
            "count": len(results),
            "sql": sql_query,
            "message": f"Consulta ejecutada exitosamente. {len(results)} filas retornadas.",
        }

    except frappe.ValidationError as e:
        return {
            "success": False,
            "error": str(e),
            "sql": sql_query,
            "message": "Error de validación en la consulta",
        }
    except Exception as e:
        frappe.log_error(
            f"Error ejecutando consulta SQL: {str(e)}", "QueryBuilder Error"
        )
        return {
            "success": False,
            "error": str(e),
            "sql": sql_query,
            "message": "Error ejecutando la consulta SQL",
        }


@frappe.whitelist()
def get_doctype_fields(doctype_name):
    """
    Obtiene los campos de un DocType específico para el Query Builder.

    Args:
        doctype_name (str): Nombre del DocType

    Returns:
        dict: Diccionario con los campos del DocType
    """
    try:
        if not doctype_name:
            frappe.throw("El nombre del DocType es requerido")

        # Verificar que el DocType existe
        if not frappe.db.exists("DocType", doctype_name):
            frappe.throw(f"El DocType '{doctype_name}' no existe")

        # Obtener metadatos del DocType
        meta = frappe.get_meta(doctype_name)

        # Campos estándar que siempre están disponibles
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

        # Campos personalizados del DocType
        custom_fields = []
        for field in meta.fields:
            if field.fieldname and field.fieldtype not in [
                "Section Break",
                "Column Break",
                "Tab Break",
            ]:
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
