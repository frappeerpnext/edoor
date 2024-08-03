# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns(filters)
	report_data = []
	if filters.group_by_ledger_type==1:
		report_data = get_report_data_group_by_ledger_type(filters)
	else:
		report_data = get_report_data(filters)
	return columns, report_data["report_data"], None, None, report_data["report_summary"]

def get_columns(filters):
	return [
		{"fieldname":"row_group", "label": "Account", "width":500,"fieldtype":"Data"},
		{"fieldname":"debit", "label": "Debit", "width":125, "fieldtype": "Currency", "align": "right"},
		{"fieldname":"credit", "label": "Credit", "width":125, "fieldtype": "Currency","align": "right"},
		{"fieldname":"net_total", "label": "Net Total", "width":125, "fieldtype": "Currency","align": "right"},
	]

def get_report_data(filters):
 
	report_data = []
	data =get_folio_transaction_data(filters,2)
	# all ledger opening balance
	opening_balance = get_opening_balance(filters=filters)
	report_data.append(opening_balance)
	#get account code level 1
	account_codes = get_account_codes()
	for g in [d for d in account_codes if d["parent_account_code"] =='All Account Code']:
		folio_transaction = [d for d in data if d["account_group"]==g["account_code"]]
		if len(folio_transaction)> 0:
			account_level_1 = {
				"row_group":  g["account_name"] if not filters.show_account_code else "{}-{}".format(g["account_code"],g["account_name"]),
				"indent": 0,
				"is_group": 1,
				"debit": sum([d["debit"] for d in folio_transaction ]),
				"credit": sum([d["credit"] for d in folio_transaction]),
				"net_total": sum([d["net_total"] for d in  folio_transaction]),
			}
			report_data.append(account_level_1)
			for c in [d for d in account_codes if d["parent_account_code"] ==g["account_code"]]:
				folio_transaction = [d for d in data if d["parent_account_code"]==c["account_code"]]
				if len(folio_transaction)> 0:
					report_data.append({
						"row_group": c["account_name"] if not  filters.show_account_code  else "{}-{}".format(c["account_code"],c["account_name"]),
						"indent": 1,
						"is_group": 1,
						"debit": sum([d["debit"] for d in data if d["parent_account_code"] == c["account_code"]]),
						"credit": sum([d["credit"] for d in data if d["parent_account_code"] == c["account_code"]]),
						"net_total": sum([d["net_total"] for d in data if d["parent_account_code"] == c["account_code"]]),
					})

					#data for level 3
					report_data = report_data  + folio_transaction


	grand_total_row = get_grand_total_row(data)
	report_data.append(grand_total_row)
	report_data.append(get_ending_balance(opening_balance, grand_total_row))
	return {"report_data": report_data, "report_summary": get_report_summary(filters, opening_balance, data)}

def get_report_data_group_by_ledger_type(filters):

	report_data = []
	data =get_folio_transaction_data(filters,3)
	# all ledger opening balance
	opening_balance = get_opening_balance(filters=filters)
	report_data.append(opening_balance)
	# property ledger 
	for l in ledger_type(filters):
		folio_transaction = [d for d in data if   d["transaction_type"] == l["value"]]
		report_data.append({
			"row_group": l["label"],
			"indent": 0,
			"is_group": 1,
			"debit": sum([d["debit"] for d in  folio_transaction]),
			"credit": sum([d["credit"] for d in  folio_transaction]),
			"net_total": sum([d["net_total"] for d in folio_transaction] ),
		})

		
		#get account code level 1
		account_codes = get_account_codes()
		for g in [d for d in account_codes if d["parent_account_code"] =='All Account Code']:
			folio_transaction = [d for d in data if d["account_group"]==g["account_code"] and d["transaction_type"] == l["value"]]
			if len(folio_transaction)> 0:
				account_level_1 = {
					"row_group":g["account_name"] if not filters.show_account_code   else "{}-{}".format(g["account_code"],g["account_name"]),
					"indent": 1,
					"is_group": 1,
					"debit": sum([d["debit"] for d in  folio_transaction]),
					"credit": sum([d["credit"] for d in  folio_transaction]),
					"net_total": sum([d["net_total"] for d in folio_transaction] ),
				}
				report_data.append(account_level_1)
				for c in [d for d in account_codes if d["parent_account_code"] ==g["account_code"]]:
					folio_transaction = [d for d in data if d["parent_account_code"]==c["account_code"] and d["transaction_type"] == l["value"]]
					if len(folio_transaction)> 0:
						report_data.append({
							"row_group":c["account_name"] if not filters.show_account_code   else "{}-{}".format(c["account_code"],c["account_name"]),
							"indent": 2,
							"is_group": 1,
							"debit": sum([d["debit"] for d in folio_transaction]),
							"credit": sum([d["credit"] for d in folio_transaction]),
							"net_total": sum([d["net_total"] for d in folio_transaction]),
						})

						#data for level 3
						report_data = report_data  + folio_transaction

	grand_total_row = get_grand_total_row(data)
	report_data.append(grand_total_row)
	report_data.append(get_ending_balance(opening_balance, grand_total_row))




	return {"report_data": report_data, "report_summary": get_report_summary(filters, opening_balance, data)}

