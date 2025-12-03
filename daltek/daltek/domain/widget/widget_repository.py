import json

import frappe


class WidgetRepository:
    """Acceso a persistencia de widgets del DocType Daltek.

    Responsable de leer y escribir el campo JSON `layout` del documento Daltek.

    IMPORTANTE: Cada documento Daltek tiene su PROPIO layout separado.
    Nunca se comparten widgets entre documentos.
    """

    def get_doc(self, doc_name: str):
        if not frappe.db.exists("Daltek", doc_name):
            raise ValueError(f"Documento Daltek '{doc_name}' no existe")
        return frappe.get_doc("Daltek", doc_name)

    def get_layout(self, doc_name: str) -> list[dict]:
        """Obtiene el layout como lista de dicts para un documento específico.

        IMPORTANTE: El layout se obtiene EXCLUSIVAMENTE del documento específico
        indicado por doc_name. No hay compartición entre documentos.

        Nunca lanza excepción por errores de parseo: en caso de problema, devuelve lista vacía
        y deja que la capa de servicio decida cómo manejarlo.

        Args:
            doc_name: Nombre ÚNICO del documento Daltek

        Returns:
            Lista de widgets del documento específico, o lista vacía si hay error
        """

        doc = self.get_doc(doc_name)
        raw_layout = getattr(doc, "layout", None)

        if not raw_layout:
            return []

        try:
            layout = json.loads(raw_layout)
            frappe.logger().debug(
                f"✅ Layout cargado para documento '{doc_name}': {len(layout)} widgets"
            )
            return layout
        except Exception as e:
            frappe.log_error(
                f"❌ No se pudo parsear layout para documento '{doc_name}': {str(e)}",
                "WidgetRepository Error",
            )
            return []

    def save_layout(self, doc_name: str, layout: list[dict]) -> None:
        """Persiste el layout en el DocType Daltek.

        IMPORTANTE: Cada documento tiene su PROPIO layout separado.
        Se guarda EXCLUSIVAMENTE en el campo 'layout' del documento específico.
        No afecta a otros documentos.

        Args:
            doc_name: Nombre ÚNICO del documento Daltek
            layout: Lista de widgets a guardar para este documento
        """

        frappe.logger().debug(
            f"💾 Guardando layout para documento '{doc_name}': {len(layout)} widgets"
        )

        # Usamos set_value para evitar cargar todo el doc cuando no es necesario
        frappe.db.set_value(
            "Daltek",
            doc_name,
            "layout",
            json.dumps(layout, ensure_ascii=False, indent=2),
        )
        frappe.db.commit()

        frappe.logger().debug(f"✅ Layout guardado para documento '{doc_name}'")

        # Limpiar caché para asegurar que los datos son frescos
        # y no se mezclen layouts de diferentes documentos
        frappe.cache().delete_key(f"daltek_layout_{doc_name}")

        # Invalidar caché del documento
        frappe.clear_document_cache("Daltek", doc_name)

        frappe.logger().debug(f"🔄 Caché limpiada para documento '{doc_name}'")
