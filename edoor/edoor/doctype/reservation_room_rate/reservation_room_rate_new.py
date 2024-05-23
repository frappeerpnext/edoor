# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt


from edoor.api.reservation import get_room_rate
import frappe
from frappe.model.document import Document
from edoor.api.utils import get_base_rate, get_working_day
import json
from  edoor.api.tax_calculation  import get_tax_breakdown
from frappe.utils.data import getdate, now
class ReservationRoomRate(Document):
	def validate(self):
		rate_type_doc = frappe.get_doc("Rate Type",self.rate_type,cache=True)
		if self.is_new():
			self.allow_discount = rate_type_doc.allow_discount or 0
		
		self.is_complimentary = rate_type_doc.is_complimentary
		self.is_house_use = rate_type_doc.is_house_use
		
		self.input_rate =float(self.input_rate or 0)
		
		if not self.is_manual_rate:
			if hasattr(self,"regenerate_rate") and  self.regenerate_rate:
				
				room_rate = get_room_rate(self.property, self.rate_type, self.room_type_id,self.business_source,self.date)	
				self.input_rate = room_rate['rate']

		self.rate = self.input_rate or 0		 
		self.discount = self.discount or 0
		
		if self.discount_type=="Percent":
			self.discount_amount =float( self.input_rate or 0 ) * ((self.discount or 0) / 100.0)
		else:
			self.discount_amount = self.discount or 0 
		self.discount = self.discount or 0

		if (self.discount_amount or 0) > (self.input_rate or 0):
			frappe.throw("Discount amount cannot greater than amount")
		if (self.has_value_changed("input_rate") or 
			self.has_value_changed("tax_rule") or 
			self.has_value_changed("rate_include_tax") or 
			self.has_value_changed("tax_1_rate") or 
			self.has_value_changed("tax_2_rate") or 
			self.has_value_changed("tax_3_rate") or 
			self.has_value_changed("discount") or
			self.has_value_changed("discount_amount")  
      		): 
  
			tax_data = get_tax_breakdown(
				tax_rule = self.tax_rule,
				rate_include_tax = self.rate_include_tax,
				tax_1_rate =self.tax_1_rate,
				tax_2_rate =self.tax_2_rate,
				tax_3_rate =self.tax_3_rate,
				discount_amount=self.discount_amount,
				rate=  self.input_rate
			)
   
			self.rate = tax_data["rate"]
			self.tax_1_name = tax_data["tax_1_name"]
			self.tax_2_name = tax_data["tax_2_name"]
			self.tax_3_name = tax_data["tax_3_name"]
			self.tax_1_amount = tax_data["tax_1_amount"]
			self.tax_2_amount = tax_data["tax_2_amount"]
			self.tax_3_amount = tax_data["tax_3_amount"]
			self.taxable_amount_1 = tax_data["taxable_amount_1"]
			self.taxable_amount_2 = tax_data["taxable_amount_2"]
			self.taxable_amount_3 = tax_data["taxable_amount_3"]
			self.total_tax = (self.tax_1_amount or 0 ) + (self.tax_2_amount or 0 ) + (self.tax_3_amount or 0 ) 
			self.total_rate = (self.rate or 0) - (self.discount_amount or 0) + self.total_tax
   

		



	 

