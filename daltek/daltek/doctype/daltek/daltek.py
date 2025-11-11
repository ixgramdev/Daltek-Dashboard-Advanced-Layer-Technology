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

        # Verificar si es un DocType custom
        doctype_doc = frappe.get_doc("DocType", doctype_name)
        is_custom = getattr(doctype_doc, "custom", 0) == 1

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


@frappe.whitelist()
def save_query(doc_name, query_data):
    try:
        if isinstance(query_data, str):
            query_data = frappe.parse_json(query_data)

        if not doc_name or doc_name.startswith("new-"):
            return {
                "success": False,
                "message": "Debes guardar el documento Daltek primero",
            }

        if not frappe.db.exists("Daltek", doc_name):
            return {
                "success": False,
                "message": f"El documento Daltek '{doc_name}' no existe",
            }

        doc = frappe.get_doc("Daltek", doc_name)
        existing_queries = (
            frappe.parse_json(doc.query_data_storage) if doc.query_data_storage else []
        )

        query = {
            "id": query_data.get("id") or frappe.generate_hash(length=8),
            "name": query_data.get("name"),
            "doctype": query_data.get("doctype"),
            "columns": query_data.get("columns", []),
            "filters": query_data.get("filters", []),
            "description": query_data.get("description", ""),
            "created_at": query_data.get("created_at") or frappe.utils.now(),
            "modified_at": frappe.utils.now(),
            "created_by": frappe.session.user,
        }

        query_index = -1
        if "id" in query_data:
            for i, existing_query in enumerate(existing_queries):
                if existing_query.get("id") == query_data["id"]:
                    query_index = i
                    break

        if query_index >= 0:
            existing_queries[query_index] = query
            message = f"Consulta '{query['name']}' actualizada exitosamente"
        else:
            existing_queries.append(query)
            message = f"Consulta '{query['name']}' guardada exitosamente"

        doc.query_data_storage = frappe.as_json(existing_queries)
        doc.save()

        return {
            "success": True,
            "message": message,
            "query": query,
            "total_queries": len(existing_queries),
        }

    except Exception as e:
        frappe.log_error(f"Error guardando consulta: {str(e)}", "Query Save Error")
        return {"success": False, "message": f"Error al guardar la consulta: {str(e)}"}


@frappe.whitelist()
def get_saved_queries(doc_name):
    """
    Obtiene todas las consultas guardadas del documento.

    Args:
        doc_name (str): Nombre del documento Daltek

    Returns:
        dict: Lista de consultas guardadas
    """
    try:
        if not doc_name or doc_name.startswith("new-"):
            return {
                "success": True,
                "queries": [],
                "message": "Documento no guardado, sin consultas disponibles",
            }

        if not frappe.db.exists("Daltek", doc_name):
            return {
                "success": False,
                "message": f"El documento Daltek '{doc_name}' no existe",
            }

        # Obtener el documento
        doc = frappe.get_doc("Daltek", doc_name)

        # Obtener consultas
        queries = (
            frappe.parse_json(doc.query_data_storage) if doc.query_data_storage else []
        )

        return {"success": True, "queries": queries, "total": len(queries)}

    except Exception as e:
        frappe.log_error(f"Error obteniendo consultas: {str(e)}", "Query Get Error")
        return {
            "success": False,
            "message": f"Error al obtener las consultas: {str(e)}",
        }


@frappe.whitelist()
def delete_query(doc_name, query_id):
    """
    Elimina una consulta específica.

    Args:
        doc_name (str): Nombre del documento Daltek
        query_id (str): ID de la consulta a eliminar

    Returns:
        dict: Resultado de la operación
    """
    try:
        if not doc_name or doc_name.startswith("new-"):
            return {
                "success": False,
                "message": "Debes guardar el documento Daltek primero",
            }

        if not frappe.db.exists("Daltek", doc_name):
            return {
                "success": False,
                "message": f"El documento Daltek '{doc_name}' no existe",
            }

        # Obtener el documento
        doc = frappe.get_doc("Daltek", doc_name)

        # Obtener consultas existentes
        existing_queries = (
            frappe.parse_json(doc.query_data_storage) if doc.query_data_storage else []
        )

        # Buscar y eliminar la consulta
        query_to_delete = None
        updated_queries = []

        for query in existing_queries:
            if query.get("id") == query_id:
                query_to_delete = query
            else:
                updated_queries.append(query)

        if not query_to_delete:
            return {
                "success": False,
                "message": f"No se encontró la consulta con ID: {query_id}",
            }

        # Guardar la lista actualizada
        doc.query_data_storage = frappe.as_json(updated_queries)
        doc.save()

        return {
            "success": True,
            "message": f"Consulta '{query_to_delete.get('name', query_id)}' eliminada exitosamente",
            "deleted_query": query_to_delete,
            "remaining_queries": len(updated_queries),
        }

    except Exception as e:
        frappe.log_error(f"Error eliminando consulta: {str(e)}", "Query Delete Error")
        return {"success": False, "message": f"Error al eliminar la consulta: {str(e)}"}
