# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from collections import Counter
from operator import itemgetter


def execute(filters=None):
	data = get_data(filters)
	opening_balance = get_opening_balance(filters)
	group_ledger_name = get_opening_balance_data(filters)
	report_data = get_report_data(filters,data,opening_balance,group_ledger_name)
	return get_columns(filters),report_data,None,None, None

def get_columns(filters):
	columns =   [
		{"fieldname":"account_name", "label":"Account Code",'align':'left',"width":500,"show_in_report":1,},
		{"fieldname":"quantity", "label":"QTY",'align':'center',"width":50,"show_in_report":1},
		{"fieldname":"amount", "label":"Amount",'align':'right',"width":200,"show_in_report":1, "fieldtype":"Currency"},
	]
	return columns

def get_data(filters):
	sql = """
			select 
				name,
				reservation_stay,
				concat(parent_account_code, '  - ', parent_account_name) as parent_account_name,
				concat(account_group , '  - ' , account_group_name) as account_group_name,
				room_number,
				guest_name,
				transaction_number,
				reference_number,
				concat(account_code, '  - ',report_description) as account_name,
				amount * if(type='Debit',1,-1) as amount,
				report_quantity as quantity,
				owner,
				transaction_type,
				creation
			from `tabFolio Transaction` 
			where
				property = %(property)s and 
        		posting_date = %(start_date)s
			order by
				account_code_sort_order,
				name
		""".format(filters.property,filters.start_date)
	
	data =   frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_opening_balance(filters):
	sql = """
		select
			ifnull(sum(amount*if(type='Debit',1,-1)),0) as amount,
			transaction_type
    	from `tabFolio Transaction` 
    	where
			property = %(property)s and 
        	posting_date < %(start_date)s
		""".format(filters.property,filters.start_date)
	data1 =   frappe.db.sql(sql,filters,as_dict=1)
	return data1

def get_opening_balance_data(filters):
	ledger_type = get_ledger_types()
	ledger_types = [l for l in ledger_type]
	for d in ledger_types:
		sql = """
			select
				ifnull(sum(amount*if(type='Debit',1,-1)),0) as amount,
				transaction_type
			from `tabFolio Transaction` 
			where
				property = '{}' and 
				transaction_type = '{}' and
				posting_date < '{}'
			""".format(filters.property,d['value'],filters.start_date)
	data2 =   frappe.db.sql(sql,filters,as_dict=1)
	return data2

def get_ledger_types():
	return [
		{"label": "Guest Ledger","value":"Reservation Folio" },
    	{"label": "Deposit Ledger","value":"Deposit Ledger" },
    	{"label": "Desk Folio","value":"Desk Folio" },
    	{"label": "Payable Ledger","value":"Payable Ledger" },
    	{"label": "City Ledger","value":"City Ledger" },
    	{"label": "POS","value":"Cashier Shift" }
		]


