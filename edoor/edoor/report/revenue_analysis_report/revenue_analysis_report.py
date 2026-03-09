# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import calendar
import json
report_config = None
precission = 2
float_precission = 2

occupy_data = None
revenue_data  =None
months = None

def execute(filters=None):
			
	if not filters.property:
		filters.property = frappe.defaults.get_user_default("business_branch")
	if not filters.property: 
		business_branch = frappe.db.get_list("Business Branch",pluck="name")
		if not filters.property and len(business_branch)>1:
			frappe.throw(_("Please select property"))
		else:
			filters.property = business_branch[0]

	global report_config
	report_config = frappe.get_cached_doc("Report Configuration", frappe.db.exists("Report Configuration",{"property":filters.property, "report":"Revenue Analysis Report"}))
	
	global 	float_precission 
	float_precission = int( frappe.get_cached_value("System Settings",None,"float_precision"))
 
	columns = get_columns(filters)
	report_data = get_report_data(filters)
	report_summary = get_report_summary(filters)
 
	return columns,report_data,"",get_report_chart(filters), report_summary

def get_columns(filters):
	columns = [
		{
			"label":_(filters.row_group),"fieldname":"row_group","width":200
		}

	]
	months = get_months(filters)
	for d in months:
		columns.append({
			"label":d.get("month_text"),
			"fieldname":"month_{}_{}".format(d.get("month"),d.get("year")),
			"align":"right",
			"width":100

		})
	# total column
	columns.append({
			"label":"Total",
			"fieldname":"total",
			"align":"right",
			"width":100
		})
	return columns

def get_months(filters):
	sql = "select distinct date_format(date,'%%b') as month_text,month(date) as month, year(date) as year from `tabDates` where date between %(start_date)s and %(end_date)s"
	data = frappe.db.sql(sql,filters,as_dict =1)
	return data

def get_report_data(filters):
	global occupy_data
	global revenue_data
	global months
 
	report_data = []
	months = get_months(filters)
	occupy_data = get_occupy_data(filters)
	revenue_data = get_room_revenue_data(filters)
	
	total_rooms = get_total_room(filters)

	for b in get_row_group():
		parent_row = {
			"row_group":b,
			"indent":0,
			"is_group":1
		}
		
		
		report_data.append(parent_row)
		# get_room_night_sold_record return occupy row and avg per night row
		occupy_rows = get_room_night_sold_record(row_group=b , data = occupy_data,months = months,total_rooms=total_rooms)
		report_data = report_data +  occupy_rows 
		report_data = report_data +  get_room_revenue_row(
      			row_group=b, 
         		data = revenue_data,
           		months = months,
             	occupy_row= occupy_rows[0]
		)
  

	# total row
	report_data = report_data + get_total_rows(
		months=months
	)
	
				
	return report_data


def get_report_summary(filters):
	if filters.show_summary:
		total_room_sold = sum([d.get("total_occupy") for d in occupy_data])
		total_revenue= sum([d.get("amount") for d in revenue_data])
		return  [
			{"label":_("Total Room Sold"),"value": total_room_sold,"indicator":"blue"},
			{"label":_("Total Revenue"),"value": total_revenue,"indicator":"green","datatype": "Currency"},
			{"label":_("ADR"),"value": total_revenue / max(total_room_sold,1),"indicator":"orange","datatype": "Currency",},
		]
	return []

def get_report_chart(filters):
    
	if filters.chart_type == "None":
		return None

	labels = []
	if filters.view_chart_by =="Month":
		if len(set([d.get("year") for d in months]) ) ==1:
			labels =  [d.get("month_text") for d in months] 
		else:
			labels =  ["{} - {}".format(d.get("month_text"), d.get("year")) for d in months] 
	else :
		labels = get_row_group()
	 
	room_sold = {
		"name":_("Room Sold"),
		"values":[]
	}
	room_revenue = {
		"name":_("Room Revenue"),
		"values":[]
	}
 
	average_rate = {
		"name":_("Average Rate"),
		"values":[]
	}
 
	datasets = []
	if filters.view_chart_by =="Month":
		for m in months:
			occupy = sum([d.get("total_occupy") or 0 for d in occupy_data if d.get("month")  == m.get("month") and d.get("year") == d.get("year")])
			room_sold.get("values").append(occupy)
			revenue = round( sum([d.get("amount") or 0 for d in revenue_data if d.get("month")  == m.get("month") and d.get("year") == d.get("year")]),precission)
			room_revenue.get("values").append(revenue)
			average_rate.get("values").append( round( revenue / max(occupy,1) , precission))
	else:
		for g in labels:
			occupy = sum([d.get("total_occupy") or 0 for d in occupy_data if d.get("row_group") == g])
			room_sold.get("values").append(occupy)
			revenue = round( sum([d.get("amount") or 0 for d in revenue_data if  d.get("row_group") == g]),precission)
			room_revenue.get("values").append(revenue)
			average_rate.get("values").append( round( revenue / max(occupy,1) , precission))
 
 
	datasets =  [room_sold, room_revenue,average_rate] 
	if filters.chart_series:
		datasets = [d for d in datasets if d.get("name") in filters.chart_series]
 
	chart =  {
		"data":{
			"labels": labels,
			"datasets":datasets
		},
		"type":  filters.chart_type,
		"lineOptions": {
			"regionFill": 1
		},
		"valuesOverPoints": 1,
		"axisOptions": {
			"xIsSeries": 1
		}
	}
	 
	return chart

