frappe.listview_settings['Business Source'] = {
    onload: function(listview) {
        
        listview.page.add_inner_button(__('Update Business Source to Transaction'), function() {
            
            frappe.confirm(
                'Are you sure you want to update business information to transaction?',
                function(){
                    frappe.call('edoor.edoor_configuration.doctype.business_source.business_source.update_to_transaction');
                    
                    
                },
                
            )
        });

        

    }
};