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
  
 