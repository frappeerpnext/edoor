# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import getdate


def execute(filters=None):
	data = get_report_data(filters)

	return get_columns(filters), data


def get_columns(filters):
	return [
		{"fieldname": "title", "label": "Title", "width":500, "align":"left"},
		{"fieldname": "current", "label": "Current", "width":100, "align":"right"},
		{"fieldname": "mtd", "label": "MTD", "width":100, "fieldtype":"Data", "align":"right"},
		{"fieldname": "ytd", "label": "YTD", "width":100, "align":"right"},
	]

def get_report_data(filters):
	
	report_data =  []
	rooms_available_record = get_current_room_in_property(filters)
	report_data.append(rooms_available_record)
	
	occupy_data = get_data_from_occupy_record(filters)
	report_data.append(occupy_data["room_occupy"])

	#total room - ooo room
	report_data.append({
		"title": "Total Rooms in Property minus OOO Rooms",
		"current":rooms_available_record["current"] - occupy_data["room_block"]["current"],
		"mtd":rooms_available_record["mtd"] - occupy_data["room_block"]["mtd"],
		"ytd":rooms_available_record["ytd"] - occupy_data["room_block"]["ytd"]
	})
	#total available room = total room - (room_occupy + room_block)
	report_data.append({
		"title": "Total Available Rooms",
		"current": rooms_available_record["current"] - ( occupy_data["room_occupy"]["current"] + occupy_data["room_block"]["current"]),
		"mtd":rooms_available_record["mtd"] - ( occupy_data["room_occupy"]["mtd"] + occupy_data["room_block"]["mtd"]),
		"ytd":rooms_available_record["ytd"] -( occupy_data["room_occupy"]["ytd"] + occupy_data["room_block"]["ytd"])
	})

	#complementary
	report_data.append(occupy_data["complimentary"])

	#houe use room
	report_data.append(occupy_data["house_use"])

	#Room occupied minus com and  house use
	report_data.append({
		"title": "Rooms Occupied minus Complimentary and House Use",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["complimentary"]["current"] + occupy_data["house_use"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["complimentary"]["mtd"] + occupy_data["house_use"]["mtd"]),
		"ytd": occupy_data["room_occupy"]["ytd"] -( occupy_data["complimentary"]["ytd"] + occupy_data["house_use"]["ytd"]),
		
	})
	#Room occupied minus compliementary
	report_data.append({
		"title": "Rooms Occupied minus Complimentary",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["complimentary"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["complimentary"]["mtd"]),
		"ytd": occupy_data["room_occupy"]["ytd"] -( occupy_data["complimentary"]["ytd"]),
		
	})
	
	#Room occupied minus  house use
	report_data.append({
		"title": "Rooms Occupied minus House Use",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["house_use"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["house_use"]["mtd"]),
		"ytd": occupy_data["room_occupy"]["ytd"] -(  occupy_data["house_use"]["ytd"]),
		
	})

	#room block
	report_data.append(occupy_data["room_block"])

	#inhouse adult
	report_data.append(occupy_data["in_house_adult"])

	#inhouse child
	report_data.append(occupy_data["in_house_child"])

	#in house pax
	report_data.append({
		"title": "Total In-house PAX",
		"current": occupy_data["in_house_adult"]["current"] + ( occupy_data["in_house_child"]["current"]),
		"mtd": occupy_data["in_house_adult"]["mtd"] + ( occupy_data["in_house_child"]["mtd"]),
		"ytd": occupy_data["in_house_adult"]["ytd"] +(  occupy_data["in_house_child"]["ytd"]),
		
	})

	# in-hopuse walk in adult
	report_data.append({
		"title": "Walk-In In-house Adult",
		"current": occupy_data["walk_in_adult"]["current"],
		"mtd": 11,#occupy_data["in_house_adult"]["mtd"] + ( occupy_data["in_house_child"]["mtd"]),
		"ytd": 22#occupy_data["in_house_adult"]["ytd"] +(  occupy_data["in_house_child"]["ytd"]),
		
	})
	
	# in-hopuse walk in child
	report_data.append({
		"title": "Walk-In In-house Child",
		"current": occupy_data["walk_in_child"]["current"],
		"mtd": 11,#occupy_data["in_house_adult"]["mtd"] + ( occupy_data["in_house_child"]["mtd"]),
		"ytd": 22#occupy_data["in_house_adult"]["ytd"] +(  occupy_data["in_house_child"]["ytd"]),
		
	})
	# in-hopuse walk in pax
	report_data.append({
		"title": "Walk-In In-house Pax",
		"current": (occupy_data["walk_in_child"]["current"] or 0) + (occupy_data["walk_in_adult"]["current"] or 0), 
		"mtd": 11,#occupy_data["in_house_adult"]["mtd"] + ( occupy_data["in_house_child"]["mtd"]),
		"ytd": 22#occupy_data["in_house_adult"]["ytd"] +(  occupy_data["in_house_child"]["ytd"]),
		
	})





	return report_data

