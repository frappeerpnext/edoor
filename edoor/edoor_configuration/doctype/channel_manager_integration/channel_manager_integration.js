// Copyright (c) 2026, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Channel Manager Integration", {
    refresh(frm) {
        frm.add_custom_button("Fetch Property Info", async function () {
            try {
                frappe.dom.freeze("Fetching data...");
                await frm.call("get_property_info"); 
            } catch (error) {
                frappe.msgprint({
                    title: "Error",
                    message: error.message,
                    indicator: "red"
                });
            } finally {
                frappe.dom.unfreeze(); 
            }
        });
    },
});