frappe.ui.form.on("Daltek", {
  onload(frm) {
    if (!frm.drag_drop_initialized) {
      frm.drag_drop_initialized = true;
      frappe.require("/assets/daltek/js/widgets.js", function () {
        console.log("Widgets cargados:", availableWidgets);
        load_drag_drop_system(frm);
      });
    }
  },

  refresh(frm) {
    toggle_tabs_visibility(frm);

    if (frm.fields_dict.query_builder_html) {
      load_query_builder(frm);
    }
  },

  name1(frm) {
    toggle_tabs_visibility(frm);
  },

  dashboard_owner(frm) {
    toggle_tabs_visibility(frm);
  },
});

function toggle_tabs_visibility(frm) {
  const is_saved = !frm.is_new();
  const has_name = frm.doc.name1 && frm.doc.name1.trim() !== "";
  const has_owner =
    frm.doc.dashboard_owner && frm.doc.dashboard_owner.trim() !== "";

  const should_show_tabs = is_saved && has_name && has_owner;

  const tabs_to_toggle = [
    "editable_menu_tab",
    "query_builder_tab",
    "preview_tab",
  ];

  tabs_to_toggle.forEach((tab_name) => {
    frm.toggle_display(tab_name, should_show_tabs);

    if (tab_name === "editable_menu_tab") {
      frm.toggle_display("editable_menu_html", should_show_tabs);
    } else if (tab_name === "query_builder_tab") {
      frm.toggle_display("query_builder_html", should_show_tabs);
      frm.toggle_display("query_data_storage", should_show_tabs);
    } else if (tab_name === "preview_tab") {
      frm.toggle_display("drag_drop_html", should_show_tabs);
      frm.toggle_display("layout_json", should_show_tabs);
      frm.toggle_display("preview", should_show_tabs);
    }
  });
}

function load_query_builder(frm) {
  frappe.call({
    method: "daltek.daltek.doctype.daltek.daltek.get_query_builder_html",
    callback: function (r) {
      if (r.message) {
        frm.fields_dict.query_builder_html.$wrapper.html(r.message);
      }
    },
    error: function (err) {
      console.error("Error cargando Query Builder:", err);
      frm.fields_dict.query_builder_html.$wrapper.html(
        "<div style='padding: 20px; color: red;'>Error al cargar Query Builder</div>",
      );
    },
  });
}

function load_drag_drop_system(frm) {
  frappe.call({
    method: "daltek.daltek.doctype.daltek.daltek.get_drag_drop_html",
    callback: function (r) {
      if (r.message) {
        frm.fields_dict.drag_drop_html.$wrapper.html(r.message);

        setTimeout(function () {
          if (
            typeof window.initDragDropSystem === "function" &&
            typeof availableWidgets !== "undefined"
          ) {
            console.log(
              "Inicializando sistema Drag and Drop con widgets:",
              availableWidgets,
            );
            window.initDragDropSystem(frm, availableWidgets);
          } else {
            console.error(
              "Sistema Drag and Drop no disponible o widgets no cargados",
            );
          }
        }, 100);
      }
    },
    error: function (err) {
      console.error("Error cargando Drag and Drop:", err);
      frm.fields_dict.drag_drop_html.$wrapper.html(
        "<div style='padding: 20px; color: red;'>Error al cargar Drag and Drop</div>",
      );
    },
  });
}
