import frappe 
from frappe.utils import getdate, add_to_date
def get_total_room_group_by_month(filters):
    sql=""
    if filters.row_group=="Room Type":
        sql="""
            select 
                rt.room_type,
                month(a.date) as month,
                year(a.date) as year,
                sum(a.total_room) as total_room
            from `tabDaily Property Data` a 
                inner join `tabRoom Type` rt on rt.name = a.room_type_id
            where 
                a.property = %(property)s and 
                a.date between %(start_date)s and %(end_date)s
            group by 
                rt.room_type,
                month(a.date),
                year(a.date) 
        """
    else:
        sql="""
            select 
                month(date) as month,
                year(date) as year,
                sum(total_room) as total_room
            from `tabDaily Property Data` 
            where 
                property = %(property)s and 
                date between %(start_date)s and %(end_date)s
            group by 
            month(date),
            year(date) 
        """
    return frappe.db.sql(sql,filters, as_dict=1)

def get_total_room_group_by_date(filters):
    sql=""
    if filters.row_group=="Room Type":
        sql="""
            select 
                rt.room_type,
                a.date,
                sum(a.total_room) as total_room
            from `tabDaily Property Data` a 
                inner join `tabRoom Type` rt on rt.name = a.room_type_id
            where 
                a.property = %(property)s and 
                a.date between %(start_date)s and %(end_date)s
            group by 
                rt.room_type,
                a.date
        """
    else:
        sql="""
            select 
                date,
                sum(total_room) as total_room
            from `tabDaily Property Data` 
            where 
                property = %(property)s and 
                date between %(start_date)s and %(end_date)s
            group by 
                date
        """
    return frappe.db.sql(sql,filters, as_dict=1)


def get_total_row(data, total_row, columns,filters,total_rooms=None):
    
    for c in [d for d in columns if "has_total" in d ]:
        total_row[c["fieldname"]] = sum(d[c["fieldname"]] for d in data if c["fieldname"] in d)
    
    if filters.row_group == 'Room':
        total_rooms = sum([d["total_days"] for d in data if "total_days" in d])
    total_row["total_rooms"] = total_rooms
    return total_row

def get_total_occupancy_row(data, total_row, columns,filters,total_rooms=None):

    for c in [d for d in columns if "has_total" in d ]:    
        occupy = sum(d[c["fieldname"]] for d in data if c["fieldname"] in d)  
        if "date_index" in c:
            if(c.get("date_index")<len(total_rooms)):
                occupancy = 100 * ( (occupy or 0) / max(total_rooms[c.get("date_index")],1))
                total_row[c["fieldname"]] = round(occupancy,2)
    
    # occupy
    occupy = sum([d["total"] for d in data])
    total_row["total"] = round( 100 *(  occupy / max(sum(total_rooms),1)),2)
    return total_row


def get_grand_total_row(data, columns,filters,total_rooms):

    row={"row_group":"Grand Total", "indent":0,"is_group":1}
    for c in [d for d in columns if "has_total" in d ]:
        row[c["fieldname"]] = sum(d[c["fieldname"]] for d in data if c["fieldname"] in d)
    
    

    
    return row
   
    
def get_grand_total_occupancy_row(data, columns,total_rooms):
    
    row={"row_group":"Occupancy (%)", "indent":0,"is_group":1}
    for c in [d for d in columns if "has_total" in d ]:
        if "date_index" in c:
            occupy =  sum(d[c["fieldname"]] for d in data if c["fieldname"] in d)
            total_room = sum([d["total_room"] for d    in total_rooms if getdate(d["date"]).day == c["date_index"] + 1 ])
            occupancy = round( occupy /  max(total_room,1) * 100,2)
            row[c["fieldname"]] =occupancy
 
    occupy = sum([d["total"] for d in data])
    row["total"] = round( 100 *(  occupy / max(sum([d["total_room"] for d in total_rooms]),1)),2)
    return row
    
def row_group():
    return [
        {"fieldname":"business_source","label": "Business Source"},
        {"fieldname":"business_source_type","label": "Business Source Type"},
        {"fieldname":"reservation_type","label": "Reservation Type"},
        {"fieldname":"guest_type","label": "Guest Type"},
        {"fieldname":"nationality","label": "Nationality"},
        {"fieldname":"room_number","label": "Room"},
        {"fieldname":"room_type","label": "Room Type"},
    ]