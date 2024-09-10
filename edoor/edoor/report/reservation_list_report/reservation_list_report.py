import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
import datetime
import uuid
def execute(filters=None): 
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Reservation List Report"} )
	# if filters.summary_filter:
	# 	if not filters.summary_fields:
	# 		filters.summary_fields = ['total_record', 'room_night']

	 

	# data = get_get_reservation_stay(filters)
	report_data = get_report_data(filters, report_config.report_fields)
	summary = get_report_summary(filters,report_config.report_fields,report_data)
	chart = get_report_chart(filters,report_data,report_config.report_fields)
	return get_report_columns(filters,report_config.report_fields),report_data,None,chart, summary

def validate(filters):
	datediff = date_diff(filters.end_date, filters.start_date)
	if filters.start_date and filters.end_date:
		if filters.start_date > filters.end_date:
			frappe.throw("The 'Start Date' ({}) must be before the 'End Date' ({})".format(filters.start_date, filters.end_date))
		if datediff > 30:
			frappe.throw("Your Max date for viewing transaction is only One Month.".format(filters.start_date, filters.end_date))

def get_report_columns(filters,  report_fields):
	columns = []
	report_fields = [d for d in report_fields if d.show_in_report==1]

	if filters.show_columns:
		report_fields = [d for d in report_fields if d.fieldname in filters.show_columns]

	for g in report_fields:
		columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })

	if filters.row_group:
		columns = [d for d in columns if d["fieldname"] != filters.row_group]

	return columns

def get_report_data (filters, report_fields):
	data = get_data(filters,report_fields)
	
	report_data = []
	if filters.row_group:
		parent_row = get_parent_row_row_by_data(filters,data)
		for parent in parent_row:
			d = parent
			if filters.row_group=="arrival_date":
				d  = frappe.format(parent,{"fieldtype":"Date"})
			report_data.append({
				"indent":0,
				report_fields[0].fieldname: d,
				"is_group":1
			})

			report_data = report_data + [d for d in data if d[filters.row_group] == parent]
			total_row = {
				"row_group":_("Total"),
				"is_total_row": 1,
			
			}
			for f in [d for d in report_fields if d.show_in_report==1 and d.show_in_summary==1]:
				total_row[f.fieldname] = (sum([d[f.fieldname] for d in data if f.fieldname in d])) 
			report_data.append(total_row)

		# report_data.append({"indent":0}) 
		# grand_total_row = ({"indent":0,report_fields[0].fieldname: "Grand Total","is_group":1,"document_name":len([d for d in data])}) 
		# for f in [d for d in report_fields if d.show_in_report==1 and d.fieldtype!='Date' and d.fieldtype!='Data' and d.fieldtype!='Link' and d.show_in_summary==1]:
		# 	grand_total_row[f.fieldname] = (sum([d[f.fieldname] for d in data]))
		# report_data.append(grand_total_row)
			
	else:
		report_data = data

	return report_data

def get_parent_row_row_by_data(filters, data):
	
	rows = set([d[filters.row_group] for d in  data])

	return rows
	
def get_data (filters,report_fields):
	sql ="select {} as indent, 0 as is_group, ".format(1 if filters.row_group else 0)

	sql ="{} {}".format(sql, ",".join([d.sql_expression for d in report_fields if d.sql_expression]))

	if filters.row_group and len([d for d in report_fields if d.fieldname == filters.row_group]) == 0:
		sql = "{} , {}".format(sql, filters.row_group)

	sql = "{} from `tabReservation Stay` as rst ".format(sql)
	sql = "{} {}".format(sql, get_filters(filters))
	# frappe.throw(sql)
	data = frappe.db.sql(sql, filters ,as_dict=1)
	return data



def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]

	if filters.show_in_summary:
		summary_fields = [d for d in summary_fields if d.fieldname in filters.show_in_summary]
		for x in summary_fields:
			summary.append({
			"value": sum([d[x.fieldname] for d in data if x.fieldname in d]),
			"indicator": x.summary_indicator,
			"label": x.label,
			"datatype": x.fieldtype
	})
	return summary

