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
	
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Manager Flash Report"} )
	report_data =  []
	rooms_available_record = get_current_room_in_property(filters)
	report_data.append(rooms_available_record)
	
	occupy_data = get_data_from_occupy_record(filters)
	report_data.append(occupy_data[0]['room_occupy'])
	report_data.append(occupy_data[0]["complimentary"])
	report_data.append(occupy_data[0]["house_use"])
	report_data.append(occupy_data[0]["room_block"])
	report_data.append(occupy_data[0]["arrival_adult"])
	report_data.append(occupy_data[0]["arrival_child"])
	report_data.append(occupy_data[0]["in_house_adult"])
	report_data.append(occupy_data[0]["in_house_child"])
	report_data.append(occupy_data[0]["departure_adult"])
	report_data.append(occupy_data[0]["departure_child"])
	report_data.append(occupy_data[0]["walk_in_adult"])
	report_data.append(occupy_data[0]["walk_in_child"])
	report_data.append(occupy_data[0]["walk_in_room_night"])
	report_data.append(occupy_data[0]["arrival_room_night"])
	report_data.append(occupy_data[0]["departure_room_night"])
	report_data.append(occupy_data[0]["no_show_room"])
	report_data.append(occupy_data[0]["no_show_adult"])
	report_data.append(occupy_data[0]["no_show_child"])
	report_data.append(occupy_data[0]["early_checked_out_adult"])
	report_data.append(occupy_data[0]["early_checked_out_child"])
	report_data.append(occupy_data[0]["early_checked_out"])
	report_data.append(occupy_data[0]["fit_room"])
	report_data.append(occupy_data[0]["git_room"])
	report_data.append(occupy_data[0]["fit_adult"])
	report_data.append(occupy_data[0]["fit_child"])
	report_data.append(occupy_data[0]["git_adult"])
	report_data.append(occupy_data[0]["git_child"])
	# report_data.append(occupy_data[0]["cancel_room"])
	# report_data.append(occupy_data[0]["cancel_adult"])
	# report_data.append(occupy_data[0]["cancel_child"])
	report_data.append(occupy_data[0]["complimentary_adult"])
	report_data.append(occupy_data[0]["complimentary_child"])
	report_data.append(occupy_data[0]["house_use_adult"])
	report_data.append(occupy_data[0]["house_use_child"])
	
	# revenue
	report_data+= get_revenue(filters)

	#ledger balance 
	report_data+= get_ledger_balance(filters)
	report_data+= get_guest_type(filters)

	#forecasting for tomorrow
	forecasting= get_forecasting(filters)
	report_data.append(forecasting[0]['tmr_room_occupy'])
	report_data.append(forecasting[0]['tmr_arrival_adult'])
	report_data.append(forecasting[0]['tmr_arrival_child'])
	report_data.append(forecasting[0]['tmr_departure_adult'])
	report_data.append(forecasting[0]['tmr_departure_child'])
	report_data.append(forecasting[0]['tmr_arrival'])
	report_data.append(forecasting[0]['tmr_departure'])

	#forecating for the next 7 days
	next_seven_day = get_forecasting_next_seven_day(filters)
	report_data.append(next_seven_day[0]['seven_day_room_occupy'])
	report_data.append(next_seven_day[0]['seven_day_arrival_adult'])
	report_data.append(next_seven_day[0]['seven_day_arrival_child'])
	report_data.append(next_seven_day[0]['seven_day_departure_adult'])
	report_data.append(next_seven_day[0]['seven_day_departure_child'])
	report_data.append(next_seven_day[0]['seven_day_arrival'])
	report_data.append(next_seven_day[0]['seven_day_departure'])

	#calculate room occupy
	#calculate room occupancy
	occpancy = {"title":"Occupancy"}
	revpar = {"title":"RevPAR"}
	adr = {"title":"ADR"}
	arrival_pax = {"title":"Arrival PAX for Tomorrow"}
	departure_pax = {"title":"Departure PAX for Tomorrow"}
	vacant_rooms = {"title":"Total Vacant Rooms"}
	room_minus_ooo_rooms = {"title":"Total Rooms in Property minus OOO Rooms"}
	room_minus_ooo_and_hous_use = {"title":"Rooms Occupied minus OOO and House Use Rooms"}
	room_minus_ooo_and_complimentary = {"title":"Rooms Occupied minus OOO and Complimentary Rooms"}
	room_minus_house_use_and_complimentary = {"title":"Rooms Occupied minus Complimentary and House Use"}
	room_minus_complimentary = {"title":"Rooms Occupied minus Complimentary"}
	room_minus_house_use = {"title":"Rooms Occupied minus House Use"}
	available_room = {"title":"Total Available Rooms"}
	total_arrival_pax = {"title":"Total Arrival PAX"}
	total_inhoue_pax = {"title":"Total In-house PAX"}
	total_departure_pax = {"title":"Total Departure PAX"}
	walkin_inhouse_pax = {"title":"Walk-In In-house Pax"}
	noshow_pax = {"title":"No Show PAX"}
	early_checkout_pax = {"title":"Early Checked Out PAX"}
	fit_pax = {"title":"FIT PAX"}
	git_pax = {"title":"GIT PAX"}
	cancalled_pax = {"title":"Cancelled PAX"}
	house_use_pax = {"title":"House Use PAX"}
	complimentary_pax = {"title":"Complimentary PAX"}
	arrival_pax_for_seven_day = {"title":"Arrival PAX for the Next 7 Days"}
	departure_pax_for_seven_day = {"title":"Departure PAX for the Next 7 Days"}
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
	calculate_adr_include_all_room_occupied = frappe.db.get_single_value("eDoor Setting", "calculate_adr_include_all_room_occupied")

	for f in ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]:
		total_room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Total Rooms in Property']) or 0
		room_occupy = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Rooms Occupy']) or 0
		room_block = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Out of Order Rooms']) or 0
		house_use_room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'House Use Rooms']) or 0
		complimentary_room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Complimentary Rooms']) or 0
		adult_arrival = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Arrival Adult']) or 0
		child_arrival = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Arrival Child']) or 0
		adult_departure = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Departure Adult']) or 0
		child_departure = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Departure Child']) or 0
		inhouse_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'In-house Adult']) or 0
		inhouse_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'In-house Child']) or 0
		walkin_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Walk-In Adult']) or 0
		walkin_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Walk-In Child']) or 0
		noshow_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'No Show Adult']) or 0
		noshow_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'No Show Child']) or 0
		early_checkout_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Early Checked Out Adult']) or 0
		early_checkout_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Early Checked Out Child']) or 0
		cancalled_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Cancelled Adult']) or 0
		cancalled_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Cancelled Child']) or 0
		house_use_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'House Use Adult']) or 0
		house_use_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'House Use Child']) or 0
		complimentary_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Complimentary Adult']) or 0
		complimentary_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Complimentary Child']) or 0
		git_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'GIT Adult']) or 0
		git_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'GIT Child']) or 0
		fit_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'FIT Adult']) or 0
		fit_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'FIT Child']) or 0
		room_charge = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Room Charge']) or 0
		# other_room_charge = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Other Room Revenue']) or 0
		
		room_minus_ooo_rooms[f] =  total_room - room_block
		available_room[f] =  total_room - (room_occupy + room_block)
		if calculate_room_occupancy_include_room_block==1:
			occpancy[f] =  room_occupy / (1 if total_room == 0 else total_room)
		else:
			occpancy[f] = room_occupy / (1 if (total_room - room_block) == 0 else (total_room - room_block))

		if calculate_adr_include_all_room_occupied==1:
			adr[f] =  (room_charge ) / (1 if room_occupy == 0 else room_occupy)
			
		else:
			adr[f] = (room_charge ) / (1 if (room_occupy - (complimentary_room + house_use_room)) == 0 else (room_occupy - (complimentary_room + house_use_room)))

		arrival_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Arrival Adult for Tomorrow']) or 0
		arrival_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Arrival Child for Tomorrow']) or 0
		arrival_pax[f] =  arrival_adult + arrival_child
		departure_adult = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Departure Adult for Tomorrow']) or 0
		departure_child = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Departure Child for Tomorrow']) or 0
		departure_pax[f] =  departure_adult + departure_child	

		arrival_adult_for_seven_day = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Arrival Adult for the Next 7 Days']) or 0
		arrival_child_for_seven_day = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Arrival Child for the Next 7 Days']) or 0
		arrival_pax_for_seven_day[f] =  arrival_adult_for_seven_day + arrival_child_for_seven_day
		departure_adult_for_seven_day = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Departure Adult for the Next 7 Days']) or 0
		departure_child_for_seven_day = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Departure Child for the Next 7 Days']) or 0
		departure_pax_for_seven_day[f] =  departure_adult_for_seven_day + departure_child_for_seven_day	

		vacant_rooms[f] =  total_room - room_occupy
		
		room_minus_ooo_and_hous_use[f] =  room_occupy - (house_use_room + room_block)
	
		room_minus_ooo_and_complimentary[f] =  room_occupy - (complimentary_room + room_block)
	
		room_minus_house_use_and_complimentary[f] =   room_occupy - (complimentary_room + house_use_room)
		
		room_minus_complimentary[f] =  total_room - complimentary_room
		
		room_minus_house_use[f] =  total_room - house_use_room
		
		total_arrival_pax[f] =  adult_arrival + child_arrival
		
		total_inhoue_pax[f] =  inhouse_adult + inhouse_child
		
		total_departure_pax[f] =  adult_departure + child_departure
		
		walkin_inhouse_pax[f] =  walkin_adult + walkin_child
		
		noshow_pax[f] =  noshow_adult + noshow_child
		
		early_checkout_pax[f] =  early_checkout_adult + early_checkout_child
		fit_pax[f] =  fit_adult + fit_child
		git_pax[f] =  git_adult + git_child
		cancalled_pax[f] =  cancalled_adult + cancalled_child
		house_use_pax[f] =  house_use_adult + house_use_child
		complimentary_pax[f] =  complimentary_adult + complimentary_child
		
		# frappe.throw(str( adr))
	report_data.append(adr)
	report_data.append(occpancy)
	report_data.append(arrival_pax)
	report_data.append(departure_pax)
	report_data.append(vacant_rooms)
	report_data.append(available_room)
	report_data.append(room_minus_ooo_rooms)
	report_data.append(room_minus_ooo_and_hous_use)
	report_data.append(room_minus_ooo_and_complimentary)
	report_data.append(room_minus_house_use_and_complimentary)
	report_data.append(room_minus_complimentary)
	report_data.append(room_minus_house_use)
	report_data.append(total_arrival_pax)
	report_data.append(total_inhoue_pax)
	report_data.append(total_departure_pax)
	report_data.append(walkin_inhouse_pax)
	report_data.append(noshow_pax)
	report_data.append(early_checkout_pax)
	report_data.append(fit_pax)
	report_data.append(git_pax)
	report_data.append(cancalled_pax)
	report_data.append(house_use_pax)
	report_data.append(arrival_pax_for_seven_day)
	report_data.append(departure_pax_for_seven_day)
	report_data.append(complimentary_pax)
	
	report_data.append(revpar)
        
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
			row = [d for d in report_data if d.get('title', 'No Title') == r.field_name]
			if r.formula:
				row=[get_row_calculate_filed(r,report_data)]
			

			if row:
				row = row[0]
				row["indent"] = 1
				row["is_bold"] = r.is_bold
    
				row["title"] = r.custom_name or r.field_name
				
				if (  "last_year_ytd" in row and row["last_year_ytd"] or 0) ==0:
					row["change_percentage"] = 100
				else:
					row["change_percentage"] = ((row["ytd"] or 0 ) - (row["last_year_ytd"] or 0 )) / (row["last_year_ytd"] or 0 )
				
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
            
