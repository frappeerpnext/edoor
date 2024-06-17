# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
class Room(Document):
	def validate(self): 
		if not self.reservation_stay:
			self.guest = None
			self.arrival_date = None
			self.departure_date = None
			self.guest_name = None

		if self.housekeeping_status_code and self.room_status and self.room_status!="Room Block": 
			status = frappe.db.get_list("Housekeeping Status", filters={"room_status":self.room_status, "housekeeping_status_code":self.housekeeping_status_code}, fields=["name","status_color", "icon","show_in_room_availability","is_block_room"])
			if len(status)>0:
				self.housekeeping_status = status[0].name
				self.status_color = status[0].status_color
				self.housekeeping_icon= status[0].icon
				self.show_in_room_availability= status[0].show_in_room_availability
				self.block_room= status[0].is_block_room
		elif  self.room_status=="Room Block":
 
			status = frappe.db.get_list("Housekeeping Status", filters={"room_status":self.room_status}, fields=["name","status_color", "icon","show_in_room_availability","is_block_room"],ignore_permissions=True)
			if len(status)>0:
				self.housekeeping_status = status[0].name
				self.status_color = status[0].status_color
				self.housekeeping_icon= status[0].icon
				self.show_in_room_availability= status[0].show_in_room_availability
				self.block_room= status[0].is_block_room


	def on_update(self):
		if self.creation != self.modified:
			update_fetch_from_fields(self)

@frappe.whitelist()
def update_to_related_transaction(param):
    param = json.loads(param)
    if  param["option_type"]=="All":
        sql="""
			update `tabReservation Stay` s
			join (
				select 
    				group_concat(room_number) as  room_number,
       				group_concat(distinct  room_type) as room_type,
           			group_concat(distinct room_type_alias) as room_type_alias, 
              		parent 
                from `tabReservation Stay Room` 
                group by  parent
       		) b
			on s.name = b.parent
			SET 
				s.rooms = b.room_number,
				s.room_types = b.room_type,
				s.room_type_alias = b.room_type_alias

        """
        frappe.db.sql(sql)
        # udpate to reservation
        sql="""
			update `tabReservation` s
			join (
				select 
    				group_concat(room_number) as  room_number,
       				group_concat(distinct  room_type) as room_type,
           			group_concat(distinct room_type_alias) as room_type_alias, 
              		reservation 
                from `tabReservation Stay Room` 
                group by  reservation
       		) b
			on s.name = b.reservation
			SET 
				s.room_numbers = b.room_number,
				s.room_types = b.room_type,
				s.room_type_alias = b.room_type_alias

        """
        frappe.db.sql(sql)
    else:
        
        sql="""
			update `tabReservation Stay` s
			join (
				select 
    				group_concat(room_number) as  room_number,
       				group_concat(distinct  room_type) as room_type,
           			group_concat(distinct room_type_alias) as room_type_alias, 
              		parent 
                from `tabReservation Stay Room` 
                where
					is_active_reservation = 1
                group by  parent
       		) b
			on s.name = b.parent
			SET 
				s.rooms = b.room_number,
				s.room_types = b.room_type,
				s.room_type_alias = b.room_type_alias

        """
        frappe.db.sql(sql)
        # udpate to reservation
        sql="""
			update `tabReservation` s
			join (
				select 
    				group_concat(room_number) as  room_number,
       				group_concat(distinct  room_type) as room_type,
           			group_concat(distinct room_type_alias) as room_type_alias, 
              		reservation 
                from `tabReservation Stay Room` 
                where
					is_active_reservation = 1
                group by  reservation
       		) b
			on s.name = b.reservation
			SET 
				s.room_numbers = b.room_number,
				s.room_types = b.room_type,
				s.room_type_alias = b.room_type_alias

        """
        frappe.db.sql(sql)
    frappe.db.commit()
    
    frappe.msgprint("Update room information to related transaction successfully.")
    
 
def update_fetch_from_fields(self):
	data_for_updates = []

	if self.has_value_changed("room_number"):
		data_for_updates.append({"doctype":"Room Block","update_field":"room_number='{}'".format(self.room_number)})
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"room_number='{}'".format(self.room_number)})
		# deposit ledter
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"room_number='{}'".format(self.room_number)})
		# desk folio
		data_for_updates.append({"doctype":"Desk Folio","update_field":"room_number='{}'".format(self.room_number)})
		# payable ledger
		data_for_updates.append({"doctype":"Payable Ledger","update_field":"room_number='{}'".format(self.room_number)})
		
  		# reservation room rate
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"room_number='{}'".format(self.room_number)})
  
  		# folio transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_number='{}'".format(self.room_number)})
  
  		# room occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"room_number='{}'".format(self.room_number)})

		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"room_number='{}'".format(self.room_number)})
  
		
	if self.has_value_changed("room_type_id"):
		data_for_updates.append({"doctype":"Room Block","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Room Block","update_field":"room_type='{}'".format(self.room_type)})
		# stay room
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Reservation Stay Room","update_field":"room_type_alias='{}'".format(self.room_type_alias)})

		# temp room occupy
		data_for_updates.append({"doctype":"Temp Room Occupy","update_field":"room_type_id='{}'".format(self.room_type_id)})
		# Room Occupy
		data_for_updates.append({"doctype":"Room Occupy","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Room Occupy","update_field":"room_type_alias='{}'".format(self.room_type_alias)})
		# deposit leder
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Deposit Ledger","update_field":"room_type='{}'".format(self.room_type)})
		# desk folio
		data_for_updates.append({"doctype":"Desk Folio","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Desk Folio","update_field":"room_type='{}'".format(self.room_type)})
		# Payable Ledger 
		data_for_updates.append({"doctype":"Payable Ledger","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Payable Ledger","update_field":"room_type='{}'".format(self.room_type)})
		
		 # reservation room rate
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Reservation Room Rate","update_field":"room_type_alias='{}'".format(self.room_type_alias)})
		 # Folio Transaction
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type='{}'".format(self.room_type)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type_alias='{}'".format(self.room_type_alias)})
		
  		
  
		#Revenue Forecast Breakdown
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"room_type_id='{}'".format(self.room_type_id)})
		data_for_updates.append({"doctype":"Revenue Forecast Breakdown","update_field":"room_type_alias='{}'".format(self.room_type_alias)})
	if data_for_updates:
		for d in set([x["doctype"] for x in data_for_updates]):
			sql="update `tab{}` set {} where room_id='{}'".format(
				d,
				",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
				self.name
			)
			
			frappe.db.sql(sql)