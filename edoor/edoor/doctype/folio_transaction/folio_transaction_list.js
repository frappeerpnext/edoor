frappe.listview_settings['Folio Transaction'] = {
    add_fields: ['transaction_type'],
    get_indicator(doc) {
        
        if (doc.transaction_type=='Reservation Folio' ) {
            return [__("Guest Folio"), "orange"];
        } else {
            return [__(doc.transaction_type), "blue"];
        }
    },
}