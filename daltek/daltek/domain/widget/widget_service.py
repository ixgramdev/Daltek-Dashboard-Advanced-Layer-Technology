import json
from typing import Any

import frappe

from ...dtos.echart_widget_dto import EChartWidgetDTO
from ...dtos.widget_dto import WidgetDTO
from .echart.echart_factory import EChartFactory
from .echart.echart_transforrmer import EChartTransformer
from .widget_repository import WidgetRepository
from .widget_validator import WidgetValidator


class WidgetService:
    """Servicio para gestionar widgets del dashboard Daltek."""

    def __init__(self):
        self.validator = WidgetValidator()
        self.echart_factory = EChartFactory
        self.echart_transformer = EChartTransformer()
        self.repository = WidgetRepository()

    # --- REPOSITORY METHODS ---
    @frappe.whitelist()
    def add(self, doc_name: str, widget: str | dict) -> dict[str, Any]:
        """Añade un nuevo widget al layout del documento en formato normalizado."""
        try:
            widget_data = json.loads(widget) if isinstance(widget, str) else widget

            widget_type = widget_data.get("type")

            if widget_type == "echart" or widget_data.get("chart_type"):
                dto = EChartWidgetDTO.from_dict(widget_data)
            else:
                dto = WidgetDTO.from_dict(widget_data)

            layout = self.repository.get_layout(doc_name)

            if not dto.id:
                dto.id = self._generate_widget_id(layout)

            if not dto.id:
                return {
                    "success": False,
                    "error": "No se pudo generar ID único para el widget",
                }

            now_iso = frappe.utils.now_datetime().isoformat()
            if not dto.created_at:
                dto.created_at = now_iso
            dto.modified_at = now_iso

            print(dto.__dict__)

            validation = self.validator.validate_widget(dto)
            if not validation.get("valid"):
                return {
                    "success": False,
                    "error": validation.get("error", "Widget inválido"),
                }

            # Convertir a formato normalizado

            dto_dict = dto.to_dict()

            # Construir configuración de EChart si es necesario
            if isinstance(dto, EChartWidgetDTO):
                echart_result = self._build_echart_config(dto)
                if not echart_result.get("success"):
                    return {
                        "success": False,
                        "error": f"Error construyendo EChart: {echart_result.get('error')}",
                    }
                # Actualizar contenido con la configuración construida
                dto_dict["content"]["config"] = echart_result.get("config")

            layout.append(dto_dict)
            self.repository.save_layout(doc_name, layout)

            return {
                "success": True,
                "message": f"Widget '{dto_dict.get('id')}' añadido correctamente",
                "widget": dto_dict,
                "layout": layout,
            }

        except Exception as e:
            frappe.log_error(f"Error en add(): {str(e)}", "WidgetService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def build_echart(self, doc_name: str, widget_id: str) -> dict[str, Any]:
        """Construye un EChart desde la configuración guardada."""
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
        """Método especializado para añadir un EChart."""
        try:
            if isinstance(chart_data, str):
                chart_data = json.loads(chart_data)
            if isinstance(chart_config, str):
                chart_config = json.loads(chart_config)
            if chart_config is None:
                chart_config = {}

            if not self.echart_factory.is_registered(chart_type):
                return {
                    "success": False,
                    "error": f"Tipo '{chart_type}' no está registrado. "
                    f"Disponibles: {', '.join(self.echart_factory.get_available_types())}",
                }

            builder = self.echart_factory.create(chart_type)
            build_result = builder.build(chart_data, chart_config)

            if not build_result.get("success"):
                return {
                    "success": False,
                    "error": build_result.get("error", "Error desconocido en build"),
                }

            widget = {
                "type": "echart",
                "chart_type": chart_type,
                "echart_data": chart_data,
                "echart_config": build_result.get("config"),
                "properties": widget_properties
                or {"title": f"{chart_type.title()} Chart"},
            }

            return self.add(doc_name, widget)

        except Exception as e:
            frappe.log_error(f"Error en add_echart(): {str(e)}", "WidgetService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def update_echart_data(
        self, doc_name: str, widget_id: str, chart_data: str | dict
    ) -> dict[str, Any]:
        """Actualiza solo los datos de un EChart."""
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

            widget["echart_data"] = chart_data

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
        """Transforma la configuración de un EChart para renderización."""
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
        """Elimina un widget del layout."""
        try:
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            layout = self.get_layout(doc_name)
            filtered_layout = [w for w in layout if w.get("id") != widget_id]

            if len(filtered_layout) == len(layout):
                return {
                    "success": False,
                    "error": f"Widget con ID '{widget_id}' no encontrado",
                }

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
        """Edita un widget existente."""
        try:
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            new_data = (
                json.loads(widget_data) if isinstance(widget_data, str) else widget_data
            )

            validation = self.validator.validate_widget(new_data)
            if not validation.get("valid"):
                return {
                    "success": False,
                    "error": validation.get("error", "Widget inválido"),
                }

            layout = self.get_layout(doc_name)

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

            new_data["id"] = widget_id
            new_data["created_at"] = old_widget.get("created_at")
            new_data["modified_at"] = frappe.utils.now_datetime().isoformat()

            layout[widget_index] = new_data

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
        """Actualiza la posición de un widget (en sección layout)."""
        try:
            layout = self.get_layout(doc_name)

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

            # Actualizar layout (formato normalizado único)
            if "layout" not in widget:
                widget["layout"] = {}

            widget["layout"].update(position)
            widget["metadata"]["modified_at"] = frappe.utils.now_datetime().isoformat()

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

        numeric_ids = []
        for wid in existing_ids:
            try:
                numeric_ids.append(int(str(wid).split("_")[0]))
            except (ValueError, IndexError):
                pass

        next_num = max(numeric_ids) + 1 if numeric_ids else len(layout) + 1
        return f"widget_{next_num}_{timestamp}"

    def _build_echart_config(self, dto: EChartWidgetDTO) -> dict[str, Any]:
        """
        Construye la configuración de un EChart usando el factory.

        Diseñado para trabajar con DTOs en formato normalizado.
        """
        try:
            chart_type = dto.chart_type

            if not self.echart_factory.is_registered(chart_type):
                return {
                    "success": False,
                    "error": f"Tipo '{chart_type}' no está registrado",
                }

            builder = self.echart_factory.create(chart_type)
            result = builder.build(dto.echart_data, dto.properties)

            return result

        except Exception as e:
            frappe.log_error(
                f"Error en _build_echart_config(): {str(e)}", "WidgetService Error"
            )
            return {
                "success": False,
                "error": str(e),
            }

    def _process_widgets_for_render(self, layout: list[dict]) -> list[dict]:
        """
        Procesa widgets para renderizado en cliente.

        Como todo está en formato normalizado, retorna directamente.
        """
        return layout

    def _normalize_widget(self, widget: dict) -> dict:
        """
        DEPRECATED: Ya no es necesario.
        Todo widget ya está en formato normalizado.
        """
        return widget

    # --- Layout ---
    @frappe.whitelist()
    def render_layout(self, doc_name: str) -> dict[str, Any]:
        """Renderiza el layout JSON del documento Daltek."""
        try:
            try:
                layout = self.repository.get_layout(doc_name)
            except ValueError as e:
                return {"success": False, "error": str(e)}

            if not layout:
                return {
                    "success": True,
                    "layout": [],
                    "widgets": [],
                    "message": "No hay widgets en el layout",
                }

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
        """Obtiene el layout del documento Daltek."""
        try:
            return self.repository.get_layout(doc_name)
        except Exception as e:
            frappe.log_error(f"Error en get_layout(): {str(e)}", "WidgetService Error")
            return []
