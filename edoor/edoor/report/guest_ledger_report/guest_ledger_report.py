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
	filters.status = filters.status or ''
	filters.status = '' if filters.status =='All Status' else filters.status
	filters.reservation_status = filters.reservation_status   or ''
	 

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
		{'fieldname':'opening_balance','label':'Opening Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'debit','label':'Debit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'credit','label':'Credit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'balance','label':'Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'is_master','label':'Master Folio','fieldtype':'Check',"header_class":'text-center',"default":True},
		{'fieldname':'status','label':'Status',"fieldtype":"status","default":True},
		{'fieldname':'reservation_status','label':'Res. Status',"fieldtype":"ReservationStatus","default":True},
		{'fieldname':'reservation_status_color' }
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
	filters.keyword = "%{}%".format(filters.keyword or "")
	if filters.folio_numbers:

		sql="""select 
			name,
			modified,
			creation,
			owner,
			posting_date,
			reservation,
			reservation_stay,
			reservation_status,
			reservation_status_color,
			business_source,
			rooms,
			room_types,
			status,
			is_master,
			guest,
			guest_name,
			phone_number,
			email,
			balance as balance

		from `tabReservation Folio`
		where
				concat(name,' ',reservation ,' ',reservation_stay , ' ' , ifnull(rooms,'') , ' ' , 'guest', ' ', guest_name, ' ',ifnull(phone_number,''), ' ' ,ifnull(email,'')) like %(keyword)s and 
				property = %(property)s and 

				business_source = if(%(business_source)s='',business_source,%(business_source)s)  and 
				guest = if(%(guest)s='',guest,%(guest)s)  and 
				ifnull(reservation,'') = if(%(reservation)s='',ifnull(reservation,''),%(reservation)s)  and 
				ifnull(reservation_stay,'') = if(%(reservation_stay)s='',ifnull(reservation_stay,''),%(reservation_stay)s)  and 
				status = if(%(status)s='',status,%(status)s)  and 
				reservation_status = if(%(reservation_status)s='',reservation_status,%(reservation_status)s)  and 
				is_master = if(%(is_master)s=0,is_master,1) and 
				name in %(folio_numbers)s
		""" 
		
		data = frappe.db.sql(sql,filters,as_dict=1)
		folio_opeing_balance = get_folio_opening_balance(filters)
		 
		for t in data:
			t["opening_balance"] =sum([d["balance"] for d in folio_opeing_balance if d["transaction_number"]==t["name"]])
			t["credit"] = sum([d["credit"] for d in  folio_transaction_amount if d["transaction_number"] == t["name"]]) or 0
			t["debit"] = sum([d["debit"] for d in  folio_transaction_amount if d["transaction_number"] == t["name"]]) or 0
			t["balance"] =t["opening_balance"] + (t["debit"] - t["credit"])

		return  sorted(data, key=lambda k: k[filters.order_by], reverse=True if filters.order_type=='desc' else False)
	return []
 

def get_folio_opening_balance(filters):
	sql="""select 
			transaction_number,
			sum(amount*if(type='Debit',1,-1)) as balance

		from `tabFolio Transaction`
		where
				transaction_type='Reservation Folio' and 
				property = %(property)s and 
				ifnull(business_source,'') = if(%(business_source)s='',ifnull(business_source,''),%(business_source)s)  and 
				ifnull(guest,'') = if(%(guest)s='',ifnull(guest,''),%(guest)s)  and 
				ifnull(reservation,'') = if(%(reservation)s='',ifnull(reservation,''),%(reservation)s)  and 
				ifnull(reservation_stay,'') = if(%(reservation_stay)s='',ifnull(reservation_stay,''),%(reservation_stay)s)  and 
				is_master_folio = if(%(is_master)s=0,is_master_folio,1) and 
				transaction_number in %(folio_numbers)s and 
				posting_date < %(start_date)s
		group by
			transaction_number
		"""
 
	if filters.folio_numbers:
		return frappe.db.sql(sql, filters,as_dict=1)
	else:
		return None
	
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
			ifnull(reservation,'') = if(%(reservation)s='',ifnull(reservation,''),%(reservation)s)  and 
			ifnull(reservation_stay,'') = if(%(reservation_stay)s='',ifnull(reservation_stay,''),%(reservation_stay)s)  and 
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
 
