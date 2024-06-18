# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt


from edoor.api.generate_room_rate import get_room_rate_breakdown
from edoor.api.reservation import get_room_rate
import frappe
from frappe.model.document import Document
from edoor.api.utils import get_base_rate, get_working_day
import json

from frappe.utils import getdate, now
class ReservationRoomRate(Document):
	def validate(self):
		if self.flags.ignore_on_validate==True:
			return 

		# track changte to imporove performance
		if self.has_value_changed("rate_type"):
			rate_type_doc = frappe.get_doc("Rate Type",self.rate_type,cache=True)
			if self.is_new():
				self.allow_discount = rate_type_doc.allow_discount or 0
			
			self.is_complimentary = rate_type_doc.is_complimentary
			self.is_house_use = rate_type_doc.is_house_use
			
		
		self.input_rate =float(self.input_rate or 0)
		
		if not self.is_manual_rate:
			if (hasattr(self,"regenerate_rate") and  self.regenerate_rate)  or self.flags.regenerate_rate:
				room_rate = get_room_rate(self.property, self.rate_type, self.room_type_id,self.business_source,self.date)
		 
				self.input_rate = room_rate['rate']

 
		if (self.has_value_changed("input_rate") or 
			self.has_value_changed("tax_rule") or 
			self.has_value_changed("rate_include_tax") or 
			self.has_value_changed("tax_1_rate") or 
			self.has_value_changed("tax_2_rate") or 
			self.has_value_changed("tax_3_rate") or 
			self.has_value_changed("discount") or
			self.has_value_changed("discount_percent") or
			self.has_value_changed("is_manual_rate") or
			self.has_value_changed("discount_amount")  or 
			self.has_value_changed("adult") or   
			self.has_value_changed("child") or   
			self.has_value_changed("is_package") or   
			self.has_value_changed("package_charge_data")   or 
			self.flags.regenerate_rate == True 
       
      	): 
      
			rate_breakdown = get_room_rate_breakdown(json.dumps({
				"rate_type":self.rate_type,
				"tax_rule":self.tax_rule,
				"rate_include_tax":self.rate_include_tax,
				"tax_1_rate":self.tax_1_rate,
				"tax_2_rate":self.tax_2_rate,
				"tax_3_rate":self.tax_3_rate,
				"input_rate":self.input_rate,
				"is_package":self.is_package,
				"discount_type":self.discount_type,
				"discount":self.discount or 0,
				"discount_amount":0,
				"adult":self.adult,
				"child":self.child,
				"package_charge_data":self.package_charge_data
			}))
   
			self.tax_rule_data = rate_breakdown["tax_rule_data"]
			self.total_tax =rate_breakdown["total_tax"]
			self.total_room_charge = rate_breakdown["total_room_charge"]
			self.total_other_charge = rate_breakdown["total_other_charge"]
			self.total_rate = rate_breakdown["total_amount"]
			self.discount_amount= rate_breakdown["discount_amount"]

		 

			if (self.discount_amount or 0) > (self.input_rate or 0):
				frappe.throw("Discount amount cannot greater than total amoun")




	def on_update(self):
		
		if self.flags.ignore_on_update==True:
			if frappe.session.user=="Administrator":
				frappe.msgprint("On update event in Reservation Room Rate is not running")
			return

		# TODO---add queue update to run update reservation and queue job to to update breadkow revenue
		#when user update record from backend
		

