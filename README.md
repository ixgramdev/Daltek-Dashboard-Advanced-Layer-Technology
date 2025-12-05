# Daltek

Mini-suite para dashboards personalizables y un Query Builder integrado en ERPNext.

Visión general
Daltek aporta una capa avanzada para crear y mostrar dashboards interactivos (drag & drop) y construir consultas mediante un Query Builder visual. Está pensado como una app para instalar en un bench de ERPNext y extender la experiencia de reportes y visualización.

Características
- Query Builder: interfaz para componer y ejecutar consultas.
- Drag & Drop: paneles personalizables con GridStack y widgets reutilizables.
- Frontend modular en `public/js`, integración desde el doctype `daltek`.

Contrato mínimo (qué hace la app)
- Entrada: consultas/definiciones de widgets y datos desde ERPNext.
- Salida: páginas HTML/JS que renderizan dashboards y resultados de consultas.
- Errores: si faltan permisos o el sitio no está migrado, el frontend mostrará errores; revisa logs y consola.

Instalación rápida (bench)

Nota: ejecuta estos comandos desde la carpeta raíz de tu bench (p. ej. `frappe-bench`).

1) Colocar el código en `apps/daltek` (si ya está, omitir):

```bash
# desde la carpeta frappe-bench
# bench get-app git@github.com:ixgramdev/Daltek-Dashboard-Advanced-Layer-Technology.git  // Clave SSH
# bench get-app https://github.com/ixgramdev/Daltek-Dashboard-Advanced-Layer-Technology.git // Clave HTTPS
```

2) Instalar la app en tu sitio:

- Si conoces el nombre del sitio (recomendado):

```bash
bench --site NOMBRE_DEL_SITIO install-app daltek
bench --site NOMBRE_DEL_SITIO migrate
```

- Si tu bench tiene un sitio por defecto configurado, puedes omitir `--site` y usar los comandos globales:

```bash
bench install-app daltek
```

- Registrar los cambios en el contenedor (Comandos Globales):

```bash
bench migrate
bench restart
```

- Para ver los sitios existentes (desde la raíz del bench):

```bash
ls sites
```

- Para establecer o cambiar el sitio por defecto (opcional):

```bash
bench set-default-site NOMBRE_DEL_SITIO
```

Notas sobre la condición de uso de comandos
- Si usas `bench` sin `--site`, los comandos afectarán al sitio por defecto configurado en el bench. Si no hay sitio por defecto, algunos comandos fallarán o pedirán especificar `--site`.
- Recomendación: cuando tengas varios sitios, siempre usa `--site NOMBRE_DEL_SITIO` para evitar cambios accidentales.

Uso rápido después de instalar
- Abre la interfaz de ERPNext y busca el Doctype/Desk relacionado con `Daltek` (o accede a la ruta donde la app inyecta su UI). Los módulos principales (Query Builder y Drag & Drop) estarán disponibles según permisos de usuario.

Archivos principales
- `daltek/daltek/doctype/daltek/daltek.py` — endpoints Python / render HTML
- `daltek/daltek/doctype/daltek/daltek.js` — integración cliente/doctype
- `daltek/public/js/query_builder/` — lógica UI del Query Builder
- `daltek/public/js/drag_and_drop/` — lógica drag & drop y widgets
- `INFORME_QUERY_BUILDER.md`, `INFORME_DRAG_DROP.md` — documentación técnica

## 📚 Documentación Importante

### Widget Configuration Modal
- **README_WIDGET_CONFIG.md** — Guía rápida del modal de configuración de widgets
- **INDICE_GLOBAL_WIDGET_CONFIG.md** — Índice completo de la funcionalidad

### Layouts Separados por Documento (✅ Resuelto)
- **INDICE_LAYOUTS_SEPARADOS.md** — Índice principal de la solución
- **SOLUCION_LAYOUTS_SEPARADOS.md** — Explicación de la solución y testing
- **VERIFICACION_FINAL_LAYOUTS.md** — Verificación técnica del código
- **ARQUITECTURA_LAYOUTS_SEPARADOS.md** — Diagramas y flujos detallados

**Problema resuelto:** Cada documento Daltek ahora tiene su propio layout separado.
No hay mezcla de widgets entre documentos. Ver `INDICE_LAYOUTS_SEPARADOS.md` para más detalles.

Contribuir / desarrollo
- Clona y trabaja en `apps/daltek`. Añade tests en la carpeta del doctype cuando desarrolles nueva lógica.
- Ejecuta `bench migrate` después de cambios en doctypes o fixtures.

Licencia
- Consulta `license.txt` en la raíz del repositorio para los términos.

Contacto
- Usa el sistema de issues del repositorio para reportar bugs o solicitar mejoras.
