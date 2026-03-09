// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rate Type", {
	refresh(frm) {
        frm.set_query("account_code", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
	},
});
