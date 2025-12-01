"""
EChart Services: Gestión centralizada de gráficos ECharts.

Módulos:
- base_echart_builder: Clase abstracta base para todos los builders
- echart_builders: Implementaciones específicas (Line, Bar, Pie, Scatter)
- echart_factory: Factory para crear builders según tipo
- echart_transformer: Transforma configuraciones para renderización
"""

from .base_echart_builder import BaseEChartBuilder
from .echart_builder import (
    BarChartBuilder,
    LineChartBuilder,
    PieChartBuilder,
    ScatterChartBuilder,
)
from .echart_factory import EChartFactory
from .echart_transforrmer import EChartTransformer

__all__ = [
    "BaseEChartBuilder",
    "LineChartBuilder",
    "BarChartBuilder",
    "PieChartBuilder",
    "ScatterChartBuilder",
    "EChartFactory",
    "EChartTransformer",
]
