

import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import uuid

def execute(filters=None):
	data = get_pickup_data(filters)
	drop = get_drop_off_data(filters)
	summary = get_summary(filters,data,drop)
	report_data = get_report_data(filters,data,drop)
	return get_columns(filters),report_data,None,None, summary

def validate(filters):
	datediff = date_diff(filters.end_date, filters.start_date)
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if datediff > 30:
			frappe.throw("Your Max date for viewing transaction is only One Month.".format(filters.start_date, filters.end_date))

def get_summary(filters,data,dropoff):
	get_count = {d['reservation'] for d in data if d["require_pickup"]==1 or d["require_drop_off"]==1}
	drop_off_adult = sum([d["adult"] for d in dropoff if d["require_drop_off"]==1])
	pickup_adult = sum([d["adult"] for d in data if d["require_pickup"]==1])
	drop_off_child = sum([d["child"] for d in dropoff if d["require_drop_off"]==1])
	pickup_child = sum([d["child"] for d in data if d["require_pickup"]==1])
	if filters.show_summary:
		return [
			{ "label":"Total Reservation","value":len(get_count),"indicator":"red"},
			{ "label":"Total Room Nights","value":sum([d["room_nights"] for d in data if d["require_pickup"]==1 or d["require_drop_off"]==1]),"indicator":"blue"},
			{ "label":"Total Pax(A/C)","value":"{}/{}".format((drop_off_adult + pickup_adult),(drop_off_child + pickup_child))},
		]

def get_columns(filters):
	columns =   [
		{"fieldname":"name", "label":"Stay #",'align':'left', "fieldtype":"Link","options":"Reservation Stay","width":190,"show_in_report":1,"url":"/frontdesk/stay-detail","post_message_action": "view_reservation_stay_detail"},
		{"fieldname":"reference_number",'align':'left', "label":"Ref #","width":95,"show_in_report":1},
		{'fieldname':'reservation_type','align':'center','label':'Type',"width":60 ,"show_in_report":1},
		{'fieldname':'arrival_date','align':'center','label':'Arrival Date',"width":120 ,"show_in_report":1,"fieldtype":"Date"},
		{'fieldname':'departure_date','align':'center','label':'Departure Date',"width":120 ,"show_in_report":1,"fieldtype":"Date"},
		{'fieldname':'room_type_alias','label':'Room Type',"width":50,"show_in_report":1},
		{'fieldname':'rooms','label':'Room','align':'left',"width":60,"show_in_report":1},
		{"fieldname":"time", 'align':'left',"label":"Time", "fieldtype":"Time","width":95,"show_in_report":1},
		{'fieldname':'flight_number','label':'Flight',"width":90,"show_in_report":1,'align':'center'},
		{"fieldname":"guest", "label":"Guest", "fieldtype":"Link","options":"Customer","width":130,"show_in_report":0,"post_message_action": "view_guest_detail","url":"/frontdesk/guest-detail"},
		{'fieldname': 'total_pax', 'label': 'Pax(A/C)','align':'center',"width":50,"show_in_report":1},
		{'fieldname':'business_source','label':'Source','align':'left',"width":100,"show_in_report":1},
		{'fieldname':'mode','label':'Mode',"width":60,"show_in_report":1,'align':'center'},
		{'fieldname':'station','label':'Station',"width":100,"show_in_report":1,'align':'left'},
		{'fieldname':'driver','label':'Driver',"width":100,"show_in_report":1,'align':'left'},
		{'fieldname':'note','label':'Note', 'align':'right',"show_in_report":1,"width":90},
	]
	return columns

def get_pickup_filters(filters):
	sql = """ and property=%(property)s and is_active_reservation=1 and
	arrival_date between %(start_date)s and %(end_date)s
				
	  		 """

	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.get("room_types"):
		sql =  """{} and  name in (
			select distinct reservation_stay from `tabReservation Room Rate` rrr 
			{}	
		) """.format(sql,get_room_rate_filters(filters))
	return sql
