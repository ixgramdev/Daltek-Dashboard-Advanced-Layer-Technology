# DataService: Capa de servicio para conexión frontend-backend
# Maneja subida de datos, filtrado, transformaciones y comunicación con Data Mapper

import json
import frappe
from typing import Dict, List, Any, Optional
from ..data_mapper.data_mapper_service import DataMapperService


class DataService:
    # Servicio principal para gestión de datos entre frontend y backend
    
    def __init__(self):
        self.mapper_service = DataMapperService()
    
    def fetch_query_data(self, doc_name: str, query_id: str) -> Dict:
        # Obtiene datos de una query ejecutada
        try:
            from ..query_service.query_service import QueryService
            
            query_service = QueryService()
            result = query_service.execute(doc_name, query_id)
            
            if not result.get('success'):
                return {
                    'success': False,
                    'error': result.get('error', 'Error ejecutando query')
                }
            
            return {
                'success': True,
                'data': result.get('results', []),
                'count': len(result.get('results', [])),
                'query_id': query_id,
                'columns': self._extract_columns(result.get('results', []))
            }
            
        except Exception as e:
            frappe.log_error(f"Error en fetch_query_data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def apply_transformations(self, data: List[Dict], config: Dict) -> Dict:
        # Aplica transformaciones del Data Mapper a los datos
        try:
            query_result = {
                'success': True,
                'results': data,
                'count': len(data)
            }
            
            mapper_config = self._build_mapper_config(config)
            result = self.mapper_service.transform(query_result, mapper_config)
            
            return result
            
        except Exception as e:
            frappe.log_error(f"Error en apply_transformations: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def save_widget_config(self, doc_name: str, widget_config: Dict) -> Dict:
        # Guarda configuración de widget con su data mapper config
        try:
            doc = frappe.get_doc('Daltek', doc_name)
            
            # Obtener layout actual
            layout = json.loads(doc.layout or '{"widgets": []}')
            
            # Agregar nuevo widget
            widget_id = f"widget_{len(layout.get('widgets', []))}"
            widget_config['id'] = widget_id
            
            layout.setdefault('widgets', []).append(widget_config)
            
            # Guardar
            doc.layout = json.dumps(layout)
            doc.save()
            
            return {
                'success': True,
                'widget_id': widget_id,
                'message': 'Widget guardado correctamente'
            }
            
        except Exception as e:
            frappe.log_error(f"Error en save_widget_config: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def upload_data(self, doc_name: str, data: List[Dict], source: str) -> Dict:
        # Sube datos desde frontend (CSV, Excel, JSON, etc)
        try:
            # Validar datos
            if not data or len(data) == 0:
                return {'success': False, 'error': 'No hay datos para subir'}
            
            # Crear metadata
            metadata = {
                'source': source,
                'uploaded_at': frappe.utils.now(),
                'uploaded_by': frappe.session.user,
                'row_count': len(data),
                'columns': list(data[0].keys()) if data else []
            }
            
            # Guardar en DocType o tabla temporal
            # Aquí puedes implementar lógica de persistencia
            
            return {
                'success': True,
                'data_id': f"upload_{frappe.utils.now_datetime().timestamp()}",
                'metadata': metadata,
                'message': f'{len(data)} registros subidos correctamente'
            }
            
        except Exception as e:
            frappe.log_error(f"Error en upload_data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def filter_data(self, data: List[Dict], filters: List[Dict]) -> Dict:
        # Aplica filtros a los datos
        try:
            from ..data_mapper.pandas_transformer import PandasTransformer
            
            transformer = PandasTransformer()
            df = transformer.load_data(data)
            
            # Aplicar cada filtro
            for filter_config in filters:
                conditions = [{
                    'column': filter_config['column'],
                    'operator': filter_config['operator'],
                    'value': filter_config['value']
                }]
                df = transformer.filter(df, conditions)
            
            filtered_data = df.to_dict('records')
            
            return {
                'success': True,
                'data': filtered_data,
                'original_count': len(data),
                'filtered_count': len(filtered_data),
                'filters_applied': len(filters)
            }
            
        except Exception as e:
            frappe.log_error(f"Error en filter_data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def aggregate_data(self, data: List[Dict], group_by: List[str], aggregations: Dict) -> Dict:
        # Agrupa y agrega datos
        try:
            from ..data_mapper.pandas_transformer import PandasTransformer
            
            transformer = PandasTransformer()
            df = transformer.load_data(data)
            
            config = {
                'group_by': group_by,
                'aggregations': aggregations
            }
            
            result_df = transformer.aggregate(df, config)
            aggregated_data = result_df.to_dict('records')
            
            return {
                'success': True,
                'data': aggregated_data,
                'original_count': len(data),
                'grouped_count': len(aggregated_data),
                'group_by': group_by
            }
            
        except Exception as e:
            frappe.log_error(f"Error en aggregate_data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def preview_widget(self, data: List[Dict], widget_type: str, widget_config: Dict) -> Dict:
        # Genera preview de cómo se verá el widget con los datos
        try:
            from ..data_mapper.widget_data_adapter import WidgetDataAdapter
            from ..data_mapper.pandas_transformer import PandasTransformer
            
            transformer = PandasTransformer()
            df = transformer.load_data(data)
            
            adapter = WidgetDataAdapter()
            
            # Generar datos según tipo de widget
            if widget_type == 'echart':
                chart_type = widget_config.get('chart_type', 'line')
                x_axis = widget_config.get('x_axis')
                y_axes = widget_config.get('y_axes', [])
                
                widget_data = adapter.to_echart_format(df, chart_type, x_axis, y_axes)
                
            elif widget_type == 'table':
                columns = widget_config.get('columns')
                widget_data = adapter.to_table_format(df, columns)
                
            elif widget_type == 'card':
                metric_config = widget_config.get('metric_config', {})
                widget_data = adapter.to_card_format(df, metric_config)
                
            else:
                return {'success': False, 'error': f'Tipo de widget no soportado: {widget_type}'}
            
            return {
                'success': True,
                'widget_type': widget_type,
                'widget_data': widget_data,
                'data_count': len(data)
            }
            
        except Exception as e:
            frappe.log_error(f"Error en preview_widget: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def validate_config(self, config: Dict, data_columns: List[Dict]) -> Dict:
        # Valida que la configuración sea correcta
        try:
            validation = self.mapper_service.validate_mapping(config, data_columns)
            return validation
            
        except Exception as e:
            frappe.log_error(f"Error en validate_config: {str(e)}")
            return {'is_valid': False, 'errors': [str(e)], 'warnings': []}
    
    def get_column_stats(self, data: List[Dict], column: str) -> Dict:
        # Obtiene estadísticas de una columna
        try:
            from ..data_mapper.pandas_transformer import PandasTransformer
            
            transformer = PandasTransformer()
            df = transformer.load_data(data)
            
            if column not in df.columns:
                return {'success': False, 'error': f'Columna {column} no existe'}
            
            col_data = df[column]
            
            stats = {
                'column': column,
                'count': len(col_data),
                'null_count': col_data.isna().sum(),
                'unique_count': col_data.nunique()
            }
            
            # Estadísticas numéricas
            if col_data.dtype in ['int64', 'float64']:
                stats['type'] = 'numeric'
                stats['min'] = float(col_data.min())
                stats['max'] = float(col_data.max())
                stats['mean'] = float(col_data.mean())
                stats['median'] = float(col_data.median())
                stats['std'] = float(col_data.std())
            else:
                stats['type'] = 'text'
                stats['sample_values'] = col_data.value_counts().head(10).to_dict()
            
            return {
                'success': True,
                'stats': stats
            }
            
        except Exception as e:
            frappe.log_error(f"Error en get_column_stats: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # Métodos privados helper
    
    def _extract_columns(self, data: List[Dict]) -> List[Dict]:
        # Extrae metadata de columnas de los datos
        if not data:
            return []
        
        return self.mapper_service.get_column_metadata(data)
    
    def _build_mapper_config(self, config: Dict) -> Dict:
        # Construye configuración completa para el Data Mapper
        return {
            'transformations': config.get('transformations', {}),
            'widget_mapping': config.get('widget_mapping', {})
        }
