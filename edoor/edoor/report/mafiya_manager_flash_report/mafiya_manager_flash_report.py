# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_years
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import re
import copy


def execute(filters=None):
	# calculate date 
	filters.current={"start_date":filters.date,"end_date":filters.date}
	
	filters.mtd={"start_date":getdate(filters.date).replace(day=1),"end_date":filters.date}
	filters.ytd={"start_date":getdate(filters.date).replace(day=1, month=1),"end_date":filters.date}

	# last year current
	last_year_current= {}
	try:
		last_year_current["start_date"] = getdate(filters.date).replace(year=getdate(filters.date).year - 1)
	except ValueError:
		last_year_current["start_date"] = add_days(getdate(filters.date),-1).replace(year=getdate(filters.date).year - 1)
	last_year_current["end_date"] = last_year_current["start_date"] 
	filters.last_year_current=last_year_current
 
	# last year mtd
	last_year_mtd = {}
	try:
		last_year_mtd["start_date"] = getdate(filters.date).replace(day=1, year=getdate(filters.date).year - 1)
	except ValueError:
		last_year_mtd["start_date"]= add_days(getdate(filters.date),-1).replace(day=1,year=getdate(filters.date).year - 1)
		
	try:
		last_year_mtd["end_date"] = getdate(filters.date).replace( year=getdate(filters.date).year - 1)
	except ValueError:
		last_year_mtd["end_date"] = add_days(getdate(filters.date),-1).replace(year=getdate(filters.date).year - 1)
	filters.last_year_mtd=last_year_mtd
	
 
	# last year ytd
	last_year_ytd={}
	try:
		last_year_ytd["start_date"] = getdate(filters.date).replace(day=1,month=1, year=getdate(filters.date).year - 1)
	except ValueError:
		last_year_ytd["start_date"] = add_days(getdate(filters.date),-1).replace(day=1,month=1,year=getdate(filters.date).year - 1)
		
	try:
		last_year_ytd["end_date"] = getdate(filters.date).replace( year=getdate(filters.date).year - 1)
	except ValueError:
		last_year_ytd["end_date"]= add_days(getdate(filters.date),-1).replace(year=getdate(filters.date).year - 1)
	
	filters.last_year_ytd= last_year_ytd
 
  
 
	# frappe.throw(str(getdate(filters.date).replace(year=getdate(filters.date).year-1)))
	data = get_report_data(filters)

	return get_columns(filters), data

def get_columns(filters):
	
	return [
		{"fieldname": "title", "label": "Title", "width":500, "align":"left"},
		{"fieldname": "current", "label": "Current", "width":100, "align":"center"},
		{"fieldname": "mtd", "label": "MTD", "width":100, "fieldtype":"Data", "align":"center"},
		{"fieldname": "ytd", "label": "YTD", "width":100, "align":"center"},
		{"fieldname": "last_year_current", "label": "Current({})".format(getdate(filters.date).year - 1), "width":150, "align":"center"},
		{"fieldname": "last_year_mtd", "label": "MTD({})".format(getdate(filters.date).year - 1), "width":150, "fieldtype":"Data", "align":"center"},
		{"fieldname": "last_year_ytd", "label": "YTD({})".format(getdate(filters.date).year - 1), "width":150, "align":"center"},
		{"fieldname": "change_percentage", "label": "% Change", "width":150, "align":"center","fieldtype":"Percent"},
	]


def get_report_data(filters):
	
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Mafiya Manager Flash Report"} )
	report_data =  []
	taxable_room_sale = get_taxable_room_sale(filters)
	report_data.append(taxable_room_sale[0]['taxable_room_sale'])
	nontaxable_room_sale = get_nontaxable_room_sale(filters)
	report_data.append(nontaxable_room_sale[0]['nontaxable_room_sale'])
	adjustment_amount = get_adj_data(filters)
	report_data.append(adjustment_amount[0]['adjustment_amount'])
	total_posted = get_total_posted_data(filters)
	report_data.append(total_posted[0]['total_posted'])
        
	return_report_data = []
	#get group list
	groups = []
	for g in [d.group for d in report_config.row_configs]:
		if g not in groups:
			groups.append(g)
        
	for g in groups:
		if g != '':
			return_report_data.append({
				"title": g,
				"indent":0
			})
		for r in [d for d in report_config.row_configs if d.group == g and d.show_in_report==1]:
			row = [d for d in report_data if isinstance(d, dict) and d.get('title', 'No Title') == r.field_name]
			if r.formula:
				row=[get_row_calculate_filed(r,report_data)]
			

			if row:
				row = row[0]
				row["indent"] = 1
				row["is_bold"] = r.is_bold
				row["group"] = g
				row["title"] = r.custom_name or r.field_name
				
				if (  "last_year_ytd" in row and row["last_year_ytd"] or 0) ==0:
					row["change_percentage"] = 100
				else:
					row["change_percentage"] = (((row["ytd"] or 0 ) - (row["last_year_ytd"] or 0 )) / (row["last_year_ytd"] or 0 )) or 0
				
				return_report_data.append(row)
				row["fieldtype"] = r.fieldtype
			 
			else:
				return_report_data.append({
					"indent": 1,
					"title": r.custom_name or r.field_name
				})
    
    
		
    
	return format_result(return_report_data)