def get_report_chart(filters,data,report_fields):
	precision = frappe.db.get_single_value("System Settings","currency_precision")
	report_fields = [d for d in report_fields if d.show_in_chart ==1]
	
	if filters.show_chart_series:
		report_fields = [d for d in report_fields if d.show_in_chart ==1 and d.fieldname in filters.show_chart_series]
	else:
		report_fields = [d for d in report_fields if d.show_in_chart_when_no_fields_selected ==1]
	
	if len(report_fields)==0:
		return None
	
	
	columns =[]
	
	datasets = []
	
	if filters.row_group:
		chart_label_field = "name"
		columns = [d[chart_label_field] for d in  data if 'is_group' in d and  d["is_group"] == 1 and d['name']!="Total" and d['name']!="Grand Total"]
	else:
		chart_label_field = "name"
		columns = [d[chart_label_field] for d in  data if 'is_group' in d and  d["is_group"] == 0 and d['name']!="Total" and d['name']!="Grand Total"]

	for f in report_fields:
		if f.show_in_chart==1:
			if filters.row_group:
				if (f.fieldtype=="Currency"):
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname],int(precision)) for d in  data if 'is_group_total' in d and  d["is_group_total"] ==1]
					})

				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in  data if    'is_group_total' in d and  d["is_group_total"] ==1]
					})
			else:
				if (f.fieldtype=="Currency"):
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname],int(precision)) for d in  data if 'is_group' in d and  d["is_group"] ==0]
					})

				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in  data if    'is_group' in d and  d["is_group"] ==0]
					})
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

def get_filters(filters):
	sql = " where property=%(property)s "

	if filters.filter_date_by =="Arrival Date":
		sql = sql +  " and rst.arrival_date between %(start_date)s and %(end_date)s "
	elif filters.filter_date_by == "Stay Date":
		filters.reservation_stays = get_reservation_stays(filters)
		sql = sql + " and rst.name in %(reservation_stays)s"
	elif filters.filter_date_by == "Reservation":
		sql = sql +  " and rst.reservation_date between %(start_date)s and %(end_date)s "
	elif filters.filter_date_by == "Departure Date":
		sql = sql +  " and rst.departure_date between %(start_date)s and %(end_date)s "

	if filters.reservation:
		sql = sql +  " and rst.reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"

	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"

	# if filters.get("room_types"):
	# 	sql = sql + " and rst.room_types in %(room_types)s"
		

	
	if filters.reservation_type:
		sql = sql + " and rst.reservation_type = %(reservation_type)s"
 
	if filters.is_active_reservation:
		sql = sql + " and rst.is_active_reservation = %(is_active_reservation)s"

	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by][0]["field"],
		filters.sort_order
	)

	return sql

def get_order_field(): 
	return [
		{"label":"Created On","field":"rst.creation"},
		{"label":"Reservation","field":"rst.reservation"},
		{"label":"Reservation Date","field":"rst.reservation_date"},
		{"label":"Reservation Stay","field":"rst.name"},
		{"label":"Arrival Date","field":"rst.arrival_date"},
		{"label":"Departure Date","field":"rst.departure_date"},
		{"label":"Room Type","field":"rst.room_type_alias"},
		{"label":"Business Source","field":"rst.business_source"},
		{"label":"Reservation Status","field":"rst.reservation_status"},
		{"label":"Last Update On","field":"rst.modified"},
		]

def get_reservation_stays(filters):
	sql = """
		select 
			distinct reservation_stay 
		from `tabRoom Occupy` 
		where 
			date  between %(start_date)s and %(end_date)s 
	"""
	if filters.reservation:
		sql = sql +  " and rst.reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"
	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"
	# if filters.get("room_types"):
	# 	sql = sql + " and rst.room_types in %(room_types)s"

	data =  frappe.db.sql(sql, filters, as_dict=1)
	return [d["reservation_stay"] for d in data]

def get_reservation(filters):
	sql = """
		select 
			distinct reservation
		from `tabRoom Occupy` 
		where 
			date  between %(start_date)s and %(end_date)s
	"""
	if filters.reservation:
		sql = sql +  " and rst.reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and rst.business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and rst.guest = %(guest)s"
	if filters.get("reservation_status"):
		sql = sql + " and rst.reservation_status in %(reservation_status)s"
	# if filters.get("room_types"):
	# 	sql = sql + " and rst.room_types in %(room_types)s"
		
	data =  frappe.db.sql(sql, filters, as_dict=1)
	return [d["reservation"] for d in data]

