import frappe 


@frappe.whitelist()
def get_summary(property,date):
    from edoor.api.frontdesk import get_dashboard_data
    data = get_dashboard_data(property=property, date=date)
    return data

@frappe.whitelist(methods="POST")
def get_all_guest(param): 
     
    filter = {
        "type":"Reservation",
        "is_active_reservation":1,
        "property":param.get("property"),
        "date":param.get("date")
    }
    
    if param.get("is_arrival"):
        filter["is_arrival"] = 1
    if param.get("is_stay_over"):
        filter["is_stay_over"] = 1
    if param.get("is_departure"):
        filter["is_departure"] = 1
    
    if param.get("business_source"):
        filter["business_source"] = param.get("business_source")
    if param.get("room_type_id"):
        filter["room_type_id"] = param.get("room_type_id")
    
    orFilters = {}
    if param.get("keyword"):
        orFilters={
            "reservation":["like","%{}%".format(param.get("keyword"))],
            "guest":["like","%{}%".format(param.get("keyword"))],
            "guest_name":["like","%{}%".format(param.get("keyword"))],
            "reservation_stay":["like","%{}%".format(param.get("keyword"))],
            "business_source":["like","%{}%".format(param.get("keyword"))],
            "room_number":["like","%{}%".format(param.get("keyword"))],
            
        }
     
    occupy_data = frappe.db.get_all(
        "Room Occupy",
        fields=[
            "reservation_stay",
            "is_arrival",
            "is_stay_over",
            "is_departure",
            "room_type",
            "room_type_id"
        ],filters=filter, or_filters=orFilters,page_length=100000)
     
    filter = {
        "is_active_reservation":1,
        "property":param.get("property"),
        "name":["in",[d.get("reservation_stay") for d in occupy_data]]
    }
    if param.get("business_source"):
        filter["business_source"] = param.get("business_source")
    orFilters = {}
    if param.get("keyword"):
        orFilters={
            "reservation":["like","%{}%".format(param.get("keyword"))],
            "guest":["like","%{}%".format(param.get("keyword"))],
            "guest_name":["like","%{}%".format(param.get("keyword"))],
            "name":["like","%{}%".format(param.get("keyword"))],
            "business_source":["like","%{}%".format(param.get("keyword"))],
            "rooms":["like","%{}%".format(param.get("keyword"))],
            "reference_number":["like","%{}%".format(param.get("keyword"))],
            "internal_reference_number":["like","%{}%".format(param.get("keyword"))],
            
        }
        
    data = frappe.db.get_all(
        "Reservation Stay",
        fields=[
            "name", 
            "reservation", 
            "arrival_date", 
            "departure_date", 
            "guest", 
            "guest_name", 
            "reservation_color", 
            "reservation_color_code", 
            "'' as photo", 
            "guest_email", 
            "guest_phone_number", 
            "room_type_alias", 
            "room_types", 
            "arrival_date", 
            "departure_date", 
            "room_nights", 
            "adult", 
            "child", 
            "status_color", 
            "business_source", 
            "reservation_status", 
            "reservation_type", 
            "reference_number", 
            "reservation_date", 
            "rooms", 
            "rooms_data",
            "is_reserved_room",
        ], filters=filter, or_filters=orFilters, page_length=10000)
    

    # update group by arrival stay over departure 
    if param["group_by_field"] == "stay_type":
        for d in data:
            occupy = [occ for occ in occupy_data if occ.get("reservation_stay") == d["name"]][0]
            if occupy["is_arrival"] == 1:
                d["stay_type"] = "Arrival"
                d["sort_order"] = 1
            elif occupy["is_stay_over"] == 1:
                d["stay_type"] = "Stay Over"
                d["sort_order"] = 2
            else:
                d["stay_type"] = "Departure"
                d["sort_order"] = 3
        param["group_by_field"] = "sort_order"
    elif param["group_by_field"] == "room_type_id":
        for d in data:
            occupy = [occ for occ in occupy_data if occ.get("reservation_stay") == d["name"]][0]
            d["room_type"] = occupy["room_type"]
            d["room_type_id"] = occupy["room_type_id"]
            
            d["sort_order"] = frappe.get_value("Room Type",occupy["room_type_id"],"sort_order")
           
        param["group_by_field"] = "sort_order"
 
 
    # First, sort by group field
    if param["group_by_field"]:
        data = sorted(data, key=lambda x: x.get(param["group_by_field"]) or "")

    # Then, sort by order field with ascending or descending logic
    if param["order_by_field"]:
        data = sorted(data, key=lambda x: x.get(param["order_by_field"]) or "", reverse=(param["sort_type"] == "desc"))
        
    # data = sorted(data, key=lambda x: (x[param["group_by_field"]], x[param["order_by_field"]] if param["sort_type"] == 'asc' else -x[param["order_by_field"]]))
    
    return data

@frappe.whitelist(methods="POST")
def get_arrival_guest(filter):
    sql = """
        select
            name, 
            reservation,
            arrival_date,
            departure_date,
            guest,
            guest_name,
            reservation_color,
            reservation_color_code,
            '' as photo,
            guest_email,
            guest_phone_number,
            room_type_alias,
            room_types,
            arrival_date,
            departure_date,
            room_nights,
            adult,
            child,
            status_color,
            business_source,
            reservation_status,
            reservation_type,
            reference_number, 
            reservation_date,
            rooms,
            rooms_data
            
        from `tabReservation Stay`
        where
            property = %(property)s and
            name in (
                select 
                    distinct reservation_stay
                from `tabRoom Occupy`
                where 
                    property = %(property)s and 
                    date = %(date)s and 
                    is_active = 1 and 
                    is_active_reservation = 1 and 
                    type = 'Reservation' and 
                    is_arrival = 1
            ) 
        
    """
    # order by %(order_by_field)s %(sort_type)s
    data = frappe.db.sql(sql,filter,as_dict=1)
    
    return data