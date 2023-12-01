from edoor.api.frontdesk import get_working_day
import frappe
import json

@frappe.whitelist(methods="POST")
def update_housekeeping_status(property, rooms, status):
   working_day = get_working_day(property)
   doc = frappe.get_doc("Housekeeping Status", status)
   for r in rooms.split(","):
      room = frappe.get_doc("Room",r)
      temp_occupy_data = frappe.db.sql("select type,reservation_status from `tabTemp Room Occupy` where room_id='{}' and date='{}' and property='{}'".format(r,working_day["date_working_day"],property), as_dict=1)
      if len(temp_occupy_data)>0:
         temp_data = temp_occupy_data[0]
         #validate if room have guest
         if temp_data["type"] =="Reservation":
            if temp_data["reservation_status"] == "In-house":
               # validate status is vacant but room have guest then show error message
               if (doc.is_room_occupy or 0) == 0:
                  frappe.throw("Room {} is occupy. You can not change   status to {}".format(room.room_number, status))
            else:
                if (doc.is_room_occupy or 0) == 1:
                  frappe.throw("Room {} is vacant. You can not change status to {}".format(room.room_number, status))
         else:
            frappe.throw("Room #{} is block. You can not change status of a block room.".format(room.room_number))
      else:
         #room is free but set to room occupy
         if (doc.is_room_occupy or 0) == 1:
            frappe.throw("Room {} is vacant. You can not change status to {}".format(room.room_number, status))

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

@frappe.whitelist(methods="POST")
def get_room_list(filter={}):
   filter["keyword"] = f"%{filter['keyword'] }%" 
   working_day = get_working_day(filter["property"])

    
   sql ="""
      select 
         name,
         room_number,
         housekeeping_status,
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
   """.format(filter["keyword"])

   if len(filter["room_type_id"])>0:
      sql = sql + " and room_type_id in %(room_type_id)s "
   
   if len(filter["housekeeping_status"])>0:
      sql = sql + " and housekeeping_status in %(housekeeping_status)s "
   
   if len(filter["building"])>0:
      sql = sql + " and building = %(building)s "
   
   if len(filter["floor"])>0:
      sql = sql + " and floor = %(floor)s "
   
   if len(filter["room_type_group"])>0:
      sql = sql + " and room_type_group = %(room_type_group)s "
   
   if len(filter["housekeeper"])>0:
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

      from `tabTemp Room Occupy`
      where 
         ifnull(room_id,'') !='' and 
         date = %(date)s and 
         room_number like %(keyword)s and 
         property = %(property)s 
   """
   if len(filter["room_type_id"])>0:
      sql = sql + " and room_type_id in %(room_type_id)s "
   
   if len(filter["building"])>0:
      sql = sql + " and building = %(building)s "

   if len(filter["floor"])>0:
      sql = sql + " and floor = %(floor)s "
   
   if len(filter["room_type_group"])>0:
      sql = sql + " and room_type_group = %(room_type_group)s "
   
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
