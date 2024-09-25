# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
from frappe.utils import getdate, add_to_date
import frappe


def get_report(filters, report_data):
    min_max_day = get_min_max_day(filters)
    report_data = get_report_data(filters,min_max_day)
    return {
        "columns":get_report_columns(filters,min_max_day),
        "data": report_data["report_data"],
        "report_summary": report_data["report_summary"],
        "report_chart": report_data["report_chart"]
    }

def get_report_columns(filters,min_max_day):
    columns = [
        {"fieldname": "row_group", "label":"Room Type", "width": 200},
    ]

    month = get_months(filters)
    for month_data in month:
    # Extract the necessary values from the month data
        col_month = month_data["col_month"]  # e.g., 'Sep', 'Oct'
        min_day = month_data["min_date"].day  # Get the minimum day (e.g., 1)
        max_day = month_data["max_date"].day  # Get the maximum day (e.g., 30)

    # Iterate over the days for each month
        for n in range(min_day, max_day + 1):
            # Append a column for each day in the month
            columns.append({
                "fieldname": "col_{}_{}".format(n, col_month),  # Unique fieldname, e.g., 'col_Sep_1'
                "label": "{} {}".format(col_month, str(n).zfill(2)),  # Label like 'Sep 01', 'Sep 02', etc.
                "width": 70,
                "align": "center"
            })
    columns.append({
        "fieldname":"total","label": "Total", "width":100, "align":"center",
    })
        
    return columns

def get_report_data(filters,min_max_day):
    report_data = []
    room_types = get_room_types(filters)
    daily_property_data = get_daily_property_data(filters)

    room_occupy = get_room_occupy(filters)
    months = get_months(filters)

    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")

    for rt in room_types:
        room_type_record = {
            "row_group": "{} ({})".format(rt["room_type"], rt["total_room"]),
            "indent": 1,
            "total": 0,
        }
        for m in months:
            date = m["min_date"]
            while date <= m["max_date"]:
                total_occupy = get_total_room_occupy_by_day(date, rt.name, daily_property_data, room_occupy)
                col_name = f"col_{date.day}_{m['col_month']}"
                room_type_record[col_name] = total_occupy
                room_type_record["total"] = (room_type_record["total"] or 0) + total_occupy
                date = add_to_date(date, days=1)

        report_data.append(room_type_record)

    # Initialize summary records
    vacant_record = {"row_group": "Vacant Room", "total": 0, "indent": 1}
    occupy_record = {"row_group": "Occupy", "total": 0, "indent": 1}
    ooo_record = {"row_group": "Out of Order", "total": 0, "indent": 1}
    occupancy_record = {"row_group": "Occupancy (%)", "total": 0, "indent": 1}
    arrival_record = {"row_group": "Arrival", "total": 0, "indent": 1}
    stay_over_record = {"row_group": "Stay Over", "total": 0, "indent": 1}
    departure_record = {"row_group": "Departure", "total": 0, "indent": 1}
    adult_record = {"row_group": "Adult", "total": 0, "indent": 1}
    child_record = {"row_group": "Child", "total": 0, "indent": 1}
    pax_record = {"row_group": "Pax", "total": 0, "indent": 1}

    # Calculate and populate summary records
    for m in months:
        date = m["min_date"]
        while date <= m["max_date"]:
            col_name = f"col_{date.day}_{m['col_month']}"
            
            # Vacant Room
            vacant_record[col_name] = sum(d.get(col_name, 0) for d in report_data)  # Use .get() to avoid KeyError
            vacant_record["total"] = vacant_record.get("total", 0) + vacant_record[col_name]
            
            # Occupy
            occupy_record[col_name] = sum(d.get("occupy", 0) for d in room_occupy if d["date"] == date)
            occupy_record["total"] = occupy_record.get("total", 0) + occupy_record[col_name]
            
            # Out of Order
            ooo_record[col_name] = sum(d.get("block", 0) for d in room_occupy if d["date"] == date)
            ooo_record["total"] = ooo_record.get("total", 0) + ooo_record[col_name]
            
            # Occupancy
            total_rooms = sum(d.get("total_room", 0) for d in daily_property_data if d["date"] == date)
            if calculate_room_occupancy_include_room_block == 0:
                total_rooms -= ooo_record.get(col_name, 0)
            total_rooms = max(total_rooms, 1)  # Avoid division by zero
			
            occupancy_record[col_name] = round((occupy_record.get(col_name, 0) / total_rooms) * 100, 2)
            
           
            
            
            # Arrival
            arrival_record[col_name] = sum(d.get("arrival", 0) for d in room_occupy if d["date"] == date)
            arrival_record["total"] = arrival_record.get("total", 0) + arrival_record[col_name]
            
            # Stay Over
            stay_over_record[col_name] = sum(d.get("stay_over", 0) for d in room_occupy if d["date"] == date)
            stay_over_record["total"] = stay_over_record.get("total", 0) + stay_over_record[col_name]
            
            # Departure
            departure_record[col_name] = sum(d.get("departure", 0) for d in room_occupy if d["date"] == date)
            departure_record["total"] = departure_record.get("total", 0) + departure_record[col_name]
            
            # Adult
            adult_record[col_name] = sum(d.get("adult", 0) for d in room_occupy if d["date"] == date)
            adult_record["total"] = adult_record.get("total", 0) + adult_record[col_name]
            
            # Child
            child_record[col_name] = sum(d.get("child", 0) for d in room_occupy if d["date"] == date)
            child_record["total"] = child_record.get("total", 0) + child_record[col_name]
            
            # Pax
            pax_record[col_name] = sum(d.get("adult", 0) + d.get("child", 0) for d in room_occupy if d["date"] == date)
            pax_record["total"] = pax_record.get("total", 0) + pax_record[col_name]
            
            date = add_to_date(date, days=1)

    # total record 
	# occupany % total
	
   
    total_room =  sum(d.get("total_room", 0) for d in daily_property_data)
    total_occupy = sum(d.get("occupy",0) for d in room_occupy)
    if calculate_room_occupancy_include_room_block==0:
        total_room = total_room -  sum(d.get("block",0) for d in room_occupy)
    total_room = max(total_room,1)#avoid divide by 0
    occupancy_record["total"] = round( total_occupy/total_room * 100,2)


    # Append summary records to report data
    report_data.extend([
        vacant_record,
        occupy_record,
        ooo_record,
        occupancy_record,
        arrival_record,
        stay_over_record,
        departure_record,
        adult_record,
        child_record,
        pax_record
    ])


    return {
        "report_data": report_data,
        "report_summary": get_report_summary(filters, room_occupy, daily_property_data),
        "report_chart": get_report_chart(filters, months, report_data)
    }

