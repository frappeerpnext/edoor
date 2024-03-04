# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff,today ,add_months, add_days,getdate
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta


def execute(filters=None):
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
		{"fieldname": "change_percentage", "label": "% Change", "width":150, "align":"right"},
	]


def get_report_data(filters):
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Manager Flash Report"} )
	report_data =  []
	rooms_available_record = get_current_room_in_property(filters)
	report_data.append(rooms_available_record)
	
	occupy_data = get_data_from_occupy_record(filters)
	report_data.append(occupy_data["room_occupy"])

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
		"change_percentage":((ytd_room-last_year_ytd_room)/(1 if ytd_room==0 else ytd_room or 0))*100,
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
		"change_percentage":((ytd_rooms - last_ytd_rooms)/(1 if ytd_rooms==0 else ytd_rooms or 0))*100,
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
		"change_percentage": ((ytd - last_ytd)/(1 if ytd==0 else ytd or 0))*100,
		
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
		"change_percentage": ((ytd - last_ytd)/(1 if ytd == 0 else ytd or 0))*100,
		
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
		
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
		
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
		
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
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
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
	})
	report_data.append(occupy_data["cancel_room"])
	report_data.append(occupy_data["cancel_adult"])
	report_data.append(occupy_data["cancel_child"])
	ytd =  occupy_data["cancel_adult"]["ytd"] +(  occupy_data["cancel_child"]["ytd"])
	last_ytd =  occupy_data["cancel_adult"]["last_year_ytd"] +(  occupy_data["cancel_child"]["last_year_ytd"])
	report_data.append({
		"title": "Cancel PAX",
		"current": occupy_data["cancel_adult"]["current"] + ( occupy_data["cancel_child"]["current"]),
		"mtd": occupy_data["cancel_adult"]["mtd"] + ( occupy_data["cancel_child"]["mtd"]),
		"ytd": ytd,
		"last_year_current": occupy_data["cancel_adult"]["last_year_current"] +(  occupy_data["cancel_child"]["last_year_current"]),
		"last_year_mtd": occupy_data["cancel_adult"]["last_year_mtd"] +(  occupy_data["cancel_child"]["last_year_mtd"]),
		"last_year_ytd": last_ytd,
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
	})
	report_data.append(occupy_data["room_charge"])
	report_data.append(occupy_data["housekeeping"])
	report_data.append(occupy_data["spa_massage"])
	report_data.append(occupy_data["service_charge"])
	report_data.append(occupy_data["non_revenue"])
	report_data.append(occupy_data["tip"])
	report_data.append(occupy_data["tour_ticket"])
	report_data.append(occupy_data["food_and_beverage"])
	report_data.append(occupy_data["other_charge"])
	report_data.append(occupy_data["merchindise"])
	ytd =  (occupy_data["room_charge"]["ytd"] or 0) /(1 if (occupy_data["room_occupy"]["ytd"])==0 else (occupy_data["room_occupy"]["ytd"]) or 0)
	last_ytd =  (occupy_data["room_charge"]["last_year_ytd"] or 0) /(1 if (occupy_data["room_occupy"]["last_year_ytd"])==0 else (occupy_data["room_occupy"]["last_year_ytd"]) or 0)
	report_data.append({
		"title": "ADR",
		"current": (occupy_data["room_charge"]["current"] or 0) / (1 if ( occupy_data["room_occupy"]["current"])==0 else (occupy_data["room_occupy"]["current"]) or 0),
		"mtd": (occupy_data["room_charge"]["mtd"] or 0) / (1 if ( occupy_data["room_occupy"]["mtd"])==0 else ( occupy_data["room_occupy"]["mtd"]) or 0),
		"ytd": ytd,
		"last_year_current": (occupy_data["room_charge"]["last_year_current"] or 0) /(1 if (occupy_data["room_occupy"]["last_year_current"])==0 else (occupy_data["room_occupy"]["last_year_current"]) or 0),
		"last_year_mtd": (occupy_data["room_charge"]["last_year_mtd"] or 0) /(1 if (occupy_data["room_occupy"]["last_year_mtd"])==0 else (occupy_data["room_occupy"]["last_year_mtd"]) or 0),
		"last_year_ytd": last_ytd,
		"change_percentage": ((ytd - last_ytd) /(1 if ytd==0 else ytd or 0))*100,
	})
	report_data.append(occupy_data["vip_guest"])

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
				return_report_data.append(row)
    
	return return_report_data #+ [{}] + report_data


