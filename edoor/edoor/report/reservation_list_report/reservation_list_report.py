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

	frappe.local.flags.print_letterhead = "Default Letterhead"

	if filters.chart_type =='pie' or filters.chart_type=="donut":
		if len(filters.show_chart_series)!=1:
			frappe.throw(_("Please select only one series for the chart, either a pie or donut chart."))


	  

	raw_data = get_data(filters,report_config.report_fields)
	report_data = get_report_data(filters = filters, report_fields= report_config.report_fields,data= raw_data)
	summary = get_report_summary( filters= filters, report_fields =  report_config.report_fields, data = raw_data )
	
	chart = get_report_chart(filters,report_data,report_config.report_fields)
	if report_data:
		report_summary = get_report_summary_by_business_source(report_data)
		report_data[0]["report_summary"] = report_summary
		report_data[0]["report_summary_fields"] = report_summary_columns(filters)

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
				"parent":parent,
				"merge_group_row":1
			} if filters.row_group == 'reservation' else {
				"indent": 0,
				report_fields[0].fieldname: formatted_parent,
				"is_group": 1,
				"parent":parent,
				"merge_group_row":1
			})

			report_data.extend([d.update({"parent":parent}) or d for d in data if d[filters.row_group] == parent])

			total_row = {
				report_fields[0].fieldname: _("Total"),
				"is_total_row": 1,
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data if  d[filters.row_group] == parent]),sum([d["child"] for d in data if d[filters.row_group] == parent])),
				"adr":sum([d["total_amount"] for d in data if d[filters.row_group] == parent])/sum([d["room_nights"] for d in data if d[filters.row_group] == parent]),
				"parent":parent,
				"reservation_type":len([d for d in data if d[filters.row_group] == parent])
			}

			for field in [d for d in report_fields if d.get("show_in_total_row",0) ==1 and d.get("fieldtype") in ["Int","Float","Currency"]]:
				total_row[field.fieldname] = sum(d[field.fieldname] for d in data if field.fieldname in d and d[filters.row_group] == parent) or 0
			
			report_data.append(total_row)

	else:
		report_data = data
		total_room_nights = sum([d["room_nights"] for d in data ])
		# we set total room niht to 1 when it 0 because we prevent error devide by 0
		if total_room_nights==0:
			total_room_nights=1
		total_row = ({
				"indent":0,
				report_fields[0].fieldname: "Total",
				"total_pax":"{}/{}".format(sum([d["adult"] for d in data]),sum([d["child"] for d in data])),
				"adr":sum([d["total_amount"] for d in data ])/ total_room_nights,
				"is_total_row":1,
				"is_group":1,
				"reservation_type":len([d for d in data])
				}) 
		for f in [d for d in report_fields if d.get("show_in_total_row",0)==1  and  d.get("fieldtype") in ["Int","Float","Currency"]]:
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
		filters.reservation_stays =get_reservation_stays(filters)
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


def report_summary_columns(filters):
	return [
		{"fieldname":"row_group", "label":"Summary by Business Source", "cell_width":25,"merge_cell":2},
		{"fieldname":"room_count", "label":"Room Count", "fieldtype":"Int", "cell_width":10,"align":"center",},
		{"fieldname":"room_nights", "label":"Room Nights", "fieldtype":"Int", "cell_width":10,"align":"center"},
		{"fieldname":"pax", "label":"Pax(A/C)", "fieldtype":"Data", "cell_width":10,"align":"center"},
		{"fieldname":"total_amount", "label":"Room Charge", "fieldtype":"Currency", "cell_width":10,"align":"right","merge_cell":2},
		{"fieldname":"debit", "label":"Debit", "fieldtype":"Currency", "cell_width":10,"align":"right"},
		{"fieldname":"credit", "label":"Credit", "fieldtype":"Currency", "cell_width":10,"align":"right"}
	]

def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]
	# frappe.msgprint(str(data))

	if filters.show_summary:
		
		if filters.row_group:
			summary.append({
				"value":len([d for d in data if d['indent']==1 and "is_total_row" not in d ]),"indicator":"Red","label":"Total Res."
			})
			summary.append({
				"value":"{}/{}".format(sum([d["adult"] for d in data if d['indent']==1 and "is_total_row" not in d]),sum([d["child"] for d in data if d['indent']==1])),"indicator":"Red","label":"Total Pax"
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
			"value": sum([d[x.fieldname] for d in data if x.fieldname in d if "is_total_row" not in d]),
			"indicator": x.summary_indicator,
			"label": x.label,
			"datatype": x.fieldtype
	})
	return summary

def get_report_chart(filters, data, report_fields):
	# frappe.throw(str([d for d in data if 'is_total_row' in d and d['is_total_row']==1]))
	if filters.chart_type=="None":
		return None
	if filters.chart_type and not filters.row_group:
		frappe.throw("Choose group by to implement with Chart Type")
	
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
	
	return [d["reservation_stay"] for d in data] + ["dummy"]

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

def get_report_summary_by_business_source(data):
	business_source = set([d["business_source"] for d in data if "business_source" in d])
	result = []
	for b in business_source:
		filter_data = [d for d in data if d.get("business_source") == b ]

		row = {
			"row_group":b,
			"room_count":len(filter_data),
			"room_nights":sum([d.get("room_nights") for d in filter_data]),
			"adult":sum([d.get("adult") for d in filter_data]),
			"child":sum([d.get("child") for d in filter_data]),
			"total_amount":sum([d.get("total_amount") for d in filter_data]),
			"debit":sum([d.get("total_debit") for d in filter_data]),
			"credit":sum([d.get("total_credit") for d in filter_data])
		}
		row["pax"] = "{}/{}".format(row["adult"], row["child"]
							  )

		result.append(row)
	if result:
		result.append({
			"row_group":"Total",
			"is_total_row":1,
			"room_count":sum([d.get("room_count") for d in result]),
			"room_nights":sum([d.get("room_nights") for d in result]),
			"adult":sum([d.get("adult") for d in result]),
			"child":sum([d.get("child") for d in result]),
			"pax":"{}/{}".format(sum([d.get("adult") for d in result]),sum([d.get("child") for d in result])),
			"total_amount":sum([d.get("total_amount") for d in result]),
			"debit":sum([d.get("debit") for d in result]),
			"credit":sum([d.get("credit") for d in result])
		})


	return result
	
