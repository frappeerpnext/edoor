import frappe
from frappe.utils import date_diff,today 
from frappe.utils.data import strip
import datetime
from frappe import _

def execute(filters=None): 
	filters.order_by = filters.order_by or 'modified'
	filters.order_type = filters.order_type or 'desc'
	filters.business_source= filters.business_source or ''
	filters.city_ledger_type= filters.city_ledger_type or ''
	
 
 



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
		{'fieldname':'name','label':'City Ledger Code','fieldtype':'Link','options':"City Ledger",'align':'center',"header_class":'text-center','post_message_action':"view_city_ledger_detail","default":True},
		{'fieldname':'business_source','label':'Source',"default":True},
		{'fieldname':'city_ledger_name','label':'City Ledger',"default":True},
		{'fieldname':'opening_balance','label':'Opening Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'debit','label':'Debit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'credit','label':'Credit', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
		{'fieldname':'balance','label':'Balance', 'fieldtype':'Currency',"header_class":'text-right',"default":True},
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
			transaction_type='City Ledger' and 
			property='{}'
		group by
			transaction_number
	""".format(filters.start_date,filters.end_date,filters.property)

	frappe.throw(sql)
	 
	return frappe.db.sql(sql, as_dict=1)


def get_report_data(folio_transaction_amount,filters):
	#get folio number from folio folio transaction
	city_ledger_codes = set([d["transaction_number"] for d in folio_transaction_amount])
	filters.city_ledger_codes = city_ledger_codes or []
	if filters.city_ledger_codes:

		sql="""select 
			name,
			modified,
			creation,
			owner,
			business_source,
			city_ledger_name,
			balance as balance
		from `tabCity Ledger` t
		where
				concat(name,' ', city_ledger_name) like '%{0}%' and 
				business_source = if(%(business_source)s='',business_source,%(business_source)s)  and 
				ifnull(city_ledger_type,'') = if(%(city_ledger_type)s='',ifnull(city_ledger_type,''),%(city_ledger_type)s)  and 
				name in %(city_ledger_codes)s 
		""".format(filters.keyword or '')
		
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
				transaction_type='City Ledger' and 
				property = %(property)s and 
				ifnull(business_source,'') = if(%(business_source)s='',ifnull(business_source,''),%(business_source)s)  and 
				ifnull(city_ledger_type,'') = if(%(city_ledger_type)s='',ifnull(city_ledger_type,''),%(city_ledger_type)s)  and 
				transaction_number in %(city_ledger_codes)s and 
				posting_date < %(start_date)s
		group by
			transaction_number
		"""
 
	if filters.city_ledger_codes:
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
			transaction_type='City Ledger' and
			property = %(property)s and 
			ifnull(business_source,'') = if(%(business_source)s='',ifnull(business_source,''),%(business_source)s)  and 
			ifnull(city_ledger_type,'') = if(%(city_ledger_type)s='',ifnull(city_ledger_type,''),%(city_ledger_type)s)  and 
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
 
