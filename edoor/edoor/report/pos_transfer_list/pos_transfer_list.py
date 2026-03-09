# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
 

def execute(filters=None):

	data = get_report_data(filters)
	summary = None
	if filters.show_summary ==1:
		summary = get_report_summary(filters)
	chart = get_chart(filters)
	return get_columns(filters), data, None,chart, summary


def get_columns(filters):
	return[
		{"fieldname":"reservation_stay", "label":"Stay #", "width":150,},
		{"fieldname":"name", "label":"Tran #", "width":150,},
		{"fieldname":"room", "label":"Room #","fieldtype":"Data","width":250,},
		{"fieldname":"posting_date", "label":"Date","fieldtype":"Date","width":150,'align':'center'},
		{"fieldname":"account", "label":"Account", "width":200},
		{"fieldname":"sale", "label":"Sale #", "width":200},
		{"fieldname":"guest_name", "label":"Guest", "width":150,},
		{"fieldname":"business_source", "label":"Source", "width":200},
		{"fieldname":"report_quantity", "label":"QTY", "width":100,'align':'center'},
		{"fieldname":"total_amount", "label":"Total Amount","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"modified_by", "label":"Modified","fieldtype":"Data", "width":150,"align":"center"},
		{"fieldname":"modified", "label":"Modified Date","fieldtype":"Datetime", "width":200,"align":"center"},
	]

def get_data(filters):
	sql="""
		select 
			name,
			transaction_type, 
			transaction_number,
			reservation,
			reservation_stay,
			business_source,
			reservation_type,
			concat(room_type,'/',room_number) as room,
			room_type,
			guest_name,
			guest_type,
			nationality,
			note,
			guest,
			posting_date, 
			concat(account_code,'-',report_description ) as account, 
			discount_amount  * if(type='Credit',-1,1) as discount_amount,
			total_tax * if(type='Credit',-1,1) as total_tax ,
			bank_fee_amount * if(type='Credit',-1,1) as bank_fee_amount,
			total_amount * if(type='Credit',-1,1) as total_amount,
		    amount * if(type='Credit',-1,1) as amount,
			report_quantity * if(type='Credit',-1,1) as report_quantity,
			type,
			account_code,
			account_group,
			parent_account_name,
			account_category,
			modified,
			account_name,
			parent_account_code,
			sale,
			SUBSTRING_INDEX(modified_by,'@',1) as modified_by,
			1 as indent
		from `tabFolio Transaction` ft
		where
			property = %(property)s and 
			posting_date between %(start_date)s and %(end_date)s and
			transaction_type in ('Reservation Folio','City Ledger','Desk Folio') and
			account_category in ('POS Bill to Room','POS Bill to City Ledger','POS Bill to Desk Folio')
		"""

	if filters.sale_number:
		sql = sql + " and ft.sale = %(sale_number)s "
	if filters.ledger_type:
		sql = sql + " and ft.transaction_type in %(ledger_type)s "

	if filters.account_code:
		if filters.account_code != 'All Account Code':
			filters.account_codes =   get_account_codes(filters.account_code)
			sql = sql + " and ft.account_code in %(account_codes)s"

	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)
	return  frappe.db.sql(sql, filters ,as_dict =1)
def get_order_field():
	return [
		{"label":"Account Code","field":"ft.account_code"},
		{"label":"Posting Date","field":"ft.posting_date"},
		{"label":"Transaction","field":"ft.name"},
		{"label":"Last Update On","field":"ft.modified"},
		]