def get_ending_balance(opening_balance, current_transaction):
	return {
		"row_group": "Ending Balance",
		"indent": 0,
		"is_group": 1,
		"debit": opening_balance["debit"] + current_transaction["debit"],
		"credit": opening_balance["credit"] + current_transaction["credit"],
		"net_total": (opening_balance["debit"] + current_transaction["debit"]) - (opening_balance["credit"] + current_transaction["credit"]) 
	}
def get_grand_total_row(data):
	return {
		"row_group": "Grand Total",
		"indent": 0,
		"is_group": 1,
		"debit":sum([d["debit"] for d in data]),
		"credit":sum([d["credit"] for d in data]),
		"net_total":sum([d["net_total"] for d in data]),
	}
def ledger_type(filters):
	ledger_types =  [
		{"label":"Guest Ledger", "value": "Reservation Folio"},
		{"label":"Deposit Ledger", "value": "Deposit Ledger"},
		{"label":"Desk Folio", "value": "Desk Folio"},
		{"label":"City Ledger", "value": "City Ledger"},
		{"label":"Payable Ledger", "value": "Payable Ledger"},
		{"label":"Food & Beverage", "value": "Cashier Shift"},
		
	]
	if filters.ledger_types:
		ledger_types = [d for d in ledger_types if d["value"] in filters.ledger_types]
	return ledger_types
	

def get_opening_balance(filters, ledger_type=None):
	sql = """select 
				'Opening Balance' as row_group,
				0 as indent,
				1 as is_group,
				ifnull(sum(amount*if(type='Debit',1,-1)),0) as net_total
			from `tabFolio Transaction`
			where 
				property = %(property)s and 
				posting_date < %(start_date)s  
			
	"""

	if filters.ledger_types:
		sql = sql + " and transaction_type in %(ledger_types)s "
	if filters.reservation_stay:
		sql = sql + " and reservation_stay  =  %(reservation_stay)s "

	if filters.reservation:
		sql = sql + " and reservation =  %(reservation)s "

	if filters.guest:
		sql = sql + " and guest  =  %(guest)s "
	
	if filters.city_ledger:
		sql = sql + " and transaction_type='City Ledger' and transaction_number=%(city_ledger)s "
 
	

	data = frappe.db.sql(sql,filters,as_dict=1)
	data[0]["credit"] = data[0]["net_total"] if data[0]["net_total"]<0 else 0
	data[0]["debit"] = data[0]["net_total"] if data[0]["net_total"]>0 else 0
	 


	return data[0]

def get_folio_transaction_data(filters,indent):

	amount_field = "total_amount"
	is_package_charge = "0"
	is_base_transaction="1"

	if filters.show_package_breakdown==1:
		amount_field = "transaction_amount"
		is_package_charge = "is_package_charge"
		is_base_transaction = "1"
	if filters.show_all_breakdown==1:
		amount_field = "amount"
		is_package_charge = "is_package_charge"
		is_base_transaction="is_base_transaction"
  
	sql = """select 
				{indent} as indent,
				{transaction_type}
				account_code,
				{row_group}  as row_group,
				parent_account_code,
				account_group,
				sum(if(type='Debit',{amount_field},0)) as debit,  
				sum(if(type='Credit',{amount_field},0)) as credit,
				sum({amount_field}*if(type='Debit',1,-1)) as net_total
			from `tabFolio Transaction`
			where 
				is_base_transaction = {is_base_transaction} and 
   				is_package_charge = {is_package_charge} and 
				property = %(property)s and 
				posting_date between %(start_date)s and %(end_date)s 
				{filter}
			group by 
				account_code,
				account_name,
				type,
				{indent},
				parent_account_code,
				account_group
			order by 
				account_code_sort_order
	"""

	filter = ""
	if filters.ledger_types:
		filter = filter + " and transaction_type in %(ledger_types)s "
	
	if filters.reservation_stay:
		filter = filter + " and reservation_stay  =  %(reservation_stay)s "

	if filters.reservation:
		filter = filter + " and reservation  =  %(reservation)s "
	
	if filters.guest:
		filter = filter + " and guest  =  %(guest)s "
	
	
	if filters.city_ledger:
		filter = filter + " and  transaction_type='City Ledger' and transaction_number=%(city_ledger)s "
	
	

	sql = sql.format(
		indent=indent, 
		transaction_type= "transaction_type," if filters.group_by_ledger_type==1 else "", 
		row_group="account_name" if not filters.show_account_code  else "concat(account_code,'-',account_name)",
		filter=filter,
		amount_field = amount_field,
		is_package_charge = is_package_charge,
		is_base_transaction=is_base_transaction
	)

 
	 
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data


def get_account_codes():
	sql ="select name as account_code, account_name, parent_account_code from `tabAccount Code` where is_group=1 order by sort_order"
	return frappe.db.sql(sql,as_dict=1)

def get_report_summary(filters, opening_data, data):
	if filters.show_summary:
		return [
			{"label": "Opening", "value": opening_data["net_total"],"datatype":"Currency"},
			{"label": "Debit", "value": sum([d["debit"] for d in data ]), "indicator": "blue","datatype":"Currency"},
			{"label": "Credit", "value": sum([d["credit"] for d in data ]), "indicator": "orange","datatype":"Currency"},
			{"label": "Balance", "value":  opening_data["net_total"] +  sum([d["debit"] -  d["credit"] for d in data ]), "indicator": "green","datatype":"Currency"},
			
		]
	return None