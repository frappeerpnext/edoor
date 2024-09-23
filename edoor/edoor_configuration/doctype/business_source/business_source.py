# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
class BusinessSource(Document):
	def validate(self):
		if self.is_new():
			if self.auto_create_city_ledger_account==1:
				if not self.city_ledger_type:
					frappe.throw("Please select city ledger type")

	def after_insert(self):
		if self.auto_create_city_ledger_account==1:
			doc = frappe.get_doc({
				'doctype': 'City Ledger',
				'property': self.property,
				'phone_number': self.phone_number,
				'email_address': self.email,
				"city_ledger_name":self.business_source,
				"business_source":self.business_source,
				"contact_name":self.contact_name,
				"city_ledger_type":self.city_ledger_type
			})
			doc.insert()
   
	def on_update(self):
		frappe.clear_document_cache('Business Source', self.name)
		if self.creation !=self.modified:
			update_fetch_from_fields(self)



def update_fetch_from_fields(self):
	if self.has_value_changed("business_source_type"):
		doctypes = ["Room Occupy","Revenue Forecast Breakdown","Reservation","Reservation Stay","Reservation Room Rate","Folio Transaction"]
		for d in doctypes:
			frappe.db.sql("update `tab{}` set business_source_type=%(business_source_type)s where business_source=%(business_source)s".format(d),{"business_source":self.name, "business_source_type":self.business_source_type})
		frappe.db.commit()


@frappe.whitelist()
def update_to_transaction():
	# room rate
	frappe.db.sql("""
		update `tabReservation Room Rate` a
		join `tabBusiness Source` b on b.name = a.business_source
		set a.business_source_type = b.business_source_type 
	""")
	# Folio Transaction
	frappe.db.sql("""
		update `tabFolio Transaction` a
		join `tabBusiness Source` b on b.name = a.business_source
		set a.business_source_type = b.business_source_type 
	""")

	# Revenue Forecast Breakdown
	frappe.db.sql("""
		update `tabRevenue Forecast Breakdown` a
		join `tabBusiness Source` b on b.name = a.business_source
		set a.business_source_type = b.business_source_type 
	""")
	
	# Room Occupy
	frappe.db.sql("""
		update `tabRoom Occupy` a
		join `tabBusiness Source` b on b.name = a.business_source
		set a.business_source_type = b.business_source_type 
	""")
	# Reservation
	frappe.db.sql("""
		update `tabReservation` a
		join `tabBusiness Source` b on b.name = a.business_source
		set a.business_source_type = b.business_source_type 
	""")

	# Reservation
	frappe.db.sql("""
		update `tabReservation Stay` a
		join `tabBusiness Source` b on b.name = a.business_source
		set a.business_source_type = b.business_source_type 
	""")

	frappe.db.commit()
	frappe.msgprint(_("Update successfully"))