def get_data_from_occupy_record(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_data_fieldname({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"room_occupy":{"title":"Rooms Occupy"},
				"room_block":{"title":"Out of Order Rooms"},
				"complimentary":{"title":"Complimentary Rooms"},
				"house_use":{"title":"House Use Rooms"},
				"in_house_adult":{"title":"In-house Adult"},	
				"arrival_adult":{"title":"Arrival Adult"},	
				"departure_adult":{"title":"Departure Adult"},	
				"in_house_child":{"title":"In-house Child"},	
				"arrival_child":{"title":"Arrival Child"},	
				"departure_child":{"title":"Departure Child"},	
				"walk_in_adult":{"title":"Walk-In Adult"},	
				"walk_in_child":{"title":"Walk-In Child"},	
				"walk_in_room_night":{"title":"Walk-In Room"},	
				"arrival_room_night":{"title":"Arrival Room",},	
				"departure_room_night":{"title":"Departure Room"},	
				"no_show_room":{"title":"No Show Room"},	
				"no_show_adult":{"title":"No Show Adult"},	
				"no_show_child":{"title":"No Show Child"},	
				"early_checked_out_adult":{"title":"Early Checked Out Adult"},	
				"early_checked_out_child":{"title":"Early Checked Out Child"},	
				"early_checked_out":{"title":"Early Checked Out Rooms"},	
				"fit_room":{"title":"FIT Rooms"},	
				"git_room":{"title":"GIT Rooms"},	
				"fit_adult":{"title":"FIT Adult"},	
				"fit_child":{"title":"FIT Child"},	
				"git_adult":{"title":"GIT Adult"},	
				"git_child":{"title":"GIT Child"},				
				"house_use_adult":{"title":"House Use Adult"},	
				"house_use_child":{"title":"House Use Child"},	
				"complimentary_adult":{"title":"Complimentary Adult"},	
				"complimentary_child":{"title":"Complimentary Child"},	
				
	}
	occupy_data = []
	for f in fields:
		row['room_occupy'][f] = sum([y["total_occupy"] for y in data if y["fieldname"]==f and y["total_occupy"] is not None]) or 0
		row['room_block'][f] = sum([y["total_block"] for y in data if y["fieldname"]==f and y["total_block"] is not None]) or 0
		row['complimentary'][f] = sum([y["total_complimentary"] for y in data if y["fieldname"]==f and y["total_complimentary"] is not None]) or 0
		row['house_use'][f] = sum([y["total_house_use"] for y in data if y["fieldname"]==f and y["total_house_use"] is not None]) or 0
		row['in_house_adult'][f] = sum([y["total_in_house_adult"] for y in data if y["fieldname"]==f and y["total_in_house_adult"] is not None]) or 0
		row['arrival_adult'][f] = sum([y["total_arrival_adult"] for y in data if y["fieldname"]==f and y["total_arrival_adult"] is not None]) or 0
		row['departure_adult'][f] = sum([y["total_departure_adult"] for y in data if y["fieldname"]==f and y["total_departure_adult"] is not None]) or 0
		row['in_house_child'][f] = sum([y["total_in_house_child"] for y in data if y["fieldname"]==f and y["total_in_house_child"] is not None]) or 0
		row['arrival_child'][f] = sum([y["total_arrival_child"] for y in data if y["fieldname"]==f and y["total_arrival_child"] is not None]) or 0
		row['departure_child'][f] = sum([y["total_departure_child"] for y in data if y["fieldname"]==f and y["total_departure_child"] is not None]) or 0
		row['walk_in_adult'][f] = sum([y["total_in_house_walk_in_adult"] for y in data if y["fieldname"]==f and y["total_in_house_walk_in_adult"] is not None]) or 0
		row['walk_in_child'][f] = sum([y["total_in_house_walk_in_child"] for y in data if y["fieldname"]==f and y["total_in_house_walk_in_child"] is not None]) or 0
		row['walk_in_room_night'][f] = sum([y["total_walk_in_room_night"] for y in data if y["fieldname"]==f and y["total_walk_in_room_night"] is not None]) or 0
		row['arrival_room_night'][f] = sum([y["total_arrival_room_night"] for y in data if y["fieldname"]==f and y["total_arrival_room_night"] is not None]) or 0
		row['departure_room_night'][f] = sum([y["total_departure_room_night"] for y in data if y["fieldname"]==f and y["total_departure_room_night"] is not None]) or 0
		row['no_show_room'][f] = sum([y["total_no_show_room"] for y in data if y["fieldname"]==f and y["total_no_show_room"] is not None]) or 0
		row['no_show_adult'][f] = sum([y["total_no_show_adult"] for y in data if y["fieldname"]==f and y["total_no_show_adult"] is not None]) or 0
		row['no_show_child'][f] = sum([y["total_no_show_child"] for y in data if y["fieldname"]==f and y["total_no_show_child"] is not None]) or 0
		row['early_checked_out_adult'][f] = sum([y["total_early_checked_out_adult"] for y in data if y["fieldname"]==f and y["total_early_checked_out_adult"] is not None]) or 0
		row['early_checked_out_child'][f] = sum([y["total_early_checked_out_child"] for y in data if y["fieldname"]==f and y["total_early_checked_out_child"] is not None]) or 0
		row['early_checked_out'][f] = sum([y["total_early_checked_out"] for y in data if y["fieldname"]==f and y["total_early_checked_out"] is not None]) or 0
		row['fit_room'][f] = sum([y["total_fit_room"] for y in data if y["fieldname"]==f and y["total_fit_room"] is not None]) or 0
		row['git_room'][f] = sum([y["total_git_room"] for y in data if y["fieldname"]==f and y["total_git_room"] is not None]) or 0
		row['fit_adult'][f] = sum([y["total_fit_adult"] for y in data if y["fieldname"]==f and y["total_fit_adult"] is not None]) or 0
		row['fit_child'][f] = sum([y["total_fit_child"] for y in data if y["fieldname"]==f and y["total_fit_child"] is not None]) or 0
		row['git_adult'][f] = sum([y["total_git_adult"] for y in data if y["fieldname"]==f and y["total_git_adult"] is not None]) or 0
		row['git_child'][f] = sum([y["total_git_child"] for y in data if y["fieldname"]==f and y["total_git_child"] is not None]) or 0
		row['house_use_adult'][f] = sum([y["total_house_use_adult"] for y in data if y["fieldname"]==f and y["total_house_use_adult"] is not None]) or 0
		row['house_use_child'][f] = sum([y["total_house_use_child"] for y in data if y["fieldname"]==f and y["total_house_use_child"] is not None]) or 0
		row['complimentary_adult'][f] = sum([y["total_complimentary_adult"] for y in data if y["fieldname"]==f and y["total_complimentary_adult"] is not None]) or 0
		row['complimentary_child'][f] = sum([y["total_complimentary_child"] for y in data if y["fieldname"]==f and y["total_complimentary_child"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_data_fieldname(filters):
	
	sql="""select 
			%(fieldname)s as fieldname,
			sum(type='Reservation' and is_active=1) as total_occupy,
			sum(type='Block') as total_block, 
			sum(type='Reservation' and is_complimentary=1 and is_active=1)  as total_complimentary ,
			sum(type='Reservation' and is_house_use=1 and is_active=1)  as total_house_use,
			sum(if(type='Reservation' and is_active=1 and reservation_status='In-house',adult,0))  as total_in_house_adult,
			sum(if(type='Reservation' and is_arrival=1 and is_active=1,adult,0))  as total_arrival_adult,
			sum(if(type='Reservation' and is_departure=1,adult,0))  as total_departure_adult,
			sum(if(type='Reservation' and is_arrival=1 and is_active=1,child,0))  as total_arrival_child,
			sum(if(type='Reservation' and is_departure=1,child,0))  as total_departure_child,
			sum(if(type='Reservation' and is_active=1 and reservation_status='In-house',child,0))  as total_in_house_child,
			sum(if(type='Reservation' and is_walk_in=1 and is_active=1,adult,0))  as total_in_house_walk_in_adult,
			sum(if(type='Reservation' and is_walk_in=1 and is_active=1,child,0))  as total_in_house_walk_in_child,
			sum(type='Reservation' and is_walk_in=1 and is_active=1)  as total_walk_in_room_night,
			sum(type='Reservation' and is_arrival=1 and is_active=1)  as total_arrival_room_night,
			sum(type='Reservation' and is_departure=1)  as total_departure_room_night,
			sum(type = 'Reservation' and reservation_status='No Show' and is_active=1) as total_no_show_room,
			sum(if(type='Reservation' and reservation_status='No Show' and is_active=1,adult,0)) as total_no_show_adult,
			sum(if(type='Reservation' and reservation_status='No Show' and is_active=1,child,0)) as total_no_show_child,
			sum(if(type='Reservation' and is_stay_over=1 and is_departure=1 and is_active=1,adult,0)) as total_early_checked_out_adult,
			sum(if(type='Reservation' and is_stay_over=1 and is_departure=1 and is_active=1,child,0)) as total_early_checked_out_child,
			sum(type='Reservation' and is_stay_over=1 and is_departure=1 and is_active=1) as total_early_checked_out,
			sum(type='Reservation' and reservation_type='FIT' and is_active=1) as total_fit_room,
			sum(type='Reservation' and reservation_type='GIT' and is_active=1) as total_git_room,
			sum(if(type='Reservation' and reservation_type='FIT' and is_active=1,adult,0)) as total_fit_adult,
			sum(if(type='Reservation' and reservation_type='FIT' and is_active=1,child,0)) as total_fit_child,
			sum(if(type='Reservation' and reservation_type='GIT' and is_active=1,adult,0)) as total_git_adult,
			sum(if(type='Reservation' and reservation_type='GIT' and is_active=1,child,0)) as total_git_child,
			sum(if(type='Reservation' and  is_house_use=1 and is_active=1,adult,0)) as total_house_use_adult,
			sum(if(type='Reservation' and is_house_use=1 and is_active=1,child,0)) as total_house_use_child,
			sum(if(type='Reservation' and is_complimentary=1 and is_active=1,adult,0)) as total_complimentary_adult,
			sum(if(type='Reservation' and is_complimentary=1 and is_active=1,child,0)) as total_complimentary_child
		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s """

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

def get_guest_type(filters):
	data = []
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_guest_type_fieldname({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	
	revenue_data = []
	for r in set([d["guest_type"] for d in data]):
		row = {"title":r}
		for f in  fields:
			
			row[f] = sum([y["guest_type_count"] for y in data if y["fieldname"]==f and y["guest_type"]==r]) or 0

		revenue_data.append(row)

	return revenue_data

def get_guest_type_fieldname(filters):
    # current
    sql="""
		select
			%(fieldname)s as fieldname,
			guest_type,
			sum(type='Reservation')  as guest_type_count 
		from `tabRoom Occupy`
		where
			property=%(property)s and 
			date between %(start_date)s and %(end_date)s and
			is_active = 1 and
			coalesce(guest_type,'') !=''
		group by 
			guest_type 
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
			
			"tmr_departure_adult":{"title":"Departure Adult for Tomorrow"},
			"tmr_departure_child":{"title":"Departure Child for Tomorrow"},
			
			"tmr_arrival":{"title":"Arrival Room Nights for Tomorrow"},
			"tmr_departure":{"title":"Departure Room Nights for Tomorrow"},
		}
	
	forecasting_data = []
	for f in fields:
		# frappe.throw(str(sum([y["total_occupy"] for y in data if y["fieldname"]==f ]) or 0))
		row['tmr_room_occupy'][f] = sum([y["total_occupy"] for y in data if y["fieldname"]==f and y["total_occupy"] is not None]) or 0
		row['tmr_arrival_adult'][f] = sum([y["total_arrival_adult"] for y in data if y["fieldname"]==f and y["total_arrival_adult"] is not None]) or 0
		row['tmr_arrival_child'][f] = sum([y["total_arrival_child"] for y in data if y["fieldname"]==f and y["total_arrival_child"] is not None]) or 0
		
		row['tmr_departure_adult'][f] = sum([y["total_departure_adult"] for y in data if y["fieldname"]==f and y["total_departure_adult"] is not None]) or 0
		row['tmr_departure_child'][f] = sum([y["total_departure_child"] for y in data if y["fieldname"]==f and y["total_departure_child"] is not None]) or 0
		
		row['tmr_arrival'][f] = sum([y["total_arrival_room_night"] for y in data if y["fieldname"]==f and y["total_arrival_room_night"] is not None]) or 0
		row['tmr_departure'][f] = sum([y["total_departure_room_night"] for y in data if y["fieldname"]==f and y["total_departure_room_night"] is not None]) or 0
		
	forecasting_data.append(row)
	
	return forecasting_data

def get_forecasting_next_seven_day(filters):
	
	data = []
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		
		data+=get_forecasting_fieldname({ "fieldname":f,"property":filters.property,"start_date":add_days(filters.get(f)["start_date"],7),"end_date":add_days(filters.get(f)["end_date"],7)})
	row = {
			"seven_day_room_occupy":{"title":"Room Occupy for the Next 7 Days"}, 
			"seven_day_arrival_adult":{"title":"Arrival Adult for the Next 7 Days"},
			"seven_day_arrival_child":{"title":"Arrival Child for the Next 7 Days"},
			
			"seven_day_departure_adult":{"title":"Departure Adult for the Next 7 Days"},
			"seven_day_departure_child":{"title":"Departure Child for the Next 7 Days"},
			
			"seven_day_arrival":{"title":"Arrival Room Nights for the Next 7 Days"},
			"seven_day_departure":{"title":"Departure Room Nights for the Next 7 Days"},
		}
	
	forecasting_data_next_seven_day = []
	for f in fields:
		# frappe.throw(str(sum([y["total_occupy"] for y in data if y["fieldname"]==f ]) or 0))
		row['seven_day_room_occupy'][f] = sum([y["total_occupy"] for y in data if y["fieldname"]==f and y["total_occupy"] is not None]) or 0
		row['seven_day_arrival_adult'][f] = sum([y["total_arrival_adult"] for y in data if y["fieldname"]==f and y["total_arrival_adult"] is not None]) or 0
		row['seven_day_arrival_child'][f] = sum([y["total_arrival_child"] for y in data if y["fieldname"]==f and y["total_arrival_child"] is not None]) or 0
		
		row['seven_day_departure_adult'][f] = sum([y["total_departure_adult"] for y in data if y["fieldname"]==f and y["total_departure_adult"] is not None]) or 0
		row['seven_day_departure_child'][f] = sum([y["total_departure_child"] for y in data if y["fieldname"]==f and y["total_departure_child"] is not None]) or 0
		
		row['seven_day_arrival'][f] = sum([y["total_arrival_room_night"] for y in data if y["fieldname"]==f and y["total_arrival_room_night"] is not None]) or 0
		row['seven_day_departure'][f] = sum([y["total_departure_room_night"] for y in data if y["fieldname"]==f and y["total_departure_room_night"] is not None]) or 0
		
	forecasting_data_next_seven_day.append(row)
	
	return forecasting_data_next_seven_day

def get_forecasting_fieldname(filters):

    sql="""
		select 
			%(fieldname)s as fieldname,
			sum(type='Reservation' and is_active=1) as total_occupy,
			sum(if(type='Reservation' and is_arrival=1 and is_active=1,adult,0))  as total_arrival_adult,
			sum(if(type='Reservation' and is_departure=1,adult,0))  as total_departure_adult,
			sum(if(type='Reservation' and is_arrival=1 and is_active=1,child,0))  as total_arrival_child,
			sum(if(type='Reservation' and is_departure=1 ,child,0))  as total_departure_child,
			sum(type='Reservation' and is_arrival=1 and is_active=1)  as total_arrival_room_night,
			sum(type='Reservation' and is_departure=1)  as total_departure_room_night
		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s 
    """
    return frappe.db.sql(sql,filters, as_dict=1)
    
    
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
	return sum([d[field] for d in report_data if d["title"] == title]) or 0