def get_drop_off_filters(filters):
	sql = """ and property=%(property)s and is_active_reservation=1 and
	departure_date between %(start_date)s and %(end_date)s
				
	  		 """

	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.get("room_types"):
		sql =  """{} and  name in (
			select distinct reservation_stay from `tabReservation Room Rate` rrr 
			{}	
		) """.format(sql,get_room_rate_filters(filters))
	return sql

def get_room_rate_filters(filters):
	sql = "where property=%(property)s "
	sql =  " {} and date between %(start_date)s and %(end_date)s ".format(sql) 

	if filters.business_source:
		sql = "{} and business_source =  %(business_source)s".format(sql)
	
	if filters.get("room_types"):
		sql = "{} and room_type_id  in %(room_types)s".format(sql)
 
	return sql

def get_pickup_data(filters):
	sql="""
			select 
				name,
				reservation_date,
				arrival_date,
				departure_date,
				rooms,
				modified,
				reference_number,
				creation,
				reservation_type,
				reservation,
				room_type_alias,
				business_source,
				adult,
				child,
				concat(adult,'/',child) as total_pax,
				pax,
				room_nights,
				guest,
				guest_name,
				is_active_reservation,
				reservation_status,
				require_pickup,
				require_drop_off,
				if(require_pickup,pickup_time,drop_off_time) as time,
				arrival_mode,
				arrival_flight_number,
				pickup_location,
				pickup_driver_name,
				pickup_driver_phone_number,
				pickup_note,
				if(require_drop_off,departure_mode,arrival_mode) as mode,
				if(require_drop_off,drop_off_location,pickup_location) as station,
				if(require_drop_off,departure_flight_number,arrival_flight_number) as flight_number,
				if(require_drop_off,drop_off_driver_name,pickup_driver_name) as driver,
				if(require_drop_off,drop_off_note,pickup_note) as note,
				departure_mode,
				departure_flight_number,
				drop_off_location,
				drop_off_driver_name,
				drop_off_driver_phone_number,
				drop_off_note
			from `tabReservation Stay` rst
			where
				1=1  
				{}
			
		""".format(get_pickup_filters(filters))

	data =   frappe.db.sql(sql,filters,as_dict=1)

	
	return data
def get_drop_off_data(filters):
	sql="""
			select 
				name,
				reservation_date,
				arrival_date,
				departure_date,
				rooms,
				modified,
				reference_number,
				creation,
				reservation_type,
				reservation,
				room_type_alias,
				business_source,
				adult,
				child,
				concat(adult,'/',child) as total_pax,
				pax,
				room_nights,
				guest,
				guest_name,
				is_active_reservation,
				reservation_status,
				require_pickup,
				require_drop_off,
				if(require_pickup,pickup_time,drop_off_time) as time,
				arrival_mode,
				arrival_flight_number,
				pickup_location,
				pickup_driver_name,
				pickup_driver_phone_number,
				pickup_note,
				if(require_drop_off,departure_mode,arrival_mode) as mode,
				if(require_drop_off,drop_off_location,pickup_location) as station,
				if(require_drop_off,departure_flight_number,arrival_flight_number) as flight_number,
				if(require_drop_off,drop_off_driver_name,pickup_driver_name) as driver,
				if(require_drop_off,drop_off_note,pickup_note) as note,
				departure_mode,
				departure_flight_number,
				drop_off_location,
				drop_off_driver_name,
				drop_off_driver_phone_number,
				drop_off_note
			from `tabReservation Stay` rst
			where
				1=1  
				{}
			
		""".format(get_drop_off_filters(filters))

	dropoff =   frappe.db.sql(sql,filters,as_dict=1)

	
	return dropoff

