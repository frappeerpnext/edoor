// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Folio Transaction", {
	onload(frm) {
        frm.set_query("discount_account", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });

        frm.set_query("bank_fee_account", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        
        frm.set_query("account_group", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        frm.set_query("tax_1_account", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        frm.set_query("tax_2_account", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        frm.set_query("tax_3_account", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        frm.set_query("account_code", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        frm.set_query("parent_account_code", function() {
            return {
                filters: [["is_group","=",0]]
            }
        });
        
	},
});
