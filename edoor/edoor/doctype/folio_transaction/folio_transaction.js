// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Folio Transaction", {
	onload(frm) {
        
        
	},
    setup(frm) {
        for (const key in frm.fields_dict) {
          if (
            [
              "Currency",
              "Data",
              "Int",
              "Link",
              "Date",
              "Datetime",
              "Float",
              "Select",
            ].includes(frm.fields_dict[key].df.fieldtype)
          ) {
            frm.fields_dict[key].$wrapper.addClass("custom_control");
          }
        }
      },
});
