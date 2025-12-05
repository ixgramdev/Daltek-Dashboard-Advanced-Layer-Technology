import json

import frappe

class QueryRepository:
    """Acceso a persistencia de queries del DocType Daltek.

    Lee y escribe el campo JSON `query_data_storage`.
    """

    STORAGE_FIELD = "query_data_storage"

    def get_doc(self, doc_name: str):
        if not frappe.db.exists("Daltek", doc_name):
            raise ValueError(f"Documento Daltek '{doc_name}' no existe")
        return frappe.get_doc("Daltek", doc_name)

    def get_queries(self, doc_name: str) -> list[dict]:
        """Obtiene la lista de queries almacenadas."""

        doc = self.get_doc(doc_name)
        raw = getattr(doc, self.STORAGE_FIELD, None)

        if not raw:
            return []

        try:
            return json.loads(raw)
        except Exception:
            frappe.log_error(
                f"No se pudo parsear queries para documento '{doc_name}'",
                "QueryRepository Error",
            )
            return []

    def save_queries(
        self, doc_name: str, queries: list[dict], auto_commit: bool = True
    ) -> None:
        """Guarda la lista completa de queries en el documento."""

        frappe.db.set_value(
            "Daltek",
            doc_name,
            self.STORAGE_FIELD,
            json.dumps(queries, ensure_ascii=False, indent=2),
        )

        if auto_commit:
            frappe.db.commit()
