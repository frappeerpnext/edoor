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
    const template = `
    {% if data.length > 0 %}
    {% var index = 1 %}
    <div class="row folio-section">
        <div class="col-4">
            <div class="p-3" style="border:1px solid #4338ca;border-radius: 10px;">
                <div class="accordion" id="accordionExample">
                    {% for d in data %}
                        <div class="card">
                            <div class="card-header" id="{{d.name}}">
                                <h2 class="mb-0">
                                    {% if index == 1 %}
                                    <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#collapse_{{d.name}}" aria-expanded="true" aria-controls="collapse_{{d.name}}">
                                    {% else %}
                                    <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#collapse_{{d.name}}" aria-expanded="false" aria-controls="collapse_{{d.name}}">
                                    {% endif %}
                                        <div class="d-flex justify-content-between">
                                            <div class="d-flex" style="gap:5px">
                                                <div>
                                                    <a style="border: 1px dashed #4338ca;border-radius: 10px;padding: 0 5px;color: #4338ca;cursor: pointer;display: inline-block;text-decoration: none;" href="/app/reservation-stay/{{d.name}}">{{d.name}}</a>
                                                </div>
                                                <div class="px-3 rounded-lg text-white" style="background-color: {{d.status_color}};"></div>
                                                <div class="px-2 bg-white rounded-lg border" style="box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;color: #4338ca;">
                                                    <strong>{{d.folios.length}}</strong>
                                                </div>
                                            </div>
                                            <div>
                                                <div class="px-2 bg-white rounded-lg border" style="box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;color: #4338ca;">
                                                    <strong>{{ frappe.format(d.balance,{"fieldtype":"Currency"})}}</strong>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="d-flex mt-1" style="gap: 3px;">
                                            <svg style="width: 13px;" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" version="1.1" fill="none" stroke="#000000" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <circle cx="8" cy="6" r="3.25"></circle> <path d="m2.75 14.25c0-2.5 2-5 5.25-5s5.25 2.5 5.25 5"></path> </g></svg>
                                            <div>{{d.guest_name}} | Room: {{d.rooms}}</div>
                                        </div>
                        
                                    </button>
                                </h2>
                            </div>
                            {% if index == 1 %}
                            <div id="collapse_{{d.name}}" class="collapse show" aria-labelledby="{{d.name}}" data-parent="#accordionExample">
                            {% else %}
                            <div id="collapse_{{d.name}}" class="collapse" aria-labelledby="{{d.name}}" data-parent="#accordionExample">
                            {% endif %}
                                <div class="card-body">
                                    <div >
                                        {% for f in d.folios %}
                                            <button class="child-folio-present mb-2 text-left rounded-lg p-2" style="color:#4338ca;border:1px solid #dfdfdf;background-color:#f7f6ff;width: 100%;">
                                                <div class="d-flex justify-content-between">
                                                    <div>
                                                        <div class="d-flex justify-content-between" style="gap:15px">
                                                            <div style="display: flex;align-items: center;">
                                                                <div>
                                                                    {% if f.is_master == 1 %}
                                                                        <div>
                                                                            <svg style="width: 20px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M21.8382 11.1263C22.0182 9.2137 22.1082 8.25739 21.781 7.86207C21.604 7.64823 21.3633 7.5172 21.106 7.4946C20.6303 7.45282 20.0329 8.1329 18.8381 9.49307C18.2202 10.1965 17.9113 10.5482 17.5666 10.6027C17.3757 10.6328 17.1811 10.6018 17.0047 10.5131C16.6865 10.3529 16.4743 9.91812 16.0499 9.04851L13.8131 4.46485C13.0112 2.82162 12.6102 2 12 2C11.3898 2 10.9888 2.82162 10.1869 4.46486L7.95007 9.04852C7.5257 9.91812 7.31351 10.3529 6.99526 10.5131C6.81892 10.6018 6.62434 10.6328 6.43337 10.6027C6.08872 10.5482 5.77977 10.1965 5.16187 9.49307C3.96708 8.1329 3.36968 7.45282 2.89399 7.4946C2.63666 7.5172 2.39598 7.64823 2.21899 7.86207C1.8918 8.25739 1.9818 9.2137 2.16181 11.1263L2.391 13.5616C2.76865 17.5742 2.95748 19.5805 4.14009 20.7902C5.32271 22 7.09517 22 10.6401 22H13.3599C16.9048 22 18.6773 22 19.8599 20.7902C20.7738 19.8553 21.0942 18.4447 21.367 16" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"></path> <path d="M9 18H15" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"></path> </g></svg>
                                                                        </div>
                                                                    {% endif %}
                                                                </div>
                                                            </div>
                                                            <div>
                                                                <div>
                                                                    <div class="folio_name">{{f.name}}</div>
                                                                    <div class="d-flex" style="gap:5px">
                                                                        <div>
                                                                            <div class="px-1 d-flex align-items-center justify-content-center " style="border: 1px solid #ccc;border-radius: 10px;">
                                                                                <div>
                                                                                    <svg style="width: 10px;" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" version="1.1" fill="none" stroke="#404040" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <circle cx="8" cy="6" r="3.25"></circle> <path d="m2.75 14.25c0-2.5 2-5 5.25-5s5.25 2.5 5.25 5"></path> </g></svg>
                                                                                    <span style="font-size: 12px;color: #5c5c5c;" style="color:#404040;">{{f.guest_name}}</span>
                                                                                </div>
                                                                            </div>
                                                                        </div>
                                                                        <div>
                                                                            {% if f.status == 'Open' %}
                                                                                <div class="px-1" style="background:#e7f4ea;border-radius:10px;color:#0a762a;text-transform:uppercase;">
                                                                                    <div>{{f.status}}</div>
                                                                                </div>
                                                                            {% endif %}
                                                                            {% if f.status == 'Close' %}
                                                                                <div>
                                                                                    <div>{{f.status}}</div>
                                                                                </div>
                                                                            {% endif %}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <div>{{frappe.format(f.balance,{"fieldtype":"Currency"})}}</div>
                                                        <div>{{frappe.format(f.posting_date,{"fieldtype":"Date"})}}</div>
                                                    </div>
                                                </div>
                                            </button>
                                        {% endfor %}
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% index = index + 1%}
                    {% endfor %}
                </div>
            </div>
        </div>
        <div class="col-8">
            <div class="p-3 folio-transaction" style="border:1px solid #4338ca;border-radius: 10px;">
                
            </div>
        </div>
    </div>
    {% endif %}
    `

    $(frm.fields_dict["reservation_folio_list"].wrapper).html("Loading reservation room rate list...");
    frm.refresh_field("reservation_folio_list"); 

    frappe.call({
        method: 'edoor.api.reservation.get_reservation_folio_list', // Replace with your actual method path
        args: {
            reservation: frm.doc.name
        },
        callback: function(response) { 
            if (response.message) {
                const html = frappe.render_template(template,{data:response.message})
                let dom = parser.parseFromString(html, "text/html").querySelector("div.folio-section")

                dom.querySelectorAll("button.child-folio-present").forEach(a=>{
                    a.addEventListener("click",function(){
                        let d = dom.querySelector(".folio-transaction")
                        d.innerHTML = '';

                        
                        const folio_name =  a.querySelector(".folio_name").textContent
                        
                        const result = response.message.flatMap(entry => 
                            entry.folios.filter(folio => folio.name === folio_name)
                        );

                        console.log(result)
                        
                        d.insertAdjacentHTML('beforeend', getFolioTransactionData(dom));
                    })
                })

                $(frm.fields_dict["reservation_folio_list"].wrapper).html(dom);

                console.log(response.message)
            }
        }
    })
}

function getFolioTransactionData (data) {
    let ui = `
        <div>aaaa</div>
    `
    return ui
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
  
 