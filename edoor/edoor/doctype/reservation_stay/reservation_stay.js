// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt


frappe.ui.form.on("Reservation Stay", {
        setup(frm) {

                for (const key in frm.fields_dict) {
                        if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
                                frm.fields_dict[key].$wrapper.addClass('custom_control');
                        }

                }

                if (!frm.doc.__islocal) {
                        getItemReservationStayList(frm) 
                        getReservationRoomRate(frm) 
                }
                
        },
        refresh(frm) {

                // set_indicator(frm);
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


async function getItemReservationStayList(frm) {
        $(frm.fields_dict["information_list"].wrapper).html("Loading reservation data...");
        frm.refresh_field("information_list");
    
        let arr_date = new Date(frm.doc.arrival_date);
        let dep_date = new Date(frm.doc.departure_date);
    
        // Format the date to show the day of the week
        let options = { weekday: 'long' };
        let arr_day = arr_date.toLocaleDateString('en-US', options);
        let dep_day = dep_date.toLocaleDateString('en-US', options);
    
        let json_date = {
            'arrival_day':arr_day,
            'departure_day':dep_day
        }  
    
        const rooms = JSON.parse(frm.doc.rooms_data)
     
        const charge_summary = await getChargeSumamry(frm)
        
        let html = frappe.render_template("reservation_stay_detail", {data:frm,day_format:json_date,charge_summary:charge_summary,rooms_data:rooms});
        $(frm.fields_dict["information_list"].wrapper).html(html);
        frm.refresh_field("information_list");


        console.log(frm)
}


function getReservationRoomRate(frm) {
        $(frm.fields_dict["room_rate_list"].wrapper).html("Loading reservation room rate list...");
        frm.refresh_field("room_rate_list");
    
        frappe.db.get_list("Reservation Room Rate", {
            fields:[
                'name',
                'date',
                'reservation_stay',
                'room_type_alias',
                'room_number',
                'guest_name',
                'adult',
                'child',
                'rate_type',
                'input_rate',
                'discount_amount',
                'total_tax',
                'total_rate',
                'is_package'
            ],
            filters:[['reservation_stay','=',frm.doc.name]],
            order_by: 'date asc'
        }).then(result=>{
            let html = frappe.render_template("room_rate_list", {data:result});
            $(frm.fields_dict["room_rate_list"].wrapper).html(html);
            frm.refresh_field("room_rate_list");
        })
    
} 
function getChargeSumamry(frm) {
        return new Promise((resolve, reject) => {
            frappe.call({
                method: 'edoor.api.reservation.get_reservation_charge_summary',
                args: {
                    reservation: frm.doc.name
                },
                callback: (r) => {
                   
                    resolve(r.message)
                   
                },
                error: (r) => {
                    reject(r)
                }
            })
        });
}