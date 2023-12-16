frappe.listview_settings['Daily Property Data'] = {
    onload: function (listview) {
        // Add a button for doing something useful.
        listview.page.add_inner_button(__("Generate Property Data"), function () {
            let d = new frappe.ui.Dialog({
                title: 'Generate Date',
                fields: [
                    {
                        label: 'Please select property',
                        fieldname: 'property',
                        fieldtype: 'Link',
                        options:"Business Branch"

                    },
                ],
                primary_action_label: 'Save',
                    primary_action(values) {
                        frappe.call({
                            method: "edoor.edoor_configuration.doctype.daily_property_data.daily_property_data.generate_property_data",
                            args: {
                                property:values.property
                            },
                            freeze: true,
                            callback: function(r){
                                d.hide();
                            },
                            error: function(r) {
                                frappe.throw(r.message)
                                
                            },
                        });	
                    
                }
            });
            
            d.show();
        })
        
        // The .addClass above is optional.  It just adds styles to the button.
    }
}