def get_data_from_occupy_record(filters):
	filters.start_date = getdate(filters.date)
	filters.end_date = getdate(filters.date)
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
			sum(if(type='Reservation' and reservation_type='GIT',child,0)) as total_git_child
		from `tabRoom Occupy` where property=%(property)s and date = %(start_date)s and %(end_date)s and is_active=1"""
	stay = """
			select sum(if(reservation_status='Cancelled',adult,0)) as total_cancel_adult,
       			sum(if(reservation_status='Cancelled',child,0)) as total_cancel_child,
       			sum(reservation_status='Cancelled') as total_cancel_room
			from `tabReservation Stay` where property=%(property)s and working_date = %(start_date)s and %(end_date)s
			"""
	tran = """
			select 
				sum(if(parent_account_code in ('10100'),amount,0) * if(type='Debit',1,-1) )  as total_room_charge,
				sum(if(parent_account_code in ('10200'),amount,0) * if(type='Debit',1,-1) )  as total_housekeeping,
				sum(if(parent_account_code in ('10300'),amount,0) * if(type='Debit',1,-1) )  as total_spa_massage,
				sum(if(parent_account_code in ('10400'),amount,0) * if(type='Debit',1,-1) )  as total_tour_and_ticket,
				sum(if(parent_account_code in ('10500'),amount,0) * if(type='Debit',1,-1) )  as total_service_charge,
				sum(if(parent_account_code in ('10600'),amount,0) * if(type='Debit',1,-1) )  as total_tip,
				sum(if(parent_account_code in ('10700'),amount,0) * if(type='Debit',1,-1) )  as total_non_revenue,
				sum(if(parent_account_code in ('10800'),amount,0) * if(type='Debit',1,-1) )  as total_fb,
				sum(if(parent_account_code in ('10900'),amount,0) * if(type='Debit',1,-1) )  as total_other_charge,
				sum(if(parent_account_code in ('11000'),amount,0) * if(type='Debit',1,-1) )  as total_merchandise
			from `tabFolio Transaction` where property=%(property)s and posting_date = %(start_date)s and %(end_date)s
			"""
	
	data = frappe.db.sql(sql,filters,as_dict=1) 
	trans = frappe.db.sql(tran,filters,as_dict=1)
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
				"room_charge":{"title":"Room Charge", "current": trans[0]["total_room_charge"] or 0,"datatype":"Currency"},	
				"housekeeping":{"title":"Housekeeping", "current": trans[0]["total_housekeeping"] or 0},	
				"spa_massage":{"title":"Spa & Massage", "current": trans[0]["total_spa_massage"] or 0},	
				"tour_ticket":{"title":"Tour Desk & Tickets", "current": trans[0]["total_tour_and_ticket"] or 0},	
				"service_charge":{"title":"Service Charge", "current": trans[0]["total_service_charge"] or 0},	
				"tip":{"title":"Tip", "current": trans[0]["total_tip"] or 0},	
				"non_revenue":{"title":"Non Revenue", "current": trans[0]["total_non_revenue"] or 0},	
				"food_and_beverage":{"title":"Food & Beverage", "current": trans[0]["total_fb"] or 0},	
				"other_charge":{"title":"Other Charge", "current": trans[0]["total_other_charge"] or 0},	
				"merchindise":{"title":"Merchindise", "current": trans[0]["total_merchandise"] or 0},	
				
	}

	#mtd
	filters.start_date = getdate(filters.date).replace(day=1)
	data = frappe.db.sql(sql,filters,as_dict=1) 
	trans = frappe.db.sql(tran,filters,as_dict=1)
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
	datas["cancel_room"]["mtd"] = data_stay[0]["total_cancel_room"] or 0 
	datas["cancel_adult"]["mtd"] = data_stay[0]["total_cancel_adult"] or 0 
	datas["cancel_child"]["mtd"] = data_stay[0]["total_cancel_child"] or 0 
	datas["room_charge"]["mtd"] = trans[0]["total_room_charge"] or 0 
	datas["housekeeping"]["mtd"] = trans[0]["total_housekeeping"] or 0 
	datas["spa_massage"]["mtd"] = trans[0]["total_spa_massage"] or 0 
	datas["tour_ticket"]["mtd"] = trans[ 0]["total_tour_and_ticket"] or 0 
	datas["service_charge"]["mtd"] = trans[ 0]["total_service_charge"] or 0 
	datas["tip"]["mtd"] = trans[ 0]["total_tip"] or 0 
	datas["non_revenue"]["mtd"] = trans[ 0]["total_non_revenue"] or 0 
	datas["food_and_beverage"]["mtd"] = trans[ 0]["total_fb"] or 0 
	datas["other_charge"]["mtd"] = trans[ 0]["total_other_charge"] or 0 
	datas["merchindise"]["mtd"] = trans[ 0]["total_merchandise"] or 0 

	#ytd
	filters.start_date = getdate(filters.date).replace(day=1, month=1)
	data = frappe.db.sql(sql,filters,as_dict=1) 
	trans = frappe.db.sql(tran,filters,as_dict=1)
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
	datas["room_charge"]["ytd"] = trans[0]["total_room_charge"] or 0 
	datas["housekeeping"]["ytd"] = trans[0]["total_housekeeping"] or 0 
	datas["spa_massage"]["ytd"] = trans[0]["total_spa_massage"] or 0 
	datas["tour_ticket"]["ytd"] = trans[ 0]["total_tour_and_ticket"] or 0 
	datas["service_charge"]["ytd"] = trans[ 0]["total_service_charge"] or 0 
	datas["tip"]["ytd"] = trans[ 0]["total_tip"] or 0 
	datas["non_revenue"]["ytd"] = trans[ 0]["total_non_revenue"] or 0 
	datas["food_and_beverage"]["ytd"] = trans[ 0]["total_fb"] or 0 
	datas["other_charge"]["ytd"] = trans[ 0]["total_other_charge"] or 0 
	datas["merchindise"]["ytd"] = trans[ 0]["total_merchandise"] or 0

	#last year current date
	filters_date = datetime.strptime(filters.date, '%Y-%m-%d')
	one_year_ago_date = filters_date- timedelta(days=365) 
	difference_one_year = (filters_date - one_year_ago_date).days
	difference_one_year_timedelta = timedelta(days=difference_one_year)
	formatted_date = filters_date - difference_one_year_timedelta
	formatted_date_str = formatted_date.strftime('%Y-%m-%d')
	filters.start_date = formatted_date_str
	data = frappe.db.sql(sql,filters,as_dict=1) 
	trans = frappe.db.sql(tran,filters,as_dict=1)
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
	datas["room_charge"]["last_year_current"] = trans[0]["total_room_charge"] or 0 
	datas["housekeeping"]["last_year_current"] = trans[0]["total_housekeeping"] or 0 
	datas["spa_massage"]["last_year_current"] = trans[0]["total_spa_massage"] or 0 
	datas["tour_ticket"]["last_year_current"] = trans[ 0]["total_tour_and_ticket"] or 0 
	datas["service_charge"]["last_year_current"] = trans[ 0]["total_service_charge"] or 0 
	datas["tip"]["last_year_current"] = trans[ 0]["total_tip"] or 0 
	datas["non_revenue"]["last_year_current"] = trans[ 0]["total_non_revenue"] or 0 
	datas["food_and_beverage"]["last_year_current"] = trans[ 0]["total_fb"] or 0 
	datas["other_charge"]["last_year_current"] = trans[ 0]["total_other_charge"] or 0 
	datas["merchindise"]["last_year_current"] = trans[ 0]["total_merchandise"] or 0 
	
	#last year mtd
	current_month = filters_date.month
	current_day = filters_date.day
	last_year = filters_date.year - 1
	date_last_year = datetime(last_year, current_month, current_day)
	filters.start_date = date_last_year.strftime('%Y-%m-%d')
	data = frappe.db.sql(sql,filters,as_dict=1)
	trans = frappe.db.sql(tran,filters,as_dict=1)
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
	datas["room_charge"]["last_year_mtd"] = trans[0]["total_room_charge"] or 0 
	datas["housekeeping"]["last_year_mtd"] = trans[0]["total_housekeeping"] or 0 
	datas["spa_massage"]["last_year_mtd"] = trans[0]["total_spa_massage"] or 0 
	datas["tour_ticket"]["last_year_mtd"] = trans[ 0]["total_tour_and_ticket"] or 0 
	datas["service_charge"]["last_year_mtd"] = trans[ 0]["total_service_charge"] or 0 
	datas["tip"]["last_year_mtd"] = trans[ 0]["total_tip"] or 0 
	datas["non_revenue"]["last_year_mtd"] = trans[ 0]["total_non_revenue"] or 0 
	datas["food_and_beverage"]["last_year_mtd"] = trans[ 0]["total_fb"] or 0 
	datas["other_charge"]["last_year_mtd"] = trans[ 0]["total_other_charge"] or 0 
	datas["merchindise"]["last_year_mtd"] = trans[ 0]["total_merchandise"] or 0 

	# last year ytd
	last_year_start_date = filters_date.replace(year=filters_date.year - 1, month=1, day=1)
	exception_message = last_year_start_date.strftime('%Y-%m-%d')
	filters.start_date = exception_message
	data = frappe.db.sql(sql,filters,as_dict=1) 
	trans = frappe.db.sql(tran,filters,as_dict=1)
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
	datas["room_charge"]["last_year_ytd"] = trans[0]["total_room_charge"] or 0 
	datas["housekeeping"]["last_year_ytd"] = trans[0]["total_housekeeping"] or 0 
	datas["spa_massage"]["last_year_ytd"] = trans[0]["total_spa_massage"] or 0 
	datas["tour_ticket"]["last_year_ytd"] = trans[ 0]["total_tour_and_ticket"] or 0 
	datas["service_charge"]["last_year_ytd"] = trans[ 0]["total_service_charge"] or 0 
	datas["tip"]["last_year_ytd"] = trans[ 0]["total_tip"] or 0 
	datas["non_revenue"]["last_year_ytd"] = trans[ 0]["total_non_revenue"] or 0 
	datas["food_and_beverage"]["last_year_ytd"] = trans[ 0]["total_fb"] or 0 
	datas["other_charge"]["last_year_ytd"] = trans[ 0]["total_other_charge"] or 0 
	datas["merchindise"]["last_year_ytd"] = trans[ 0]["total_merchandise"] or 0 

	datas["room_occupy"]["change_percentage"] = ((datas["room_occupy"]["ytd"]-datas["room_occupy"]["last_year_ytd"])/(1 if datas["room_occupy"]["last_year_ytd"]==0 else datas["room_occupy"]["last_year_ytd"] or 0))*100
	datas["room_block"]["change_percentage"] = ((datas["room_block"]["ytd"]-datas["room_block"]["last_year_ytd"])/(1 if datas["room_block"]["last_year_ytd"]==0 else datas["room_block"]["last_year_ytd"] or 0))*100
	datas["complimentary"]["change_percentage"] = ((datas["complimentary"]["ytd"]-datas["complimentary"]["last_year_ytd"])/(1 if datas["complimentary"]["last_year_ytd"]==0 else datas["complimentary"]["last_year_ytd"] or 0))*100
	datas["house_use"]["change_percentage"] = ((datas["house_use"]["ytd"]-datas["house_use"]["last_year_ytd"])/(1 if datas["house_use"]["last_year_ytd"]==0 else datas["house_use"]["last_year_ytd"] or 0))*100
	datas["in_house_adult"]["change_percentage"] = ((datas["in_house_adult"]["ytd"]-datas["in_house_adult"]["last_year_ytd"]) /(1 if datas["in_house_adult"]["last_year_ytd"]==0 else datas["in_house_adult"]["last_year_ytd"] or 0))*100
	datas["arrival_adult"]["change_percentage"] = ((datas["arrival_adult"]["ytd"]-datas["arrival_adult"]["last_year_ytd"])/(1 if datas["arrival_adult"]["last_year_ytd"]==0 else datas["arrival_adult"]["last_year_ytd"] or 0))*100
	datas["departure_adult"]["change_percentage"] = ((datas["departure_adult"]["ytd"]- datas["departure_adult"]["last_year_ytd"]) /(1 if  datas["departure_adult"]["last_year_ytd"]==0 else datas["departure_adult"]["last_year_ytd"] or 0))*100
	datas["in_house_child"]["change_percentage"] = ((datas["in_house_child"]["ytd"]-datas["in_house_child"]["last_year_ytd"])/(1 if datas["in_house_child"]["last_year_ytd"]==0 else datas["in_house_child"]["last_year_ytd"] or 0))*100
	datas["arrival_child"]["change_percentage"] = ((datas["arrival_child"]["ytd"]-datas["arrival_child"]["last_year_ytd"])/(1 if datas["arrival_child"]["last_year_ytd"]==0 else datas["arrival_child"]["last_year_ytd"] or 0))*100
	datas["departure_child"]["change_percentage"] = ((datas["departure_child"]["ytd"]-datas["departure_child"]["last_year_ytd"])/(1 if datas["departure_child"]["last_year_ytd"]==0 else datas["departure_child"]["last_year_ytd"] or 0))*100
	datas["walk_in_adult"]["change_percentage"] = ((datas["walk_in_adult"]["ytd"]-datas["walk_in_adult"]["last_year_ytd"])/(1 if datas["walk_in_adult"]["last_year_ytd"]==0 else datas["walk_in_adult"]["last_year_ytd"] or 0))*100
	datas["walk_in_child"]["change_percentage"] = ((datas["walk_in_child"]["ytd"]-datas["walk_in_child"]["last_year_ytd"]) /(1 if  datas["walk_in_child"]["last_year_ytd"]==0 else datas["walk_in_child"]["last_year_ytd"] or 0))*100
	datas["walk_in_room_night"]["change_percentage"] = ((datas["walk_in_room_night"]["ytd"]-datas["walk_in_room_night"]["last_year_ytd"]) /(1 if  datas["walk_in_room_night"]["last_year_ytd"]==0 else datas["walk_in_room_night"]["last_year_ytd"] or 0))*100
	datas["arrival_room_night"]["change_percentage"] = ((datas["arrival_room_night"]["ytd"]-datas["arrival_room_night"]["last_year_ytd"]) /(1 if datas["arrival_room_night"]["last_year_ytd"]==0 else datas["arrival_room_night"]["last_year_ytd"] or 0))*100
	datas["departure_room_night"]["change_percentage"] = ((datas["departure_room_night"]["ytd"]-datas["departure_room_night"]["last_year_ytd"]) /(1 if datas["departure_room_night"]["last_year_ytd"]==0 else datas["departure_room_night"]["last_year_ytd"] or 0))*100
	datas["no_show_room"]["change_percentage"] = ((datas["no_show_room"]["ytd"] -datas["no_show_room"]["last_year_ytd"])/(1 if datas["no_show_room"]["last_year_ytd"]==0 else datas["no_show_room"]["last_year_ytd"] or 0))*100
	datas["no_show_adult"]["change_percentage"] = ((datas["no_show_adult"]["ytd"]-datas["no_show_adult"]["last_year_ytd"])/(1 if datas["no_show_adult"]["last_year_ytd"]==0 else datas["no_show_adult"]["last_year_ytd"] or 0))*100
	datas["no_show_child"]["change_percentage"] = ((datas["no_show_child"]["ytd"]-datas["no_show_child"]["last_year_ytd"]) /(1 if datas["no_show_child"]["last_year_ytd"]==0 else datas["no_show_child"]["last_year_ytd"] or 0))*100
	datas["early_checked_out_adult"]["change_percentage"] = ((datas["early_checked_out_adult"]["ytd"]-datas["early_checked_out_adult"]["last_year_ytd"])/(1 if datas["early_checked_out_adult"]["last_year_ytd"]==0 else datas["early_checked_out_adult"]["last_year_ytd"] or 0))*100
	datas["early_checked_out_child"]["change_percentage"] = ((datas["early_checked_out_child"]["ytd"]-datas["early_checked_out_child"]["last_year_ytd"])/(1 if datas["early_checked_out_child"]["last_year_ytd"]==0 else datas["early_checked_out_child"]["last_year_ytd"] or 0) )*100
	datas["early_checked_out"]["change_percentage"] = ((datas["early_checked_out"]["ytd"]-datas["early_checked_out"]["last_year_ytd"])/(1 if datas["early_checked_out"]["last_year_ytd"]==0 else datas["early_checked_out"]["last_year_ytd"] or 0))*100
	datas["fit_room"]["change_percentage"] = ((datas["fit_room"]["ytd"]-datas["fit_room"]["last_year_ytd"])/(1 if datas["fit_room"]["last_year_ytd"]==0 else datas["fit_room"]["last_year_ytd"] or 0))*100
	datas["git_room"]["change_percentage"] = ((datas["git_room"]["ytd"]-datas["git_room"]["last_year_ytd"])/(1 if datas["git_room"]["last_year_ytd"]==0 else datas["git_room"]["last_year_ytd"] or 0))*100
	datas["fit_adult"]["change_percentage"] = ((datas["fit_adult"]["ytd"]-datas["fit_adult"]["last_year_ytd"])/(1 if datas["fit_adult"]["last_year_ytd"]==0 else datas["fit_adult"]["last_year_ytd"] or 0))*100
	datas["fit_child"]["change_percentage"] = ((datas["fit_child"]["ytd"]-datas["fit_child"]["last_year_ytd"])/(1 if datas["fit_child"]["last_year_ytd"]==0 else datas["fit_child"]["last_year_ytd"] or 0))*100
	datas["git_adult"]["change_percentage"] = ((datas["git_adult"]["ytd"]-datas["git_adult"]["last_year_ytd"])/(1 if datas["git_adult"]["last_year_ytd"]==0 else datas["git_adult"]["last_year_ytd"] or 0))*100
	datas["git_child"]["change_percentage"] = ((datas["git_child"]["ytd"]-datas["git_child"]["last_year_ytd"])/(1 if datas["git_child"]["last_year_ytd"]==0 else datas["git_child"]["last_year_ytd"] or 0))*100
	datas["vip_guest"]["change_percentage"] = ((datas["vip_guest"]["ytd"]-datas["vip_guest"]["last_year_ytd"])/(1 if datas["vip_guest"]["last_year_ytd"]==0 else datas["vip_guest"]["last_year_ytd"] or 0))*100
	datas["cancel_room"]["change_percentage"] = ((datas["cancel_room"]["ytd"]-datas["cancel_room"]["last_year_ytd"])/(1 if datas["cancel_room"]["last_year_ytd"]==0 else datas["cancel_room"]["last_year_ytd"] or 0))*100
	datas["cancel_adult"]["change_percentage"] = ((datas["cancel_adult"]["ytd"]-datas["cancel_adult"]["last_year_ytd"])/(1 if datas["cancel_adult"]["last_year_ytd"]==0 else datas["cancel_adult"]["last_year_ytd"] or 0))*100
	datas["cancel_child"]["change_percentage"] = ((datas["cancel_child"]["ytd"]-datas["cancel_child"]["last_year_ytd"])/(1 if datas["cancel_child"]["last_year_ytd"]==0 else datas["cancel_child"]["last_year_ytd"] or 0))*100
	datas["room_charge"]["change_percentage"] = ((datas["room_charge"]["ytd"]-datas["room_charge"]["last_year_ytd"])/(1 if datas["room_charge"]["last_year_ytd"]==0 else datas["room_charge"]["last_year_ytd"] or 0))*100
	datas["housekeeping"]["change_percentage"] = ((datas["housekeeping"]["ytd"]-datas["housekeeping"]["last_year_ytd"])/(1 if datas["housekeeping"]["last_year_ytd"]==0 else datas["housekeeping"]["last_year_ytd"] or 0))*100
	datas["spa_massage"]["change_percentage"] = ((datas["spa_massage"]["ytd"]-datas["spa_massage"]["last_year_ytd"])/(1 if datas["spa_massage"]["last_year_ytd"]==0 else datas["spa_massage"]["last_year_ytd"] or 0))*100
	datas["tour_ticket"]["change_percentage"] = ((datas["tour_ticket"]["ytd"]-datas["tour_ticket"]["last_year_ytd"])/(1 if datas["tour_ticket"]["last_year_ytd"]==0 else datas["tour_ticket"]["last_year_ytd"] or 0))*100
	datas["service_charge"]["change_percentage"] = ((datas["service_charge"]["ytd"]-datas["service_charge"]["last_year_ytd"])/(1 if datas["service_charge"]["last_year_ytd"]==0 else datas["service_charge"]["last_year_ytd"] or 0))*100
	datas["tip"]["change_percentage"] = ((datas["tip"]["ytd"]-datas["tip"]["last_year_ytd"]) /(1 if datas["tip"]["last_year_ytd"]==0 else datas["tip"]["last_year_ytd"] or 0))*100
	datas["non_revenue"]["change_percentage"] = ((datas["non_revenue"]["ytd"]-datas["non_revenue"]["last_year_ytd"])/(1 if datas["non_revenue"]["last_year_ytd"]==0 else datas["non_revenue"]["last_year_ytd"] or 0))*100
	datas["food_and_beverage"]["change_percentage"] = ((datas["food_and_beverage"]["ytd"]-datas["food_and_beverage"]["last_year_ytd"])/(1 if datas["food_and_beverage"]["last_year_ytd"]==0 else datas["food_and_beverage"]["last_year_ytd"] or 0))*100
	datas["other_charge"]["change_percentage"] = ((datas["other_charge"]["ytd"]-datas["other_charge"]["last_year_ytd"])/(1 if datas["other_charge"]["last_year_ytd"]==0 else datas["other_charge"]["last_year_ytd"] or 0))*100
	datas["merchindise"]["change_percentage"] = ((datas["merchindise"]["ytd"]-datas["merchindise"]["last_year_ytd"])/(1 if datas["merchindise"]["last_year_ytd"]==0 else datas["other_charge"]["last_year_ytd"] or 0))*100

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

	filters_date = datetime.strptime(filters.date, '%Y-%m-%d')
	one_year_ago_date = filters_date- timedelta(days=365) 
	difference_one_year = (filters_date - one_year_ago_date).days
	difference_one_year_timedelta = timedelta(days=difference_one_year)
	formatted_date = filters_date - difference_one_year_timedelta
	formatted_date_str = formatted_date.strftime('%Y-%m-%d')
	filters.last_current_start_date = formatted_date_str

	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(last_current_start_date)s and %(date)s"

	last_year_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0

	current_month = filters_date.month
	current_day = filters_date.day
	last_year = filters_date.year - 1
	date_last_year = datetime(last_year, current_month, current_day)
	filters.last_year_mtd = date_last_year.strftime('%Y-%m-%d')
	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(last_year_mtd)s and %(date)s"

	last_year_mtd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0

	last_year_start_date = filters_date.replace(year=filters_date.year - 1, month=1, day=1)
	exception_message = last_year_start_date.strftime('%Y-%m-%d')
	filters.last_year_ytd = exception_message
	sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(last_year_ytd)s and %(date)s"

	last_year_ytd_total_room= frappe.db.sql(sql,filters,as_dict=1)[0]["total_room"] or 0
	return {
			"title": "Total Rooms in Property",
			"current":total_room,
			"mtd": mtd_total_room,
			"ytd":ytd_total_room,
			"last_year_current":last_year_total_room,
			"last_year_mtd":last_year_mtd_total_room,
			"last_year_ytd":last_year_ytd_total_room,
			"change_percentage":((ytd_total_room/last_year_ytd_total_room)-1)*100,
	}