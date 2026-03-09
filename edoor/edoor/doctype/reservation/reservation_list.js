frappe.listview_settings['Reservation'] = {
    add_fields: ['reservation_status', 'status_color'],
    onload: function(listview) {
        if(frappe.session.user!="Administrator"){
          listview.page.btn_primary.hide();
            listview.page.actions.find('a:contains("Delete")').hide();
            listview.page.actions.find('a:contains("Edit")').hide();
            

        }
          
      },
      
    get_indicator(doc) { 

        return  [`<span style="font-size: 12px;background-color:${doc.status_color}; color:#FFF; padding: 5px 10px;border-radius: 10px;">${__(doc.reservation_status)}</span>`]; 
        
    },
}
