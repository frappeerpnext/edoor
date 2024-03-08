# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_years
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta


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
		{"fieldname": "current", "label": "Current", "width":100, "align":"right"},
		{"fieldname": "mtd", "label": "MTD", "width":100, "fieldtype":"Data", "align":"right"},
		{"fieldname": "ytd", "label": "YTD", "width":100, "align":"right"},
		{"fieldname": "last_year_current", "label": "Current({})".format(getdate(filters.date).year - 1), "width":150, "align":"right"},
		{"fieldname": "last_year_mtd", "label": "MTD({})".format(getdate(filters.date).year - 1), "width":150, "fieldtype":"Data", "align":"right"},
		{"fieldname": "last_year_ytd", "label": "YTD({})".format(getdate(filters.date).year - 1), "width":150, "align":"right"},
		{"fieldname": "change_percentage", "label": "% Change", "width":150, "align":"right","fieldtype":"Percent"},
	]


def get_report_data(filters):
	
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Manager Flash Report"} )
	report_data =  []
	rooms_available_record = get_current_room_in_property(filters)
	report_data.append(rooms_available_record)
	
	occupy_data = get_data_from_occupy_record(filters)
	
	report_data.append(occupy_data["room_occupy"])
	ytd_room = rooms_available_record["ytd"] - occupy_data["room_occupy"]["ytd"]
	last_year_ytd_room = rooms_available_record["last_year_ytd"] - occupy_data["room_occupy"]["last_year_ytd"]
	report_data.append({
		"title": "Total Vacant Rooms",
		"current":rooms_available_record["current"] - occupy_data["room_occupy"]["current"],
		"mtd":rooms_available_record["mtd"] - occupy_data["room_occupy"]["mtd"],
		"ytd":ytd_room,
		"last_year_current":rooms_available_record["last_year_current"] - occupy_data["room_occupy"]["last_year_current"],
		"last_year_mtd":rooms_available_record["last_year_mtd"] - occupy_data["room_occupy"]["last_year_mtd"],
		"last_year_ytd":last_year_ytd_room,
		"change_percentage":f"{((ytd_room - last_year_ytd_room) / (1 if ytd_room==0 else ytd_room or 0)) * 100:.2f}%",
	})
	#total room - ooo room
	ytd_room = rooms_available_record["ytd"] - occupy_data["room_block"]["ytd"]
	last_year_ytd_room = rooms_available_record["last_year_ytd"] - occupy_data["room_block"]["last_year_ytd"]
	report_data.append({
		"title": "Total Rooms in Property minus OOO Rooms",
		"current":rooms_available_record["current"] - occupy_data["room_block"]["current"],
		"mtd":rooms_available_record["mtd"] - occupy_data["room_block"]["mtd"],
		"ytd":ytd_room,
		"last_year_current":rooms_available_record["last_year_current"] - occupy_data["room_block"]["last_year_current"],
		"last_year_mtd":rooms_available_record["last_year_mtd"] - occupy_data["room_block"]["last_year_mtd"],
		"last_year_ytd":last_year_ytd_room,
		"change_percentage":f"{((ytd_room - last_year_ytd_room) / (1 if ytd_room==0 else ytd_room or 0)) * 100:.2f}%",
	})
	#total available room = total room - (room_occupy + room_block)
	ytd_rooms = rooms_available_record["ytd"] -( occupy_data["room_occupy"]["ytd"] + occupy_data["room_block"]["ytd"])
	last_ytd_rooms = rooms_available_record["last_year_ytd"] -( occupy_data["room_occupy"]["last_year_ytd"] + occupy_data["room_block"]["last_year_ytd"])
	report_data.append({
		"title": "Total Available Rooms",
		"current": rooms_available_record["current"] - ( occupy_data["room_occupy"]["current"] + occupy_data["room_block"]["current"]),
		"mtd":rooms_available_record["mtd"] - ( occupy_data["room_occupy"]["mtd"] + occupy_data["room_block"]["mtd"]),
		"ytd":ytd_rooms,
		"last_year_current":rooms_available_record["last_year_current"] -( occupy_data["room_occupy"]["last_year_current"] + occupy_data["room_block"]["last_year_current"]),
		"last_year_mtd":rooms_available_record["last_year_mtd"] -( occupy_data["room_occupy"]["last_year_mtd"] + occupy_data["room_block"]["last_year_mtd"]),
		"last_year_ytd":last_ytd_rooms,
		"change_percentage":f"{((ytd_rooms - last_ytd_rooms) / (1 if ytd_rooms==0 else ytd_rooms or 0)) * 100:.2f}%",
	})

	#complementary
	report_data.append(occupy_data["complimentary"])

	#houe use room
	report_data.append(occupy_data["house_use"])

	#Room occupied minus com and  house use
	ytd = occupy_data["room_occupy"]["ytd"] -( occupy_data["complimentary"]["ytd"] + occupy_data["house_use"]["ytd"])
	last_ytd = occupy_data["room_occupy"]["last_year_ytd"] -( occupy_data["complimentary"]["last_year_ytd"] + occupy_data["house_use"]["last_year_ytd"])
	report_data.append({
		"title": "Rooms Occupied minus Complimentary and House Use",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["complimentary"]["current"] + occupy_data["house_use"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["complimentary"]["mtd"] + occupy_data["house_use"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["room_occupy"]["last_year_current"] -( occupy_data["complimentary"]["last_year_current"] + occupy_data["house_use"]["last_year_current"]),
		"last_year_mtd": occupy_data["room_occupy"]["last_year_mtd"] -( occupy_data["complimentary"]["last_year_mtd"] + occupy_data["house_use"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})
	#Room occupied minus com and  ooo
	ytd = occupy_data["room_occupy"]["ytd"] -( occupy_data["complimentary"]["ytd"] + occupy_data["room_block"]["ytd"])
	last_ytd = occupy_data["room_occupy"]["last_year_ytd"] -( occupy_data["complimentary"]["last_year_ytd"] + occupy_data["room_block"]["last_year_ytd"])
	report_data.append({
		"title": "Rooms Occupied minus OOO and Complimentary Rooms",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["complimentary"]["current"] + occupy_data["room_block"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["complimentary"]["mtd"] + occupy_data["room_block"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["room_occupy"]["last_year_current"] -( occupy_data["complimentary"]["last_year_current"] + occupy_data["room_block"]["last_year_current"]),
		"last_year_mtd": occupy_data["room_occupy"]["last_year_mtd"] -( occupy_data["complimentary"]["last_year_mtd"] + occupy_data["room_block"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})
	#Room occupied minus ooo and  house use
	ytd = occupy_data["room_occupy"]["ytd"] -( occupy_data["room_block"]["ytd"] + occupy_data["house_use"]["ytd"])
	last_ytd = occupy_data["room_occupy"]["last_year_ytd"] -( occupy_data["room_block"]["last_year_ytd"] + occupy_data["house_use"]["last_year_ytd"])
	report_data.append({
		"title": "Rooms Occupied minus OOO and House Use Rooms",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["room_block"]["current"] + occupy_data["house_use"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["room_block"]["mtd"] + occupy_data["house_use"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["room_occupy"]["last_year_current"] -( occupy_data["room_block"]["last_year_current"] + occupy_data["house_use"]["last_year_current"]),
		"last_year_mtd": occupy_data["room_occupy"]["last_year_mtd"] -( occupy_data["room_block"]["last_year_mtd"] + occupy_data["house_use"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})
	#Room occupied minus compliementary
	ytd = occupy_data["room_occupy"]["ytd"] -( occupy_data["complimentary"]["ytd"])
	last_ytd = occupy_data["room_occupy"]["last_year_ytd"] -( occupy_data["complimentary"]["last_year_ytd"])
	report_data.append({
		"title": "Rooms Occupied minus Complimentary",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["complimentary"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["complimentary"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["room_occupy"]["last_year_current"] -( occupy_data["complimentary"]["last_year_current"]),
		"last_year_mtd": occupy_data["room_occupy"]["last_year_mtd"] -( occupy_data["complimentary"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})
	
	#Room occupied minus  house use
	ytd = occupy_data["room_occupy"]["ytd"] -(  occupy_data["house_use"]["ytd"])
	last_ytd = occupy_data["room_occupy"]["last_year_ytd"] -(  occupy_data["house_use"]["last_year_ytd"])
	report_data.append({
		"title": "Rooms Occupied minus House Use",
		"current": occupy_data["room_occupy"]["current"] - ( occupy_data["house_use"]["current"]),
		"mtd": occupy_data["room_occupy"]["mtd"] - ( occupy_data["house_use"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["room_occupy"]["last_year_current"] -(  occupy_data["house_use"]["last_year_current"]),
		"last_year_mtd": occupy_data["room_occupy"]["last_year_mtd"] -(  occupy_data["house_use"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})

	#room block
	report_data.append(occupy_data["room_block"])

	#arrival adult
	report_data.append(occupy_data["arrival_adult"])
	#arrival child
	report_data.append(occupy_data["arrival_child"])
	#arrival pax
	ytd = occupy_data["arrival_adult"]["ytd"] +(  occupy_data["arrival_child"]["ytd"])
	last_ytd = occupy_data["arrival_adult"]["last_year_ytd"] + (occupy_data["arrival_child"]["last_year_ytd"])
	report_data.append({
		"title": "Total Arrival PAX",
		"current": occupy_data["arrival_adult"]["current"] + ( occupy_data["arrival_child"]["current"]),
		"mtd": occupy_data["arrival_adult"]["mtd"] + ( occupy_data["arrival_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["arrival_adult"]["last_year_current"] +(  occupy_data["arrival_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["arrival_adult"]["last_year_mtd"] +(  occupy_data["arrival_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})

	#inhouse adult
	report_data.append(occupy_data["in_house_adult"])
	#inhouse child
	report_data.append(occupy_data["in_house_child"])
	#in house pax
	ytd = occupy_data["in_house_adult"]["ytd"] +(  occupy_data["in_house_child"]["ytd"])
	last_ytd = occupy_data["in_house_adult"]["last_year_ytd"] +(  occupy_data["in_house_child"]["last_year_ytd"])
	report_data.append({
		"title": "Total In-house PAX",
		"current": occupy_data["in_house_adult"]["current"] + ( occupy_data["in_house_child"]["current"]),
		"mtd": occupy_data["in_house_adult"]["mtd"] + ( occupy_data["in_house_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["in_house_adult"]["last_year_current"] +(  occupy_data["in_house_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["in_house_adult"]["last_year_mtd"] +(  occupy_data["in_house_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
		
	})

	#departure adult
	report_data.append(occupy_data["departure_adult"])
	#departure child
	report_data.append(occupy_data["departure_child"])
	#departure pax
	ytd = occupy_data["departure_adult"]["ytd"] +(  occupy_data["departure_child"]["ytd"])
	last_ytd = occupy_data["departure_adult"]["last_year_ytd"] +(  occupy_data["departure_child"]["last_year_ytd"])
	report_data.append({
		"title": "Total Departure PAX",
		"current": occupy_data["departure_adult"]["current"] + ( occupy_data["departure_child"]["current"]),
		"mtd": occupy_data["departure_adult"]["mtd"] + ( occupy_data["departure_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["departure_adult"]["last_year_current"] +(  occupy_data["departure_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["departure_adult"]["last_year_mtd"] +(  occupy_data["departure_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})

	# in-hopuse walk in adult
	report_data.append(occupy_data["walk_in_adult"])
	
	# in-hopuse walk in child
	report_data.append(occupy_data["walk_in_child"])
	# in-hopuse walk in pax
	ytd =  occupy_data["walk_in_child"]["ytd"] +(  occupy_data["walk_in_adult"]["ytd"])
	last_ytd = occupy_data["walk_in_child"]["last_year_ytd"] +(  occupy_data["walk_in_adult"]["last_year_ytd"])
	report_data.append({
		"title": "Walk-In In-house Pax",
		"current": (occupy_data["walk_in_child"]["current"] or 0) + (occupy_data["walk_in_adult"]["current"] or 0), 
		"mtd": occupy_data["walk_in_child"]["mtd"] + ( occupy_data["walk_in_adult"]["mtd"]),
		"ytd":ytd,
		"last_year_current": occupy_data["walk_in_child"]["last_year_current"] +(  occupy_data["walk_in_adult"]["last_year_current"]),
		"last_year_mtd": occupy_data["walk_in_child"]["last_year_mtd"] +(  occupy_data["walk_in_adult"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	#walk in room night
	report_data.append(occupy_data["walk_in_room_night"])
	#arrival room night
	report_data.append(occupy_data["arrival_room_night"])
	#departure room night
	report_data.append(occupy_data["departure_room_night"])
	ytd =  occupy_data["arrival_room_night"]["ytd"] +(  occupy_data["departure_room_night"]["ytd"])
	last_ytd = occupy_data["arrival_room_night"]["last_year_ytd"] +(  occupy_data["departure_room_night"]["last_year_ytd"])
	report_data.append({
		"title": "Total Room Nights",
		"current": occupy_data["arrival_room_night"]["current"] + ( occupy_data["departure_room_night"]["current"]),
		"mtd": occupy_data["arrival_room_night"]["mtd"] + ( occupy_data["departure_room_night"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["arrival_room_night"]["last_year_current"] +(  occupy_data["departure_room_night"]["last_year_current"]),
		"last_year_mtd": occupy_data["arrival_room_night"]["last_year_mtd"] +(  occupy_data["departure_room_night"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	#walk-in room night
	report_data.append(occupy_data["no_show_room"])
	report_data.append(occupy_data["no_show_adult"])
	report_data.append(occupy_data["no_show_child"])
	ytd =  occupy_data["no_show_adult"]["ytd"] +(  occupy_data["no_show_child"]["ytd"])
	last_ytd = occupy_data["no_show_adult"]["last_year_ytd"] +(  occupy_data["no_show_child"]["last_year_ytd"])
	report_data.append({
		"title": "No Show PAX",
		"current": occupy_data["no_show_adult"]["current"] + ( occupy_data["no_show_child"]["current"]),
		"mtd": occupy_data["no_show_adult"]["mtd"] + ( occupy_data["no_show_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["no_show_adult"]["last_year_current"] +(  occupy_data["no_show_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["no_show_adult"]["last_year_mtd"] +(  occupy_data["no_show_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	report_data.append(occupy_data["early_checked_out_adult"])
	report_data.append(occupy_data["early_checked_out_child"])
	ytd =  occupy_data["early_checked_out_adult"]["ytd"] +(  occupy_data["early_checked_out_child"]["ytd"])
	last_ytd = occupy_data["early_checked_out_adult"]["last_year_ytd"] +(  occupy_data["early_checked_out_child"]["last_year_ytd"])
	report_data.append({
		"title": "Early Checked Out PAX",
		"current": occupy_data["early_checked_out_adult"]["current"] + ( occupy_data["early_checked_out_child"]["current"]),
		"mtd": occupy_data["early_checked_out_adult"]["mtd"] + ( occupy_data["early_checked_out_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["early_checked_out_adult"]["last_year_current"] +(  occupy_data["early_checked_out_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["early_checked_out_adult"]["last_year_mtd"] +(  occupy_data["early_checked_out_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	report_data.append(occupy_data["early_checked_out"])
	report_data.append(occupy_data["fit_room"])
	report_data.append(occupy_data["git_room"])
	report_data.append(occupy_data["fit_adult"])
	report_data.append(occupy_data["fit_child"])
	ytd =  occupy_data["fit_adult"]["ytd"] +(  occupy_data["fit_child"]["ytd"])
	last_ytd =  occupy_data["fit_adult"]["last_year_ytd"] +(  occupy_data["fit_child"]["last_year_ytd"])
	report_data.append({
		"title": "FIT PAX",
		"current": occupy_data["fit_adult"]["current"] + ( occupy_data["fit_child"]["current"]),
		"mtd": occupy_data["fit_adult"]["mtd"] + ( occupy_data["fit_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["fit_adult"]["last_year_current"] +(  occupy_data["fit_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["fit_adult"]["last_year_mtd"] +(  occupy_data["fit_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	report_data.append(occupy_data["git_adult"])
	report_data.append(occupy_data["git_child"])
	ytd =  occupy_data["git_adult"]["ytd"] +(  occupy_data["git_child"]["ytd"])
	last_ytd =  occupy_data["git_adult"]["last_year_ytd"] +(  occupy_data["git_child"]["last_year_ytd"])
	report_data.append({
		"title": "GIT PAX",
		"current": occupy_data["git_adult"]["current"] + ( occupy_data["git_child"]["current"]),
		"mtd": occupy_data["git_adult"]["mtd"] + ( occupy_data["git_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["git_adult"]["last_year_current"] +(  occupy_data["git_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["git_adult"]["last_year_mtd"] +(  occupy_data["git_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	report_data.append(occupy_data["cancel_room"])
	report_data.append(occupy_data["cancel_adult"])
	report_data.append(occupy_data["cancel_child"])
	ytd =  occupy_data["cancel_adult"]["ytd"] +(  occupy_data["cancel_child"]["ytd"])
	last_ytd =  occupy_data["cancel_adult"]["last_year_ytd"] +(  occupy_data["cancel_child"]["last_year_ytd"])
	report_data.append({
		"title": "Cancelled PAX",
		"current": occupy_data["cancel_adult"]["current"] + ( occupy_data["cancel_child"]["current"]),
		"mtd": occupy_data["cancel_adult"]["mtd"] + ( occupy_data["cancel_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["cancel_adult"]["last_year_current"] +(  occupy_data["cancel_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["cancel_adult"]["last_year_mtd"] +(  occupy_data["cancel_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	keys = ["vip_guest","house_use","complimentary","house_use_adult","house_use_child"]
	for k in keys:
		report_data.append(occupy_data[k])
		 
 
	ytd =  occupy_data["house_use_adult"]["ytd"] +(  occupy_data["house_use_child"]["ytd"])
	last_ytd =  occupy_data["house_use_adult"]["last_year_ytd"] +(  occupy_data["house_use_child"]["last_year_ytd"])
	report_data.append({
		"title": "House Use PAX",
		"current": occupy_data["house_use_adult"]["current"] + ( occupy_data["house_use_child"]["current"]),
		"mtd": occupy_data["house_use_adult"]["mtd"] + ( occupy_data["house_use_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["house_use_adult"]["last_year_current"] +(  occupy_data["house_use_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["house_use_adult"]["last_year_mtd"] +(  occupy_data["house_use_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": f"{((ytd - last_ytd) / (1 if ytd==0 else ytd or 0)) * 100:.2f}%",
	})
	report_data.append(occupy_data["complimentary_adult"])
	report_data.append(occupy_data["complimentary_child"])
	ytd =  occupy_data["complimentary_adult"]["ytd"] +(  occupy_data["complimentary_child"]["ytd"])
	last_ytd =  occupy_data["complimentary_adult"]["last_year_ytd"] +(  occupy_data["complimentary_child"]["last_year_ytd"])
	report_data.append({
		"title": "Complimentary PAX",
		"current": occupy_data["complimentary_adult"]["current"] + ( occupy_data["complimentary_child"]["current"]),
		"mtd": occupy_data["complimentary_adult"]["mtd"] + ( occupy_data["complimentary_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["complimentary_adult"]["last_year_current"] +(  occupy_data["complimentary_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["complimentary_adult"]["last_year_mtd"] +(  occupy_data["complimentary_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd 
	})

	
	
	# revenue
	report_data+= get_revenue(filters)
	
	#ledger balance 
	report_data+= get_ledger_balance(filters)

	#forcasting 
	report_data+= get_forecasting(filters)
     

	#calculate room occupy
	#calculate room occupancy
	occpancy = {"title":"Occupancy"}
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
	 
	for f in ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]:
		if calculate_room_occupancy_include_room_block==1:
			total_room = sum([d[f] for d in report_data if d["title"]=='Total Rooms in Property']) or 0
			room_occupy = sum([d[f] for d in report_data if d["title"]=='Rooms Occupy']) or 0
			occpancy[f] =  room_occupy / (1 if total_room == 0 else total_room)
		else:
			occpancy[f] = 50
	report_data.append(occpancy)
        
	return_report_data = []
	#get group list
	groups = []
	for g in [d.group for d in report_config.row_configs]:
		if g not in groups:
			groups.append(g)
        
	for g in groups:
		return_report_data.append({
			"title": g,
			"indent":0
		})
		for r in [d for d in report_config.row_configs if d.group == g and d.show_in_report==1]:
			row = [d for d in report_data if d["title"] == r.field_name]
			if row:
				row = row[0]
				row["indent"] = 1
				row["title"] = r.custom_name or r.field_name

				if (  "last_year_ytd" in row and row["last_year_ytd"] or 0) ==0:
					row["change_percentage"] = 100
				else:
					row["change_percentage"] = ((row["ytd"] or 0 ) - (row["last_year_ytd"] or 0 )) / (row["last_year_ytd"] or 0 )
     			
				return_report_data.append(row)
			else:
				return_report_data.append({
					"indent": 1,
					"title": r.custom_name or r.field_name
				})
    
    
			
    
	return return_report_data #+ [{}] + report_data


def get_data_from_occupy_record(filters):
	
	filters.start_date = filters.current["start_date"]
	filters.end_date = filters.current["end_date"]
	sql="""select 
			sum(type='Reservation') as total_occupy,
			sum(type='Block') as total_block, 
			sum(type='Reservation' and is_complimentary=1)  as total_complimentary ,
			sum(type='Reservation' and is_house_use=1)  as total_house_use,
			sum(if(type='Reservation',adult,0))  as total_in_house_adult,
			sum(if(type='Reservation' and is_arrival=1,adult,0))  as total_arrival_adult,
			sum(if(type='Reservation' and is_departure=1,adult,0))  as total_departure_adult,
			sum(if(type='Reservation' and is_arrival=1,child,0))  as total_arrival_child,
			sum(if(type='Reservation' and is_departure=1,child,0))  as total_departure_child,
			sum(if(type='Reservation',child,0))  as total_in_house_child,
			sum(if(type='Reservation' and is_walk_in=1,adult,0))  as total_in_house_walk_in_adult,
			sum(if(type='Reservation' and is_walk_in=1,child,0))  as total_in_house_walk_in_child,
			sum(type='Reservation' and is_walk_in=1)  as total_walk_in_room_night,
			sum(type='Reservation' and is_arrival=1)  as total_arrival_room_night,
			sum(type='Reservation' and is_departure=1)  as total_departure_room_night,
			sum(type='Reservation' and guest_type='VIP')  as total_vip_guest,
			sum(type = 'Reservation' and reservation_status='No Show') as total_no_show_room,
			sum(if(type='Reservation' and reservation_status='No Show',adult,0)) as total_no_show_adult,
			sum(if(type='Reservation' and reservation_status='No Show',child,0)) as total_no_show_child,
			sum(if(type='Reservation' and is_stay_over=1 and is_departure=1,adult,0)) as total_early_checked_out_adult,
			sum(if(type='Reservation' and is_stay_over=1 and is_departure=1,child,0)) as total_early_checked_out_child,
			sum(type='Reservation' and is_stay_over=1 and is_departure=1) as total_early_checked_out,
			sum(type='Reservation' and reservation_type='FIT') as total_fit_room,
			sum(type='Reservation' and reservation_type='GIT') as total_git_room,
			sum(if(type='Reservation' and reservation_type='FIT',adult,0)) as total_fit_adult,
			sum(if(type='Reservation' and reservation_type='FIT',child,0)) as total_fit_child,
			sum(if(type='Reservation' and reservation_type='GIT',adult,0)) as total_git_adult,
			sum(if(type='Reservation' and reservation_type='GIT',child,0)) as total_git_child,
			sum(is_house_use=1 and type='Reservation') as total_house_use_room,
			sum(is_complimentary=1 and type='Reservation') as total_complimentary_room,
			sum(if(type='Reservation' and  is_house_use=1,adult,0)) as total_house_use_adult,
			sum(if(type='Reservation' and is_house_use=1,child,0)) as total_house_use_child,
			sum(if(type='Reservation' and is_complimentary=1 ,adult,0)) as total_complimentary_adult,
			sum(if(type='Reservation' and is_complimentary=1 ,child,0)) as total_complimentary_child
		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s and is_active=1"""
	stay = """
			select sum(if(reservation_status='Cancelled',adult,0)) as total_cancel_adult,
       			sum(if(reservation_status='Cancelled',child,0)) as total_cancel_child,
       			sum(reservation_status='Cancelled') as total_cancel_room
			from `tabReservation Stay` where property=%(property)s and working_date between %(start_date)s and %(end_date)s
			"""
	data = frappe.db.sql(sql,filters,as_dict=1) 
	data_stay = frappe.db.sql(stay,filters,as_dict=1) 
	datas = {
				"room_occupy":{"title":"Rooms Occupy", "current": data[0]["total_occupy"] or 0},
				"room_block":{"title":"Out of Order Rooms", "current": data[0]["total_block"] or 0},
				"complimentary":{"title":"Complimentary Rooms", "current": data[0]["total_complimentary"] or 0},
				"house_use":{"title":"House Use Rooms", "current": data[0]["total_house_use"] or 0},
				"in_house_adult":{"title":"In-house Adult", "current": data[0]["total_in_house_adult"] or 0},	
				"arrival_adult":{"title":"Arrival Adult", "current": data[0]["total_arrival_adult"] or 0},	
				"departure_adult":{"title":"Departure Adult", "current": data[0]["total_departure_adult"] or 0},	
				"in_house_child":{"title":"In-house Child", "current": data[0]["total_in_house_child"] or 0},	
				"arrival_child":{"title":"Arrival Child", "current": data[0]["total_arrival_child"] or 0},	
				"departure_child":{"title":"Departure Child", "current": data[0]["total_departure_child"] or 0},	
				"walk_in_adult":{"title":"Walk-In Adult", "current": data[0]["total_in_house_walk_in_adult"] or 0},	
				"walk_in_child":{"title":"Walk-In Child", "current": data[0]["total_in_house_walk_in_child"] or 0},	
				"walk_in_room_night":{"title":"Walk-In Room", "current": data[0]["total_walk_in_room_night"] or 0},	
				"arrival_room_night":{"title":"Arrival Room Nights", "current": data[0]["total_arrival_room_night"] or 0},	
				"departure_room_night":{"title":"Departure Room Nights", "current": data[0]["total_departure_room_night"] or 0},	
				"no_show_room":{"title":"No Show Room", "current": data[0]["total_no_show_room"] or 0},	
				"no_show_adult":{"title":"No Show Adult", "current": data[0]["total_no_show_adult"] or 0},	
				"no_show_child":{"title":"No Show Child", "current": data[0]["total_no_show_child"] or 0},	
				"early_checked_out_adult":{"title":"Early Checked Out Adult", "current": data[0]["total_early_checked_out_adult"] or 0},	
				"early_checked_out_child":{"title":"Early Checked Out Child", "current": data[0]["total_early_checked_out_child"] or 0},	
				"early_checked_out":{"title":"Early Checked Out Rooms", "current": data[0]["total_early_checked_out"] or 0},	
				"fit_room":{"title":"FIT Rooms", "current": data[0]["total_fit_room"] or 0},	
				"git_room":{"title":"GIT Rooms", "current": data[0]["total_git_room"] or 0},	
				"fit_adult":{"title":"FIT Adult", "current": data[0]["total_fit_adult"] or 0},	
				"fit_child":{"title":"FIT Child", "current": data[0]["total_fit_child"] or 0},	
				"git_adult":{"title":"GIT Adult", "current": data[0]["total_git_adult"] or 0},	
				"git_child":{"title":"GIT Child", "current": data[0]["total_git_child"] or 0},	
				"vip_guest":{"title":"VIP Guest", "current": data[0]["total_vip_guest"] or 0},	
				"cancel_room":{"title":"Cancelled Rooms", "current": data_stay[0]["total_cancel_room"] or 0},	
				"cancel_adult":{"title":"Cancelled Adult", "current": data_stay[0]["total_cancel_adult"] or 0},	
				"cancel_child":{"title":"Cancelled Child", "current": data_stay[0]["total_cancel_child"] or 0},		
				"house_use":{"title":"House Use Rooms", "current": data[0]["total_house_use_room"] or 0},	
				"complimentary":{"title":"Complimentary Rooms", "current": data[0]["total_complimentary_room"] or 0},	
				"house_use_adult":{"title":"House Use Adult", "current": data[0]["total_house_use_adult"] or 0},	
				"house_use_child":{"title":"House Use Child", "current": data[0]["total_house_use_child"] or 0},	
				"complimentary_adult":{"title":"Complimentary Adult", "current": data[0]["total_complimentary_adult"] or 0},	
				"complimentary_child":{"title":"Complimentary Child", "current": data[0]["total_complimentary_child"] or 0},	
				
	}

	filters.start_date = filters.mtd["start_date"]
	data = frappe.db.sql(sql,filters,as_dict=1) 
	data_stay = frappe.db.sql(stay,filters,as_dict=1) 

	datas["room_occupy"]["mtd"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["mtd"] = data[0]["total_block"] or 0 
	datas["complimentary"]["mtd"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["mtd"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["mtd"] = data[0]["total_in_house_adult"] or 0 
	datas["arrival_adult"]["mtd"] = data[0]["total_arrival_adult"] or 0 
	datas["departure_adult"]["mtd"] = data[0]["total_departure_adult"] or 0 
	datas["in_house_child"]["mtd"] = data[0]["total_in_house_child"] or 0 
	datas["arrival_child"]["mtd"] = data[0]["total_arrival_child"] or 0 
	datas["departure_child"]["mtd"] = data[0]["total_departure_child"] or 0 
	datas["walk_in_adult"]["mtd"] = data[0]["total_in_house_walk_in_adult"] or 0 
	datas["walk_in_child"]["mtd"] = data[0]["total_in_house_walk_in_child"] or 0 
	datas["walk_in_room_night"]["mtd"] = data[0]["total_walk_in_room_night"] or 0 
	datas["arrival_room_night"]["mtd"] = data[0]["total_arrival_room_night"] or 0 
	datas["departure_room_night"]["mtd"] = data[0]["total_departure_room_night"] or 0 
	datas["no_show_room"]["mtd"] = data[0]["total_no_show_room"] or 0 
	datas["no_show_adult"]["mtd"] = data[0]["total_no_show_adult"] or 0 
	datas["no_show_child"]["mtd"] = data[0]["total_no_show_child"] or 0 
	datas["early_checked_out"]["mtd"] = data[0]["total_early_checked_out"] or 0 
	datas["early_checked_out_adult"]["mtd"] = data[0]["total_early_checked_out_adult"] or 0 
	datas["early_checked_out_child"]["mtd"] = data[0]["total_early_checked_out_child"] or 0 
	datas["fit_room"]["mtd"] = data[0]["total_fit_room"] or 0 
	datas["git_room"]["mtd"] = data[0]["total_git_room"] or 0 
	datas["fit_adult"]["mtd"] = data[0]["total_fit_adult"] or 0 
	datas["fit_child"]["mtd"] = data[0]["total_fit_child"] or 0 
	datas["git_adult"]["mtd"] = data[0]["total_git_adult"] or 0 
	datas["git_child"]["mtd"] = data[0]["total_git_child"] or 0 
	datas["vip_guest"]["mtd"] = data[0]["total_vip_guest"] or 0 
	datas["house_use"]["mtd"] = data[0]["total_house_use_room"] or 0 
	datas["complimentary"]["mtd"] = data[0]["total_complimentary_room"] or 0 
	datas["house_use_adult"]["mtd"] = data[0]["total_house_use_adult"] or 0 
	datas["house_use_child"]["mtd"] = data[0]["total_house_use_child"] or 0 
	datas["complimentary_adult"]["mtd"] = data[0]["total_complimentary_adult"] or 0 
	datas["complimentary_child"]["mtd"] = data[0]["total_complimentary_child"] or 0 
	datas["cancel_room"]["mtd"] = data_stay[0]["total_cancel_room"] or 0 
	datas["cancel_adult"]["mtd"] = data_stay[0]["total_cancel_adult"] or 0 
	datas["cancel_child"]["mtd"] = data_stay[0]["total_cancel_child"] or 0 

	

	#ytd
	filters.start_date = filters.ytd["start_date"]
	data = frappe.db.sql(sql,filters,as_dict=1) 
	data_stay = frappe.db.sql(stay,filters,as_dict=1) 

	datas["room_occupy"]["ytd"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["ytd"] = data[0]["total_block"] or 0 
	datas["complimentary"]["ytd"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["ytd"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["ytd"] = data[0]["total_in_house_adult"] or 0 
	datas["arrival_adult"]["ytd"] = data[0]["total_arrival_adult"] or 0 
	datas["departure_adult"]["ytd"] = data[0]["total_departure_adult"] or 0 
	datas["in_house_child"]["ytd"] = data[0]["total_in_house_child"] or 0 
	datas["arrival_child"]["ytd"] = data[0]["total_arrival_child"] or 0 
	datas["departure_child"]["ytd"] = data[0]["total_departure_child"] or 0 
	datas["walk_in_adult"]["ytd"] = data[0]["total_in_house_walk_in_adult"] or 0 
	datas["walk_in_child"]["ytd"] = data[0]["total_in_house_walk_in_child"] or 0 
	datas["walk_in_room_night"]["ytd"] = data[0]["total_walk_in_room_night"] or 0 
	datas["arrival_room_night"]["ytd"] = data[0]["total_arrival_room_night"] or 0 
	datas["departure_room_night"]["ytd"] = data[0]["total_departure_room_night"] or 0 
	datas["no_show_room"]["ytd"] = data[0]["total_no_show_room"] or 0 
	datas["no_show_adult"]["ytd"] = data[0]["total_no_show_adult"] or 0 
	datas["no_show_child"]["ytd"] = data[0]["total_no_show_child"] or 0 
	datas["early_checked_out_adult"]["ytd"] = data[0]["total_early_checked_out_adult"] or 0 
	datas["early_checked_out_child"]["ytd"] = data[0]["total_early_checked_out_child"] or 0 
	datas["early_checked_out"]["ytd"] = data[0]["total_early_checked_out"] or 0 
	datas["fit_room"]["ytd"] = data[0]["total_fit_room"] or 0 
	datas["git_room"]["ytd"] = data[0]["total_git_room"] or 0 
	datas["fit_adult"]["ytd"] = data[0]["total_fit_adult"] or 0 
	datas["fit_child"]["ytd"] = data[0]["total_fit_child"] or 0 
	datas["git_adult"]["ytd"] = data[0]["total_git_adult"] or 0 
	datas["git_child"]["ytd"] = data[0]["total_git_child"] or 0 
	datas["vip_guest"]["ytd"] = data[0]["total_vip_guest"] or 0 
	datas["cancel_room"]["ytd"] = data_stay[0]["total_cancel_room"] or 0 
	datas["cancel_adult"]["ytd"] = data_stay[0]["total_cancel_adult"] or 0 
	datas["cancel_child"]["ytd"] = data_stay[0]["total_cancel_child"] or 0  
	datas["house_use"]["ytd"] = data[0]["total_house_use_room"] or 0 
	datas["complimentary"]["ytd"] = data[0]["total_complimentary_room"] or 0 
	datas["house_use_adult"]["ytd"] = data[0]["total_house_use_adult"] or 0 
	datas["house_use_child"]["ytd"] = data[0]["total_house_use_child"] or 0 
	datas["complimentary_adult"]["ytd"] = data[0]["total_complimentary_adult"] or 0 
	datas["complimentary_child"]["ytd"] = data[0]["total_complimentary_child"] or 0 

	

	#last year current date
	filters.start_date = filters.last_year_current["start_date"]	
	filters.end_date = filters.last_year_current["end_date"]
	data = frappe.db.sql(sql,filters,as_dict=1) 
	data_stay = frappe.db.sql(stay,filters,as_dict=1) 

	
	datas["room_occupy"]["last_year_current"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["last_year_current"] = data[0]["total_block"] or 0 
	datas["complimentary"]["last_year_current"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["last_year_current"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["last_year_current"] = data[0]["total_in_house_adult"] or 0 
	datas["arrival_adult"]["last_year_current"] = data[0]["total_arrival_adult"] or 0 
	datas["departure_adult"]["last_year_current"] = data[0]["total_departure_adult"] or 0 
	datas["in_house_child"]["last_year_current"] = data[0]["total_in_house_child"] or 0 
	datas["arrival_child"]["last_year_current"] = data[0]["total_arrival_child"] or 0 
	datas["departure_child"]["last_year_current"] = data[0]["total_departure_child"] or 0 
	datas["walk_in_adult"]["last_year_current"] = data[0]["total_in_house_walk_in_adult"] or 0 
	datas["walk_in_child"]["last_year_current"] = data[0]["total_in_house_walk_in_child"] or 0 
	datas["walk_in_room_night"]["last_year_current"] = data[0]["total_walk_in_room_night"] or 0 
	datas["arrival_room_night"]["last_year_current"] = data[0]["total_arrival_room_night"] or 0 
	datas["departure_room_night"]["last_year_current"] = data[0]["total_departure_room_night"] or 0 
	datas["no_show_room"]["last_year_current"] = data[0]["total_no_show_room"] or 0 
	datas["no_show_adult"]["last_year_current"] = data[0]["total_no_show_adult"] or 0 
	datas["no_show_child"]["last_year_current"] = data[0]["total_no_show_child"] or 0 
	datas["early_checked_out_adult"]["last_year_current"] = data[0]["total_early_checked_out_adult"] or 0 
	datas["early_checked_out_child"]["last_year_current"] = data[0]["total_early_checked_out_child"] or 0 
	datas["early_checked_out"]["last_year_current"] = data[0]["total_early_checked_out"] or 0 
	datas["fit_room"]["last_year_current"] = data[0]["total_fit_room"] or 0 
	datas["git_room"]["last_year_current"] = data[0]["total_git_room"] or 0 
	datas["fit_adult"]["last_year_current"] = data[0]["total_fit_adult"] or 0 
	datas["fit_child"]["last_year_current"] = data[0]["total_fit_child"] or 0 
	datas["git_adult"]["last_year_current"] = data[0]["total_git_adult"] or 0 
	datas["git_child"]["last_year_current"] = data[0]["total_git_child"] or 0 
	datas["vip_guest"]["last_year_current"] = data[0]["total_vip_guest"] or 0 
	datas["cancel_room"]["last_year_current"] = data_stay[0]["total_cancel_room"] or 0 
	datas["cancel_adult"]["last_year_current"] = data_stay[0]["total_cancel_adult"] or 0 
	datas["cancel_child"]["last_year_current"] = data_stay[0]["total_cancel_child"] or 0 
	datas["house_use"]["last_year_current"] = data[0]["total_house_use_room"] or 0 
	datas["complimentary"]["last_year_current"] = data[0]["total_complimentary_room"] or 0 
	datas["house_use_adult"]["last_year_current"] = data[0]["total_house_use_adult"] or 0 
	datas["house_use_child"]["last_year_current"] = data[0]["total_house_use_child"] or 0 
	datas["complimentary_adult"]["last_year_current"] = data[0]["total_complimentary_adult"] or 0 
	datas["complimentary_child"]["last_year_current"] = data[0]["total_complimentary_child"] or 0 

 
	
	#last year mtd
	
	filters.start_date = filters.last_year_mtd["start_date"]	
	filters.end_date = filters.last_year_mtd["end_date"]
	data = frappe.db.sql(sql,filters,as_dict=1)
	data_stay = frappe.db.sql(stay,filters,as_dict=1)  
	

	datas["room_occupy"]["last_year_mtd"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["last_year_mtd"] = data[0]["total_block"] or 0 
	datas["complimentary"]["last_year_mtd"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["last_year_mtd"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["last_year_mtd"] = data[0]["total_in_house_adult"] or 0 
	datas["arrival_adult"]["last_year_mtd"] = data[0]["total_arrival_adult"] or 0 
	datas["departure_adult"]["last_year_mtd"] = data[0]["total_departure_adult"] or 0 
	datas["in_house_child"]["last_year_mtd"] = data[0]["total_in_house_child"] or 0 
	datas["arrival_child"]["last_year_mtd"] = data[0]["total_arrival_child"] or 0 
	datas["departure_child"]["last_year_mtd"] = data[0]["total_departure_child"] or 0 
	datas["walk_in_adult"]["last_year_mtd"] = data[0]["total_in_house_walk_in_adult"] or 0 
	datas["walk_in_child"]["last_year_mtd"] = data[0]["total_in_house_walk_in_child"] or 0 
	datas["walk_in_room_night"]["last_year_mtd"] = data[0]["total_walk_in_room_night"] or 0 
	datas["arrival_room_night"]["last_year_mtd"] = data[0]["total_arrival_room_night"] or 0 
	datas["departure_room_night"]["last_year_mtd"] = data[0]["total_departure_room_night"] or 0 
	datas["no_show_room"]["last_year_mtd"] = data[0]["total_no_show_room"] or 0 
	datas["no_show_adult"]["last_year_mtd"] = data[0]["total_no_show_adult"] or 0 
	datas["no_show_child"]["last_year_mtd"] = data[0]["total_no_show_child"] or 0 
	datas["early_checked_out_adult"]["last_year_mtd"] = data[0]["total_early_checked_out_adult"] or 0 
	datas["early_checked_out_child"]["last_year_mtd"] = data[0]["total_early_checked_out_child"] or 0 
	datas["early_checked_out"]["last_year_mtd"] = data[0]["total_early_checked_out"] or 0 
	datas["fit_room"]["last_year_mtd"] = data[0]["total_fit_room"] or 0 
	datas["git_room"]["last_year_mtd"] = data[0]["total_git_room"] or 0 
	datas["fit_adult"]["last_year_mtd"] = data[0]["total_fit_adult"] or 0 
	datas["fit_child"]["last_year_mtd"] = data[0]["total_fit_child"] or 0 
	datas["git_adult"]["last_year_mtd"] = data[0]["total_git_adult"] or 0 
	datas["git_child"]["last_year_mtd"] = data[0]["total_git_child"] or 0 
	datas["vip_guest"]["last_year_mtd"] = data[0]["total_vip_guest"] or 0 
	datas["cancel_room"]["last_year_mtd"] = data_stay[0]["total_cancel_room"] or 0 
	datas["cancel_adult"]["last_year_mtd"] = data_stay[0]["total_cancel_adult"] or 0 
	datas["cancel_child"]["last_year_mtd"] = data_stay[0]["total_cancel_child"] or 0 
	datas["house_use"]["last_year_mtd"] = data[0]["total_house_use_room"] or 0 
	datas["complimentary"]["last_year_mtd"] = data[0]["total_complimentary_room"] or 0 
	datas["house_use_adult"]["last_year_mtd"] = data[0]["total_house_use_adult"] or 0 
	datas["house_use_child"]["last_year_mtd"] = data[0]["total_house_use_child"] or 0 
	datas["complimentary_adult"]["last_year_mtd"] = data[0]["total_complimentary_adult"] or 0 
	datas["complimentary_child"]["last_year_mtd"] = data[0]["total_complimentary_child"] or 0 

	

	# last year ytd
	filters.start_date = filters.last_year_ytd["start_date"]	
	filters.end_date= filters.last_year_ytd["end_date"]	
	# frappe.throw(str(filters.end_date))
	data = frappe.db.sql(sql,filters,as_dict=1) 
	data_stay = frappe.db.sql(stay,filters,as_dict=1) 

	datas["room_occupy"]["last_year_ytd"] = data[0]["total_occupy"] or 0 
	datas["room_block"]["last_year_ytd"] = data[0]["total_block"] or 0 
	datas["complimentary"]["last_year_ytd"] = data[0]["total_complimentary"] or 0 
	datas["house_use"]["last_year_ytd"] = data[0]["total_house_use"] or 0 
	datas["in_house_adult"]["last_year_ytd"] = data[0]["total_in_house_adult"] or 0 
	datas["arrival_adult"]["last_year_ytd"] = data[0]["total_arrival_adult"] or 0 
	datas["departure_adult"]["last_year_ytd"] = data[0]["total_departure_adult"] or 0 
	datas["in_house_child"]["last_year_ytd"] = data[0]["total_in_house_child"] or 0 
	datas["arrival_child"]["last_year_ytd"] = data[0]["total_arrival_child"] or 0 
	datas["departure_child"]["last_year_ytd"] = data[0]["total_departure_child"] or 0 
	datas["walk_in_adult"]["last_year_ytd"] = data[0]["total_in_house_walk_in_adult"] or 0 
	datas["walk_in_child"]["last_year_ytd"] = data[0]["total_in_house_walk_in_child"] or 0 
	datas["walk_in_room_night"]["last_year_ytd"] = data[0]["total_walk_in_room_night"] or 0 
	datas["arrival_room_night"]["last_year_ytd"] = data[0]["total_arrival_room_night"] or 0 
	datas["departure_room_night"]["last_year_ytd"] = data[0]["total_departure_room_night"] or 0 
	datas["no_show_room"]["last_year_ytd"] = data[0]["total_no_show_room"] or 0 
	datas["no_show_adult"]["last_year_ytd"] = data[0]["total_no_show_adult"] or 0 
	datas["no_show_child"]["last_year_ytd"] = data[0]["total_no_show_child"] or 0 
	datas["early_checked_out_adult"]["last_year_ytd"] = data[0]["total_early_checked_out_adult"] or 0 
	datas["early_checked_out_child"]["last_year_ytd"] = data[0]["total_early_checked_out_child"] or 0 
	datas["early_checked_out"]["last_year_ytd"] = data[0]["total_early_checked_out"] or 0 
	datas["fit_room"]["last_year_ytd"] = data[0]["total_fit_room"] or 0 
	datas["git_room"]["last_year_ytd"] = data[0]["total_git_room"] or 0 
	datas["fit_adult"]["last_year_ytd"] = data[0]["total_fit_adult"] or 0 
	datas["fit_child"]["last_year_ytd"] = data[0]["total_fit_child"] or 0 
	datas["git_adult"]["last_year_ytd"] = data[0]["total_git_adult"] or 0 
	datas["git_child"]["last_year_ytd"] = data[0]["total_git_child"] or 0 
	datas["vip_guest"]["last_year_ytd"] = data[0]["total_vip_guest"] or 0 
	datas["cancel_room"]["last_year_ytd"] = data_stay[0]["total_cancel_room"] or 0 
	datas["cancel_adult"]["last_year_ytd"] = data_stay[0]["total_cancel_adult"] or 0 
	datas["cancel_child"]["last_year_ytd"] = data_stay[0]["total_cancel_child"] or 0 
	datas["house_use"]["last_year_ytd"] = data[0]["total_house_use_room"] or 0 
	datas["complimentary"]["last_year_ytd"] = data[0]["total_complimentary_room"] or 0 
	datas["house_use_adult"]["last_year_ytd"] = data[0]["total_house_use_adult"] or 0 
	datas["house_use_child"]["last_year_ytd"] = data[0]["total_house_use_child"] or 0 
	datas["complimentary_adult"]["last_year_ytd"] = data[0]["total_complimentary_adult"] or 0 
	datas["complimentary_child"]["last_year_ytd"] = data[0]["total_complimentary_child"] or 0  



	# frappe.throw(str(filters.end_date))
	return datas

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
 


def get_revenue(filters):
	data = []
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_revenue_by_fieldname({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	
	revenue_data = []
	for r in set([d["flash_report_revenue_group"] for d in data]):
		row = {"title":r}
		for f in  fields:
			
			row[f] = sum([y["amount"] for y in data if y["fieldname"]==f and y["flash_report_revenue_group"]==r]) or 0

		revenue_data.append(row)
	# frappe.throw(str(revenue_data))
	total_row={"title":"Total Revenue"	}
	for f in  ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]:
		total_row[f] = sum([y["amount"] for y in data if y["fieldname"]==f]) or 0

	revenue_data.append(total_row)

	return revenue_data

def get_revenue_by_fieldname(filters):
    # current
    sql="""
		select
			%(fieldname)s as fieldname,
			flash_report_revenue_group,
  			sum(amount*if(type='Debit',1,-1)) as amount
		from `tabFolio Transaction`
		where
			property=%(property)s and 
			posting_date between %(start_date)s and %(end_date)s and 
			coalesce(flash_report_revenue_group,'') !=''
		group by 
			flash_report_revenue_group 
    """
    return frappe.db.sql(sql,filters, as_dict=1)
    

def get_ledger_balance(filters):
	data = []
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_ledger_balance_fieldname({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	
	ledger_balance_data = []
	for r in set([d["transaction_type"] for d in data]):
		row = {"title":r}
		for f in  fields:
			
			row[f] = sum([y["amount"] for y in data if y["fieldname"]==f and y["transaction_type"]==r]) or 0

		ledger_balance_data.append(row)
	# frappe.throw(str(ledger_balance_data))
	total_row={"title":"Total Ledger Balance"	}
	for f in  ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]:
		total_row[f] = sum([y["amount"] for y in data if y["fieldname"]==f]) or 0

	ledger_balance_data.append(total_row)

	return ledger_balance_data

def get_ledger_balance_fieldname(filters):

    sql="""
		select
			%(fieldname)s as fieldname,
			transaction_type,
  			sum(amount*if(type='Debit',1,-1)) as amount
		from `tabFolio Transaction`
		where
			property=%(property)s and 
			posting_date <=%(end_date)s and 
			transaction_type !='Cashier Shift' 
		group by 
			transaction_type 
    """
    return frappe.db.sql(sql,filters, as_dict=1)
def get_forecasting(filters):
	
	data = []
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_forecasting_fieldname({ "fieldname":f,"property":filters.property,"start_date":add_days(filters.get(f)["start_date"],1),"end_date":add_days(filters.get(f)["end_date"],1)})
	row = {
			"tmr_room_occupy":{"title":"Room Occupy for Tomorrow"}, 
			"tmr_arrival_adult":{"title":"Arrival Adult for Tomorrow"},
			"tmr_arrival_child":{"title":"Arrival Child for Tomorrow"},
			"tmr_arrival_pax":{"title":"Arrival PAX for Tomorrow"},
			"tmr_departure_adult":{"title":"Departure Adult for Tomorrow"},
			"tmr_departure_child":{"title":"Departure Child for Tomorrow"},
			"tmr_departure_pax":{"title":"Departure PAX for Tomorrow"},
			"tmr_arrival":{"title":"Arrival Room Nights for Tomorrow"},
			"tmr_departure":{"title":"Departure Room Nights for Tomorrow"},
		}
	
	forecasting_data = []
	for f in fields:
		
		row['tmr_room_occupy'][f] = [y["total_occupy"] for y in data if y["fieldname"]==f ] or 0
		
	forecasting_data.append(row)
	frappe.throw(str(forecasting_data))
	return forecasting_data

def get_forecasting_fieldname(filters):

    sql="""
		select 
			%(fieldname)s as fieldname,
			sum(type='Reservation') as total_occupy,
			sum(if(type='Reservation' and is_arrival=1,adult,0))  as total_arrival_adult,
			sum(if(type='Reservation' and is_departure=1,adult,0))  as total_departure_adult,
			sum(if(type='Reservation' and is_arrival=1,child,0))  as total_arrival_child,
			sum(if(type='Reservation' and is_departure=1,child,0))  as total_departure_child,
			sum(type='Reservation' and is_arrival=1)  as total_arrival_room_night,
			sum(type='Reservation' and is_departure=1)  as total_departure_room_night
		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s and is_active=1
    """
    return frappe.db.sql(sql,filters, as_dict=1)
    