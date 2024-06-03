# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import date_diff,today ,add_months, add_days,getdate,add_years
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime, timedelta
import re
import datetime
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
		{"fieldname": "title", "label": "Title", "width":300, "align":"left"},
		{"fieldname": "current", "label": "Current", "width":150, "align":"right"},
		{"fieldname": "mtd", "label": "MTD", "width":100, "fieldtype":"Data", "align":"right"},
		{"fieldname": "ytd", "label": "YTD", "width":100, "align":"right"},
		{"fieldname": "last_year_current", "label": "Current({})".format(getdate(filters.date).year - 1), "width":150, "align":"right"},
		{"fieldname": "last_year_mtd", "label": "MTD({})".format(getdate(filters.date).year - 1), "width":150, "fieldtype":"Data", "align":"right"},
		{"fieldname": "last_year_ytd", "label": "YTD({})".format(getdate(filters.date).year - 1), "width":150, "align":"right"},
		{"fieldname": "change_percentage", "label": "% Change", "width":150, "align":"right","fieldtype":"Percent"},
	]


def get_report_data(filters):
	
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Mafiya Manager Flash Report"} )
	report_data =  []
	rooms_available_record = get_current_room_in_property(filters)
	report_data.append(rooms_available_record[0]['total_room'])
	taxable_room_sale = get_taxable_room_sale(filters)

	report_data.append(taxable_room_sale[0]['total_posted'])
	# report_data.append(taxable_room_sale[0]['taxable_room_posted'])
	report_data.append(taxable_room_sale[0]['room_revenue_posted'])
	report_data.append(taxable_room_sale[0]['other_room_revenue_posted'])
	report_data.append(taxable_room_sale[0]['total_room_posted'])
	report_data.append(taxable_room_sale[0]['adjustment_amount'])
	report_data.append(taxable_room_sale[0]['total_room_revenue'])
	report_data.append(taxable_room_sale[0]['tour_activitie'])
	report_data.append(taxable_room_sale[0]['other_revenue'])
	report_data.append(taxable_room_sale[0]['transportation_revenue'])
	report_data.append(taxable_room_sale[0]['income'])
	report_data.append(taxable_room_sale[0]['net_income'])
	report_data.append(taxable_room_sale[0]['deposit_bank'])
	report_data.append(taxable_room_sale[0]['total_rack_room'])
	report_data.append(taxable_room_sale[0]['total_other_room'])
	report_data.append(taxable_room_sale[0]['other_charge_discount'])
	report_data.append(taxable_room_sale[0]['room_tax'])



	occupy_data = get_data_from_occupy_record(filters)
	report_data.append(occupy_data[0]['room_occupy'] or 0)
	report_data.append(occupy_data[0]["complimentary"] or 0)
	report_data.append(occupy_data[0]["house_use"] or 0)
	report_data.append(occupy_data[0]["room_block"] or 0)
	report_data.append(occupy_data[0]['total_adult_room_night'])
	report_data.append(occupy_data[0]['total_child_room_night'])
	report_data.append(occupy_data[0]['total_walk_in_room_night'])
	report_data.append(occupy_data[0]['total_arrival_adult'])
	report_data.append(occupy_data[0]['total_arrival_child'])
	report_data.append(occupy_data[0]['total_git_room_night'])
	report_data.append(occupy_data[0]['total_fit_room_night'])

	for_tomorrow = get_forecasting(filters)
	report_data.append(for_tomorrow[0]['total_departure'])
	report_data.append(for_tomorrow[0]['total_arrival'])
	report_data.append(for_tomorrow[0]['total_adult_child'])
	report_data.append(for_tomorrow[0]['total_exp_inhouse'])
	report_data.append(for_tomorrow[0]['total_block'])
	report_data.append(for_tomorrow[0]['exp_pickup_drop_off'])
	report_data.append(for_tomorrow[0]['exp_stay_over'])
	report_data.append(for_tomorrow[0]['total_occupy'])

	weekday_and_weekend_sales = get_weekday_and_weekend_sale(filters)
	report_data.append(weekday_and_weekend_sales[0]['weekday_sales'])
	report_data.append(weekday_and_weekend_sales[0]['weekend_sales'])
	report_data+= get_ledger_balance(filters)
	report_data+= get_revenue(filters)  
	return_report_data = []
	
			
	#calculate room occupancy
	occpancy = {"title":"Occupancy"}
	revpar = {"title":"RevPAR"}
	adr = {"title":"ADR"}
	vacant_room_night = {"title":"Vacant Room Nights"}
	exp_vacant_room_night = {"title":"Total Expected Vacant Rooms"}
	total_sale_center = {"title":"Total Sales Center"}
	total_exp_inhouse = {"title":"Total Expected Inhouse"}
	total_exp_stay_over = {"title":"Total Expected Stay Over"}
	avg_daily_gl = {"title":"Avg Daily GL Balance"}
	avg_daily_cl = {"title":"Avg Daily CL Balance"}
	avg_daily_al = {"title":"Avg Daily AL Balance"}
	weekday_percent = {"title":"Weekday %"}
	weekend_percent = {"title":"Weekend %"}
	total_payment = {"title":"Total Payment"}
	total_room_available = {"title":"Total Rooms To Sell"}
	fb_revenue = {"title":"Food & Beverage"}
	
	exp_inhouse_occ = (for_tomorrow[0]['total_exp_inhouse']['current'] / rooms_available_record[0]['total_room']['current']) * 100
	inhouse_occ = format(exp_inhouse_occ,'.2f')
	total_exp_inhouse['current'] = f"{int(for_tomorrow[0]['total_exp_inhouse']['current'])} ({inhouse_occ}% occ)"
	report_data.append(total_exp_inhouse or 0)

	exp_vacant_room_night['current'] =  int(rooms_available_record[0]['total_room']['current']) - int(for_tomorrow[0]['total_occupy']['current']) - int(for_tomorrow[0]['total_block']['current'])
	
	exp_stayover_occ = (for_tomorrow[0]['exp_stay_over']['current'] / rooms_available_record[0]['total_room']['current']) * 100
	stayover_occ = format(exp_stayover_occ,'.2f')
	total_exp_stay_over['current'] = f"{int(for_tomorrow[0]['exp_stay_over']['current'])} ({stayover_occ}% occ)"
	report_data.append(total_exp_stay_over or 0)
	calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
	calculate_adr_include_all_room_occupied = frappe.db.get_single_value("eDoor Setting", "calculate_adr_include_all_room_occupied")
	
	for f in ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]:
		total_room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Total Rooms in Property']) or 0
		room_occupy = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Rooms Sold']) or 0
		
		room_block = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Out of Order Rooms']) or 0
		house_use_room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'House Use Rooms']) or 0
		complimentary_room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Complimentary Rooms']) or 0
		room_charge = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Room']) or 0
		room = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Room']) or 0
		transportation = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Transportation']) or 0
		tour = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Tour activities']) or 0
		other = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Other']) or 0
		cl_balance = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'City Ledger']) or 0
		gl_balance = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Reservation Folio']) or 0
		al_balance = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Total Ledger Balance']) or 0
		weekday_sale = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Weekday Sales']) or 0
		weekend_sale = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Weekend Sales']) or 0
		cash = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Cash Payment Received']) or 0
		bank = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Bank Payment Received']) or 0
		deposit_cash = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Deposit Cash']) or 0
		deposit_bank = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Deposit Bank']) or 0
		food = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Food']) or 0
		alcohol = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Alcohol']) or 0
		nonalcohol = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Non-Alcohol']) or 0
		tax = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'F&B Tax']) or 0
		discount = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'F&B Discount']) or 0
		fb_other = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'F&B Other']) or 0
		fb_breakfast = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'F&B Breakfast Revenue']) or 0
		room_disc = sum([d.get(f, 0) for d in report_data if d.get('title', 'No Title') == 'Room Discount']) or 0
		start_date_str = filters.get(f)["start_date"]
		end_date_str = filters.get(f)["end_date"]
	
		vacant_room_night[f] =  total_room - room_occupy - room_block
		total_room_available[f] =  total_room - room_block
		fb_revenue[f] = food + alcohol + nonalcohol + tax + discount + fb_other +fb_breakfast
		total_sale_center[f] = room + transportation + tour + other
		total_payment[f] = cash + bank + deposit_cash + deposit_bank
		if calculate_adr_include_all_room_occupied==1:
			adr[f] =  (room_charge - room_disc) / (1 if room_occupy == 0 else room_occupy)
			
		else:
			adr[f] = (room_charge - room_disc) / (1 if (room_occupy - (complimentary_room + house_use_room)) == 0 else (room_occupy - (complimentary_room + house_use_room)))
		if calculate_room_occupancy_include_room_block==0:
			total_room = total_room - room_block
		occpancy[f] =  room_occupy / (1 if total_room == 0 else total_room)
		revpar[f] = (room_charge )/(1 if total_room == 0 else total_room)
		avg_daily_gl[f] = gl_balance/(1 if date_diff(end_date_str,start_date_str)==0 else date_diff(end_date_str,start_date_str))
		avg_daily_cl[f] = cl_balance/(1 if date_diff(end_date_str,start_date_str)==0 else date_diff(end_date_str,start_date_str))
		avg_daily_al[f] = al_balance/(1 if date_diff(end_date_str,start_date_str)==0 else date_diff(end_date_str,start_date_str))
		weekday_percent[f] = (weekday_sale/ (1 if (room_charge - room_disc) == 0 else (room_charge - room_disc)))
		weekend_percent[f] = (weekend_sale/ (1 if (room_charge - room_disc) == 0 else (room_charge - room_disc)))
		# frappe.throw(str( adr))
	report_data.append(adr or 0)
	report_data.append(occpancy or 0)
	report_data.append(revpar or 0)
	report_data.append(vacant_room_night or 0)
	report_data.append(total_sale_center or 0)
	report_data.append(avg_daily_gl or 0)
	report_data.append(avg_daily_cl or 0)
	report_data.append(avg_daily_al or 0)
	report_data.append(weekday_percent or 0)
	report_data.append(weekend_percent or 0)
	report_data.append(total_payment or 0)
	report_data.append(exp_vacant_room_night or 0)
	report_data.append(total_room_available or 0)
	report_data.append(fb_revenue or 0)

	today =  datetime.datetime.strptime(filters.date, "%Y-%m-%d").date()
	date = today + datetime.timedelta(days=2)
	num_days = 7
	date_data = [date + datetime.timedelta(days=i) for i in range(num_days)]
	# frappe.throw(str(tuple(date_data)))
	data = []
	data += get_forecasting_for_sevenday({
			"fieldname": "current",
			"property": filters.property, 
			"date_data": tuple(date_data)  
	})
	
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
		else:
			return_report_data.append({
				"title": '',
				"indent":0
			})
		if g == '7 Day Upcoming Forecast':
			for d in date_data:
				current_value = sum([y["total_occupy"] for y in data if y["fieldname"] == 'current' and y['date'] == d and y["total_occupy"] is not None]) or 0
				forecast_day = (current_value / rooms_available_record[0]['total_room']['current']) * 100
				result = format(forecast_day,'.2f')
				return_report_data.append({
					"indent": 1,
					"title": d.strftime("%d-%m-%Y %A"),
					"current":f"{int(current_value)} ({result}% occ)",
					"group":g
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
		data+=get_data_transaction({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
		
				"total_posted":{"title":"Total Posted"},
				
				"room_revenue_posted":{"title":"Room Revenue Posted"},
				"other_room_revenue_posted":{"title":"Other Room Revenue Posted"},
				"total_room_posted":{"title":"Total Room Posted"},
				"adjustment_amount":{"title":"Adjustment"},
				"total_room_revenue":{"title":"Room"},
				"tour_activitie":{"title":"Tour activities"},
				"other_revenue":{"title":"Other"},
				"transportation_revenue":{"title":"Transportation"},
				"income":{"title":"Income"},
				"net_income":{"title":"Net Income"},
				"deposit_bank":{"title":"Deposits"},
				"total_rack_room":{"title":"Total RACK Rooms"},
				"total_other_room":{"title":"Total Other Rooms"},
				"other_charge_discount":{"title":"Other Charge Discount"},
				"room_tax":{"title":"Room Tax"},
			
				
	}
	occupy_data = []
	for f in fields:
		
		row['total_posted'][f] = sum([y["total_posted"] for y in data if y["fieldname"]==f and y["total_posted"] is not None]) or 0
		row['room_revenue_posted'][f] = sum([y["room_revenue_posted"] for y in data if y["fieldname"]==f and y["room_revenue_posted"] is not None]) or 0
		row['other_room_revenue_posted'][f] = sum([y["other_room_revenue_posted"] for y in data if y["fieldname"]==f and y["other_room_revenue_posted"] is not None]) or 0
		row['total_room_posted'][f] = sum([y["total_room_posted"] for y in data if y["fieldname"]==f and y["total_room_posted"] is not None]) or 0
		row['adjustment_amount'][f] = sum([y["adjustment_amount"] for y in data if y["fieldname"]==f and y["adjustment_amount"] is not None]) or 0
		row['total_room_revenue'][f] = sum([y["total_room_revenue"] for y in data if y["fieldname"]==f and y["total_room_revenue"] is not None]) or 0
		row['tour_activitie'][f] = sum([y["tour_activitie"] for y in data if y["fieldname"]==f and y["tour_activitie"] is not None]) or 0
		row['other_revenue'][f] = sum([y["other_revenue"] for y in data if y["fieldname"]==f and y["other_revenue"] is not None]) or 0
		row['transportation_revenue'][f] = sum([y["transportation_revenue"] for y in data if y["fieldname"]==f and y["transportation_revenue"] is not None]) or 0
		row['income'][f] = sum([y["income"] for y in data if y["fieldname"]==f and y["income"] is not None]) or 0
		row['net_income'][f] = sum([y["net_income"] for y in data if y["fieldname"]==f and y["net_income"] is not None]) or 0
		row['deposit_bank'][f] = sum([y["deposit_bank"] for y in data if y["fieldname"]==f and y["deposit_bank"] is not None]) or 0
		row['total_rack_room'][f] = sum([y["total_rack_room"] for y in data if y["fieldname"]==f and y["total_rack_room"] is not None]) or 0
		row['total_other_room'][f] = sum([y["total_other_room"] for y in data if y["fieldname"]==f and y["total_other_room"] is not None]) or 0
		row['other_charge_discount'][f] = sum([y["other_charge_discount"] for y in data if y["fieldname"]==f and y["other_charge_discount"] is not None]) or 0
		row['room_tax'][f] = sum([y["room_tax"] for y in data if y["fieldname"]==f and y["room_tax"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data
def get_weekday_and_weekend_sale(filters):
	data = []
	
	fields = ["current", "mtd", "ytd", "last_year_current", "last_year_mtd", "last_year_ytd"]
	for f in fields:
		start_date_str = filters.get(f)["start_date"]
		end_date_str = filters.get(f)["end_date"]
		start_date = datetime.datetime.strptime(str(start_date_str), "%Y-%m-%d").date()
		end_date = datetime.datetime.strptime(str(end_date_str), "%Y-%m-%d").date()

		total_days = (end_date - start_date).days + 1  # Add 1 to include the end_date

		for i in range(total_days):
			date = start_date + datetime.timedelta(days=i)
			day_type = "weekday" if date.weekday() < 5 else "weekend"
			
			data += get_data_field({"fieldname": f, "property": filters.property, "dates": (date,), "day_type": day_type})

# Initialize row dictionary
	row = {"weekday_sales": {"title": "Weekday Sales"}, "weekend_sales": {"title": "Weekend Sales"}}
	occupy_data=[]

	# Calculate weekend and weekday sales
	for f in fields:
		row['weekend_sales'][f] = sum([y["sale"] for y in data if y["day_type"] == "weekend" and y["fieldname"] == f and y.get("sale") is not None]) or 0
		row['weekday_sales'][f] = sum([y["sale"] for y in data if y["day_type"] == "weekday" and y["fieldname"] == f and y.get("sale") is not None]) or 0
	occupy_data.append(row)

	return occupy_data


def get_data_transaction(filters):
	sql="""select 
			%(fieldname)s as fieldname, 
    		sum(if(flash_report_revenue_group in ('Room Charge','Other Room Revenue','Room Tax'),amount * if(type='Debit',1,-1),0)) as total_posted,
    		sum(if(flash_report_revenue_group in ('Room Tax'),amount * if(type='Debit',1,-1),0)) as room_tax,
    		sum(if(flash_report_revenue_group = 'Room Charge' and discount_amount = 0 and reservation_status='In-house' and parent_reference IS NULL,1,0)) as total_rack_room,
    		sum(if(flash_report_revenue_group = 'Room Charge' and discount_amount > 0 and reservation_status='In-house' and parent_reference IS NULL,1,0)) as total_other_room,
    		sum(if(flash_report_revenue_group in ('Room Charge','Room Discount','Room Tax'),amount * if(type='Debit',1,-1),0)) as total_room_revenue,
    		sum(if(flash_report_revenue_group in ('Deposit Bank'),amount * if(type='Debit',1,-1),0)) as deposit_bank,
    		sum(if(flash_report_revenue_group = 'Room Charge' and parent_reference IS NULL,1,0)) as room_revenue_posted,
    		sum(if(flash_report_revenue_group = 'Other Room Revenue' and parent_reference IS NULL,1,0)) as other_room_revenue_posted,
    		sum(if(parent_reference IS NULL and flash_report_revenue_group in ('Room Charge','Other Room Revenue'),1,0)) as total_room_posted,
			sum(if(account_category in ('Room Charge Adjustment'),amount * if (type='Debit',1,-1),0)) as adjustment_amount,
			sum(if(flash_report_revenue_group in ('Tour Activities'),amount * if (type='Debit',1,-1),0)) as tour_activitie,
			sum(if(flash_report_revenue_group in ('Other Revenue','Other Discount'),amount * if (type='Debit',1,-1),0)) as other_revenue,
			sum(if(account_group_name in ('Charge','Tax') and transaction_type!='Payable Ledger',amount * if (type='Debit',1,-1),0)) as income,
			sum(if(account_group_name in ('Charge','Tax','Discount'),amount * if (type='Debit',1,-1),0)) as net_income,
			COALESCE(SUM(IF(account_category = 'Transportation', amount * IF(type = 'Debit', 1, -1), 0)), 0) as transportation_revenue,
			COALESCE(SUM(IF(account_category = 'Other Charge Discount', amount * IF(type = 'Debit', 1, -1), 0)), 0) as other_charge_discount
		from `tabFolio Transaction` 
		where
			posting_date between %(start_date)s and %(end_date)s and
			property = %(property)s """

	return frappe.db.sql(sql,filters,as_dict=1)

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

def get_data_field(filters):
    sql = """SELECT 
                 %(fieldname)s AS fieldname, 
				 %(day_type)s as day_type,
                 SUM(IF(flash_report_revenue_group in ('Room Charge','Room Tax'), amount * IF(type='Debit',1,-1), 0)) AS sale
             FROM 
                 `tabFolio Transaction` 
             WHERE 
                 posting_date IN %(dates)s AND
                 property = %(property)s"""
    
    return frappe.db.sql(sql, filters, as_dict=1)


def get_data_from_occupy_record(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_data_fieldname({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"room_occupy":{"title":"Rooms Sold"},
				"room_block":{"title":"Out of Order Rooms"},
				"complimentary":{"title":"Complimentary Rooms"},
				"house_use":{"title":"House Use Rooms"},	
				"total_adult_room_night":{"title":"Adult Room Nights"},	
				"total_child_room_night":{"title":"Child Room Nights"},	
				"total_walk_in_room_night":{"title":"Walkin Room Nights"},	
				"total_git_room_night":{"title":"GIT Room Nights"},	
				"total_fit_room_night":{"title":"FIT Room Nights"},	
				"total_arrival_adult":{"title":"Adult Arrivals"},	
				"total_arrival_child":{"title":"Child Arrivals"},	
				
	}
	occupy_data = []
	for f in fields:
		row['room_occupy'][f] = sum([y["total_occupy"] for y in data if y["fieldname"]==f and y["total_occupy"] is not None]) or 0
		row['room_block'][f] = sum([y["total_block"] for y in data if y["fieldname"]==f and y["total_block"] is not None]) or 0
		row['complimentary'][f] = sum([y["total_complimentary"] for y in data if y["fieldname"]==f and y["total_complimentary"] is not None]) or 0
		row['house_use'][f] = sum([y["total_house_use"] for y in data if y["fieldname"]==f and y["total_house_use"] is not None]) or 0
		row['total_arrival_adult'][f] = sum([y["total_arrival_adult"] for y in data if y["fieldname"]==f and y["total_arrival_adult"] is not None]) or 0
		row['total_arrival_child'][f] = sum([y["total_arrival_child"] for y in data if y["fieldname"]==f and y["total_arrival_child"] is not None]) or 0
		row['total_walk_in_room_night'][f] = sum([y["total_walk_in_room_night"] for y in data if y["fieldname"]==f and y["total_walk_in_room_night"] is not None]) or 0
		row['total_adult_room_night'][f] = sum([y["total_adult_room_night"] for y in data if y["fieldname"]==f and y["total_adult_room_night"] is not None]) or 0
		row['total_child_room_night'][f] = sum([y["total_child_room_night"] for y in data if y["fieldname"]==f and y["total_child_room_night"] is not None]) or 0
		row['total_git_room_night'][f] = sum([y["total_git_room_night"] for y in data if y["fieldname"]==f and y["total_git_room_night"] is not None]) or 0
		row['total_fit_room_night'][f] = sum([y["total_fit_room_night"] for y in data if y["fieldname"]==f and y["total_fit_room_night"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_data_fieldname(filters):
	
	sql="""select 
			%(fieldname)s as fieldname,
			sum(type='Reservation' and is_active=1) as total_occupy,
			sum(type='Block') as total_block, 
			sum(type='Reservation' and is_complimentary=1 and is_active=1)  as total_complimentary ,
			sum(type='Reservation' and is_house_use=1 and is_active=1)  as total_house_use,
			sum(if(type='Reservation' and is_arrival=1 and is_active=1,adult,0))  as total_arrival_adult,
			sum(if(type='Reservation' and is_arrival=1 and is_active=1,child,0))  as total_arrival_child,
			sum(if(type='Reservation' and is_active=1,adult,0))  as total_adult_room_night,
			sum(if(type='Reservation' and is_active=1,child,0))  as total_child_room_night,
			sum(type='Reservation' and is_walk_in=1 and is_active=1)  as total_walk_in_room_night,
			sum(type='Reservation' and reservation_type='FIT' and is_active=1) as total_fit_room_night,
			sum(type='Reservation' and reservation_type='GIT' and is_active=1) as total_git_room_night
		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s """

	return frappe.db.sql(sql,filters,as_dict=1)

def get_current_room_in_property(filters):
	data = []
	
	fields = ["current","mtd","ytd","last_year_current","last_year_mtd","last_year_ytd"]
	for f in fields:
		data+=get_current_room_data({ "fieldname":f,"property":filters.property,"start_date":filters.get(f)["start_date"],"end_date":filters.get(f)["end_date"]})
	# frappe.throw(str(data))
	row = {
				"total_room":{"title":"Total Rooms in Property"},	
				
	}
	occupy_data = []
	for f in fields:
		row['total_room'][f] = sum([y["total_room"] for y in data if y["fieldname"]==f and y["total_room"] is not None]) or 0

	occupy_data.append(row)

	return occupy_data

def get_current_room_data(filters):
	
	sql = "select %(fieldname)s as fieldname,sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between %(start_date)s and %(end_date)s"
 
	return frappe.db.sql(sql,filters,as_dict=1)
def get_forecasting(filters):
	
	data = []
	fields = ["current"]
	for f in fields:
		data+=get_forecasting_fieldname({ "fieldname":f,"property":filters.property,"start_date":add_days(filters.get(f)["start_date"],1),"end_date":add_days(filters.get(f)["end_date"],1)})
	row = {
			"total_arrival":{"title":"Total Arrivals"}, 
			"total_departure":{"title":"Total Departures"},
			"total_exp_inhouse":{"title":"Expected Inhouse"},
			"total_adult_child":{"title":"Total Adults/Children"},
			"total_block":{"title":"Total Unavailable"},
			"exp_stay_over":{"title":"Expected Stay Over"},
			"exp_pickup_drop_off":{"title":"Total Expected Pickup/Drop-off"},
			"total_occupy":{"title":"Total Expected Occupy"},
		}
	
	forecasting_data = []
	for f in fields:
		# frappe.throw(str(sum([y["total_occupy"] for y in data if y["fieldname"]==f ]) or 0))
		row['total_occupy'][f] = int(sum([y["total_occupy"] for y in data if y["fieldname"]==f and y["total_occupy"] is not None]) or 0)
		row['total_arrival'][f] = int(sum([y["total_arrival"] for y in data if y["fieldname"]==f and y["total_arrival"] is not None]) or 0)
		row['total_departure'][f] = int(sum([y["total_departure"] for y in data if y["fieldname"]==f and y["total_departure"] is not None]) or 0)
		row['total_exp_inhouse'][f] = int(sum([y["total_exp_inhouse"] for y in data if y["fieldname"]==f and y["total_exp_inhouse"] is not None]) or 0)
		row['total_block'][f] = int(sum([y["total_block"] for y in data if y["fieldname"]==f and y["total_block"] is not None]) or 0)
		row['total_adult_child'][f] = "{}/{}".format(int(sum([y["total_adult"] for y in data if y["fieldname"]==f and y["total_adult"] is not None]) or 0),int(sum([y["total_child"] for y in data if y["fieldname"]==f and y["total_child"] is not None]) or 0))
		row['exp_stay_over'][f] = int(sum([y["exp_stay_over"] for y in data if y["fieldname"]==f and y["exp_stay_over"] is not None]) or 0)
		row['exp_pickup_drop_off'][f] = "{}/{}".format(int(sum([y["exp_pickup"] for y in data if y["fieldname"]==f and y["exp_pickup"] is not None]) or 0),int(sum([y["exp_drop_off"] for y in data if y["fieldname"]==f and y["exp_drop_off"] is not None]) or 0))


		
	forecasting_data.append(row)
	
	return forecasting_data


def get_forecasting_fieldname(filters):

    sql="""
		select 
			%(fieldname)s as fieldname,
			sum(type='Reservation' and is_active=1) as total_occupy,
			sum(type='Block') as total_block, 
			sum(type='Reservation' and is_arrival=1 and is_active=1)  as total_arrival,
			sum(type='Reservation' and is_departure=1)  as total_departure,
			sum(type='Reservation' and is_active=1 and is_arrival=1)  as total_exp_inhouse,
			sum(if(type='Reservation' and is_active=1,adult,0)) as total_adult,
			sum(if(type='Reservation' and is_active=1,child,0)) as total_child,
			sum(type='Reservation' and is_active=1 and is_stay_over=1) as exp_stay_over,
			sum(type='Reservation' and is_active=1 and pick_up=1) as exp_pickup,
			sum(type='Reservation' and is_active=1 and drop_off=1) as exp_drop_off
		from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s 
    """
    return frappe.db.sql(sql,filters, as_dict=1)
def get_forecasting_for_sevenday(filters):

    sql="""
		select 
			%(fieldname)s as fieldname,
			date,
			sum(type='Reservation' and is_active=1) as total_occupy
		from `tabRoom Occupy` where property=%(property)s and date IN %(date_data)s
		group by date
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
	return sum([d[field] for d in report_data if isinstance(d, dict) and d.get("title") == title]) or 0
