// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt


frappe.ui.form.on("Reservation Stay", {
        setup(frm) {

                for (const key in frm.fields_dict) {
                        if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
                                frm.fields_dict[key].$wrapper.addClass('custom_control');
                        }

                }
                
        },
        refresh(frm) {

                set_indicator(frm);
                if (frappe.session.user != "Administrator") {
                        
                        for (const field of frm.meta.fields) {
                                 if(field.fieldtype!="HTML" &&  field.fieldtype!="Tab Break"){ 
                                        frm.set_df_property(field.fieldname, "hidden", 1);
                                }

                        }
                }
                renderGeneralInforamtion(frm);


        },
});


function set_indicator(frm) {
        if (frm.doc.__islocal)
                return;

        if (frm.doc.adr > 0) frm.dashboard.add_indicator(__("ADR: {0}", [format_currency(frm.doc.adr)]), "blue");
        if (frm.doc.room_rate_discount > 0) frm.dashboard.add_indicator(__("Room Rate Discount: {0}", [format_currency(frm.doc.room_rate_discount)]), "red");
        if (frm.doc.total_room_rate_tax > 0) frm.dashboard.add_indicator(__("Total Room Rate Tax: {0}", [format_currency(frm.doc.total_room_rate_tax)]), "green");
        if (frm.doc.total_room_rate > 0) frm.dashboard.add_indicator(__("Total Room Rate: {0}", [format_currency(frm.doc.total_room_rate)]), "green");
        if (frm.doc.total_debit > 0) frm.dashboard.add_indicator(__("Total Debit: {0}", [format_currency(frm.doc.total_debit)]), "gray");
        if (frm.doc.total_credit > 0) frm.dashboard.add_indicator(__("Total Credit: {0}", [format_currency(frm.doc.total_credit)]), "pink");
        if (frm.doc.balance) frm.dashboard.add_indicator(__("Balance: {0}", [format_currency(frm.doc.balance)]), "blue");
}

function renderGeneralInforamtion(frm){
  
        const html = frappe.render_template("general_information", {doc:frm.doc, frappe:frappe})
   
        $(frm.fields_dict['html_general_information'].wrapper).html(html);
        frm.refresh_field('html_general_information');  


}