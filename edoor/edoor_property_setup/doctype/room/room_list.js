frappe.listview_settings['Room'] = {
    onload: function(listview) {
        listview.page.add_inner_button(__('Sort Order Room'), function() {
            let msg = frappe.msgprint(
                '<iframe src="/frontdesk/room-sort-order" frameBorder="0" width="100%" height="650" title="Sort Order Account Code"></iframe>',
                'Sort Order Room'
            );
            msg.$wrapper.find('.modal-dialog').css("max-width", "90%");
        });
    },
    add_fields: ['status_color', 'housekeeping_status'],
    hide_name_column: false, // hide the last column which shows the `name`
    // set this to true to apply indicator function on draft documents too
    get_indicator(doc) {
        
        if(doc.disabled==0){
            return [__("Enabled"), "blue"];
        }else{
            return [__("Disabled"), "gray"];
        }
    },

    formatters: {
        
        housekeeping_status: function(value, field, doc) {
             
            return "<div style='background: " + doc.status_color + ";padding: 4px;border-radius: 11px;text-align: center;'>"  + value + "</div>"
          
        },
        
    }
   
    
}
