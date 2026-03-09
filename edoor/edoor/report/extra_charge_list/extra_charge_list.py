# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
 

def execute(filters=None):

	data = get_report_data(filters)
	summary = None
	if filters.show_summary ==1:
		summary = get_report_summary(data)

	if filters.chart_type =='pie' or filters.chart_type=="donut":
		if len(filters.chart_series)!=1:
			frappe.throw(_("Please select only one series for the chart, either a pie or donut chart."))

	chart = get_chart(filters)
	return get_columns(filters), data, None,chart, summary


def get_columns(filters):
	return[
		{"fieldname":"reservation_stay", "label":"Stay #", "fieldtype":"Link","options":"Reservation Stay","width":150,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{"fieldname":"name", "label":"Tran #", "width":150,},
		{"fieldname":"room", "label":"Room #","fieldtype":"Data","width":250,},
		{"fieldname":"posting_date", "label":"Date","fieldtype":"Date","width":150,"align":"center"},
		{"fieldname":"account", "label":"Account", "width":400},
		{"fieldname":"guest_name", "label":"Guest", "width":150,},
		{"fieldname":"business_source", "label":"Source", "width":200},
		{"fieldname":"report_quantity", "label":"QTY", "width":100,"align":"center"},
		{"fieldname":"amount", "label":"Amount","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"discount_amount", "label":"Discount","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"total_tax", "label":"Tax","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"total_amount", "label":"Total Amount","fieldtype":"Currency", "width":100,"align":"right"},
		{"fieldname":"modified_by", "label":"Modified","fieldtype":"Data", "width":150,"align":"center"},
		{"fieldname":"modified", "label":"Modified Date","fieldtype":"Datetime", "width":200,"align":"center"},
	]

def get_data(filters):
	sql="""
		select 
			name,
			transaction_type, 
			reservation,
			reservation_stay,
			business_source,
			reservation_type,
			concat(room_type,'/',room_number) as room,
			room_type,
			room_number,
			guest_type,
			nationality,
			reservation_type,
			guest_name,
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
			creation,
			SUBSTRING_INDEX(modified_by,'@',1) as modified_by,
			1 as indent
		from `tabFolio Transaction` ft
		where
			property = %(property)s and 
			posting_date between %(start_date)s and %(end_date)s and
			account_group in ('10000','40000') and
			transaction_type = 'Reservation Folio' and
			ifnull(parent_reference,'') = '' and
			account_category not in ('Room Charge')
		"""

	if filters.account_category:

		sql = sql + " and ft.account_category = %(account_category)s "
	if filters.parent_account:

		sql = sql + " and ft.parent_account_code = %(parent_account)s "

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
		{"label":"Account Category","field":"ft.aaccount_category"},
		{"label":"Parent Account","field":"ft.parent_account_code"},
		{"label":"Transaction","field":"ft.name"},
		{"label":"Last Update On","field":"ft.modified"},
		]

def get_report_data(filters):
	
	data = get_data(filters)
	if filters.row_group:
		group_column = get_group_by_column(filters)
		group_data = sorted(set([d[group_column["data_field"]] for d  in data]))
		report_data = []
		for g in group_data:
			d = g
			if group_column["fieldtype"]=="Date":
				d  = frappe.format(g,{"fieldtype":"Date"})
			report_data.append({
					"reservation_stay":d,
					"indent":0,
					"is_group":1,
			})
			report_data = report_data + [d.update({"indent":1,"parent":id}) or d for d in data if d[group_column["data_field"]]==g]

			#add total row
			report_data.append({
					"reservation_stay":"Total",
					"indent":1,
					"is_group":1,
					"report_quantity": sum([d["report_quantity"] for d in data if d[group_column["data_field"]]==g]),
					"amount": sum([d["amount"] for d in data if d[group_column["data_field"]]==g]),
					"discount_amount": sum([d["discount_amount"] for d in data if d[group_column["data_field"]]==g]),
					"total_tax": sum([d["total_tax"]for d in data if d[group_column["data_field"]]==g]),
					"total_amount": sum([d["total_amount"]for d in data if d[group_column["data_field"]]==g])

			})
		report_data.append({
					"reservation_stay":"Grand Total",
					"indent":0,
					"is_group":1,
					"report_quantity": sum([d["report_quantity"] for d in data]),
					"amount": sum([d["amount"] for d in data]),
					"discount_amount": sum([d["discount_amount"] for d in data]),
					"total_tax": sum([d["total_tax"]for d in data]),
					"total_amount": sum([d["total_amount"]for d in data])

			})
		return report_data


	else:
		
		# frappe.throw(str(sum([d["amount"] for d in data])))
		# data.append({})
		data.append({
					"name":"Grand Total",
					"indent":0,
					"is_group":1,
					"report_quantity": sum([d["report_quantity"] for d in data]),
					"amount": sum([d["amount"] for d in data]),
					"discount_amount": sum([d["discount_amount"] for d in data]),
					"total_tax": sum([d["total_tax"]for d in data]),
					"total_amount": sum([d["total_amount"]for d in data])

			})

		return data

def get_report_summary(data):
	return [
		{"label":"QTY",  "datatype": "Int", "value":sum([d["report_quantity"] for d in data if "report_quantity" in d  and not "is_group" in d]), "indicator":"blue"},
		{"label":"Amount",  "datatype": "Currency", "value":sum([d["amount"] for d in data if "amount" in d  and not "is_group" in d]), "indicator":"blue"},
		{"label":"Discount", "datatype": "Currency", "value":sum([d["discount_amount"] for d in data  if "discount_amount" in d and not "is_group" in d]), "indicator":"red"},
		{"label":"Total Tax",  "datatype": "Currency","value":sum([d["total_tax"] for d in data if  "total_tax" in d and not "is_group" in d]), "indicator":"green"},
		{"label":"Total Amount",  "datatype": "Currency","value":sum([d["total_amount"] for d in data if  "total_amount" in d and not "is_group" in d]), "indicator":"green"}
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
def get_group_by_column(filters):
 
	return  [d for d in group_by_columns() if d["label"] == filters.row_group][0]

def group_by_columns():
	
	return [
		{"data_field":"posting_date", "label":"Date","fieldtype":"Date"},
		{"data_field":"account_name", "label":"Account Code","fieldtype":"Data"},
		{"data_field":"account_category", "label":"Account Category" ,"fieldtype":"Data" },
		{"data_field":"parent_account_name", "label":"Parent Account" ,"fieldtype":"Data" },
		{"data_field":"business_source", "label":"Business Source" ,"fieldtype":"Data" },
		{"data_field":"reservation_type", "label":"Reservation Type" ,"fieldtype":"Data" },
		{"data_field":"guest_type", "label":"Guest Type" ,"fieldtype":"Data" },
		{"data_field":"nationality", "label":"Nationality" ,"fieldtype":"Data" },
		{"data_field":"room_type", "label":"Room Type" ,"fieldtype":"Data" },
		{"data_field":"room_number", "label":"Room" ,"fieldtype":"Data" },
		
	]

def get_field(filters):
 
	return  [d for d in group_by_columns() if d["label"] == filters.view_chart_by][0]	

def get_chart_series():
	return [
		{"data_field":"report_quantity","label":"Quantity","short_label":"QTY", "fieldtype":"Int", "align":"center","chart_color":"#dc9819"},
		{"data_field":"amount","label":"Amount", "short_label":"Amount", "fieldtype":"Currency", "align":"right","chart_color":"#1987dc"},
		{"data_field":"discount_amount","label":"Discount Amount", "short_label":"Discount", "fieldtype":"Currency", "align":"right","chart_color":"#fd4e8a"},
		{"data_field":"total_tax","label":"Total Tax", "short_label":"Tax", "fieldtype":"Currency", "align":"right","chart_color":"#d7e528"},
		{"data_field":"total_amount","label":"Total Amount", "short_label":"Total Amount", "fieldtype":"Currency", "align":"right","chart_color":"#df7b5c"},
		
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