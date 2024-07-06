from edoor.api.frontdesk import get_working_day
import frappe
import json
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_years

@frappe.whitelist(methods="POST")
def update_housekeeping_status(property, rooms, status):
   working_day = get_working_day(property) 
   for r in rooms.split(","):
      room = frappe.get_doc("Room",r) 
      
      room.housekeeping_status_code = status
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
def get_room_list(filter):

   filter["keyword"] = f"%{filter['keyword'] }%" if "keyword" in filter else f'%%'
   
   working_day = get_working_day(filter["property"])

   sql ="""
      select 
         name,
         room_number,
         housekeeping_status,
         housekeeping_status_code,
         room_status,
         building,
         '' as reservation_status,
         status_color,
         housekeeper,
         room_type,
         floor,
         '' as room_block
      from `tabRoom`
      where
         property = %(property)s  and 
         room_number like %(keyword)s
   """

   if 'room_type_id' in filter and  len(filter["room_type_id"])>0:
      sql = sql + " and room_type_id in %(room_type_id)s "
   
   if  'housekeeping_status' in filter and  len(filter["housekeeping_status"])>0:
      sql = sql + " and housekeeping_status in %(housekeeping_status)s "
   
   if  'building' in filter and len(filter["building"])>0:
      sql = sql + " and building = %(building)s "
   
   if   'floor' in filter and len(filter["floor"])>0:
      sql = sql + " and floor = %(floor)s "
   
   if  'room_type_group' in filter and len(filter["room_type_group"])>0:
      sql = sql + " and room_type_group = %(room_type_group)s "
   
   if  'housekeeper' in filter and len(filter["housekeeper"])>0:
      sql = sql + " and housekeeper = %(housekeeper)s "
   
   data = frappe.db.sql(sql,filter,as_dict=1)
   sql ="""
      select 
            date,
            room_id,
            is_arrival,                           
            is_departure, 
            reservation_stay,                      
            reservation_status,
            type,
            stay_room_id

      from `tabRoom Occupy`
      where 
         ifnull(room_id,'') !='' and 
         date = %(date)s and 
         room_number like %(keyword)s and 
         property = %(property)s 
   """
   if  'room_type_id' in filter and  len(filter["room_type_id"])>0:
      sql = sql + " and room_type_id in %(room_type_id)s "
   
   if 'building' in filter and len(filter["building"])>0:
      sql = sql + " and building = %(building)s "

   if  'floor' in filter and len(filter["floor"])>0:
      sql = sql + " and floor = %(floor)s "
   
   if  'room_type_group' in filter and len(filter["room_type_group"])>0:
      sql = sql + " and room_type_group = %(room_type_group)s "
   
   if   'date' in filter and len(filter["date"])>0:
      sql = sql + " and date = %(date)s "

   #filter from room occpuy in have room in room list 
   if len(data)>0:
      filter["room_ids"]=[d["name"] for d in data]
      sql = sql + " and room_id in %(room_ids)s " 
        

   occupy_data= frappe.db.sql(sql,filter,as_dict=1)
    
 
   for d in occupy_data:
      data_room = [r for r in data if r["name"]==d["room_id"] ]
      room = None
      if data_room:
         room = data_room[0]
         
      
      if room:
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
         #if block
            room["room_block"] = d["stay_room_id"]
            room["housekeeping_status"] = frappe.db.get_single_value("eDoor Setting","room_block_status")
            room["status_color"] = frappe.db.get_single_value("eDoor Setting","room_block_color")

   return data