def get_room_occupy(filters):
	sql = """select 
				date, 
				room_type_id,
				sum(type='Reservation' and is_active=1 and is_active_reservation =1 ) as occupy, 
				sum(type='Reservation' and is_arrival=1 and is_active=1 and is_active_reservation =1 ) as arrival, 
				sum(type='Reservation' and is_arrival=0 and is_departure=0 and is_active=1 and is_active_reservation =1 ) as stay_over, 
				sum(type='Reservation' and is_departure=1 and is_active_reservation =1) as departure, 
				sum(adult) as adult, 
				sum(child) as child, 
				sum(type='Block') as block 
			from `tabRoom Occupy` 
			where 
				property=%(property)s and 
				date between %(start_date)s and %(end_date)s  
			group by 
				date,
				room_type_id"""

	return frappe.db.sql(sql,filters, as_dict=1)


def get_total_room_occupy_by_day(date,room_type_id, daily_property_data, occupy_data):
	total_rooms = sum(d["total_room"] for d in daily_property_data if d["date"]==date and d["room_type_id"]==room_type_id)
	occupy =sum(d["occupy"] for d in occupy_data if d["date"]==date and d["room_type_id"]==room_type_id)
	block =sum(d["block"] for d in occupy_data if d["date"]==date and d["room_type_id"]==room_type_id)
	return total_rooms -( (occupy or 0) + (block or 0))

def get_room_types(filters):
	sql = "select rt.name,  rt.room_type, count(r.name) as total_room from `tabRoom Type` rt inner join `tabRoom` r on r.room_type_id=rt.name and r.disabled=0 where r.property=%(property)s group by rt.name, rt.room_type  order by rt.sort_order "
	return frappe.db.sql(sql, filters, as_dict = 1)

def get_daily_property_data(filters):
	sql = "select date, room_type_id, total_room from `tabDaily Property Data` where date between %(start_date)s and %(end_date)s and property = %(property)s"
	return frappe.db.sql(sql,filters,as_dict=1)

def get_min_max_day(filters):
	sql = "select min(day(date)) as min_day, max(day(date)) as max_day from `tabDates` where date between %(start_date)s and %(end_date)s"
	data = frappe.db.sql(sql,filters,as_dict=1)
	return data [0]

def get_months(filters):
	sql="select   month(date) as month, year(date) as year, date_format(date, '%%b-%%Y') as str_month, min(date) as min_date,max(date) as max_date,date_format(date, '%%b') as col_month from `tabDates` where date between %(start_date)s and %(end_date)s group by month(date),year(date) order by year(date), month(date)"
	return frappe.db.sql(sql,filters, as_dict=1)