def format_result(data):
	for d in [x for x in data if 'fieldtype' in x and x["fieldtype"]]:
		for f in   ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]:
			if(d["fieldtype"]=="Percent"):
				d[f] = frappe.format(d[f]*100,{"fieldtype":d["fieldtype"]})
			else:
				d[f] = frappe.format(d[f],{"fieldtype":d["fieldtype"]})
	return data
            
def get_taxable_room_sale(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_data_fieldname({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"taxable_room_sale":{"title":"Taxable Room Sales"}
				
	}
	occupy_data = []
	for f in fields:
		row['taxable_room_sale'][f] = sum([y["taxable_room_sale"] for y in data if y["fieldname"]==f and y["taxable_room_sale"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_data_fieldname(filters):
	
	sql="""select 
			%(fieldname)s as fieldname, 
    		sum(amount * if (type='Debit',1,-1)) as taxable_room_sale 
		from `tabFolio Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and
			account_category in ('Room Charge','Room Tax','Room Discount','Service Charge') and property=%(property)s """

	return frappe.db.sql(sql,filters,as_dict=1)
def get_nontaxable_room_sale(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_notaxable({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"nontaxable_room_sale":{"title":"Non-Taxable Room Sales"}
				
	}
	occupy_data = []
	for f in fields:
		row['nontaxable_room_sale'][f] = sum([y["nontaxable_room_sale"] for y in data if y["fieldname"]==f and y["nontaxable_room_sale"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_notaxable(filters):
	
	sql="""select 
			%(fieldname)s as fieldname, 
    		sum(amount * if (type='Debit',1,-1)) as nontaxable_room_sale 
		from `tabFolio Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and
			total_tax = 0 and
			account_category in ('Room Charge','Room Discount','Service Charge') and property=%(property)s """

	return frappe.db.sql(sql,filters,as_dict=1)
def get_adj_data(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_adjustment({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"adjustment_amount":{"title":"Adjustment"}
				
	}
	occupy_data = []
	for f in fields:
		row['adjustment_amount'][f] = sum([y["adjustment_amount"] for y in data if y["fieldname"]==f and y["adjustment_amount"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_adjustment(filters):
	
	sql="""select 
			%(fieldname)s as fieldname, 
    		sum(amount * if (type='Debit',1,-1)) as adjustment_amount
		from `tabFolio Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and
			account_category = 'Room Charge Adjustment' and property=%(property)s """

	return frappe.db.sql(sql,filters,as_dict=1)
def get_total_posted_data(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_total_posted({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"total_posted":{"title":"Total Posted"}
				
	}
	occupy_data = []
	for f in fields:
		row['total_posted'][f] = sum([y["total_posted"] for y in data if y["fieldname"]==f and y["total_posted"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_total_posted(filters):
	
	sql="""select 
			%(fieldname)s as fieldname, 
    		sum(amount * if (type='Debit',1,-1)) as total_posted
		from `tabFolio Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and
			account_category in ('Room Charge','Room Tax','Room Discount','Service Charge') and property=%(property)s """

	return frappe.db.sql(sql,filters,as_dict=1)


def get_current_room_in_property(filters):
	sql = "select count(name) as total_room from `tabRoom` where property=%(property)s"
	total_room = frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"]
	
	filters.start_date = filters.mtd["start_date"]
	filters.end_date= filters.mtd["end_date"]
	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"

	mtd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
 
	filters.start_date = filters.ytd["start_date"]
	filters.end_date= filters.ytd["end_date"]

	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"

	ytd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0

	# Last Year current date 
	filters.start_date = filters.last_year_current["start_date"]
	filters.end_date= filters.last_year_current["end_date"]


	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"

	last_year_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
	
 	# last year MTD
	filters.start_date = filters.last_year_mtd["start_date"]
	filters.end_date= filters.last_year_mtd["end_date"]
	
	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"

	last_year_mtd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
	# last year YTD
	filters.start_date = filters.last_year_ytd["start_date"]
	filters.end_date= filters.last_year_ytd["end_date"]
	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"
	last_year_ytd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
	return {
			"title": "Total Rooms in Property",
			"current":total_room,
			"mtd": mtd_total_room,
			"ytd":ytd_total_room,
			"last_year_current":last_year_total_room,
			"last_year_mtd":last_year_mtd_total_room,
			"last_year_ytd":last_year_ytd_total_room,
			
	}

    
def get_row_calculate_filed(row,data):
	formula = row.formula
	 
	titles = re.findall(r"'([^']+)'", formula)
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
 
	result = {"title":row.field_name}
	for f in fields:
		formula_copy = copy.deepcopy(formula)
		for t in titles:
			n = get_value_field_title(data, t, f)
			formula_copy=formula_copy.replace("'{}'".format(t),str(n))
   
		result[f] =  eval(formula_copy)
  
	return result

def get_value_field_title(report_data, title,field):
	return sum([d[field] for d in report_data if isinstance(d, dict) and d.get("title") == title]) or 0
