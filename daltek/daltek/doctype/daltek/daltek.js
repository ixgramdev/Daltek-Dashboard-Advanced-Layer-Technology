// daltek.js
frappe.ui.form.on("Daltek", {
    onload(frm) {
        if (!frm.drag_drop_initialized) {
            frm.drag_drop_initialized = true;
            frappe.require("/assets/daltek/js/widgets.js", function() {
                console.log("Widgets cargados:", availableWidgets);
                init_drag_drop_view(frm);
            });
        }
    }
});

function init_drag_drop_view(frm) {
    const wrapper = frm.fields_dict['drag_drop_html'].wrapper;
    wrapper.innerHTML = ''; // limpiar contenido previo

    const layout = document.createElement('div');
    layout.style.display = 'flex';
    layout.style.height = '600px';

    // Canvas principal
    const canvas = document.createElement('div');
    canvas.id = 'canvas';
    canvas.style.flex = '1';
    canvas.style.padding = '10px';
    canvas.style.background = '#171717';

    // Panel lateral con mini-previews
    const sidebar = document.createElement('div');
    sidebar.id = 'widget-menu';
    sidebar.style.width = '200px';
    sidebar.style.borderLeft = '1px solid #ddd';
    sidebar.style.padding = '10px';
    sidebar.innerHTML = '<h5>Dashboard Widgets</h5>';

    layout.appendChild(canvas);
    layout.appendChild(sidebar);
    wrapper.appendChild(layout);

    // Inicializar GridStack en el canvas
    const grid = GridStack.init({
        column: 12,
        cellHeight: 80,
        verticalMargin: 10,
        disableOneColumnMode: true,
    }, '#canvas');

    syncLayoutWithGridStack(frm, grid);

    // Cargar widgets en el menú lateral
    window.availableWidgets.forEach(widget => {
        const widgetItem = document.createElement('div');
        widgetItem.innerHTML = widget.previewHtml;
        widgetItem.draggable = true;
        widgetItem.style.marginBottom = '10px';

        // --- EVENTO DE ARRASTRE MANUAL (ghost) ---
        widgetItem.addEventListener('mousedown', e => {
            e.preventDefault();

            const ghost = widgetItem.cloneNode(true);
            ghost.style.position = 'absolute';
            ghost.style.pointerEvents = 'none';
            ghost.style.opacity = '0.8';
            ghost.style.zIndex = 9999;
            ghost.style.left = e.pageX + 'px';
            ghost.style.top = e.pageY + 'px';
            document.body.appendChild(ghost);

            const onMouseMove = moveEvent => {
                const ghostWidth = ghost.offsetWidth;
                const ghostHeight = ghost.offsetHeight;

                ghost.style.left = (moveEvent.pageX - ghostWidth / 2) + 'px';
                ghost.style.top = (moveEvent.pageY - ghostHeight / 2) + 'px';
            };

            const onMouseUp = upEvent => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                document.body.removeChild(ghost);

                const canvasRect = canvas.getBoundingClientRect();
                if (
                    upEvent.clientX >= canvasRect.left &&
                    upEvent.clientX <= canvasRect.right &&
                    upEvent.clientY >= canvasRect.top &&
                    upEvent.clientY <= canvasRect.bottom
                ) {
                    placeWidgetInGrid(frm, grid, widget, upEvent);
                }
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        sidebar.appendChild(widgetItem);
    });

    // Renderizar widgets existentes desde layout_json
    render_widgets_from_json(frm, grid);
}

/**
 * Coloca un widget dentro del GridStack según la posición del mouse.
 */
function placeWidgetInGrid(frm, grid, widgetData, mouseEvent) {
    const canvas = document.getElementById('canvas');
    const canvasRect = canvas.getBoundingClientRect();

    // Posición relativa dentro del canvas
    const offsetX = mouseEvent.clientX - canvasRect.left;
    const offsetY = mouseEvent.clientY - canvasRect.top;

    // Calcular la celda del grid
    const cellWidth = canvas.offsetWidth / grid.getColumn();
    const cellHeight = grid.getCellHeight();

    const col = Math.floor(offsetX / cellWidth);
    const row = Math.floor(offsetY / cellHeight);

    // Crear el widget en la posición calculada
    add_widget_instance(frm, grid, widgetData, { x: col, y: row });
}

/**
 * Crea una instancia del widget en el grid.
 */
function add_widget_instance(frm, grid, widgetData, pos = { x: 0, y: 0 }) {
    const id = widgetData.id + '_' + Date.now();

    const node = document.createElement('div');
    node.className = 'grid-stack-item';
    node.dataset.id = id;
    node.dataset.type = widgetData.type;
    node.innerHTML = `
        <div class="grid-stack-item-content" style="padding:10px;background:${widgetData.options.color};border-radius:8px;">
            <h5 style="font-size:12px;color:white;">${widgetData.options.title}</h5>
            <span style="font-size:24px;color:white;">${widgetData.options.number || 0}</span>
            <button style="border-radius:50%;width:24px;height:24px;">⚙</button>
        </div>
    `;

    // Añadir al grid
    grid.addWidget(node, { x: pos.x, y: pos.y, w: 4, h: 3 });

    // Guardar en layout_json
    const currentWidgets = frm.doc.layout_json || [];
    currentWidgets.push({
        id: widgetData.id,
        type: widgetData.type,
        position: { col: pos.x, row: pos.y, width: 4, height: 3 },
        properties: { ...widgetData.options }
    });
    frm.set_value('layout_json', currentWidgets);

    // Botón de configuración
    node.querySelector('button').addEventListener('click', () => {
        openPropertyPanel(frm, node);
    });
}

/**
 * Sincroniza los cambios del grid con layout_json.
 */
function syncLayoutWithGridStack(frm, grid) {
    grid.on('change', function(event, items) {
        const updatedWidgets = items.map(item => {
            const original = frm.doc.layout_json.find(w => w.id === item.el.dataset.id);
            return {
                id: original.id,
                type: original.type,
                position: { col: item.x, row: item.y, width: item.w, height: item.h },
                properties: { ...original.properties }
            };
        });
        frm.set_value('layout_json', updatedWidgets);
    });
}

/**
 * Renderiza los widgets guardados en layout_json.
 */
function render_widgets_from_json(frm, grid) {
    const widgets = frm.doc.layout_json || [];
    widgets.forEach(widget => {
        const id = widget.id + '_' + Date.now();

        const node = document.createElement('div');
        node.className = 'grid-stack-item';
        node.dataset.id = id;
        node.dataset.type = widget.type;
        node.innerHTML = `
            <div class="grid-stack-item-content" style="padding:10px;background:${widget.properties.color};border-radius:8px;">
                <h5 style="font-size:12px;color:white;">${widget.properties.title}</h5>
                <span style="font-size:24px;color:white;">${widget.properties.number || 0}</span>
                <button style="border-radius:50%;width:24px;height:24px;">⚙</button>
            </div>
        `;

        grid.addWidget(node, widget.position);

        node.querySelector('button').addEventListener('click', () => {
            openPropertyPanel(frm, node);
        });
    });
}

/**
 * Panel de propiedades simple para renombrar un widget.
 */
function openPropertyPanel(frm, widgetDiv) {
    const widgets = frm.doc.layout_json || [];
    const instance = widgets.find(w => widgetDiv.dataset.id === w.id);

    if (!instance) return;

    const newTitle = prompt("Nuevo título:", instance.properties.title);
    if (newTitle !== null) {
        instance.properties.title = newTitle;
        widgetDiv.querySelector('h5').textContent = newTitle;
        frm.set_value('layout_json', widgets);
    }
}
