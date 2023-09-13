import frappe

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
