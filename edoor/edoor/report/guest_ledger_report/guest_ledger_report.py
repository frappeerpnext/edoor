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



	validate(filters)
	report_data = []
	skip_total_row=False
	message=None


	folio_transaction_amount_data =  get_folio_transaction_amount(filters)
	report_data = get_report_data(folio_transaction_amount_data,filters) 
	return get_columns(filters), report_data, message, None, get_report_summary(folio_transaction_amount_data,filters),skip_total_row
 
def validate(filters):
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))


				

def get_columns(filters):
	
	columns = [
		{'fieldname':'name','label':'Folio Number','fieldtype':'Link','options':"Reservation Folio",'align':'center',"header_class":'text-center','post_message_action':"view_folio_detail","default":True},
		 {'fieldname':'posting_date','label':'Date','fieldtype':'Date','align':'center',"header_class":'text-center',"default":True},
		{'fieldname':'reservation','label':'Reservation #','fieldtype':'Link','options':"Reservation",'align':'center',"header_class":'text-center','post_message_action':"view_reservation_detail","default":True},
		{'fieldname':'reservation_stay','label':'Stay #','fieldtype':'Link','options':"Reservation Stay",'align':'center',"header_class":'text-center','post_message_action':"view_reservation_stay_detail","default":True},
		{'fieldname':'business_source','label':'Source',"default":True},
		{'fieldname':'room_types','label':'Room Type',"default":True},
		  {'fieldname':'rooms','label':'Rooms',"align":'center',"header_class":'text-center',"default":True},
		 {'fieldname':'guest','label':'Guest','fieldtype':'Link',"options":"Customer","align":'center','extra_field':'guest_name', 'extra_field_separator':'-','post_message_action':"view_guest_detail","default":True},
		 {'fieldname':'guest_name','label':'Guest Name'},
		{'fieldname':'phone_number','label':'Phone #',"default":True},
		{'fieldname':'email','label':'Email',"default":True},
		{'fieldname':'debit','label':'Debit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'credit','label':'Credit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'balance','label':'Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'is_master','label':'Master Folio',"fieldtype":"check","default":True}
	]
	 

	return columns

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
	filters.folio_numbers = folio_numbers or []
	if filters.folio_numbers:
		sql="""select 
			name,
			posting_date,
			reservation,
			reservation_stay,
			reservation_status,
			business_source,
			rooms,
			room_types,
			status,
			is_master,
			guest,
			guest_name,
			phone_number,
			email,
			total_debit as debit,
			total_credit as credit,
			balance as balance

		from `tabReservation Folio`
		where
				concat(name,' ',reservation ,' ',reservation_stay , ' ' , ifnull(rooms,'') , ' ' , 'guest', ' ', guest_name, ' ',ifnull(phone_number,''), ' ' ,ifnull(email,'')) like '%{0}%' and 
				property = %(property)s and 

				business_source = if(%(business_source)s='',business_source,%(business_source)s)  and 
				guest = if(%(guest)s='',guest,%(guest)s)  and 
				is_master = if(%(is_master)s=0,is_master,1) and 
				name in %(folio_numbers)s
			order by  {1} {2} 
		""".format(filters.keyword or '',filters.order_by,filters.order_type)
		
		data = frappe.db.sql(sql,filters,as_dict=1)
		for t in data:
			t["credit"] = sum([d["credit"] for d in  folio_transaction_amount if d["transaction_number"] == t["name"]]) or 0
			t["debit"] = sum([d["debit"] for d in  folio_transaction_amount if d["transaction_number"] == t["name"]]) or 0
			t["balance"] = t["debit"] - t["credit"]

		return data
	return []
 

def get_report_summary(filio_transaction_amount,filters):

	report_summary=[]
	
	sql="select sum(amount * if(type='Credit',-1,1)) as amount from `tabFolio Transaction` where posting_date<'{}' and transaction_type='Reservation Folio'".format(filters.start_date)
	data = frappe.db.sql(sql,as_dict=1) 
	opening_balance = 0.00
	credit = sum([d["credit"] for d in filio_transaction_amount]) or 0
	debit = sum([d["debit"] for d in filio_transaction_amount]) or 0

	if data:
		opening_balance= data[0]["amount"] or 0
	
	balance = opening_balance + debit
	balance = balance - credit
	
	report_summary.append({"label":"Opening Balance","value":opening_balance or 0,"indicator":"red"})	
	report_summary.append({"label":"Debit","value":debit or 0,"indicator":"blue"})	
	report_summary.append({"label":"Credit","value":credit or 0,"indicator":"blue"})	
	report_summary.append({"label":"Ending Balance","value":balance or 0,"indicator":"green"})	

	return report_summary
 
