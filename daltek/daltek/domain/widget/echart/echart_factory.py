"""
EChartFactory: Implementa el patrón Factory para crear instancias de builders específicos.

Responsabilidades:
- Registrar los tipos de charts disponibles
- Retornar el builder correcto según el tipo
- Manejar tipos desconocidos con errores descriptivos
"""

from .base_echart_builder import BaseEChartBuilder


class EChartFactory:
    """
    Factory que crea instancias de builders de EChart según su tipo.
    Utiliza el patrón Strategy para permitir diferentes estrategias de construcción.
    """

    # Registry de builders disponibles (se populan con las subclases)
    _builders: dict[str, type[BaseEChartBuilder]] = {}

    @classmethod
    def register(cls, chart_type: str, builder_class: type[BaseEChartBuilder]) -> None:
        """
        Registra un nuevo tipo de chart con su builder correspondiente.

        Args:
            chart_type: Tipo de chart (ej: 'line', 'bar', 'pie')
            builder_class: Clase del builder (debe heredar de BaseEChartBuilder)
        """
        if not issubclass(builder_class, BaseEChartBuilder):
            raise TypeError(
                f"{builder_class.__name__} debe heredar de BaseEChartBuilder"
            )

        cls._builders[chart_type.lower()] = builder_class

    @classmethod
    def create(cls, chart_type: str) -> BaseEChartBuilder | None:
        """
        Crea una instancia del builder para el tipo de chart especificado.

        Args:
            chart_type: Tipo de chart (ej: 'line', 'bar', 'pie')

        Returns:
            Instancia del builder o None si el tipo no existe

        Raises:
            ValueError: Si el tipo de chart no está registrado
        """
        chart_type_lower = chart_type.lower().strip()

        if chart_type_lower not in cls._builders:
            available = ", ".join(sorted(cls._builders.keys()))
            raise ValueError(
                f"Tipo de chart '{chart_type}' no soportado. "
                f"Tipos disponibles: {available}"
            )

        builder_class = cls._builders[chart_type_lower]
        return builder_class()

    @classmethod
    def get_available_types(cls) -> list[str]:
        """
        Retorna lista de tipos de chart disponibles.

        Returns:
            Lista de tipos registrados
        """
        return sorted(list(cls._builders.keys()))

    @classmethod
    def is_registered(cls, chart_type: str) -> bool:
        """
        Verifica si un tipo de chart está registrado.

        Args:
            chart_type: Tipo de chart

        Returns:
            True si está registrado
        """
        return chart_type.lower() in cls._builders

    @classmethod
    def unregister(cls, chart_type: str) -> bool:
        """
        Desregistra un tipo de chart (útil para testing).

        Args:
            chart_type: Tipo de chart

        Returns:
            True si fue desregistrado, False si no existía
        """
        chart_type_lower = chart_type.lower()
        if chart_type_lower in cls._builders:
            del cls._builders[chart_type_lower]
            return True
        return False

    @classmethod
    def reset(cls) -> None:
        """
        Limpia el registro (útil para testing).
        """
        cls._builders.clear()

    @classmethod
    def get_registry(cls) -> dict[str, type[BaseEChartBuilder]]:
        """
        Retorna el diccionario completo de builders registrados.
        Útil para debugging.

        Returns:
            Dict con chart_type -> BuilderClass
        """
        return cls._builders.copy()
