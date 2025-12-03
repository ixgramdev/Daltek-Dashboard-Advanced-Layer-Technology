frappe.listview_settings["Daltek"] = {
  onload(listview) {
    // Interceptar el método make_new_doc SOLO UNA VEZ
    if (!listview._daltek_intercepted) {
      listview._daltek_intercepted = true;

      const original_make_new_doc = listview.make_new_doc.bind(listview);
      listview.make_new_doc = function () {
        show_daltek_creation_dialog(listview);
        return false;
      };
    }
  },
};

function show_daltek_creation_dialog(listview) {
  frappe.prompt(
    [
      {
        fieldname: "name1",
        fieldtype: "Data",
        label: __("Dashboard Name"),
        reqd: 1,
        description: __("Enter a unique name for your dashboard"),
      },
    ],
    function (values) {
      frappe.call({
        method: "frappe.client.insert",
        args: {
          doc: {
            doctype: "Daltek",
            name1: values.name1,
            dashboard_owner: frappe.session.user,
          },
        },
        callback(r) {
          if (r.message) {
            if (listview && listview.refresh) {
              listview.refresh();
            }

            frappe.set_route("Form", "Daltek", r.message.name);
            frappe.show_alert({
              message: __("Dashboard '{0}' created successfully", [
                values.name1,
              ]),
              indicator: "green",
            });
          }
        },
        error(r) {
          frappe.msgprint({
            title: __("Error"),
            indicator: "red",
            message:
              r.message || __("Could not create dashboard. Please try again."),
          });
        },
      });
    },
    __("Create New Dashboard"),
    __("Create"),
  );
}
