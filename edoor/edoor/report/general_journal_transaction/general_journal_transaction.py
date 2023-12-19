# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
 

def execute(filters=None):
 
	
	 
	 


	data = get_report_data(filters)
	summary = None
	if filters.show_summary ==1:
		summary = get_report_summary(data)

	return get_columns(filters), data, None,None, summary


def get_columns(filters):
	return[
		{"fieldname":"ledger","label":"Ledger/Date", "width":250},
		{"fieldname":"name", "label":"Tran #","fieldtype":"Link","options":"Folio Transaction", "width":150,},
		{"fieldname":"account", "label":"Account", "width":400},
		{"fieldname":"debit", "label":"Debit","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"credit", "label":"Credit","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"net_total", "label":"Net Total","fieldtype":"Currency", "width":100,"align":"right"},
	]

def get_data(filters):
	sql="""
		select 
			name,
			transaction_type, 
			date_format(posting_date,'%%d-%%m-%%Y') as ledger, 
			concat(account_code,'-',report_description ) as account, 
			if(type='Debit',amount,0) as debit,
			if(type='Debit',0,amount) as credit,
			1 as indent
		from `tabFolio Transaction`
		where
			property = %(property)s and 
			posting_date between %(start_date)s and %(end_date)s 
		"""
	# add additional filter
	if filters.ledger_type:
		sql = sql + " and transaction_type in %(ledger_type)s "
	if filters.room_type:
		sql = sql + " and room_type_id = %(room_type)s "

	if filters.business_source:
		sql = sql + " and business_source = %(business_source)s "
	
	if filters.guest:
		sql = sql + " and guest = %(guest)s "

	if filters.guest_type:
		sql = sql + " and guest_type = %(guest_type)s "
	
	if filters.business_source_type:
		sql = sql + " and business_source_type = %(business_source_type)s "
		
	if filters.reservation:
		sql = sql + " and reservation = %(reservation)s "

	if filters.reservation_stay:
		sql = sql + " and reservation_stay = %(reservation_stay)s "


	if filters.account_category:

		sql = sql + " and account_category = %(account_category)s "

	if filters.city_ledger:
		sql = sql + " and (transaction_number = %(city_ledger)s or (target_transaction_type='City Ledger' and target_transaction_number=%(city_ledger)s))"

	if filters.account_code:
		if filters.account_code != 'All Account Code':
			filters.account_codes =   get_account_codes(filters.account_code)
			sql = sql + " and account_code in %(account_codes)s"
 
	sql = sql + """
	order by 
		posting_date,
		name
	"""
	
	return  frappe.db.sql(sql, filters ,as_dict =1)

def get_report_data(filters):
	data = get_data(filters)
	report_data = []
	for l in ledger_type():
		transaction_data = [d for d in data if d["transaction_type"] == l["value"]]
		if len(transaction_data)> 0:
			report_data.append({
				"ledger":l["label"],
				"indent":0,
				"is_group":1,
				"debit": sum([d["debit"] for d in transaction_data]),
				"credit": sum([d["credit"] for d in transaction_data]),
				"net_total": sum([d["debit"] - d["credit"] for d in transaction_data])
			})
			report_data = report_data + transaction_data

			#add total row
			report_data.append({
					"ledger":"Total",
					"indent":1,
					"is_group":1,
					"debit": sum([d["debit"] for d in transaction_data]),
					"credit": sum([d["credit"] for d in transaction_data]),
					"net_total": sum([d["debit"] - d["credit"] for d in transaction_data])

			})


	if len(data)> 0:
		report_data.append({})
		report_data.append({
					"ledger":"Grand Total",
					"indent":0,
					"is_group":1,
					"debit": sum([d["debit"] for d in data]),
					"credit": sum([d["credit"] for d in data]),
					"net_total": sum([d["debit"] - d["credit"] for d in data])

			})



	return report_data

def ledger_type():
	return [
		{"label":"Guest Ledger", "value":"Reservation Folio"},
		{"label":"Deposit Ledger", "value":"Deposit Ledger"},
		{"label":"Desk Folio", "value":"Desk Folio"},
		{"label":"City Ledger", "value":"City Ledger"},
		{"label":"Payable Ledger", "value":"Payable Ledger"},
		{"label":"F&B", "value":"Cashier Shift"}
	]

def get_report_summary(data):
	return [
		{"label":"Debit",  "datatype": "Currency", "value":sum([d["debit"] for d in data if "debit" in d  and not "is_group" in d]), "indicator":"blue"},
		{"label":"Credit", "datatype": "Currency", "value":sum([d["credit"] for d in data  if "credit" in d and not "is_group" in d]), "indicator":"red"},
		{"label":"Net Total",  "datatype": "Currency","value":sum([d["debit"] - d["credit"] for d in data if  "debit" in d  and "credit" in d and not "is_group" in d]), "indicator":"green"}
	]

def get_account_codes(account_code):
	account_codes = [account_code]
	d = frappe.get_doc("Account Code", account_code)
	if d.is_group:
		account_codes = account_codes + get_account_code_children(account_code)
	return account_codes
		
def get_account_code_children(parent_account_code):
	
	account_codes = []
	sql = "select name,is_group from `tabAccount Code` where parent_account_code = '{}'".format(parent_account_code)
	data = frappe.db.sql(sql,as_dict=1)
	 
	for d in data:
		account_codes.append(d["name"])
		if d["is_group"]==1:
			
			x =  get_account_code_children(d["name"])
			
			account_codes = account_codes + x
	
	return account_codes