def get_report_data(filters,data,dropoff):
	report_data = []
	
	pickup = sorted(set([d["require_pickup"] for d in data if d['require_pickup']==1]))
	if pickup:	
		report_data.append({
				"indent":0,
				"name": "Pick-up Guest",
				"is_group":1,

			})
		if filters.show_in_group_by:
			group_column = get_group_by_column(filters)
		
			group_data = sorted(set([d[group_column["data_field"]] for d  in data if d['require_pickup']==1]))
			for g in group_data:
				d = g
				if group_column["fieldtype"]=="Date":
					d  = frappe.format(g,{"fieldtype":"Date"})
				id =  str(uuid.uuid4())
				report_data.append({
				"indent":1,
				"name": d,
				"is_group":1,
				"id":id
				})
				report_data = report_data +  [d.update({"indent":2,"parent":id}) or d for d in data if d[group_column["data_field"]]==g and d['require_pickup']==1]
			
				report_data.append({
				"indent":1,
				"name": "Total",
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d[group_column["data_field"]]==g and d['require_pickup']==1]),sum([d["child"] for d in data if d[group_column["data_field"]]==g and d['require_pickup']==1])),
				"is_total_row":1,
				"is_group":0,
				"parent":id
				})
		else:
			report_data = report_data +  [d.update({"indent":2}) or d for d in data if d['require_pickup']==1]
			report_data.append({
				"indent":1,
				"name": "Total",
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d['require_pickup']==1]),sum([d["child"] for d in data if d['require_pickup']==1])),
				"is_total_row":1,
				"is_group":1,
			})

	drop_off = sorted(set([d["require_drop_off"] for d in dropoff if d['require_drop_off']==1]))
	if drop_off:	
		report_data.append({
				"indent":0,
				"name": "Drop-off Guest",
				"is_group":1,

			})	
		if filters.show_in_group_by:
			group_column = get_group_by_column(filters)
		
			group_data = sorted(set([d[group_column["data_field"]] for d  in dropoff if d['require_drop_off']==1]))
			for g in group_data:
				d = g
				if group_column["fieldtype"]=="Date":
					d  = frappe.format(g,{"fieldtype":"Date"})
				id =  str(uuid.uuid4())
				report_data.append({
				"indent":1,
				"name": d,
				"is_group":1,
				"id":id
				})
				report_data = report_data +  [d.update({"indent":2,"parent":id}) or d for d in dropoff if d[group_column["data_field"]]==g and d['require_drop_off']==1]
			
				report_data.append({
				"indent":1,
				"name": "Total",
				"total_pax":"{}/{}".format(sum([d["adult"] for d in dropoff if d[group_column["data_field"]]==g and d['require_drop_off']==1]),sum([d["child"] for d in dropoff if d[group_column["data_field"]]==g and d['require_drop_off']==1])),
				"is_total_row":1,
				"is_group":0,
				"parent":id
				})
		else:
			report_data = report_data +  [d.update({"indent":2}) or d for d in dropoff if d['require_drop_off']==1]
			report_data.append({
				"indent":1,
				"name": "Total",
				"total_pax":"{}/{}".format(sum([d["adult"] for d in dropoff if d['require_drop_off']==1]),sum([d["child"] for d in dropoff if d['require_drop_off']==1])),
				"is_total_row":1,
				"is_group":1,
			})
	
	drop_off_adult = sum([d["adult"] for d in dropoff if d["require_drop_off"]==1])
	pickup_adult = sum([d["adult"] for d in data if d["require_pickup"]==1])
	drop_off_child = sum([d["child"] for d in dropoff if d["require_drop_off"]==1])
	pickup_child = sum([d["child"] for d in data if d["require_pickup"]==1])
	
	report_data.append({
				"indent":0,
				"name": "",
				"is_separator":1})
	report_data.append({
				"indent":0,
				"name": "Grand Total",
				"total_pax":"{}/{}".format((drop_off_adult + pickup_adult),(drop_off_child + pickup_child)),
				"is_total_row":1,
				"is_group":1,
				"is_grand_total":1
			})
	return report_data
	
def get_group_by_column(filters):
 
	return  [d for d in group_by_columns() if d["label"] == filters.show_in_group_by][0]

def group_by_columns():
	
	return [
		{"data_field":"arrival_date", "label":"Arrival Date","fieldtype":"Date"},
		{"data_field":"departure_date", "label":"Departure Date" ,"fieldtype":"Date" },
		{"data_field":"reservation", "label":"Reservation" ,"fieldtype":"Data" },
		{"data_field":"business_source", "label":"Business Source" ,"fieldtype":"Data" },
		{"data_field":"room_types", "label":"Room Type" ,"fieldtype":"Data" },
	]