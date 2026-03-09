frappe.listview_settings['Room Type'] = {
    onload: function(listview) {
        // update to related transaction
        listview.page.add_inner_button(__('Update to Related Transaction'), function() {
            var d = new frappe.ui.Dialog({
                'fields': [
                    {'fieldname': 'message', 'fieldtype': 'HTML'},
                    {'fieldname': 'option_type', 'label': "Update Option", 'fieldtype': 'Select', 'options': "\nAll\nFuture Transaction Only"}
                ],
                primary_action: function(value){
       
                    if (!value.option_type){
                        frappe.throw("Please select update option type.")
                    }
                    frappe.call("edoor.edoor_property_setup.doctype.room.room.update_to_related_transaction",{"param":value}).then(r=>{
                        d.hide();
                    })
                    
                }
            });
            d.fields_dict.message.$wrapper.html('Do you want to update to all related transaction from the begining or for the future related transaction only?');
            d.show();
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
