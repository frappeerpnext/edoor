// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("City Ledger", {
	refresh(frm) { 
        if (!frm.doc.__islocal) {
            frm.dashboard.add_indicator(__("Total Debit: {0}", [format_currency(frm.doc.total_debit)]), "blue");
            frm.dashboard.add_indicator(__("Total Credit: {0}", [format_currency(frm.doc.total_credit)]), "blue");
            frm.dashboard.add_indicator(__("Balance: {0}", [format_currency(frm.doc.balance)]), "blue");
        }
	},
});
