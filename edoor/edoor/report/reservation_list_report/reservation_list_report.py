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

	 

	raw_data = get_data(filters,report_config.report_fields)
	report_data = get_report_data(filters = filters, report_fields= report_config.report_fields,data= raw_data)
	summary = get_report_summary( filters= filters, report_fields =  report_config.report_fields, data = raw_data )
	
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

def get_report_data(filters, report_fields, data):
	report_data = []
	if filters.row_group:
		parent_rows = sorted(set(get_parent_row_row_by_data(filters, data)))
		
		for parent in parent_rows:
			formatted_parent = frappe.format(parent, {"fieldtype": "Date"}) if filters.row_group in ["arrival_date", "departure_date", "reservation_date"] else parent
			
			report_data.append({
				"indent": 0,
				"name": formatted_parent,
				"is_group": 1,
				"parent":parent
			} if filters.row_group == 'reservation' else {
				"indent": 0,
				report_fields[0].fieldname: formatted_parent,
				"is_group": 1,
				"parent":parent
			})

			report_data.extend([d.update({"parent":parent}) or d for d in data if d[filters.row_group] == parent])

			total_row = {
				report_fields[0].fieldname: _("Total"),
				"is_total_row": 1,
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if d[filters.row_group] == parent]),sum([d["child"] for d in data if d[filters.row_group] == parent])),
				"adr":sum([d["total_amount"] for d in data if d[filters.row_group] == parent])/sum([d["room_nights"] for d in data if d[filters.row_group] == parent]),
				"parent":parent,
				"reservation_type":len([d for d in data if d[filters.row_group] == parent])
			}

			for field in [d for d in report_fields if d.show_in_report and d.show_in_summary]:
				total_row[field.fieldname] = sum(d[field.fieldname] for d in data if field.fieldname in d and d[filters.row_group] == parent)

			report_data.append(total_row)

	else:
		report_data = data
		total_row = ({
				"indent":0,
				report_fields[0].fieldname: "Total",
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data]),sum([d["child"] for d in data])),
				"adr":sum([d["total_amount"] for d in data ])/sum([d["room_nights"] for d in data ]),
				"is_total_row":1,
				"is_group":1,
				"reservation_type":len([d for d in data])
				}) 
		for f in [d for d in report_fields if d.show_in_report==1 and d.fieldtype!='Date' and d.fieldtype!='Data' and d.fieldtype!='Link' and d.show_in_summary==1]:
			total_row[f.fieldname] = (sum([d[f.fieldname] for d in data]))
		report_data.append(total_row)

	return report_data


def get_parent_row_row_by_data(filters, data):
	
	rows = set([d[filters.row_group] for d in  data])

	return rows
	
def get_data (filters,report_fields):
	sql ="select {} as indent, 0 as is_group, ".format(1 if filters.row_group else 0)

	sql ="{} {}".format(sql, ",".join([d.sql_expression for d in report_fields if d.sql_expression]))

	if filters.row_group and len([d for d in report_fields if d.fieldname == filters.row_group]) == 0:
		sql = "{} , {}".format(sql, filters.row_group)

	sql = "{} from `tabReservation Stay` ".format(sql)
	sql = sql + " where property=%(property)s "

	if filters.filter_date_by =="Arrival Date":
		sql = sql +  " and arrival_date between %(start_date)s and %(end_date)s "
	elif filters.filter_date_by == "Stay Date":
		filters.reservation_stays = get_reservation_stays(filters)
		sql = sql + " and name in %(reservation_stays)s"
	elif filters.filter_date_by == "Reservation":
		sql = sql +  " and reservation_date between %(start_date)s and %(end_date)s "
	elif filters.filter_date_by == "Departure Date":
		sql = sql +  " and departure_date between %(start_date)s and %(end_date)s "

	if filters.reservation:
		sql = sql +  " and reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and guest = %(guest)s"

	if filters.get("reservation_status"):
		sql = sql + " and reservation_status in %(reservation_status)s"

	# if filters.get("room_types"):
	# 	sql = sql + " and room_types in %(room_types)s"
		

	
	if filters.reservation_type:
		sql = sql + " and reservation_type = %(reservation_type)s"
 
	if filters.is_active_reservation:
		sql = sql + " and is_active_reservation = %(is_active_reservation)s"

	order_field = [d for d in get_order_field() if d["label"] == filters.order_by][0]["field"]
	sql = sql + " order by {} {}".format(order_field, filters.sort_order)
	
 	# frappe.throw(sql)
	data = frappe.db.sql(sql, filters ,as_dict=1)
	
	return data



