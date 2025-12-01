# Capa de endpoints - maneja validación y parseo JSON
# Llamados desde daltek.py (controlador)

import json
import frappe
from .data_service import DataService


class DataServiceEndpoints:
    # Endpoints para servicio de datos - maneja validación de entrada y parseo JSON
    
    def __init__(self):
        self.service = DataService()
    
    def fetch_query_data(self, doc_name, query_id):
        # Ejecuta query y retorna datos con metadata
        try:
            result = self.service.fetch_query_data(doc_name, query_id)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en fetch_query_data: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def apply_transformations(self, data, config):
        # Aplica transformaciones del Data Mapper
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(config, str):
                config = json.loads(config)
            
            result = self.service.apply_transformations(data, config)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en apply_transformations: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def save_widget_config(self, doc_name, widget_config):
        # Guarda configuración de widget en layout
        try:
            if isinstance(widget_config, str):
                widget_config = json.loads(widget_config)
            
            result = self.service.save_widget_config(doc_name, widget_config)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en save_widget_config: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def upload_data(self, doc_name, data, source="manual"):
        # Sube datos desde frontend (CSV/Excel/JSON)
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            result = self.service.upload_data(doc_name, data, source)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en upload_data: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def filter_data(self, data, filters):
        # Aplica filtros a los datos
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(filters, str):
                filters = json.loads(filters)
            
            result = self.service.filter_data(data, filters)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en filter_data: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def aggregate_data(self, data, group_by, aggregations):
        # Agrupa y agrega datos
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(group_by, str):
                group_by = json.loads(group_by)
            if isinstance(aggregations, str):
                aggregations = json.loads(aggregations)
            
            result = self.service.aggregate_data(data, group_by, aggregations)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en aggregate_data: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def preview_widget(self, data, widget_type, widget_config=None):
        # Genera preview de widget
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(widget_config, str):
                widget_config = json.loads(widget_config)
            
            result = self.service.preview_widget(data, widget_type, widget_config)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en preview_widget: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def validate_config(self, config, data_columns):
        # Valida configuración de mapper
        try:
            if isinstance(config, str):
                config = json.loads(config)
            if isinstance(data_columns, str):
                data_columns = json.loads(data_columns)
            
            result = self.service.validate_config(config, data_columns)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en validate_config: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
    
    def get_column_stats(self, data, column):
        # Obtiene estadísticas de una columna
        try:
            if isinstance(data, str):
                data = json.loads(data)
            
            result = self.service.get_column_stats(data, column)
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en get_column_stats: {str(e)}", "DataService Error")
            return {"success": False, "error": str(e)}