def get_data_from_occupy_record(filters):
	filters.start_date = getdate(filters.date)
	filters.end_date = getdate(filters.date)
	sql="""select 
			sum(type='Reservation') as total_occupy,
			sum(type='Block') as total_block, 
			sum(type='Reservation' and is_complimentary=1)  as total_complimentary ,
			sum(type='Reservation' and is_house_use=1)  as total_house_use,
			sum(if(type='Reservation',adult,0))  as total_in_house_adult,
			sum(if(type='Reservation',child,0))  as total_in_house_child,
			sum(if(type='Reservation' and is_walk_in=1,adult,0))  as total_in_house_walk_in_adult,
			sum(if(type='Reservation' and is_walk_in=1,child,0))  as total_in_house_walk_in_child

		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s and is_active=1"""
	
	data = frappe.db.sql(sql,filters,as_dict=1) 

	datas = {
				"room_occupy":{"title":"Rooms Occupy", "current": data[0]["total_occupy"] or 0},
				"room_block":{"title":"Out of Order Rooms", "current": data[0]["total_block"] or 0},
				"complimentary":{"title":"Complimentary Rooms", "current": data[0]["total_complimentary"] or 0},
				"house_use":{"title":"House Use Rooms", "current": data[0]["total_house_use"] or 0},
				"in_house_adult":{"title":"In-house Adult", "current": data[0]["total_in_house_adult"] or 0},	
				"in_house_child":{"title":"In-house Child", "current": data[0]["total_in_house_child"] or 0},	
				"walk_in_adult":{"title":"Walk-In Adult", "current": data[0]["total_in_house_walk_in_adult"] or 0},	
				"walk_in_child":{"title":"Walk-In Child", "current": data[0]["total_in_house_walk_in_child"] or 0},	
	}

	#mtd
	filters.start_date = getdate(filters.date).replace(day=1)
	data = frappe.db.sql(sql,filters,as_dict=1) 

	datas["room_occupy"]["mtd"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["mtd"] = data[0]["total_block"] or 0 
	datas["complimentary"]["mtd"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["mtd"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["mtd"] = data[0]["total_in_house_adult"] or 0 
	datas["in_house_child"]["mtd"] = data[0]["total_in_house_child"] or 0 

	#ytd
	filters.start_date = getdate(filters.date).replace(day=1, month=1)
	data = frappe.db.sql(sql,filters,as_dict=1) 

	datas["room_occupy"]["ytd"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["ytd"] = data[0]["total_block"] or 0 
	datas["complimentary"]["ytd"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["ytd"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["ytd"] = data[0]["total_in_house_adult"] or 0 
	datas["in_house_child"]["ytd"] = data[0]["total_in_house_child"] or 0 

	

	return datas

def get_current_room_in_property(filters):
	sql = "select count(name) as total_room from `tabRoom` where property=%(property)s"
	total_room = frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"]
	
	filters.mtd_start_date = getdate(filters.date).replace(day=1)
	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(mtd_start_date)s and %(date)s"

	mtd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
 
	filters.ytd_start_date = getdate(filters.date).replace(day=1,month=1)

	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(ytd_start_date)s and %(date)s"

	ytd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
	return {
			"title": "Total Rooms in Property",
			"current":total_room,
			"mtd": mtd_total_room,
			"ytd":ytd_total_room
	}