def get_report_data(filters):
	
	data = get_data(filters)
	pos_bill_to_room = [d for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']
	pos_bill_to_city_ledger = [d for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']
	pos_bill_to_desk_folio = [d for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']
	# frappe.throw(str(pos_bill_to_room))
	report_data = []
	if pos_bill_to_room:
		report_data.append({
			"indent":0,
			"is_group":1,
			"reservation_stay":"POS Bill to Room",
			"transaction_type":[d["transaction_type"] for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']
		})
		report_data = report_data +  [d.update({"indent":1}) or d for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']
		report_data.append({
			"indent":0,
			"is_group":1,
			"reservation_stay":"Total",
			"transaction_type":[d["transaction_type"] for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room'],
			"report_quantity": sum([d["report_quantity"] for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']),
			"amount": sum([d["amount"] for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']),
			"discount_amount": sum([d["discount_amount"] for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']),
			"total_tax": sum([d["total_tax"]for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']),
			"total_amount": sum([d["total_amount"]for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room'])
		})
	if pos_bill_to_city_ledger:
		report_data.append({
				"indent":0,
				"is_group":1,
				"reservation_stay":"POS Bill to City Ledger",
				"transaction_type":[d["transaction_type"] for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']
			})
		report_data = report_data +  [d.update({"indent":1,"reservation_stay":d['transaction_number'],}) or d for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']
		report_data.append({
			"indent":0,
			"is_group":1,
			"reservation_stay":"Total",
			"transaction_type":[d["transaction_type"] for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger'],
			"report_quantity": sum([d["report_quantity"] for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']),
			"amount": sum([d["amount"] for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']),
			"discount_amount": sum([d["discount_amount"] for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']),
			"total_tax": sum([d["total_tax"]for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']),
			"total_amount": sum([d["total_amount"]for d in data if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger'])
		})
	if pos_bill_to_desk_folio:
		report_data.append({
				"indent":0,
				"is_group":1,
				"reservation_stay":"POS Bill to Desk Folio",
				"transaction_type":[d["transaction_type"] for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']
			})
		report_data = report_data +  [d.update({"indent":1,"reservation_stay":d['transaction_number']}) or d for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']
		report_data.append({
			"indent":0,
			"is_group":1,
			"reservation_stay":"Total",
			"transaction_type":[d["transaction_type"] for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio'],
			"report_quantity": sum([d["report_quantity"] for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']),
			"amount": sum([d["amount"] for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']),
			"discount_amount": sum([d["discount_amount"] for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']),
			"total_tax": sum([d["total_tax"]for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']),
			"total_amount": sum([d["total_amount"]for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio'])
		})
	report_data.append({
					"reservation_stay":"Grand Total",
					"indent":0,
					"is_total_row":1,
					"report_quantity": sum([d["report_quantity"] for d in data if d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']]),
					"amount": sum([d["amount"] for d in data if d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']]),
					"discount_amount": sum([d["discount_amount"] for d in data if d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']]),
					"total_tax": sum([d["total_tax"]for d in data if d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']]),
					"total_amount": sum([d["total_amount"]for d in data if d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']])

			})

	return report_data

def get_report_summary(filters):
	data = get_data(filters)
	return [
		 {"label":"Total QTY",  "datatype": "Int", "value":sum([d["report_quantity"] for d in data if d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']]), "indicator":"blue"},
		 {"label":"Total Bill to Room",  "datatype": "Currency", "value":sum([d["amount"] for d in data if d['transaction_type']=='Reservation Folio' and d['account_category']=='POS Bill to Room']), "indicator":"blue"},
		 {"label":"Total Bill to City Ledger", "datatype": "Currency", "value":sum([d["amount"] for d in data  if d['transaction_type']=='City Ledger' and d['account_category']=='POS Bill to City Ledger']), "indicator":"red"},
		 {"label":"Total Bill to Desk Folio",  "datatype": "Currency","value":sum([d["amount"] for d in data if d['transaction_type']=='Desk Folio' and d['account_category']=='POS Bill to Desk Folio']), "indicator":"green"},
		 {"label":"Total Amount",  "datatype": "Currency","value":sum([d["total_amount"] for d in data if  d['transaction_type'] in ['Desk Folio','City Ledger','Reservation Folio'] and d['account_category'] in ['POS Bill to Desk Folio','POS Bill to City Ledger','POS Bill to Room']]), "indicator":"green"}
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
# def get_group_by_column(filters):
 
# 	return  [d for d in group_by_columns() if d["label"] == filters.row_group][0]

def group_by_columns():
	
	return [
		{"data_field":"posting_date", "label":"Date","fieldtype":"Date"},
		{"data_field":"account_name", "label":"Account Code","fieldtype":"Data"},
		{"data_field":"transaction_type", "label":"Ledger Type" ,"fieldtype":"Data" },
		{"data_field":"guest_type", "label":"Guest Type" ,"fieldtype":"Data" },
		{"data_field":"nationality", "label":"Nationality" ,"fieldtype":"Data" },

	]

def get_field(filters):
 
	return  [d for d in group_by_columns() if d["label"] == filters.view_chart_by][0]	

def get_chart_series():
	return [
		{"data_field":"report_quantity","label":"Quantity","short_label":"QTY", "fieldtype":"Int", "align":"center","chart_color":"#dc9819"},
		{"data_field":"amount","label":"Amount", "short_label":"Amount", "fieldtype":"Currency", "align":"right","chart_color":"#1987dc"},
		
	]
def get_chart(filters):
	currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
	data = get_data(filters)
	chart_series = filters.get("chart_series")
	if filters.chart_type=="None" or not chart_series or not  filters.view_chart_by:
		return None

	dataset = []
	colors = []

	report_fields = get_chart_series()
	group_column = get_field(filters)

	group_data = sorted(set([d[group_column["data_field"]] for d  in data]))

	for d in chart_series:
		field = [x for x in report_fields if x["label"] == d][0]
		

		dataset_values = []
		for g in group_data: 
			amount = sum([d[field["data_field"]] for d in data if d[group_column["data_field"]] == g])
			
			if field["fieldtype"]  =="Currency":
				amount = round(amount,int(currency_precision))


			dataset_values.append(
				amount
			)



		dataset.append({'name':field["label"],'values':dataset_values})
		colors.append(field["chart_color"])

 
	chart = {
		'data':{
			'labels': [frappe.format(d,{"fieldtype":group_column["fieldtype"]}) for d in  group_data] ,
			'datasets':dataset
		},
		"type": filters.chart_type,
		# "lineOptions": {
		# 	"regionFill": 1,
		# },
		'valuesOverPoints':1,
		"axisOptions": {"xIsSeries": 1},
		
	}
	return chart