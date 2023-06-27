# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

from edoor.api.frontdesk import get_working_day
import frappe
from frappe.model.document import Document

class ReservationFolio(Document):
	def validate(self):
		self.balance = (self.total_debit or 0) -( self.total_credit or 0)
		#validate working day 
		if self.is_new():
			working_day = get_working_day(self.property)
			if not working_day["name"]:
				frappe.throw("Please start working")
			
			if not working_day["cashier_shift"]["name"]:
				frappe.throw("Please start cashier shift")
			

			self.working_day = working_day["name"]
			self.working_date = working_day["date_working_day"]
			self.posting_date = self.working_date
			self.cashier_shift = working_day["cashier_shift"]["name"]


		if self.balance > 0 and self.status == "Closed":
			frappe.throw("Cannot close folio with balance is greater than 0")
	def on_update(self):
		if self.is_master==1:
			#reset other is master = 0
			frappe.db.sql("update `tabReservation Folio` set is_master=0 where is_master=1 and name<>'{}' and reservation_stay='{}'".format(self.name,self.reservation_stay))
