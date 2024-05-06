frappe.listview_settings['Reservation Folio'] = {
    add_fields: ['tax_invoice_type'],
    // set this to true to apply indicator function on draft documents too


    get_indicator(doc) {
           
    if(doc.tax_invoice_type=='Tax Invoice'){ 
        return [__("Tax Invoice"), "green"];
    }else if(doc.tax_invoice_type=='Commercial Invoice') {
        return [__("Commercial Invoice"), "orange"];
    }
        
    },
    
}

 