def get_group_by_column(filters):
 
	return  [d for d in group_by_columns() if d["label"] == filters.group_by][0]

def group_by_columns():
	
	return [
		{"data_field":"arrival_date", "label":"Arrival Date","fieldtype":"Date"},
		{"data_field":"departure_date", "label":"Departure Date" ,"fieldtype":"Date" },
		{"data_field":"reservation", "label":"Reservation" ,"fieldtype":"Data" },
		{"data_field":"name", "label":"Reservation Stay" ,"fieldtype":"Data" },
		{"data_field":"reservation_date", "label":"Reservation Date" ,"fieldtype":"Date" },
		{"data_field":"guest", "label":"Guest" ,"fieldtype":"Data" },
		{"data_field":"reservation_type", "label":"Reservation Type" ,"fieldtype":"Data" },
		{"data_field":"nationality", "label":"Nationality" ,"fieldtype":"Data" },
		{"data_field":"business_source", "label":"Business Source" ,"fieldtype":"Data" },
		{"data_field":"business_source_type", "label":"Business Source Type" ,"fieldtype":"Data" },
		{"data_field":"room_types", "label":"Room Type" ,"fieldtype":"Data" },
		{"data_field":"rate_type", "label":"Rate Type" ,"fieldtype":"Data" },
		{"data_field":"reservation_status", "label":"Reservation Status" ,"fieldtype":"Data" },
	]

def get_field(filters):
 
	return  [d for d in get_report_field() if d["label"] == filters.view_chart_by][0]

def get_report_field():
	return [
		{"data_field":"arrival_date", "label":"Arrival Date","fieldtype":"Date"},
		{"data_field":"departure_date", "label":"Departure Date" ,"fieldtype":"Date" },
		{"data_field":"reservation", "label":"Reservation" ,"fieldtype":"Data" },
		{"data_field":"name", "label":"Reservation Stay" ,"fieldtype":"Data" },
		{"data_field":"reservation_date", "label":"Reservation Date" ,"fieldtype":"Date" },
		{"data_field":"guest_name", "label":"Guest" ,"fieldtype":"Data" },
		{"data_field":"reservation_type", "label":"Reservation Type" ,"fieldtype":"Data" },
		{"data_field":"nationality", "label":"Nationality" ,"fieldtype":"Data" },
		{"data_field":"business_source", "label":"Business Source" ,"fieldtype":"Data" },
		{"data_field":"business_source_type", "label":"Business Source Type" ,"fieldtype":"Data" },
		{"data_field":"room_types", "label":"Room Type" ,"fieldtype":"Data" },
		{"data_field":"rate_type", "label":"Rate Type" ,"fieldtype":"Data" },
		{"data_field":"reservation_status", "label":"Reservation Status" ,"fieldtype":"Data" },
	]

	

def get_chart_series():
	return [
		{"data_field":"total_debit","label":"Total Debit","short_label":"Debit", "fieldtype":"Currency", "align":"center","chart_color":"#dc9819"},
		{"data_field":"total_credit","label":"Total Credit", "short_label":"Credit", "fieldtype":"Currency", "align":"right","chart_color":"#1987dc"},
		{"data_field":"balance","label":"Balance", "short_label":"Balance", "fieldtype":"Currency", "align":"right","chart_color":"#fd4e8a"},
		{"data_field":"adult","label":"Adult", "short_label":"Adult", "fieldtype":"Integer", "align":"right","chart_color":"#d7e528"},
		{"data_field":"child","label":"Child", "short_label":"Child", "fieldtype":"Integer", "align":"right","chart_color":"#df7b5c"},
		{"data_field":"pax","label":"Pax", "short_label":"Pax", "fieldtype":"Integer", "align":"right","chart_color":"#df7b5c"},
		{"data_field":"room_nights","label":"Room Nights", "short_label":"Room Nights", "fieldtype":"Integer", "align":"right","chart_color":"#3ce18e"}
	]