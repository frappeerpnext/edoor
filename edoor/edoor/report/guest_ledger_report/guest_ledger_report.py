from edoor.api.frontdesk import get_working_day
import frappe
from frappe.utils import date_diff,today 
from frappe.utils.data import strip
import datetime
from frappe import _

def execute(filters=None): 

	if not filters.property:
		frappe.throw("Please select property")
	
	working_day = get_working_day(filters.property) 

	filters.end_date = working_day["date_working_day"]
	filters.order_by = filters.order_by or 'modified'
	filters.order_type = filters.order_type or 'desc'
	
	filters.guest = filters.guest or ''
	filters.business_source= filters.business_source or ''
	filters.reservation= filters.reservation or ''
	filters.reservation_stay= filters.reservation_stay or ''

	
 
	report_data = []
	skip_total_row=False
	message=None

	report_data = get_report_data(filters) 
	summary = get_report_summary(filters)
	summary.append({"label": "Audit Date", "value": working_day["date_working_day"], "datatype":"Date" })
	return get_columns(filters), report_data, message, None, summary,skip_total_row
 
 		

def get_columns(filters):
	
	columns = [
		{'fieldname':'name','label':'Folio Number','fieldtype':'Link','options':"Reservation Folio","header_class":'text-center','post_message_action':"view_folio_detail","default":True,"show_in_report":1},
		{'fieldname':'posting_date','label':'Date','fieldtype':'Date','align':'center',"header_class":'text-center',"default":True,"show_in_report":1},
		{'fieldname':'reservation','label':'Reservation #','fieldtype':'Link','options':"Reservation","header_class":'text-center','post_message_action':"view_reservation_detail","default":True,"show_in_report":1},
		{'fieldname':'reservation_stay','label':'Stay #','fieldtype':'Link','options':"Reservation Stay","header_class":'text-center','post_message_action':"view_reservation_stay_detail","default":True,"show_in_report":1},
		{'fieldname':'business_source','label':'Source',"default":True,"show_in_report":1},
		{'fieldname':'room','label':'Room(s)',"default":True,"show_in_report":1,'align':'left'},
		{'fieldname':'guest_name', 'label':'Guest',"align":'left' ,"default":True,"show_in_report":1,"default":True},	
		{'fieldname':'phone_number','label':'Phone #',"default":False},
		{'fieldname':'debit','label':'Debit', 'fieldtype':'Currency',"header_class":'text-right',"default":True,"show_in_report":1,"align":'right'},
		{'fieldname':'credit','label':'Credit', 'fieldtype':'Currency',"header_class":'text-right',"default":True,"show_in_report":1,"align":'right'},
		{'fieldname':'balance','label':'Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True,"show_in_report":1,"align":'right'},
		{'fieldname':'status','label':'Status',"fieldtype":"status","default":True},
		{'fieldname':'reservation_status','label':'Res. Status',"fieldtype":"ReservationStatus","default":True,"show_in_report":1,'align':'center'},

	]
	 

	return columns

 
def get_report_data(filters):
	#get folio number from folio folio transaction

	filters.keyword = "%{}%".format(filters.keyword or "")

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
		concat(room_types,'/',rooms) as room,
		status,
		is_master,
		guest_name,
		guest,
		phone_number,
		email,
		total_credit as credit,
		total_debit as debit,
		balance as balance

	from `tabReservation Folio`
	where
			concat(name,' ',reservation ,' ',reservation_stay , ' ' , ifnull(rooms,'') , ' ' , 'guest', ' ', guest_name, ' ',ifnull(phone_number,''), ' ' ,ifnull(email,'')) like %(keyword)s and 
			property = %(property)s and 

			business_source = if(%(business_source)s='',business_source,%(business_source)s)  and 
			guest = if(%(guest)s='',guest,%(guest)s)  and 
			ifnull(reservation,'') = if(%(reservation)s='',ifnull(reservation,''),%(reservation)s)  and 
			ifnull(reservation_stay,'') = if(%(reservation_stay)s='',ifnull(reservation_stay,''),%(reservation_stay)s)  and 
			status ='Open' 
			
	""" 
	
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data
 


def get_report_summary(filters):

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
		
			posting_date < %(end_date)s
		"""
	data = frappe.db.sql(sql,filters,as_dict=1) 
	opening_balance = 0.00

	# get current transaction amount
	sql="""
		select 
			sum(if(type='Debit',0,amount)) as credit,
			sum(if(type='Credit',0,amount)) as debit
		from `tabFolio Transaction`
		where 
			transaction_type='Reservation Folio' and
			property = %(property)s and 
			ifnull(business_source,'') = if(%(business_source)s='',ifnull(business_source,''),%(business_source)s)  and 
			ifnull(guest,'') = if(%(guest)s='',ifnull(guest,''),%(guest)s)  and 
			ifnull(reservation,'') = if(%(reservation)s='',ifnull(reservation,''),%(reservation)s)  and 
			ifnull(reservation_stay,'') = if(%(reservation_stay)s='',ifnull(reservation_stay,''),%(reservation_stay)s)  and 
	
			posting_date = %(end_date)s
	""".format(filters.start_date)

	current_data = frappe.db.sql(sql, filters, as_dict=1)

	
	credit = sum([d["credit"] or 0 for d in current_data ]) or 0
	debit = sum([d["debit"] or 0 for d in current_data]) or 0

	if data:
		opening_balance= data[0]["amount"] or 0
	
	balance = opening_balance + debit
	balance = balance - credit
	
	report_summary.append({"label":"Opening Balance","value":frappe.format_value(opening_balance or 0,"Currency"),"indicator":"red"})	
	report_summary.append({"label":"Debit","value":frappe.format_value(debit or 0,"Currency"),"indicator":"blue"})	
	report_summary.append({"label":"Credit","value":frappe.format_value(credit or 0,"Currency"),"indicator":"blue"})	
	report_summary.append({"label":"Ending Balance","value":frappe.format_value(balance or 0,"Currency"),"indicator":"green"})	

	return report_summary
 