def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]
	# frappe.throw(str(data))

	if filters.show_summary:
		
		if filters.row_group:
			summary.append({
				"value":len([d for d in data if d['indent']==1 ]),"indicator":"Red","label":"Total Res."
			})
			summary.append({
				"value":"{}/{}".format(sum([d["adult"] for d in data if d['indent']==1]),sum([d["child"] for d in data if d['indent']==1])),"indicator":"Red","label":"Total Pax"
			})
		else:
			summary.append({
				"value":len([d for d in data if d['is_group']==0 ]),"indicator":"Red","label":"Total Res."
			})
			summary.append({
				"value":"{}/{}".format(sum([d["adult"] for d in data if d['is_group']==0]),sum([d["child"] for d in data if d['is_group']==0])),"indicator":"Red","label":"Total Pax"
			})
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

def get_report_chart(filters, data, report_fields):
	# frappe.throw(str(filters.row_group))
	precision = frappe.db.get_single_value("System Settings", "currency_precision")
	report_fields = [d for d in report_fields if d.show_in_chart == 1]
	if filters.show_chart_series:
		report_fields = [d for d in report_fields if d.show_in_chart == 1 and d.fieldname in filters.show_chart_series]
	else:
		report_fields = [d for d in report_fields if d.show_in_chart_when_no_fields_selected == 1]

	if len(report_fields) == 0:
		return None
	columns = []
	datasets = []
	if filters.row_group:
		columns = [
        d.get('reservation', d.get('name'))  # Use 'reservation' if available, otherwise 'name'
        for d in data 
        if 'is_group' in d and d["is_group"] == 1
    ]
	else:
		chart_label_field = "name"
		columns = [d[chart_label_field] for d in data if 'is_group' in d and d["is_group"] == 0 ]

	for f in report_fields:
		if f.show_in_chart == 1:
			if filters.row_group:
				if f.fieldtype == "Currency":
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname], int(precision)) for d in data if 'is_total_row' in d and d['is_total_row']==1]
					})
				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in data if 'is_total_row' in d and d['is_total_row']==1]
					})
			else:
				if f.fieldtype == "Currency":
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname], int(precision)) for d in data if 'is_group' in d and d["is_group"] == 0]
					})
				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in data if 'is_group' in d and d["is_group"] == 0]
					})

	chart = {
		'data': {
			'labels': columns,
			'datasets': datasets
		},
		"type": filters.chart_type,
		"lineOptions": {
			"regionFill": 1,
		},
		'valuesOverPoints': 1,
		"axisOptions": {"xIsSeries": 1}
	}

	return chart




def get_order_field(): 
	return [
		{"label":"Created On","field":"creation"},
		{"label":"Reservation","field":"reservation"},
		{"label":"Reservation Date","field":"reservation_date"},
		{"label":"Reservation Stay","field":"name"},
		{"label":"Arrival Date","field":"arrival_date"},
		{"label":"Departure Date","field":"departure_date"},
		{"label":"Room Type","field":"room_type_alias"},
		{"label":"Business Source","field":"business_source"},
		{"label":"Reservation Status","field":"reservation_status"},
		{"label":"Last Update On","field":"modified"},
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
		sql = sql +  " and reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and guest = %(guest)s"
	if filters.get("reservation_status"):
		sql = sql + " and reservation_status in %(reservation_status)s"
	# if filters.get("room_types"):
	# 	sql = sql + " and room_types in %(room_types)s"

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
		sql = sql +  " and reservation  =  %(reservation)s"
	if filters.business_source:
		sql = sql + " and business_source = %(business_source)s"
	if filters.guest:
		sql = sql + " and guest = %(guest)s"
	if filters.get("reservation_status"):
		sql = sql + " and reservation_status in %(reservation_status)s"
	# if filters.get("room_types"):
	# 	sql = sql + " and room_types in %(room_types)s"
		
	data =  frappe.db.sql(sql, filters, as_dict=1)
	return [d["reservation"] for d in data]

