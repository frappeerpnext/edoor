// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Reservation Folio", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Reservation Folio", {
    	refresh(frm) {

            set_indicator(frm);
    
    	},
    });

    function set_indicator(frm){
        if(frm.doc.__islocal)
                return;

        if (frm.doc.total_debit > 0 )  frm.dashboard.add_indicator(__("Total Debit: {0}",[format_currency(frm.doc.total_debit)]) ,"gray");
        if (frm.doc.total_credit > 0 )  frm.dashboard.add_indicator(__("Total Credit: {0}",[format_currency(frm.doc.total_credit)]) ,"pink");
        if (frm.doc.balance )  frm.dashboard.add_indicator(__("Balance: {0}",[format_currency(frm.doc.balance)]) ,"blue");
    }