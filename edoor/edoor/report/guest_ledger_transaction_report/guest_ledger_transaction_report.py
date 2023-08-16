# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	#validate 
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if (filters.end_date - filters.start_date).days > 30:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
	return get_columns(filters), get_report_data(filters),None, None,get_report_summary(filters)



def get_columns(filters):
	return [
		{'fieldname':'name','label':'Folio Tran. #','fieldtype':'Link','options':"Folio Transaction",'align':'center',"header_class":'text-center','post_message_action':"view_folio_transaction_detail","default":True},
		{'fieldname':'posting_date','label':'Date','fieldtype':'Date','align':'center',"header_class":'text-center',"default":True},
		{'fieldname':'reservation','label':'Reservation #','fieldtype':'Link','options':"Reservation",'align':'center',"header_class":'text-center','post_message_action':"view_reservation_detail","default":True},
		{'fieldname':'reservation_stay','label':'Stay #','fieldtype':'Link','options':"Reservation Stay",'align':'center',"header_class":'text-center','post_message_action':"view_reservation_stay_detail","default":True},
		{'fieldname':'account_name','label':'Account Name',"default":True},
		{'fieldname':'room_number','label':'Room ','align':'center',"header_class":'text-center',"default":True},
		{'fieldname':'guest','label':'Stay #','fieldtype':'Link','options':"Customer",'align':'center',"header_class":'text-center','post_message_action':"view_guest_detail","default":True},
		# {'fieldname':'business_source','label':'Source',"default":True},
		# {'fieldname':'room_types','label':'Room Type',"default":True},
		#   {'fieldname':'rooms','label':'Rooms',"align":'center',"header_class":'text-center',"default":True},
		#  {'fieldname':'guest','label':'Guest','fieldtype':'Link',"options":"Customer","align":'center','extra_field':'guest_name', 'extra_field_separator':'-','post_message_action':"view_guest_detail","default":True},
		#  {'fieldname':'guest_name','label':'Guest Name'},
		# {'fieldname':'phone_number','label':'Phone #',"default":True},
		# {'fieldname':'email','label':'Email',"default":True},
		{'fieldname':'debit','label':'Debit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'credit','label':'Credit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		
		# {'fieldname':'balance','label':'Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		# {'fieldname':'is_master','label':'Master Folio',"fieldtype":"check","default":True}
	]

def get_report_data(filters):
	sql ="""
		select 
			name ,
			posting_date,
			room_number,
			account_name,
			type,
			amount,
			reservation,
			reservation_stay,
			business_source,
			guest,
			guest_name,
			parent_account_name,
			reservation_status
		from `tabFolio Transaction` 
		where
			transaction_type='Reservation Folio'
	"""
	data = frappe.db.sql(sql, as_dict=1)
	for d in data:
		if d["type"]=="Debit":
			d["debit"] = d["amount"] or 0
		else:
			d["credit"] = d["amount"] or 0

	return data

def get_report_summary(filters):

	return[
		{"label":"Opening Balance","value":150},
		{"label":"Debit","value":150,"indicator":"red"},
		{"label":"Credit","value":150},
		{"label":"Ending Balance","value":150},
	] 