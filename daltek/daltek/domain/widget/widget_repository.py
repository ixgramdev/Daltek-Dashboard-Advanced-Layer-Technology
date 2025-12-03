import json

import frappe


class WidgetRepository:
    """Acceso a persistencia de widgets del DocType Daltek.

    Responsable de leer y escribir el campo JSON `layout` del documento Daltek.
    """

    def get_doc(self, doc_name: str):
        if not frappe.db.exists("Daltek", doc_name):
            raise ValueError(f"Documento Daltek '{doc_name}' no existe")
        return frappe.get_doc("Daltek", doc_name)

    def get_layout(self, doc_name: str) -> list[dict]:
        """Obtiene el layout como lista de dicts.

        Nunca lanza excepción por errores de parseo: en caso de problema, devuelve lista vacía
        y deja que la capa de servicio decida cómo manejarlo.
        """

        doc = self.get_doc(doc_name)
        raw_layout = getattr(doc, "layout", None)

        if not raw_layout:
            return []

        try:
            return json.loads(raw_layout)
        except Exception:
            frappe.log_error(
                f"No se pudo parsear layout para documento '{doc_name}'",
                "WidgetRepository Error",
            )
            return []

    def save_layout(self, doc_name: str, layout: list[dict]) -> None:
        """Persiste el layout en el DocType Daltek."""

        # Usamos set_value para evitar cargar todo el doc cuando no es necesario
        frappe.db.set_value(
            "Daltek",
            doc_name,
            "layout",
            json.dumps(layout, ensure_ascii=False, indent=2),
        )
        frappe.db.commit()