def get_report_data(filters,data,data1,data2):
	report_data = []
	ledger_type = get_ledger_types()
	
	opening_balance = sorted(set([d['amount'] for d in data1]))
	
	ledger_types = [l for l in ledger_type]
	
	report_data.append({
		"indent":0,
		"account_name":"Opening Balance",
		"amount":opening_balance,
	})

	if filters.group_by_ledger_name:
		
		for l in ledger_types:
			group_account_name = sorted(set(d['account_group_name'] for d in data if d['transaction_type']==l['value']))
			opening_balance_data = sorted(set(d['amount'] for d in data2))
			
			if len(group_account_name) > 0 :
				report_data.append({
					"indent":0,
					"account_name":l['label'],
				})
				report_data.append({
					"indent":0,
					"account_name":l['label'] + " Opening Balance",
					"amount": opening_balance_data
				})
				for d in group_account_name:
					report_data.append({
						"indent":0,
						"account_name":d,
					})
					parent_account_name = sorted(set(g['parent_account_name'] for g in data if g['account_group_name'] == d and g['transaction_type']==l['value']))
					
					for p in parent_account_name:
						account_name = sorted(set([d["account_name"] for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']]))
						if filters.show_account_code == 1:
							report_data.append({
								"indent": 1,
								"account_name": p,
								
							})
							
							for a in account_name:
								report_data.append({
									"indent": 2,
									"account_name": a,
									"quantity":len([d["quantity"] for d in data if d["account_name"] == a]),
									"amount":sum([d["amount"] for d in data if d["account_name"] == a])
									
								})
								# report_data = report_data + ([d.update({"indent":2,}) or d for d in data if d['parent_account_name'] == p])
						else:
							code, description = p.split("  - ", 1)
							report_data.append({
								"indent": 1,
								"account_name": description,
			
							})
							for a in account_name:
								code, description = a.split("  - ", 1)
								report_data.append({
									"indent": 2,
									"account_name": description,
									"quantity":len([d["quantity"] for d in data if d["account_name"] == a]),
									"amount":sum([d["amount"] for d in data if d["account_name"] == a])
									
								})
							
						report_data.append({
							"indent":1,
							"account_name":" *Total " + p,
							"quantity": len([d["quantity"] for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']]),
							"amount": sum([d["amount"] for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']])
						})
					report_data.append({
						"indent":0,
						"account_name":" **Total " + d,
						"quantity": len([f["quantity"] for f in data if f['account_group_name'] == d and f['transaction_type']==l['value']]),
						"amount": sum([f["amount"] for f in data if f['account_group_name'] == d and f['transaction_type']==l['value']])
					})
					report_data.append({
							"indent":0,
							"account_name": "",
							"is_separator":1})
				report_data.append({
					"indent":0,
					"account_name":l['label'] + " Ending Balance",
					"amount":opening_balance_data[0] + sum([f["amount"] for f in data if f['transaction_type']==l['value']]),
				})
				report_data.append({
							"indent":0,
							"account_name": "",
							"is_separator":1})
						
	else:
		group_account_name = sorted(set([d['account_group_name'] for d in data]))
		for d in group_account_name:
			report_data.append({
				"indent":0,
				"account_name":d,
			})
			parent_account_name = sorted(set(g['parent_account_name'] for g in data if g['account_group_name'] == d))
					
			for p in parent_account_name:
				account_name = sorted(set([d["account_name"] for d in data if d['parent_account_name'] == p]))
				if filters.show_account_code == 1:
					report_data.append({
								"indent": 1,
								"account_name": p,
								
					})
							
					for a in account_name:
						report_data.append({
									"indent": 2,
									"account_name": a,
									"quantity":len([d["quantity"] for d in data if d["account_name"] == a]),
									"amount":sum([d["amount"] for d in data if d["account_name"] == a])
									
						})
								# report_data = report_data + ([d.update({"indent":2,}) or d for d in data if d['parent_account_name'] == p])
				else:
					code, description = p.split("  - ", 1)
					report_data.append({
								"indent": 1,
								"account_name": description,
			
					})
					for a in account_name:
						code, description = a.split("  - ", 1)
						report_data.append({
							"indent": 2,
							"account_name": description,
							"quantity":len([d["quantity"] for d in data if d["account_name"] == a]),
							"amount":sum([d["amount"] for d in data if d["account_name"] == a])
									
						})
							
				report_data.append({
					"indent":1,
					"account_name":" *Total " + p,
					"quantity": len([d["quantity"] for d in data if d['parent_account_name'] == p]),
					"amount": sum([d["amount"] for d in data if d['parent_account_name'] == p])
				})
			report_data.append({
				"indent":0,
				"account_name":" **Total " + d,
				"quantity": len([f["quantity"] for f in data if f['account_group_name'] == d]),
				"amount": sum([f["amount"] for f in data if f['account_group_name'] == d])
			})
			report_data.append({
					"indent":0,
					"account_name": "",
					"is_separator":1})
	report_data.append({
		"indent":0,
		"account_name":"Ending Balance",
		"amount":opening_balance[0] + sum([f["amount"] for f in data]),
	})

	return report_data