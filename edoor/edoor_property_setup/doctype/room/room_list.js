frappe.listview_settings['Room'] = {
    add_fields: ['status_color', 'housekeeping_status'],
    hide_name_column: false, // hide the last column which shows the `name`
    // set this to true to apply indicator function on draft documents too
    formatters: {
        
        housekeeping_status: function(value, field, doc) {
             
            return "<div style='background: " + doc.status_color + ";padding: 4px;border-radius: 11px;text-align: center;'>"  + value + "</div>"
          
        },
        
    }
   
    
}
