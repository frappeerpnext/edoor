frappe.listview_settings['Reservation Stay'] = {
    add_fields: ['reservation_status', 'status_color'],
    get_indicator(doc) { 

        return  [`<span style="font-size: 12px;background-color:${doc.status_color}; color:#FFF; padding: 5px 10px;border-radius: 10px;">${__(doc.reservation_status)}</span>`]; 
        
    },
}
