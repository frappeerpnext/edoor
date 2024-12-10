# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import calendar

def execute(filters=None):
	if not filters.property:
		filters.property = frappe.defaults.get_user_default("business_branch")
	if not filters.property: 
		business_branch = frappe.db.get_list("Business Branch",pluck="name")
		if not filters.property and len(business_branch)>1:
			frappe.throw(_("Please select property"))
		else:
			filters.property = business_branch[0]

	columns = get_columns(filters)
	report_data = get_report_data(filters)
	return columns,report_data

def get_columns(filters):
	columns = [
		{
			"lable":_("Business Source Type"),"fieldname":"row_group","width":200
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
	business_source_type = get_business_source_type(filters)
	report_data = []
	months = get_months(filters)
	occupy_data = get_occupy_data(filters)
	total_rooms = get_total_room(filters)

	for b in business_source_type:
		parent_row = {
			"row_group":b.get("name"),
			"indent":0,
			"is_group":1
		}
		
		
		report_data.append(parent_row)
		# get_room_night_sold_record return occupy row and avg per night row
		report_data = report_data +  get_room_night_sold_record(row_group=b.get("name") , data = occupy_data,months = months,total_rooms=total_rooms)

	# total row
	report_data = report_data + get_total_rows(
		occupy_data=occupy_data,
		months=months
	)
	
				
	return report_data

def get_occupy_data(filters):
    sql= """
		select 
			date_format(date,'%%b') as month_text,
   			month(date) as month, 
      		year(date) as year,
			business_source_type as row_group,
			count(name) as total_occupy
		from `tabRoom Occupy`
		where
			property = %(property)s and 
			date between %(start_date)s and %(end_date)s and 
			is_active = 1 
		group by
			date_format(date,'%%b'),
   			month(date) , 
      		year(date) ,
			business_source_type 
    """
    
    data = frappe.db.sql(sql, filters , as_dict=  1)
   
    return data


def get_room_revenue_data(filters):
    sql="""
		select 
			month(date) as month, 
      		year(date) as year,
			business_source_type as row_group,
			sum(total_amount * if(type = 'Debit',1,-1)) as amount
		from `tabFolio Transaction` 
		where
			property = %(property)s and 
			posting_date between %(start_date)s and %(end_date)s 
		group by 
			
   
    """    
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
        occupy = sum([d.get("total_occupy") for d in data if d.get("month") == m.get("month") and d.get("year") == m.get("year") and d.get("row_group") == row_group] )
        occupy_row["month_{}_{}".format(m.get("month"),m.get("year"))] = occupy
        avg_per_night_row["month_{}_{}".format(m.get("month"),m.get("year"))] = round(occupy / m["total_days"],2)
        
        # percentage of night sold
        total_room = sum([d.get("total_room") for d in total_rooms if d.get("month") == m.get("month") and d.get("year") ==m.get("year")])
        occupancy_row["month_{}_{}".format(m.get("month"),m.get("year"))] = round( occupy / sum([d.get("total_occupy") for d in data]) * 100,2)
        
    # total
    occupy_row["total"] = sum([d.get("total_occupy") for d in data if d.get("row_group") == row_group])
    avg_per_night_row["total"] = round( sum([d.get("total_occupy") for d in data if d.get("row_group") == row_group]) / sum([d.get("total_days") for d in months]),2)
    occupancy_row["total"] =  round( sum([d.get("total_occupy") for d in data if d.get("row_group") == row_group]) / sum([d.get("total_occupy") for d in data]) * 100,2)
    
    
    return [occupy_row,avg_per_night_row,occupancy_row]
    
def get_total_rows(occupy_data,months):
	
	room_sold_row = {
			"row_group":_("Total Night(s) Sold"),
   			"is_total_row":1,
      "indent":0

		}
	for  m in months:
		column_key ="month_{}_{}".format(m.get("month"),m.get("year")) 
		room_sold_row[column_key] = sum([d.get("total_occupy") for d in occupy_data if d.get("month") ==m.get("month") and d.get("year") == m.get("year")])
	room_sold_row["total"] = sum([d.get("total_occupy") for d in occupy_data])
	return [[],room_sold_row]
def get_business_source_type(filters):
    sql = "select name from `tabBusiness Source Type` order by name"
    return frappe.db.sql(sql,as_dict=1) 

def get_total_room(filters):
    sql = "select month(date) as month, year(date) as year, sum(total_room) as total_room from `tabDaily Property Data` where date between %(start_date)s and %(end_date)s group by month(date),year(date)"
    return frappe.db.sql(sql,filters,as_dict=1)