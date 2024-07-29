import frappe
from frappe import _

def get_room_occupy_group_by_field(filters):
    if filters.parent_row_group:
        return [d["value"] for d in room_occupy_group_by_fields() if d["key"] == filters.parent_row_group][0]
    else:
        return "''"

def room_occupy_group_by_fields():
	# a. is base table alias
	return [
		{"key":"Date", "value": "date_format(date,'%%d-%%m-%%Y')" },
		{"key":"Month", "value": "date_format(date,'%%b-%%Y')"},
		{"key":"Year", "value": "year(date)"},
		{"key":"Reservation Type", "value": "reservation_type"},
		{"key":"Business Source", "value": "business_source"},
		{"key":"Business Source Type", "value": "business_source_type"},
		{"key":"Room Type", "value": "room_type_id"},
		{"key":"Guest Type", "value": "guest_type"},
		{"key":"Nationality", "value": "nationality"}
	]


def get_folio_transaction_group_by_field(filters):
    if filters.parent_row_group:
        return [d["value"] for d in folio_transaction_group_by_fields() if d["key"] == filters.parent_row_group][0]
    else:
        return "''"



def folio_transaction_group_by_fields():
	#  is base table alias
	return [
		{"key":"Date", "value": "date_format(posting_date,'%%d-%%m-%%Y')" },
		{"key":"Month", "value": "date_format(posting_date,'%%b-%%Y')"},
		{"key":"Year", "value": "year(posting_date)"},
		{"key":"Reservation Type", "value": "reservation_type"},
		{"key":"Business Source", "value": "business_source"},
		{"key":"Business Source Type", "value": "business_source_type"},
		{"key":"Room Type", "value": "room_type_id"},
		{"key":"Guest Type", "value": "guest_type"},
		{"key":"Nationality", "value": "nationality"}
	]

def get_parent_group_by_record(filters):
	 
	if filters.parent_row_group:
		sql =""
		if filters.parent_row_group == "Date":
			sql = "select distinct date_format(date,'%%d-%%m-%%Y') as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s"		
		elif filters.parent_row_group == "Month":
			sql = "select distinct date_format(date,'%%b-%%Y') as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s"		
		elif filters.parent_row_group == "Year":
			sql = "select distinct date_format(date,'%%Y') as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s"
		

		data = frappe.db.sql(sql,filters, as_dict=1)
		if len(data)>0:
			return data
	
	return [{"parent_row_group":""}]
		

def report_group_row_from_result_data(occupy_data, folio_transaction_data):
	row_group = [d["row_group"] for d in occupy_data]
	row_group = row_group +  [d["row_group"] for d in folio_transaction_data]
	row_group = set(row_group)
	row_group =  [{"row_group": d} for d in row_group]
	return row_group

def get_parent_group_row_from_result_data(occupy_data, folio_transaction_data):
	row_group = [d["parent_row_group"] or "Not Set" for d in occupy_data]
 
	row_group = row_group +  [d["parent_row_group"] or "Not Set" for d in folio_transaction_data]
	row_group = set(row_group)
	row_group =  [{"parent_row_group": d} for d in row_group]
 
	return sorted(row_group, key=lambda k: k['parent_row_group'])

def get_row_group_from_result_data(occupy_data, folio_transaction_data):
	row_group = [{"row_group":d["row_group"] or "Not Set", "parent_row_group":d["parent_row_group"]} for d in occupy_data]
	row_group = row_group +  [{"row_group":d["row_group"] or "Not Set", "parent_row_group":d["parent_row_group"]} for d in folio_transaction_data]
	row_group =list(set(frozenset(d.items()) for d in row_group))
	row_group =[{k: v for k, v in d} for d in row_group]
	return sorted(row_group, key=lambda k: k['row_group'])


def get_parent_row_group_label(filters, name):
	if filters.parent_row_group=="Room Type":
		return frappe.db.get_value("Room Type",name,"room_type")
	else:
		return name
	
def get_report_fields(filters, report_config):
	if filters.show_columns:
		return  [d for d in report_config.report_fields if d.fieldname in filters.show_columns]
	else:
		return report_config.report_fields
	
