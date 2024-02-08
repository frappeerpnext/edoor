# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	data = get_data(filters)
	opening_balance = get_opening_balance(filters)
	group_ledger_name = get_opening_balance_data(filters)
	report_data = get_report_data(filters,data,opening_balance,group_ledger_name)
	return get_columns(filters),report_data,None,None, None

def get_columns(filters):
	columns =   [
		{"fieldname":"account_name", "label":"Account Code",'align':'left',"width":300,"show_in_report":1,},
		{"fieldname":"reservation_stay", "label":"Stay #",'align':'left', "fieldtype":"Link","options":"Reservation Stay","width":125,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{'fieldname':'reference_number','align':'left','label':'Ref #',"width":140,"show_in_report":1},
		{'fieldname':'name','label':'Tran #',"width":160,'fieldtype':'Link','options':"Folio Transaction","header_class":'text-center','post_message_action':"view_folio_transation_detail","default":True,"show_in_report":1},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":130,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{"fieldname":"guest_name", "label":"Guest Name",'align':'left',"width":130,"show_in_report":1},
		{"fieldname":"quantity", "label":"QTY",'align':'center',"width":50,"show_in_report":1},
		{"fieldname":"amount", "label":"Amount",'align':'right',"width":130,"show_in_report":1, "fieldtype":"Currency"},
		{'fieldname':'owner','label':'By','align':'center',"width":130,"show_in_report":1},
		{'fieldname':'creation','label':'Date','align':'left',"show_in_report":1,"width":120, "fieldtype":"Date"},
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

def get_filters(filters):
	sql = " and property=%(property)s and posting_date < %(start_date)s "

	return sql
def get_opening_balance(filters):
	sql = """
		select
			ifnull(sum(amount*if(type='Debit',1,-1)),0) as amount,
			transaction_type
    	from `tabFolio Transaction` ft
    	where
			1=1  
			{}
		""".format(get_filters(filters))
	data1 =   frappe.db.sql(sql,filters,as_dict=1)
	return data1

def get_opening_balance_data(filters):
	ledger_type = get_ledger_types()
	ledger_types = [l for l in ledger_type]
	for d in ledger_types:
		sql = """
			select
				ifnull(sum(amount*if(type='Debit',1,-1)),0) as amount
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
	# frappe.throw(str(opening_balance))
	ledger_types = [l for l in ledger_type]
	
	report_data.append({
		"indent":0,
		"account_name":"Opening Balance",
		"amount": opening_balance[0],
	})

	if filters.group_by_ledger_name:
		
		for l in ledger_types:
			group_account_name = sorted(set(d['account_group_name'] for d in data if d['transaction_type']==l['value']))
			
			opening_balance_data = sorted(set(d['amount'] for d in data2))
			# transc = sorted(set([d['transaction_type'] for d in data1 if d['transaction_type'] == l['value']]))
			# frappe.throw(str(opening_balance_data[0]))
			if len(group_account_name) > 0 :
				report_data.append({
					"indent":0,
					"account_name":l['label'],
				})
			
				report_data.append({
						"indent":0,
						"account_name":l['label'] + " Opening Balance",
						"amount": opening_balance_data[0] 
					})
				for d in group_account_name:
					report_data.append({
						"indent":0,
						"account_name":d,
					})
					parent_account_name = sorted(set(g['parent_account_name'] for g in data if g['account_group_name'] == d and g['transaction_type']==l['value']))
			
					for p in parent_account_name:
						if filters.show_account_code == 1:
							report_data.append({
								"indent": 1,
								"account_name": p,
							})
							report_data = report_data + ([d.update({"indent":2}) or d for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']])
						else:
							code, description = p.split("  - ", 1)
							report_data.append({
								"indent": 1,
								"account_name": description,
							})
							report_data = report_data + ([d.update({"indent": 2, "account_name": d["account_name"].split("  - ", 1)[1]}) or d for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']])
						report_data.append({
							"indent":1,
							"account_name":" *Total " + p,
							"quantity": sum([d["quantity"] for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']]),
							"amount": sum([d["amount"] for d in data if d['parent_account_name'] == p and d['transaction_type']==l['value']])
						})
					report_data.append({
						"indent":0,
						"account_name":" **Total " + d,
						"quantity": sum([f["quantity"] for f in data if f['account_group_name'] == d and f['transaction_type']==l['value']]),
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
				if filters.show_account_code == 1:
					report_data.append({
						"indent": 1,
						"account_name": p,
					})
					report_data = report_data + ([d.update({"indent":2}) or d for d in data if d['parent_account_name'] == p])
				else:
					code, description = p.split("  - ", 1)
					report_data.append({
						"indent": 1,
						"account_name": description,
					})
					report_data = report_data + ([d.update({"indent": 2, "account_name": d["account_name"].split("  - ", 1)[1]}) or d for d in data if d['parent_account_name'] == p])
				report_data.append({
					"indent":1,
					"account_name":" *Total " + p,
					"quantity": sum([d["quantity"] for d in data if d['parent_account_name'] == p]),
					"amount": sum([d["amount"] for d in data if d['parent_account_name'] == p])
				})

			report_data.append({
					"indent":0,
					"account_name":" **Total " + d,
					"quantity": sum([f["quantity"] for f in data if f['account_group_name'] == d]),
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