def get_occupy_data(filters):
	
	sql= """
		select 
			date_format(date,'%%b') as month_text,
			month(date) as month, 
			year(date) as year,
			{row_group} as row_group,
			count(name) as total_occupy
		from `tabRoom Occupy`
		where
			type = 'Reservation' and
			coalesce(business_source,'') != '' and
			property = %(property)s and 
			date between %(start_date)s and %(end_date)s and 
			is_active = 1 
		group by
			date_format(date,'%%b'),
			month(date) , 
			year(date) ,
			{row_group} 
	""".format(row_group = get_report_group_key( filters.row_group))
	
	data = frappe.db.sql(sql, filters , as_dict=  1)
	
	return data



def get_room_revenue_data(filters):
	condition =  json.loads(report_config.other_setting).get("room_revenue_condition").get("condition")

	sql="""
		select 
			month(posting_date) as month, 
			year(posting_date) as year,
			{row_group} as row_group,
			sum(total_amount * if(type = 'Debit',1,-1)) as amount
		from `tabFolio Transaction` 
		where
			transaction_type = 'Reservation Folio' and 
			coalesce(business_source,'') != '' and
			property = %(property)s and 
			posting_date between %(start_date)s and %(end_date)s  and 
			{condition}
		group by 
			month(posting_date) ,
			year(posting_date) ,
			{row_group} 
	""".format(condition =condition, row_group = get_report_group_key( filters.row_group) )
 
	return frappe.db.sql(sql,filters,as_dict=1)

def get_room_night_sold_record( row_group, data=None,months=None,total_rooms=[]):
    data = data or []
    occupy_row = {
		"row_group": _("Total Room Night Sold"),
		"indent":1
	}
    avg_per_night_row = {
		"row_group": _("Avg Per Night"),
		"indent":1
	}
    
    occupancy_row = {
		"row_group": _("% Room Nights Sold"),
		"indent":1
	}
    
    for m in months:
        m["total_days"] = calendar.monthrange(m.get("year"), m.get("month"))[1]
        column_key = "month_{}_{}".format(m.get("month"),m.get("year"))
        occupy = sum([d.get("total_occupy") for d in data if d.get("month") == m.get("month") and d.get("year") == m.get("year") and d.get("row_group") == row_group] )
        occupy_row[column_key] = occupy

        avg_per_night_row[column_key] = round(occupy / m["total_days"],float_precission)
        
        occupancy_row["month_{}_{}".format(m.get("month"),m.get("year"))] = round( occupy / sum([d.get("total_occupy") for d in data]) * 100,float_precission)
        
    # total
    occupy_row["total"] = sum([d.get("total_occupy") for d in data if d.get("row_group") == row_group])
    avg_per_night_row["total"] = round( sum([d.get("total_occupy") for d in data if d.get("row_group") == row_group]) / sum([d.get("total_days") for d in months]),float_precission)
    occupancy_row["total"] =  round( sum([d.get("total_occupy") for d in data if d.get("row_group") == row_group]) / sum([d.get("total_occupy") for d in data]) * 100,float_precission)
    
    
    return [occupy_row,avg_per_night_row,occupancy_row]