def get_report_summary(filters, occupay_data, daily_property_data):
	if not filters.show_summary:
		return None
	summary = []
	
	total_rooms = sum([d["total_room"] for d in  daily_property_data])
 
	if not filters.show_summary_fields or  "total_room" in filters.show_summary_fields :
		summary.append({
			"label": "Total Rooms",
			"value": total_rooms,
		})
		
	occupy = sum([d["occupy"] for d in  occupay_data])
	if not filters.show_summary_fields or  "occupy" in filters.show_summary_fields:
		summary.append({
			"label": "Occupy",
			"value": occupy,
			"indicator":"green"
		})
	
	block = sum([d["block"] for d in  occupay_data])
	if not filters.show_summary_fields or  "ooo" in filters.show_summary_fields:
		summary.append({
			"label": "OOO",
			"value": block,
			"indicator":"red"
		})
	if not filters.show_summary_fields or  "vacant" in filters.show_summary_fields:
		summary.append({
			"label": "Vacant",
			"value": (total_rooms or 0) - (occupy + block)
		})

	if not filters.show_summary_fields or  "occupancy" in filters.show_summary_fields:
		calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
		if calculate_room_occupancy_include_room_block  == 0:
			total_rooms = total_rooms - block

		summary.append({
			"label": "Occupancy",
			"value":  occupy / total_rooms * 100,
			"datatype":"Percent" ,
			"indicator":"green"
		})
	if not filters.show_summary_fields or  "arrival" in filters.show_summary_fields:
		summary.append({
			"label": "Arrival",
			"value": sum([d["arrival"] for d in  occupay_data]),
			"indicator":"blue"
		})
	if not filters.show_summary_fields or  "stay_over" in filters.show_summary_fields:
		summary.append({
			"label": "Stay Over",
			"value": sum([d["stay_over"] for d in  occupay_data]),
			"indicator":"blue"
		})
	
	if not filters.show_summary_fields or  "departure" in filters.show_summary_fields:
			summary.append({
				"label": "departure",
				"value": sum([d["departure"] for d in  occupay_data]),
				"indicator":"blue"
			})
	if not filters.show_summary_fields or  "pax" in filters.show_summary_fields:
		summary.append({
			"label": "Pax",
			"value": "{}".format(sum([d["adult"] + d["child"] for d in  occupay_data]))
		})
	
	if not filters.show_summary_fields or  "adult" in filters.show_summary_fields:
		summary.append({
			"label": "Adult",
			"value":sum([d["adult"]  for d in  occupay_data])
		})
	if not filters.show_summary_fields or  "child" in filters.show_summary_fields:
		summary.append({
			"label": "Child",
			"value":sum([d["child"]  for d in  occupay_data])
		})

	
	return summary


def get_report_chart(filters,months,data):
    min_day = min([d["min_date"].day for d in months])
    max_day = max([d["max_date"].day for d in months])
    precision = frappe.db.get_single_value("System Settings","currency_precision")
    columns = []
    datasets = [
        {"name":"Vacant Room"},
        {"name":"Occupy"},
        {"name":"Occupancy(%)"},
        {"name":"Out of Order"},
        {"name":"Arrival"},
        {"name":"Stay Over"},
        {"name":"Departure"},
        {"name":"Adult"},
        {"name":"Child"},
        {"name":"Pax"},
    ]
    if filters.show_chart_fields:
        datasets = [d for d in datasets if d["name"] in filters.show_chart_fields]

    for n in range(min_day, max_day +1):
        columns.append(n)


    for s in datasets:
        values = []
        month = get_months(filters)
        for month_data in month:
        # Extract the necessary values from the month data
            col_month = month_data["col_month"]  # e.g., 'Sep', 'Oct'
            min_days = month_data["min_date"].day  # Get the minimum day (e.g., 1)
            max_days = month_data["max_date"].day  # Get the maximum day (e.g., 30)

        # Iterate over the days for each month
            for n in range(min_days, max_days + 1):
                col_name= "col_{}_{}".format(n, col_month)
                values.append(sum([d[col_name] for d in data if "row_group" in d and d["row_group"]==s["name"]]))
        s["values"] = values


    chart = {
        'data':{
            'labels':columns,
            'datasets':datasets
        },
        "type": filters.chart_type,
        "lineOptions": {
            "regionFill": 1,
        },
        'valuesOverPoints':1,
        "axisOptions": {"xIsSeries": 1}
    }

    return chart