import json
from typing import Any

import frappe

from .query_builder import QueryBuilder
from .query_repository import QueryRepository
from .query_validator import QueryValidator


class QueryService:
    def __init__(self):
        self.repository = QueryRepository()
        self.validator = QueryValidator()

    # --- CRUD ---

    @frappe.whitelist()
    def save(
        self, doc_name: str, query_json: str | dict, auto_commit: bool = True
    ) -> dict[str, Any]:
        """
        Guarda una nueva consulta en el campo JSON.

        Args:
            doc_name: Nombre del documento Daltek
            query_json: Datos de la consulta (string JSON o dict)
            auto_commit: Si es True, hace commit automáticamente (default: True)

        Returns:
            Dict con success, message, queries y saved_query
        """
        try:
            query_data = (
                json.loads(query_json) if isinstance(query_json, str) else query_json
            )
            # Validación estructural mediante QueryValidator
            validation = self.validator.validate_query(query_data)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "; ".join(validation["errors"]),
                }

            queries = self.repository.get_queries(doc_name)

            if not query_data.get("id"):
                query_data["id"] = self._generate_query_id(queries)

            if not query_data.get("created_at"):
                query_data["created_at"] = frappe.utils.now_datetime().isoformat()

            query_data["modified_at"] = frappe.utils.now_datetime().isoformat()

            queries.append(query_data)

            # Guardado directo mediante el repositorio
            self.repository.save_queries(doc_name, queries, auto_commit=auto_commit)

            return {
                "success": True,
                "message": f"Consulta '{query_data['name']}' guardada correctamente",
                "queries": queries,
                "saved_query": query_data,
            }

        except Exception as e:
            frappe.log_error(f"Error en save(): {str(e)}", "QueryService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def edit(
        self,
        doc_name: str,
        query_id: str,
        query_json: str | dict,
        auto_commit: bool = True,
    ) -> dict[str, Any]:
        """
        Edita una consulta existente.

        Args:
            doc_name: Nombre del documento Daltek
            query_id: ID de la consulta a editar
            query_json: Nuevos datos de la consulta (string JSON o dict)
            auto_commit: Si es True, hace commit automáticamente (default: True)

        Returns:
            Dict con success, message, queries y saved_query
        """
        try:
            query_data = (
                json.loads(query_json) if isinstance(query_json, str) else query_json
            )
            queries = self.repository.get_queries(doc_name)

            index = None
            for i, q in enumerate(queries):
                if q.get("id") == query_id:
                    index = i
                    break

            if index is None:
                return {
                    "success": False,
                    "error": f"Consulta con ID '{query_id}' no encontrada",
                }

            query_data["id"] = query_id
            query_data["created_at"] = queries[index].get("created_at")
            query_data["modified_at"] = frappe.utils.now_datetime().isoformat()

            queries[index] = query_data

            # Guardado directo mediante el repositorio
            self.repository.save_queries(doc_name, queries, auto_commit=auto_commit)

            return {
                "success": True,
                "message": f"Consulta '{query_data['name']}' actualizada correctamente",
                "queries": queries,
                "saved_query": query_data,
            }

        except Exception as e:
            frappe.log_error(f"Error en edit(): {str(e)}", "QueryService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def delete(
        self, doc_name: str, query_id: str, auto_commit: bool = True
    ) -> dict[str, Any]:
        """
        Elimina una consulta del documento.

        Args:
            doc_name: Nombre del documento Daltek
            query_id: ID de la consulta a eliminar
            auto_commit: Si es True, hace commit automáticamente (default: True)

        Returns:
            Dict con success, message y queries actualizadas
        """
        try:
            queries = self.repository.get_queries(doc_name)
            filtered = [q for q in queries if q.get("id") != query_id]

            if len(filtered) == len(queries):
                return {
                    "success": False,
                    "error": f"Consulta con ID '{query_id}' no encontrada",
                }

            # Guardado directo mediante el repositorio
            self.repository.save_queries(doc_name, filtered, auto_commit=auto_commit)

            return {
                "success": True,
                "message": "Consulta eliminada correctamente",
                "queries": filtered,
            }

        except Exception as e:
            frappe.log_error(f"Error en delete(): {str(e)}", "QueryService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def get(self, doc_name: str, query_id: str) -> dict[str, Any]:
        try:
            queries = self.repository.get_queries(doc_name)

            for q in queries:
                if q.get("id") == query_id:
                    return {"success": True, "query": q}

            return {"success": False, "error": f"Consulta '{query_id}' no encontrada"}

        except Exception as e:
            frappe.log_error(f"Error en get(): {str(e)}", "QueryService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def get_all(self, doc_name: str) -> dict[str, Any]:
        queries = self.repository.get_queries(doc_name)
        return {"success": True, "queries": queries, "count": len(queries)}

    def _generate_query_id(self, queries: list[dict]) -> str:
        """
        Genera un ID único para una nueva consulta.
        Usa timestamp + contador para garantizar unicidad.

        Args:
            queries: Lista de consultas existentes

        Returns:
            ID único para la consulta
        """
        import time

        timestamp = int(time.time() * 1000)
        existing_ids = [q.get("id") for q in queries if q.get("id")]

        # Si hay IDs numéricos, usar el siguiente número
        numeric_ids = []
        for qid in existing_ids:
            try:
                numeric_ids.append(int(str(qid).split("_")[0]))
            except (ValueError, IndexError):
                pass

        next_num = max(numeric_ids) + 1 if numeric_ids else len(queries) + 1
        return f"{next_num}_{timestamp}"

    @frappe.whitelist()
    def auto_save(
        self, doc_name: str, query_id: str, query_json: str | dict
    ) -> dict[str, Any]:
        """
        Auto-guardado silencioso sin commit para no interrumpir el flujo del cliente.
        Útil para guardar cambios incrementales mientras el usuario edita.

        Args:
            doc_name: Nombre del documento Daltek
            query_id: ID de la consulta (puede ser None para nuevas queries)
            query_json: Datos de la consulta (string JSON o dict)

        Returns:
            Dict con success, message y saved_query
        """
        try:
            # Si no hay query_id, guardar como nueva
            if not query_id or query_id == "null" or query_id == "undefined":
                return self.save(doc_name, query_json, auto_commit=False)

            # Si hay query_id, actualizar existente
            return self.edit(doc_name, query_id, query_json, auto_commit=False)

        except Exception as e:
            frappe.log_error(f"Error en auto_save(): {str(e)}", "QueryService Error")
            return {"success": False, "error": str(e)}

    @frappe.whitelist()
    def execute(self, doc_name: str, query_id: str) -> dict[str, Any]:
        """
        Ejecuta una consulta guardada en el documento Daltek.
        Obtiene la consulta por ID, construye el SQL y ejecuta.

        Args:
            doc_name: Nombre del documento Daltek
            query_id: ID de la consulta a ejecutar

        Returns:
            Dict con success, results y metadata
        """
        try:
            # Validar documento
            if not frappe.db.exists("Daltek", doc_name):
                return {
                    "success": False,
                    "error": f"Documento Daltek '{doc_name}' no existe",
                }

            # Obtener la consulta
            query_result = self.get(doc_name, query_id)

            if not query_result.get("success"):
                return query_result

            query_data = query_result.get("query")

            # Construir el SQL desde el JSON de la consulta
            # La consulta guardada tiene: {id, name, doctype, columns, filters, description}
            # Necesitamos transformarlo al formato que espera QueryBuilder
            query_json = {
                "select": query_data.get("columns", ["*"]),
                "from": query_data.get("doctype"),
                "where": [],
            }

            # Transformar filtros al formato de QueryBuilder
            filters = query_data.get("filters", [])
            for f in filters:
                query_json["where"].append(
                    {
                        "field": f.get("col") or f.get("field"),
                        "operator": f.get("op") or f.get("operator"),
                        "value": f.get("val") or f.get("value"),
                    }
                )

            # Construir y ejecutar SQL
            builder = QueryBuilder(query_json)
            sql = builder.build()

            # Ejecutar consulta
            results = frappe.db.sql(sql, as_dict=True)

            return {
                "success": True,
                "query_id": query_id,
                "query_name": query_data.get("name"),
                "sql": sql,
                "results": results,
                "count": len(results),
            }

        except Exception as e:
            frappe.log_error(f"Error en execute(): {str(e)}", "QueryService Error")
            return {"success": False, "error": str(e)}