def get_room_revenue_row( row_group, data=None,months=None,occupy_row=None):
	
	
	data = data or []
	revenue_row = {
		"row_group": _("Room Revenue"),
		"indent":1
	}
	adr = {
		"row_group": _("Average Room Rate"),
		"indent":1
	}
	
	percent_of_revenue = {
		"row_group": _("% of Revenue"),
		"indent":1
	}
	
	for m in months:
     
		column_key = "month_{}_{}".format(m.get("month"),m.get("year"))
		revenue =  sum([d.get("amount") for d in  data if d.get("month") == m.get("month") and d.get("year") == m.get("year") and d.get("row_group") == row_group]) or 0
		revenue_row[column_key] = "-" if  revenue  == 0 else frappe.format(revenue or 0 , {"fieldtype":"Currency"})
		# adr
		adr[column_key] = revenue / max(occupy_row.get(column_key) ,1)
		adr[column_key] = "-" if  adr[column_key]  == 0 else frappe.format(adr[column_key] , {"fieldtype":"Currency"})
		total_revenue = max(sum([d.get("amount") for d in data if d.get("month") == m.get("month") and d.get("year") == m.get("year") ]),1)
		percent_of_revenue[column_key] =  round(revenue / total_revenue * 100,float_precission)
 


	# total
	revenue =  sum([d.get("amount") for d in data if d.get("row_group") == row_group])
	revenue_row["total"] = frappe.format(revenue, {"fieldtype":"Currency"})

	adr["total"] =  total_revenue / max(occupy_row.get("total"),1)
	adr["total"] =  frappe.format(adr["total"], {"fieldtype":"Currency"})
	# get reveue by row gorup
	total_revenue = sum([d.get("amount") for d in data])
	percent_of_revenue["total"] = (revenue or 0)  / max(total_revenue,1)
	percent_of_revenue["total"] =  round(percent_of_revenue["total"] * 100 , float_precission)


	return [revenue_row,adr,percent_of_revenue]

def get_total_rows(months):
	
	room_sold_row = {
			"row_group":_("Total Night(s) Sold"),
   			"is_total_row":1,
      "indent":0

		}
	total_revenue_row = {
			"row_group":_("Total Revenue"),
   			"is_total_row":1,
      		"indent":0
		}
 
	average_rate = {
			"row_group":_("Average Rate"),
   			"is_total_row":1,
      		"indent":0
		}

	for  m in months:
		column_key ="month_{}_{}".format(m.get("month"),m.get("year")) 

		room_sold = sum([d.get("total_occupy") for d in occupy_data if d.get("month") ==m.get("month") and d.get("year") == m.get("year")])
		room_sold_row[column_key] = room_sold
		
		total_revenue = sum([d.get("amount") for d in revenue_data if d.get("month") ==m.get("month") and d.get("year") == m.get("year")])
		total_revenue_row[column_key] = total_revenue
		total_revenue_row[column_key] = "-" if total_revenue  == 0 else frappe.format(total_revenue , {"fieldtype":"Currency"})

		adr = total_revenue / max(room_sold,1)
		average_rate[column_key] =  "-" if adr == 0  else frappe.format(adr, {"fieldtype":"Currency"})

	total_room_sold =  sum([d.get("total_occupy") for d in occupy_data])
	room_sold_row["total"] = total_room_sold
	total_revenue = sum([d.get("amount") for d in revenue_data])
	total_revenue_row["total"] = frappe.format(total_revenue,{"fieldtype":"Currency"})
	
	average_rate["total"] = frappe.format(total_revenue / max(total_room_sold,1),{"fieldtype":"Currency"})
	return [[],room_sold_row,total_revenue_row,average_rate]


def get_row_group():
    data = set([d.get("row_group") for d in occupy_data] + [d.get("row_group") for d in revenue_data]) 
    
    return sorted(data)

               
def get_total_room(filters):
    sql = "select month(date) as month, year(date) as year, sum(total_room) as total_room from `tabDaily Property Data` where date between %(start_date)s and %(end_date)s group by month(date),year(date)"
    return frappe.db.sql(sql,filters,as_dict=1)

def get_report_group_key(row_group):
     
    data = [
        {"key":"room_type","label": "Room Type"},
        {"key":"business_source_type","label": "Business Source Type"},
        {"key":"business_source","label": "Business Source"},
        {"key":"business_source_group","label": "Business Source Group"},
        {"key":"reservation_type","label": "Reservation Type"},
        {"key":"guest_type","label": "Guest Type"},
        {"key":"nationality","label": "Nationality"},
        {"key":"room_number","label": "Room Number"},
        
	]
   
    return [d for d in data if d.get("label") == row_group][0].get("key")