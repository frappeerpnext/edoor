// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Reservation", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Reservation", {
	refresh(frm) {
         

        if (!frm.doc.__islocal) {
            getItemReservationList(frm)
            getReseravationStayList(frm)
            getReservationRoomRate(frm)
            getReservationFolio(frm)
        }
	},
});

function set_indicator(frm){
    if(frm.doc.__islocal)
			return;

    if (frm.doc.adr > 0 )  frm.dashboard.add_indicator(__("ADR: {0}", [format_currency(frm.doc.adr)]),"blue");
    if (frm.doc.room_rate_discount > 0 )  frm.dashboard.add_indicator(__("Room Rate Discount: {0}",[format_currency(frm.doc.room_rate_discount)]) ,"red");        
    if (frm.doc.total_room_rate_tax > 0 )  frm.dashboard.add_indicator(__("Total Room Rate Tax: {0}",[format_currency(frm.doc.total_room_rate_tax)]) ,"green");
    if (frm.doc.total_room_rate > 0 )  frm.dashboard.add_indicator(__("Total Room Rate: {0}",[format_currency(frm.doc.total_room_rate)]) ,"green");
    if (frm.doc.total_debit > 0 )  frm.dashboard.add_indicator(__("Total Debit: {0}",[format_currency(frm.doc.total_debit)]) ,"gray");
    if (frm.doc.total_credit > 0 )  frm.dashboard.add_indicator(__("Total Credit: {0}",[format_currency(frm.doc.total_credit)]) ,"pink");
    if (frm.doc.balance > 0 )  frm.dashboard.add_indicator(__("Balance: {0}",[format_currency(frm.doc.balance)]) ,"blue");
}

async function getItemReservationList(frm) {
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
    
    let html = frappe.render_template("reservation_detail", {data:frm,day_format:json_date,charge_summary:charge_summary,rooms_data:rooms});
    $(frm.fields_dict["information_list"].wrapper).html(html);
    frm.refresh_field("information_list");


    
   
}

function getReseravationStayList(frm){
    $(frm.fields_dict["reservation_stay_list_info"].wrapper).html("Loading reservation stay list...");
    frm.refresh_field("reservation_stay_list_info");

    frappe.db.get_list("Reservation Stay", 
    {
        fields:['name',
        'arrival_date',
        'departure_date',
        'room_nights',
        'room_type_alias',
        'rooms', 
        'guest_name',
        'adult',
        'child',
        'adr',
        'total_room_rate',
        'total_debit',
        'total_credit',
        'balance',
        'status_color',
        'reservation_status',
        'is_master',
        'rooms_data',
        'allow_post_to_city_ledger',
        'paid_by_master_room',
        'require_pickup',
        'require_drop_off'],
        filters: [['reservation', '=', frm.doc.name]],
    }).then(result=>{
            const sortedResult = result.sort((a, b) => (a.is_master === 1 ? -1 : 1));

            const parsedResult = sortedResult.map(item => {
                const roomsJson = JSON.parse(item.rooms_data);
                return { ...item, rooms_data: roomsJson };
            });
            let html = frappe.render_template("reservation_stay_list", {data:parsedResult});
            $(frm.fields_dict["reservation_stay_list_info"].wrapper).html(html);
            frm.refresh_field("reservation_stay_list_info");
    })
}


//get reservation room rate
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
            'rate',
            'discount_amount',
            'total_tax',
            'total_rate',
            'is_package'
        ],
        filters:[['reservation','=',frm.doc.name]],
        order_by: 'date asc'
    }).then(result=>{
        let html = frappe.render_template("room_rate_list", {data:result});
        $(frm.fields_dict["room_rate_list"].wrapper).html(html);
        frm.refresh_field("room_rate_list");
    })

}


function getReservationFolio(frm) {
    let parser = new DOMParser()
    $(frm.fields_dict["reservation_folio_list"].wrapper).html("Loading reservation folio list...");
    frm.refresh_field("reservation_folio_list"); 

    frappe.call({
        method: 'edoor.api.reservation.get_reservation_folio_list', 
        args: {
            reservation: frm.doc.name
        },
        callback: function(response) { 
            if (response.message) {
                const html = frappe.render_template("reservation_folio",{data:response.message})
                let dom = parser.parseFromString(html, "text/html").querySelector("#wrapper_folio_list")
                const buttons = dom.querySelectorAll("button.child-folio-present");

                if (dom){
                    if (dom.querySelector("#wrapper_folio_detail")){
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
                if ((response.message.length) > 0) {
                    $(frm.fields_dict["reservation_folio_list"].wrapper).html(dom);
                }else {
                    $(frm.fields_dict["reservation_folio_list"].wrapper).html("<div style='padding: 8px 10px;background:#edf6fd;color:#005ca3;border-radius:8px;'>This reservation does not have a folio assigned.</div>");
                }
                
            }
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