def get_occupy_data_filters(filters):
	sql =  " and date between %(start_date)s and %(end_date)s and property=%(property)s "
	if filters.room_type:
		sql = "{} and room_type_id=%(room_type)s".format(sql)   
	if filters.reservation_type:
		sql = "{} and reservation_type=%(reservation_type)s".format(sql)

	if filters.business_source:
		sql = "{} and business_source=%(business_source)s".format(sql)

	if filters.guest_type:
		sql = "{} and guest_type=%(guest_type)s".format(sql)
	
	if filters.business_source_type:
		sql = "{} and business_source_type=%(business_source_type)s".format(sql)

	#exclude empty
	if filters.parent_row_group:
		sql = "{} and {}!='' ".format(sql, get_room_occupy_group_by_field(filters)) 

	return sql
 
	
def get_folio_transaction_filters(filters):
	sql =  " and posting_date between %(start_date)s and %(end_date)s and property=%(property)s "
	if filters.room_type:
		sql = "{} and room_type_id=%(room_type)s".format(sql)
	if filters.reservation_type:
		sql = "{} and reservation_type=%(reservation_type)s".format(sql)


	if filters.business_source:
		sql = "{} and business_source=%(business_source)s".format(sql)

	if filters.guest_type:
		sql = "{} and guest_type=%(guest_type)s".format(sql)

	if filters.business_source_type:
		sql = "{} and business_source_type=%(business_source_type)s".format(sql)

	#exclude empty
	if filters.parent_row_group:
		sql = "{} and {}!='' ".format(sql, get_folio_transaction_group_by_field(filters)) 
	return sql
 
	
def get_report_summary( filters, total_record,report_config):
	report_summary = []
	report_fields = get_report_fields(filters, report_config)
	if filters.show_summary_field:
		report_fields = [d for d in report_fields if d.fieldname in filters.show_summary_field]
	
	for f in report_fields :
			if f.show_in_summary==1:
				report_summary.append({"label":_(f.label),"value":frappe.format_value(total_record[f.fieldname],f.fieldtype),"indicator":f.summary_indicator or "blue"})

	return report_summary


def get_report_chart(filters,report_data,report_config):
	precision = frappe.db.get_single_value("System Settings","currency_precision")
	report_fields = get_report_fields(filters, report_config)
	 
	if filters.show_chart_series:
		report_fields = [d for d in report_fields if d.show_in_chart ==1 and d.fieldname in filters.show_chart_series]
	else:
		report_fields = [d for d in report_fields if d.show_in_chart_when_no_fields_selected ==1]
	
	if len(report_fields)==0:
		return None
	

	columns =[]
	
	datasets = []
	chart_label_field = "row_group"
	if filters.row_group == "Room Type":
		chart_label_field = "room_type"
	if not filters.parent_row_group:
		columns = [d[chart_label_field]  for d in  report_data if d["is_group"] == 0 and d["row_group"]!="Grand Total"]
 
		for f in report_fields:
			if f.show_in_chart==1:
				if (f.fieldtype=="Currency"):
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname], int(precision)) for d in  report_data if d["is_group"] == 0 and d["is_total_row"] ==0]
					})
				elif f.fieldtype=="Percent":
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname], 2) for d in  report_data if d["is_group"] == 0 and d["is_total_row"] ==0]
					})
				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in  report_data if d["is_group"] == 0 and d["is_total_row"] ==0]
					})

	else:
		columns = [d[chart_label_field] for d in  report_data if 'is_group' in d and  d["is_group"] == 1 and  d["row_group"]!="Grand Total"]
		for f in report_fields:
			if f.show_in_chart==1:
				if (f.fieldtype=="Currency"):
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname],int(precision)) for d in  report_data if 'is_group_total' in d and  d["is_group_total"] ==1]
					})
				elif f.fieldtype=="Percent":
					 
					datasets.append({
						"name": f.label,
						"values": [round(d[f.fieldname],2) for d in  report_data if 'is_group_total' in d and  d["is_group_total"] ==1]
					})
				else:
					datasets.append({
						"name": f.label,
						"values": [d[f.fieldname] for d in  report_data if 'is_group_total' in d and  d["is_group_total"] ==1]
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
