# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff,today 
from frappe.utils.data import strip
import datetime
from frappe import _

def execute(filters=None): 
	filters.order_by = filters.order_by or 'modified'
	filters.order_type = filters.order_type or 'desc'
	filters.is_master = filters.is_master or 0
	filters.guest = filters.guest or ''
	filters.business_source= filters.business_source or ''
	filters.reservation= filters.reservation or ''
	filters.reservation_stay= filters.reservation_stay or ''
	filters.account_code = filters.account_code or ''
	filters.room_id = filters.room_id or ''



	validate(filters)
	report_data = []
	skip_total_row=False
	message=None


	folio_transaction_amount_data =  get_folio_transaction_amount(filters)
	report_data = get_report_data(folio_transaction_amount_data,filters) 
	return get_columns(), report_data, message, None, get_report_summary(folio_transaction_amount_data,filters),skip_total_row
 
def validate(filters):
	datediff = date_diff(filters.end_date, filters.start_date)
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if datediff > 30:
			frappe.throw("Your Max date for viewing transaction is only One Month.".format(filters.start_date, filters.end_date))


def get_columns():
	return [
		{'fieldname':'reservation','label':'Reservation #','fieldtype':'Link','options':"Reservation",'align':'center',"header_class":'text-center','post_message_action':"view_reservation_detail","default":True,"show_in_report":1},
		{'fieldname':'reservation_stay','label':'Stay #','fieldtype':'Link','options':"Reservation Stay",'align':'center',"header_class":'text-center','post_message_action':"view_reservation_stay_detail","default":True,"show_in_report":1},
		{'fieldname':'transaction_number','label':'Res # Folio','fieldtype':'Link','options':"Reservation Folio",'post_message_action':"view_folio_detail","default":True},
		{'fieldname':'name','label':'Folio Tran. #','fieldtype':'Link','options':"Folio Transaction",'align':'center','post_message_action':"view_folio_transaction_detail","default":True,"show_in_report":1},
		{'fieldname':'posting_date','label':'Date','fieldtype':'Date','align':'center',"header_class":'text-center',"default":True,"show_in_report":1},
		{'fieldname':'guest','label':'Guest',"default":True,"show_in_report":1},
		{'fieldname':'guest_name','label':'Guest Name',"default":True,"show_in_report":1},
		{'fieldname':'room_number','label':'Room ','align':'center',"header_class":'text-center',"default":True,"show_in_report":1},
		{'fieldname':'room_type','label':'Room Type',"default":True,"show_in_report":1},
		{'fieldname':'account_code', 'label': 'Account Code','extra_field':"account_name", 'extra_field_separator':"-",'header_class':"text-left" ,'default':True},
		{'fieldname':'business_source','label':'Source',"default":True,"show_in_report":1},
		{'fieldname':'parent_account_name','label':'Parent Account Name'},
		{'fieldname':'debit','label':'Debit', 'fieldtype':'Currency',"header_class":'text-right','align':'right',"default":True,"show_in_report":1},
		{'fieldname':'credit','label':'Credit', 'fieldtype':'Currency',"header_class":'text-right','align':'right',"default":True,"show_in_report":1},
		{'fieldname':'creation','label':'Creation','fieldtype':'Timeago',"default":True},
	]

def get_folio_transaction_amount(filters):
	sql="""
		select 
			transaction_number,
			sum(if(type='Debit',0,amount)) as credit,
			sum(if(type='Credit',0,amount)) as debit
		from `tabFolio Transaction`
		where
			posting_date between '{}' and '{}' and 
			transaction_type='Reservation Folio' 
		group by
			transaction_number
	""".format(filters.start_date,filters.end_date)

 
	 
	return frappe.db.sql(sql, as_dict=1)

def get_report_data(folio_transaction_amount,filters):
	#get folio number from folio folio transaction
	folio_numbers = set([d["transaction_number"] for d in folio_transaction_amount])
	filters.keyword = "%{}%".format(filters.keyword or "")
	filters.folio_numbers = folio_numbers or []
	return_culomn = [
					"if(ifnull(parent_reference,'') = '',name,parent_reference) as name",
					"modified",
					"creation",
					"owner",
					"posting_date",
					"room_number",
					"room_id",
					"room_type",
					"account_name",
					"transaction_number",
					"account_code",
					"type",
					"amount",
					"reservation",
					"business_source",
					"reservation_stay",
					"is_master_folio",
					"guest",
					"guest_name",
					"parent_account_name",
					"reservation_status"]
	if not filters.order_by in return_culomn and filters.order_by != "name":
		return_culomn.append(
			filters.order_by
		)
	if filters.folio_numbers:
		sql ="""
			select 
			{1}
			from `tabFolio Transaction` 
			where
				transaction_type='Reservation Folio' and
				property = %(property)s and 
				concat(name , ' ' ,' ',transaction_number ,' ', ifnull(room_number,'') , ' ', guest_name, ' ',account_code, ' ' ,account_name) like %(keyword)s and
				business_source = if(%(business_source)s='',business_source,%(business_source)s)  and 
				ifnull(reservation,'') = if(%(reservation)s='',ifnull(reservation,''),%(reservation)s)  and 
				ifnull(reservation_stay,'') = if(%(reservation_stay)s='',ifnull(reservation_stay,''),%(reservation_stay)s)  and 
				ifnull(account_code,'') = if(%(account_code)s='',ifnull(account_code,''),%(account_code)s)  and
				ifnull(room_id,'') = if(%(room_id)s='',ifnull(room_id,''),%(room_id)s)  and
				is_master_folio = if(%(is_master)s=0,is_master_folio,1)
				
		""".format(filters.keyword or '',','.join(return_culomn))
		data = frappe.db.sql(sql,filters,as_dict=1)
		for d in data:
			if d["type"]=="Debit":
				d["debit"] = d["amount"] or 0
			else:
				d["credit"] = d["amount"] or 0
		return  sorted(data, key=lambda k: k[filters.order_by], reverse=True if filters.order_type=='desc' else False)
	return []

def get_report_summary(filio_transaction_amount,filters):

	report_summary=[]
	
	sql="""
		select 
			sum(amount * if(type='Credit',-1,1)) as amount 
		from `tabFolio Transaction` 
		where 
			transaction_type='Reservation Folio' and
			property = %(property)s and 
			ifnull(business_source,'') = if(%(business_source)s='',ifnull(business_source,''),%(business_source)s)  and 
			ifnull(guest,'') = if(%(guest)s='',ifnull(guest,''),%(guest)s)  and 
			is_master_folio = if(%(is_master)s=0,is_master_folio,1) and 
			posting_date < %(start_date)s
		"""
	data = frappe.db.sql(sql,filters,as_dict=1) 
	opening_balance = 0.00
	credit = sum([d["credit"] for d in filio_transaction_amount]) or 0
	debit = sum([d["debit"] for d in filio_transaction_amount]) or 0

	if data:
		opening_balance= data[0]["amount"] or 0
	
	balance = opening_balance + debit
	balance = balance - credit
	
	report_summary.append({"label":"Opening Balance","value":frappe.format_value(opening_balance or 0,"Currency"),"indicator":"red"})	
	report_summary.append({"label":"Debit","value":frappe.format_value(debit or 0,"Currency"),"indicator":"blue"})	
	report_summary.append({"label":"Credit","value":frappe.format_value(credit or 0,"Currency"),"indicator":"blue"})	
	report_summary.append({"label":"Ending Balance","value":frappe.format_value(balance or 0,"Currency"),"indicator":"green"})	
	

	return report_summary