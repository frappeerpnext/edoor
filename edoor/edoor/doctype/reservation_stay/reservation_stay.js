// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt


frappe.ui.form.on("Reservation Stay", {
        onload(frm) {
                audit_trail_detail(frm)
        },
        setup(frm) {
                for (const key in frm.fields_dict) {
                        if (["Currency", "Data", "Int", "Link", "Date", "Datetime", "Float", "Select"].includes(frm.fields_dict[key].df.fieldtype)) {
                                frm.fields_dict[key].$wrapper.addClass('custom_control');
                        }
                }  
        },
        refresh(frm) {
                if (!frm.doc.__islocal) {
                        frm.set_intro("We reserved room for this reservation.", "blue");
                }
                // // set_indicator(frm);
                // if (frappe.session.user != "Administrator") {
                        
                //         for (const field of frm.meta.fields) {
                //                  if(field.fieldtype!="HTML" &&  field.fieldtype!="Tab Break"){ 
                //                         frm.set_df_property(field.fieldname, "hidden", 1);
                //                 }

                //         }
                // }
                if (!frm.doc.__islocal) {
                        getItemReservationStayList(frm) 
                        getReservationRoomRate(frm) 
                        getReservationStayFolio(frm)
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

function getReservationStayFolio(frm) {
        let parser = new DOMParser()
        $(frm.fields_dict["reservation_stay_folio_list"].wrapper).html("Loading reservation stay folio list...");
        frm.refresh_field("reservation_stay_folio_list"); 

        frappe.db.get_list("Reservation Folio", {
                fields:["name","status","is_master","rooms","note","room_types","guest","guest_name","phone_number","email","photo","status","balance","owner","creation","reservation","reservation_stay","business_source","doctype","total_credit","total_debit","tax_invoice_number","folio_type","folio_type_color"],
                filters:[['reservation_stay','=',frm.doc.name]],
                order_by: 'creation asc'
        }).then(result=>{
                result.sort((a, b) => b.is_master - a.is_master);

                const html = frappe.render_template("reservation_stay_folio",{data:result})
                let dom = parser.parseFromString(html, "text/html").querySelector("#wrapper_folio_list")
                const buttons = dom.querySelectorAll("button.child-folio-present")

                if (dom){
                        if (dom.querySelector("#wrapper_folio_detail")) {
                                dom.querySelector("#wrapper_folio_detail").innerHTML = '<div>Please select folio!</div>'
                        }
                        buttons.forEach(r=>{
                                r.addEventListener('click',function(){
                                buttons.forEach(btn => {
                                        btn.classList.remove('show')
                                        btn.style.color = '#4338ca'
                                        btn.style.borderColor = '#dfdfdf'
                                        
                                });
                                this.classList.add('show');
                                this.style.color = '#ff3720'
                                this.style.borderColor = '#ff3720'

                                folioDetailClick(this.dataset.id)
                                })
                        })
                }
                if ((result.length) > 0) {
                        $(frm.fields_dict["reservation_stay_folio_list"].wrapper).html(dom);
                }else {
                        $(frm.fields_dict["reservation_stay_folio_list"].wrapper).html("<div style='padding: 8px 10px;background:#edf6fd;color:#005ca3;border-radius:8px;'>This reservation does not have a folio assigned.</div>");
                }
        })
}

function folioDetailClick(folio_number){
        frappe.call({
            method: 'edoor.api.reservation.get_folio_transaction', 
            args: {
                transaction_type:"Reservation Folio",
                transaction_number:folio_number,
                breakdown_account_code:0
            },
            callback: function(response) { 
                if (response.message) {
                    const html = frappe.render_template("folio_detail",{data:response.message})
                    document.querySelector("#wrapper_folio_detail").innerHTML = (html)
    
                    document.querySelectorAll(".time_creation").forEach(r=> {
                        let timestamp = r.textContent
                        let date = new Date(timestamp);
    
                        let prettyDates = prettyDate(date)
                        r.textContent = prettyDates
                    }) 
                }
            }
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

function prettyDate(date) {
        var diff = Math.floor((new Date() - date) / 1000);
        var dayDiff = Math.floor(diff / 86400);
    
        if (isNaN(dayDiff) || dayDiff < 0) {
            return '';
        }
    
        if (dayDiff === 0) {
            if (diff < 60) return 'Just now';
            if (diff < 120) return '1 minute ago';
            if (diff < 3600) return Math.floor(diff / 60) + ' minutes ago';
            if (diff < 7200) return '1 hour ago';
            if (diff < 86400) return Math.floor(diff / 3600) + ' hours ago';
        }
    
        if (dayDiff === 1) return 'Yesterday';
        if (dayDiff < 7) return dayDiff + ' days ago';
        if (dayDiff < 31) return Math.ceil(dayDiff / 7) + ' weeks ago';
        if (dayDiff < 365) return Math.ceil(dayDiff / 30) + ' months ago';
        return Math.ceil(dayDiff / 365) + ' years ago';
}

function audit_trail_detail (frm){ 
        if (frm.doc.checked_in_date) {
                audit_data(frm.doc.checked_in_date, frm.doc.checked_in_by, txt_by='Check-in by')
        }
        if (frm.doc.checked_out_date) {
                audit_data(frm.doc.checked_out_date, frm.doc.checked_out_by, txt_by='Check Out by')
        }
        if (frm.doc.cancelled_date) {
                audit_data(frm.doc.cancelled_date, frm.doc.cancelled_by, txt_by='Cancelled By')
        }
}
function audit_data (date_by, checked_by, txt_by) {
        const auditTrail = document.querySelector('.list-unstyled.sidebar-menu.text-muted')
        if (auditTrail) {
                if (checked_by == frappe.session.user) {
                        checked_by = 'You'
                }
                let date = new Date(date_by);
                let date_pretty = prettyDate(date)
                const li = document.createElement('li');
                if (li) {
                        li.style = 'margin-top:15px'
                        li.textContent = `${txt_by} · ${checked_by.split("@")[0]} ${date_pretty}`;
                        auditTrail.appendChild(li);
                }               
        }
}
