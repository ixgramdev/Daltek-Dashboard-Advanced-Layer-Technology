import json
from typing import Any

import frappe

from .echart.echart_factory import EChartFactory
from .echart.echart_transforrmer import EChartTransformer
from .widget_validator import WidgetValidator


class WidgetService:
    """
    Servicio para gestionar widgets del dashboard Daltek.
    CRUD operations sobre el campo `layout` (JSON) del DocType Daltek.
    """

    def __init__(self):
        self.validator = WidgetValidator()
        self.echart_factory = EChartFactory
        self.echart_transformer = EChartTransformer()

    # --- CRUD OPERATIONS ---

    @frappe.whitelist()
    def render_layout(self, doc_name: str) -> dict[str, Any]:
        """
        Renderiza el layout JSON del documento Daltek en ejecución.
        Obtiene el layout guardado y lo prepara para renderizar en el cliente.

        Args:
            doc_name: Nombre del documento Daltek

        Returns:
            Dict con success, layout y widgets renderizados
        """
        try:
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            layout = self.get_layout(doc_name)

            if not layout:
                return {
                    "success": True,
                    "layout": [],
                    "widgets": [],
                    "message": "No hay widgets en el layout",
                }

            # Procesar widgets para renderizado
            rendered_widgets = self._process_widgets_for_render(layout)

            return {
                "success": True,
                "layout": layout,
                "widgets": rendered_widgets,
                "count": len(rendered_widgets),
            }

        except Exception as e:
            frappe.log_error(
                f"Error en render_layout(): {str(e)}", "WidgetService Error"
            )
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def get_layout(self, doc_name: str) -> list[dict]:
        """
        Obtiene el layout (lista de widgets) del documento Daltek.

        Args:
            doc_name: Nombre del documento Daltek

        Returns:
            Lista de widgets o lista vacía si no existe layout
        """
        try:
            if not frappe.db.exists("Daltek", doc_name):
                frappe.throw(f"Documento Daltek '{doc_name}' no existe")

            doc = frappe.get_doc("Daltek", doc_name)
            layout = self._parse_layout(doc.layout)

            return layout

        except Exception as e:
            frappe.log_error(f"Error en get_layout(): {str(e)}", "WidgetService Error")
            return []

    @frappe.whitelist()
    def add(self, doc_name: str, widget: str | dict) -> dict[str, Any]:
        """
        Añade un nuevo widget al layout del documento.

        Args:
            doc_name: Nombre del documento Daltek
            widget: Dict o JSON string con los datos del widget

        Returns:
            Dict con success, message y layout actualizado
        """
        try:
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            # Parsear widget si es string
            widget_data = json.loads(widget) if isinstance(widget, str) else widget

            # Validar widget
            validation = self.validator.validate_widget(widget_data)
            if not validation.get("valid"):
                return {
                    "success": False,
                    "error": validation.get("error", "Widget inválido"),
                }

            # Obtener layout actual
            layout = self.get_layout(doc_name)

            # Asignar ID único si no tiene
            if not widget_data.get("id"):
                widget_data["id"] = self._generate_widget_id(layout)

            # Añadir metadata
            widget_data["created_at"] = frappe.utils.now_datetime().isoformat()
            widget_data["modified_at"] = frappe.utils.now_datetime().isoformat()

            # Si es un chart de EChart, procesarlo
            if widget_data.get("type") in self.echart_factory.get_available_types():
                echart_result = self._build_echart(widget_data)
                if not echart_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Error construyendo EChart: {echart_result.get('error')}",
                    }
                # Almacenar configuración del EChart
                widget_data["echart_config"] = echart_result.get("config")

            # Agregar widget a layout
            layout.append(widget_data)

            # Guardar en BD
            frappe.db.set_value(
                "Daltek",
                doc_name,
                "layout",
                json.dumps(layout, ensure_ascii=False, indent=2),
            )
            frappe.db.commit()

            return {
                "success": True,
                "message": f"Widget '{widget_data.get('id')}' añadido correctamente",
                "widget": widget_data,
                "layout": layout,
            }

        except Exception as e:
            frappe.log_error(f"Error en add(): {str(e)}", "WidgetService Error")
            return {"success": False, "error": str(e)}

    # --- MÉTODOS PARA ECHART ---

    @frappe.whitelist()
    def build_echart(self, doc_name: str, widget_id: str) -> dict[str, Any]:
        """
        Construye un EChart desde la configuración guardada.
        Útil para reconstruir un chart después de cambios en datos.

        Args:
            doc_name: Nombre del documento Daltek
            widget_id: ID del widget

        Returns:
            Dict con success y configuración del EChart
        """
        try:
            layout = self.get_layout(doc_name)
            widget = None

            for w in layout:
                if w.get("id") == widget_id:
                    widget = w
                    break

            if not widget:
                return {
                    "success": False,
                    "error": f"Widget '{widget_id}' no encontrado",
                }

            if widget.get("type") not in self.echart_factory.get_available_types():
                return {
                    "success": False,
                    "error": "Widget no es de tipo EChart",
                }

            # Construir el chart
            result = self._build_echart(widget)
            return result

        except Exception as e:
            frappe.log_error(
                f"Error en build_echart(): {str(e)}", "WidgetService Error"
            )
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def add_echart(
        self,
        doc_name: str,
        chart_type: str,
        chart_data: str | dict,
        chart_config: str | dict = None,
        widget_properties: dict = None,
    ) -> dict[str, Any]:
        """
        Método especializado para añadir un EChart.
        Simplifica el proceso: valida datos, construye config, y añade widget.

        Args:
            doc_name: Nombre del documento Daltek
            chart_type: Tipo de chart (line, bar, pie, scatter)
            chart_data: Datos del chart (series, categories, etc)
            chart_config: Configuración visual del chart (colors, title, etc)
            widget_properties: Propiedades del widget (title, size, etc)

        Returns:
            Dict con success y widget completo
        """
        try:
            # Parsear strings a dicts
            if isinstance(chart_data, str):
                chart_data = json.loads(chart_data)
            if isinstance(chart_config, str):
                chart_config = json.loads(chart_config)
            if chart_config is None:
                chart_config = {}

            # Validar que el tipo exista
            if not self.echart_factory.is_registered(chart_type):
                return {
                    "success": False,
                    "error": f"Tipo '{chart_type}' no está registrado. "
                    f"Disponibles: {', '.join(self.echart_factory.get_available_types())}",
                }

            # Construir configuración del EChart
            builder = self.echart_factory.create(chart_type)
            build_result = builder.build(chart_data, chart_config)

            if not build_result.get("success"):
                return {
                    "success": False,
                    "error": build_result.get("error", "Error desconocido en build"),
                }

            # Crear widget con la configuración
            widget = {
                "type": "echart",  # Tipo principal del widget
                "chart_type": chart_type,  # Subtipo específico (line, bar, pie, scatter)
                "echart_data": chart_data,
                "echart_config": build_result.get("config"),
                "properties": widget_properties
                or {"title": f"{chart_type.title()} Chart"},
            }

            # Añadir el widget
            return self.add(doc_name, widget)

        except Exception as e:
            frappe.log_error(f"Error en add_echart(): {str(e)}", "WidgetService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def update_echart_data(
        self, doc_name: str, widget_id: str, chart_data: str | dict
    ) -> dict[str, Any]:
        """
        Actualiza solo los datos de un EChart sin modificar su configuración.
        Util para actualizar información sin cambiar estilos.

        Args:
            doc_name: Nombre del documento Daltek
            widget_id: ID del widget
            chart_data: Nuevos datos para el chart

        Returns:
            Dict con success y widget actualizado
        """
        try:
            if isinstance(chart_data, str):
                chart_data = json.loads(chart_data)

            layout = self.get_layout(doc_name)
            widget = None

            for w in layout:
                if w.get("id") == widget_id:
                    widget = w
                    break

            if not widget:
                return {
                    "success": False,
                    "error": f"Widget '{widget_id}' no encontrado",
                }

            chart_type = widget.get("type")
            if chart_type not in self.echart_factory.get_available_types():
                return {
                    "success": False,
                    "error": "Widget no es de tipo EChart",
                }

            # Actualizar datos
            widget["echart_data"] = chart_data

            # Reconstruir configuración con nuevos datos
            chart_config = widget.get("echart_config", {})
            builder = self.echart_factory.create(chart_type)
            build_result = builder.build(chart_data, chart_config)

            if not build_result.get("success"):
                return {
                    "success": False,
                    "error": f"Error actualizando datos: {build_result.get('error')}",
                }

            widget["echart_config"] = build_result.get("config")
            widget["modified_at"] = frappe.utils.now_datetime().isoformat()

            # Guardar cambios
            frappe.db.set_value(
                "Daltek",
                doc_name,
                "layout",
                json.dumps(layout, ensure_ascii=False, indent=2),
            )
            frappe.db.commit()

            return {
                "success": True,
                "message": "Datos del EChart actualizados",
                "widget": widget,
            }

        except Exception as e:
            frappe.log_error(
                f"Error en update_echart_data(): {str(e)}", "WidgetService Error"
            )
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def transform_echart_for_render(
        self, doc_name: str, widget_id: str
    ) -> dict[str, Any]:
        """
        Transforma la configuración de un EChart para renderización en cliente.
        Aplica transformaciones finales antes de enviar al navegador.

        Args:
            doc_name: Nombre del documento Daltek
            widget_id: ID del widget

        Returns:
            Dict con success y widget transformado
        """
        try:
            layout = self.get_layout(doc_name)
            widget = None

            for w in layout:
                if w.get("id") == widget_id:
                    widget = w
                    break

            if not widget:
                return {
                    "success": False,
                    "error": f"Widget '{widget_id}' no encontrado",
                }

            # Transformar el widget
            transformed = self.echart_transformer.transform_widget(widget)

            return {
                "success": True,
                "widget": transformed,
            }

        except Exception as e:
            frappe.log_error(
                f"Error en transform_echart_for_render(): {str(e)}",
                "WidgetService Error",
            )
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def delete(self, doc_name: str, widget_id: str) -> dict[str, Any]:
        """
        Elimina un widget del layout.

        Args:
            doc_name: Nombre del documento Daltek
            widget_id: ID del widget a eliminar

        Returns:
            Dict con success, message y layout actualizado
        """
        try:
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            layout = self.get_layout(doc_name)

            # Buscar y eliminar widget
            filtered_layout = [w for w in layout if w.get("id") != widget_id]

            if len(filtered_layout) == len(layout):
                return {
                    "success": False,
                    "error": f"Widget con ID '{widget_id}' no encontrado",
                }

            # Guardar layout actualizado
            frappe.db.set_value(
                "Daltek",
                doc_name,
                "layout",
                json.dumps(filtered_layout, ensure_ascii=False, indent=2),
            )
            frappe.db.commit()

            return {
                "success": True,
                "message": f"Widget '{widget_id}' eliminado correctamente",
                "layout": filtered_layout,
            }

        except Exception as e:
            frappe.log_error(f"Error en delete(): {str(e)}", "WidgetService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def edit(
        self, doc_name: str, widget_id: str, widget_data: str | dict
    ) -> dict[str, Any]:
        """
        Edita un widget existente.
        Obtiene el widget actual, lo elimina y añade la versión actualizada.

        Args:
            doc_name: Nombre del documento Daltek
            widget_id: ID del widget a editar
            widget_data: Dict o JSON string con los nuevos datos

        Returns:
            Dict con success, message y layout actualizado
        """
        try:
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            # Parsear datos si es string
            new_data = (
                json.loads(widget_data) if isinstance(widget_data, str) else widget_data
            )

            # Validar nuevo widget
            validation = self.validator.validate_widget(new_data)
            if not validation.get("valid"):
                return {
                    "success": False,
                    "error": validation.get("error", "Widget inválido"),
                }

            # Obtener layout actual
            layout = self.get_layout(doc_name)

            # Buscar widget actual
            widget_index = None
            old_widget = None
            for i, w in enumerate(layout):
                if w.get("id") == widget_id:
                    widget_index = i
                    old_widget = w
                    break

            if widget_index is None:
                return {
                    "success": False,
                    "error": f"Widget con ID '{widget_id}' no encontrado",
                }

            # Mantener ID y timestamps de creación
            new_data["id"] = widget_id
            new_data["created_at"] = old_widget.get("created_at")
            new_data["modified_at"] = frappe.utils.now_datetime().isoformat()

            # Actualizar widget en layout
            layout[widget_index] = new_data

            # Guardar en BD
            frappe.db.set_value(
                "Daltek",
                doc_name,
                "layout",
                json.dumps(layout, ensure_ascii=False, indent=2),
            )
            frappe.db.commit()

            return {
                "success": True,
                "message": f"Widget '{widget_id}' actualizado correctamente",
                "widget": new_data,
                "layout": layout,
            }

        except Exception as e:
            frappe.log_error(f"Error en edit(): {str(e)}", "WidgetService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def update_position(
        self, doc_name: str, widget_id: str, position: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Actualiza solo la posición de un widget (x, y, width, height).
        Útil para drag & drop sin recargar el widget completo.

        Args:
            doc_name: Nombre del documento Daltek
            widget_id: ID del widget
            position: Dict con {x, y, width, height} o {col, row, width, height}

        Returns:
            Dict con success y widget actualizado
        """
        try:
            layout = self.get_layout(doc_name)

            # Buscar widget
            widget = None
            for w in layout:
                if w.get("id") == widget_id:
                    widget = w
                    break

            if widget is None:
                return {
                    "success": False,
                    "error": f"Widget '{widget_id}' no encontrado",
                }

            # Actualizar posición
            if "position" not in widget:
                widget["position"] = {}

            widget["position"].update(position)
            widget["modified_at"] = frappe.utils.now_datetime().isoformat()

            # Guardar
            frappe.db.set_value(
                "Daltek",
                doc_name,
                "layout",
                json.dumps(layout, ensure_ascii=False, indent=2),
            )
            frappe.db.commit()

            return {
                "success": True,
                "message": "Posición actualizada",
                "widget": widget,
            }

        except Exception as e:
            frappe.log_error(
                f"Error en update_position(): {str(e)}", "WidgetService Error"
            )
            return {"success": False, "error": str(e)}

    # --- PRIVATE HELPER METHODS ---

    def _parse_layout(self, layout_data: str | list) -> list[dict]:
        """Parsea el layout del BD (string JSON) a list."""
        if not layout_data:
            return []

        if isinstance(layout_data, str):
            try:
                return json.loads(layout_data)
            except json.JSONDecodeError:
                return []
        elif isinstance(layout_data, list):
            return layout_data
        else:
            return []

    def _generate_widget_id(self, layout: list[dict]) -> str:
        """Genera un ID único para un nuevo widget."""
        import time

        timestamp = int(time.time() * 1000)
        existing_ids = [w.get("id") for w in layout if w.get("id")]

        # Extraer números de IDs existentes
        numeric_ids = []
        for wid in existing_ids:
            try:
                numeric_ids.append(int(str(wid).split("_")[0]))
            except (ValueError, IndexError):
                pass

        next_num = max(numeric_ids) + 1 if numeric_ids else len(layout) + 1
        return f"widget_{next_num}_{timestamp}"

    def _build_echart(self, widget_data: dict) -> dict[str, Any]:
        """
        Construye la configuración de un EChart usando el factory.

        Args:
            widget_data: Dict con los datos del widget

        Returns:
            Dict con success y configuración del EChart
        """
        try:
            chart_type = widget_data.get("type")

            if not self.echart_factory.is_registered(chart_type):
                return {
                    "success": False,
                    "error": f"Tipo '{chart_type}' no está registrado",
                }

            # Obtener datos y configuración
            chart_data = widget_data.get("echart_data", {})
            chart_config = widget_data.get("properties", {})

            # Crear builder
            builder = self.echart_factory.create(chart_type)

            # Construir configuración
            result = builder.build(chart_data, chart_config)

            return result

        except Exception as e:
            frappe.log_error(
                f"Error en _build_echart(): {str(e)}", "WidgetService Error"
            )
            return {
                "success": False,
                "error": str(e),
            }

    def _process_widgets_for_render(self, layout: list[dict]) -> list[dict]:
        """
        Procesa widgets para renderizado en cliente.
        Añade metadatos y prepara datos para visualización.
        """
        rendered = []
        for widget in layout:
            rendered_widget = {
                "id": widget.get("id"),
                "type": widget.get("type"),
                "title": widget.get("properties", {}).get("title", "Widget"),
                "position": widget.get("position", {}),
                "properties": widget.get("properties", {}),
                "data": widget.get("data", {}),
                "created_at": widget.get("created_at"),
                "modified_at": widget.get("modified_at"),
            }
            rendered.append(rendered_widget)

        return rendered
