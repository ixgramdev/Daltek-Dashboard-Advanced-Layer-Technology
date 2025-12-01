"""
DTOs (Data Transfer Objects) para widgets.

Módulo que contiene las clases DTO para transferir datos de widgets
entre capas de la aplicación.
"""

from .echart_widget_dto import EChartWidgetDTO
from .widget_dto import WidgetDTO

__all__ = ["WidgetDTO", "EChartWidgetDTO"]
