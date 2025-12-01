"""
Data Mapper Module
Capa de transformación entre Queries y Widgets
"""

from .data_mapper_service import DataMapperService
from .pandas_transformer import PandasTransformer
from .widget_data_adapter import WidgetDataAdapter
from .mapping_validator import MappingValidator

__all__ = [
    "DataMapperService",
    "PandasTransformer",
    "WidgetDataAdapter",
    "MappingValidator",
]
