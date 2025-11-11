# Copyright (c) 2025, GSI and contributors
# For license information, please see license.txt

import os

import frappe
from frappe.model.document import Document


class Daltek(Document):
    pass


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
        return f"<div style='padding: 20px; color: red;'>{error_msg}</div>"
    except Exception as e:
        error_msg = f"Error cargando Query Builder: {str(e)}"
        frappe.log_error(error_msg)
        return f"<div style='padding: 20px; color: red;'>{error_msg}</div>"
