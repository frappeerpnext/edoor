from edoor.api.frontdesk import get_working_day
import frappe
import json

@frappe.whitelist(methods="POST")
def update_housekeeping_status(rooms, status):
    
   doc = frappe.get_doc("Housekeeping Status", status)
   for r in rooms.split(","):
      room = frappe.get_doc("Room",r)
      if room.reservation_stay:
         if (doc.is_room_occupy or 0) == 0:
            frappe.throw("Room {} is occupy. You can not change   status to {}".format(room.room_number, status))
      if room.is_block:
         frappe.throw("Room #{} is block. You can not change status of a block room.".format(room.room_number))
      else:
         room.housekeeping_status = status
         room.status_color = doc.status_color
         room.save()
      frappe.db.commit()

   return "Ok"

@frappe.whitelist(methods="POST")
def update_housekeeper(rooms, housekeeper):
    for r in rooms.split(","):
       frappe.db.set_value("Room", r,"housekeeper", housekeeper)

    frappe.db.commit()
    return "Ok"

@frappe.whitelist()
def get_room_list(filter={}):
   filter = json.loads(filter)
   working_day=get_working_day(filter["property"])
   def multiple_filter_format(fieldname):
      return " and {} in ({})".format(fieldname, (",".join("'{}'".format(str(x)) for x in filter[fieldname])))
   def single_filter_format(fieldname):
      return " and {} = '{}'".format(fieldname,filter[fieldname])
   sql_filter = ""
   if(filter['room_type_id']):
      sql_filter += multiple_filter_format('room_type_id')
   if(filter['housekeeping_status']):
      sql_filter += multiple_filter_format('housekeeping_status')
   if('building' in filter and filter['building']):
      sql_filter += single_filter_format('building')
   if('floor' in filter and filter['floor']):
      sql_filter += single_filter_format('floor')
   
   if('room_type_group' in filter and filter['room_type_group']):
      sql_filter += single_filter_format('room_type_group')
   if('housekeeper' in filter and filter['housekeeper']):
      sql_filter += single_filter_format('housekeeper')
   if ('keyword' in filter and filter['keyword']):
      sql_filter += " and room_number like '%{}%'".format(filter['keyword'])
   

   
   sql ="""
      select 
         name,
         room_number,
         housekeeping_status,
         status_color,
         housekeeper,
         room_type,
         guest,
         guest_name
      from `tabRoom`
      where
         property = %(property)s 
         {}
   """.format(sql_filter)
  
   data = frappe.db.sql(sql,filter,as_dict=1)
   occupy_data= frappe.db.sql("""
      select 
            date,
            room_id,
            is_arrival,                           
            is_departure, 
            reservation_stay,                      
            reservation_status,
            type
      from `tabTemp Room Occupy`
      where 
         date =%(date)s and 
         property = %(property)s  
         {} and
         ifnull(room_id,'') !=''
   """.format(sql_filter),filter,as_dict=1)

   for d in occupy_data:
      room = [r for r in data if r["name"]==d["room_id"] ][0]
      if d["type"] =="Reservation":
         room["reservation_stay"] = d["reservation_stay"]
         
         room["reservation_status"] =d["reservation_status"]

         if d["is_arrival"]==1:
            if working_day["date_working_day"] == d["date"] and d["reservation_status"]=="Reserved":
               room["reservation_status"] = "Arrival"

         elif  d["is_departure"] ==1 and d["reservation_status"] in ["In-house","Reserved"]:
            room["reservation_status"] = "Departure"
         elif d["is_arrival"]==0 and d["is_departure"] ==0 and d["reservation_status"] in ["In-house"]:
            room["reservation_status"] = "Stay Over"

         #get guest and guest name from stay
         if d["reservation_stay"]:
            guest, guest_name = frappe.db.get_value('Reservation Stay', d["reservation_stay"] , ['guest', 'guest_name'])
            room["guest"] =guest
            room["guest_name"] =guest_name
      else:
         #room block
         pass
         # room["reservation_status"] =d["reservation_status"]
   return data
