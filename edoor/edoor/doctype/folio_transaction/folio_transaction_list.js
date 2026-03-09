frappe.listview_settings['Folio Transaction'] = {
    add_fields: ['transaction_type',"is_auto_post","total_amount","account_code","account_name","reservation_stay"],
    get_indicator(doc) {
        if (doc.transaction_type=='Reservation Folio' ) {
            return [__("Guest Folio"), "orange"];
        } else if (doc.transaction_type=='Cashier Shift' ) {
            return [__("F&B"), "yellow"];
        } else {
            return [__(doc.transaction_type), "blue"];
        }
    },
}


if (frappe.is_mobile()){
    frappe.views.ListView = class ListView extends frappe.views.ListView {

    get_mobile_row(left = "", doc) { 
        if (this.doctype === "Folio Transaction") {
            return frappe.render_template("mobile_list_view_row_template",{left:left,doc:doc,modified:comment_when(doc.modified,true)})           
        }
	}
    get_list_row_html(doc) {
      
		return this.get_mobile_row(
			this.get_left_html(doc),
			doc
		);
	}
}

document.querySelector('style').textContent +=
    `@media (min-width: 768px) { 
        .list-row-container .details-row { display: none; }
    }
    .list-row-container .details-row {
        color: #666;
        padding: 0 0 0 40px !important;
    }
    `
}