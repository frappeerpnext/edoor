import frappe 

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


def get_total_row(data, total_row, columns,filters,total_rooms=None):
    
    for c in [d for d in columns if "has_total" in d ]:
        total_row[c["fieldname"]] = sum(d[c["fieldname"]] for d in data if c["fieldname"] in d)
    
    if filters.row_group == 'Room':
        total_rooms = sum([d["total_days"] for d in data if "total_days" in d])

        
    if total_rooms==0:
            total_rooms =1
    total_row["occupancy"] = 100 *( total_row["total"] / total_rooms)       
    return total_row
    
def get_grand_total_row(data, columns,filters,total_rooms):
    row={"row_group":"Grand Total", "indent":0,"is_group":1}
    for c in [d for d in columns if "has_total" in d ]:
        row[c["fieldname"]] = sum(d[c["fieldname"]] for d in data if c["fieldname"] in d)
    

    if total_rooms==0:
            total_rooms =1
    row["occupancy"] = 100 *( row["total"] / total_rooms)      
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