# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import copy


def execute(filters=None):
	report_config = frappe.get_last_doc("Report Configuration", filters={"property":filters.property, "report":"Stay Over Guest Report"} )
	
	report_data = get_report_data(filters, report_config.report_fields)
	summary = get_report_summary(filters, report_config.report_fields, report_data)
	columns = get_report_columns(filters, report_config.report_fields)

	if filters.sort_order_field and filters.show_in_group_by:
		return None

	if filters.sort_order_field:
		# Apply sort
		report_data = copy.deepcopy(report_data)

		# Define a helper function to handle None values and mixed types
		def sort_key(x):
			value = x.get(filters.sort_order_field, None)
			if value is None:
				return ""  # Treat None as an empty string or some default value
			if isinstance(value, str):
				return (
					value.lower()
				)  # Sort strings lexicographically (case-insensitive)
			return value  # Sort numbers normally

		# Perform the sorting
		report_data = sorted(
			[d for d in report_data if d.get("is_total_row", 0) == 0],
			key=sort_key,
			reverse=(filters.sort_type == "DESC"),
		)

		# Keep total rows at the bottom
		report_data = report_data + [
			d for d in report_data if d.get("is_total_row", 0) == 1
		]
	else:
		report_data = report_data

	return  columns, report_data, None, None, summary


def get_report_columns(filters,  report_fields):
	columns = []
	report_fields = [d for d in report_fields if d.show_in_report==1]

	if filters.show_columns:
		report_fields = [d for d in report_fields if d.fieldname in filters.show_columns]

	for g in report_fields:
		columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })

	if filters.show_in_group_by:
		columns = [d for d in columns if d["fieldname"] != filters.show_in_group_by]

	return columns

def get_report_data (filters, report_fields):
	data = get_data(filters,report_fields)
	
	report_data = []
	if filters.show_in_group_by:
		parent_row = get_parent_row_row_by_data(filters,data)
		for parent in parent_row:
			report_data.append({
				"indent":0,
				report_fields[0].fieldname: parent,
				"is_group":1
			})

			report_data = report_data + [d for d in data if d[filters.show_in_group_by] == parent]
			
	else:
		report_data = data

	return report_data

def get_parent_row_row_by_data(filters, data):
	
	rows = set([d[filters.show_in_group_by] for d in  data])

	return rows
	
def get_data (filters,report_fields):
	sql ="select {} as indent, 0 as is_group, ".format(1 if filters.show_in_group_by else 0)

	sql ="{} {}".format(sql, ",".join([d.sql_expression for d in report_fields if d.sql_expression]))

	if filters.show_in_group_by and len([d for d in report_fields if d.fieldname == filters.show_in_group_by]) == 0:
		sql = "{} , {}".format(sql, filters.show_in_group_by)

	sql = "{} from `tabReservation Stay`  ".format(sql)
	sql = "{} {}".format(sql, get_filters(filters))
	data = frappe.db.sql(sql, filters ,as_dict=1)

	return data

def get_filters(filters):
	sql = "where property=%(property)s  and is_active_reservation = 1 "
	sql =  " {} and arrival_date < %(start_date)s and departure_date > %(end_date)s ".format(sql) 
	if filters.business_source:
		sql = "{} and business_source =  %(business_source)s".format(sql)
	
	if filters.room_types:
		sql = """{} and  name in (
			select distinct reservation_stay from `tabRoom Occupy` r 
			{}	
		) """.format(sql,get_room_rate_filters(filters))
	return sql 

def get_room_rate_filters(filters):
	sql = "where property=%(property)s and is_stay_over = 1 "
	sql =  " {} and date between %(start_date)s and %(end_date)s ".format(sql) 

	if filters.business_source:
		sql = "{} and business_source =  %(business_source)s".format(sql)
	
	if filters.room_types:
		sql = "{} and room_type_id  in %(room_types)s".format(sql)
 
	return sql

def get_report_summary(filters,report_fields, data):
	summary = []
	summary_fields = [d for d in report_fields if d.show_in_summary==1 ]
	if filters.show_in_summary:
		summary_fields = [d for d in summary_fields if d.fieldname in filters.show_in_summary]

	for x in summary_fields:
		summary.append({
        "value": sum([d[x.fieldname] for d in data if d["is_group"] == 0 and x.fieldname in d]),
        "indicator": x.summary_indicator,
        "label": x.label,
        "datatype": x.fieldtype
})
	return summary



