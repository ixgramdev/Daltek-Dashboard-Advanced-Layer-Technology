from typing import Any


class QueryValidator:
    """Validaciones centralizadas para los datos de consultas.

    Esta clase NO conoce nada de Frappe ni de persistencia; solo valida
    la estructura y reglas de negocio básicas de una consulta.
    """

    REQUIRED_FIELDS = ["name"]

    def validate_query(self, query: dict[str, Any]) -> dict[str, Any]:
        """Valida una única consulta.

        Retorna un dict con:
            - valid: bool
            - errors: list[str]
        """

        errors: list[str] = []

        # Campos requeridos simples
        for field in self.REQUIRED_FIELDS:
            if not query.get(field):
                errors.append(f"Campo requerido faltante o vacío: '{field}'")

        # Validar tipo básico de estructura (opcional, ampliable)
        params = query.get("params")
        if params is not None and not isinstance(params, (dict, list)):
            errors.append("El campo 'params' debe ser dict o list si se proporciona")

        return {"valid": len(errors) == 0, "errors": errors}

    def validate_batch(self, queries: list[dict[str, Any]]) -> dict[str, Any]:
        """Valida múltiples consultas a la vez.

        Útil si en algún momento quieres validar colecciones completas
        (por ejemplo antes de un guardado masivo).
        """

        all_errors: list[dict[str, Any]] = []
        valid_queries: list[dict[str, Any]] = []

        for index, query in enumerate(queries):
            result = self.validate_query(query)
            if not result["valid"]:
                all_errors.append(
                    {
                        "index": index,
                        "name": query.get("name"),
                        "errors": result["errors"],
                    }
                )
            else:
                valid_queries.append(query)

        return {
            "valid": len(all_errors) == 0,
            "errors": all_errors,
            "valid_queries": valid_queries,
            "total": len(queries),
            "valid_count": len(valid_queries),
        }
