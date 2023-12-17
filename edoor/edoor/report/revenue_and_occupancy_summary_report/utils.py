import frappe

def get_room_occupy_group_by_field(filters):
    if filters.parent_row_group:
        return [d["value"] for d in room_occupy_group_by_fields() if d["key"] == filters.parent_row_group][0]
    else:
        return "''"

def room_occupy_group_by_fields():
	# a. is base table alias
	return [
		{"key":"Date", "value": "date" },
		{"key":"Month", "value": "date_format(date,'%%b-%%Y')"},
		{"key":"Year", "value": "year(date)"},
		{"key":"Reservation Type", "value": "reservation_type"},
		{"key":"Business Source", "value": "business_source"},
		{"key":"Room Type", "value": "room_type_id"}
	]


def get_folio_transaction_group_by_field(filters):
    if filters.parent_row_group:
        return [d["value"] for d in folio_transaction_group_by_fields() if d["key"] == filters.parent_row_group][0]
    else:
        return "''"



def folio_transaction_group_by_fields():
	#  is base table alias
	return [
		{"key":"Date", "value": "posting_date" },
		{"key":"Month", "value": "date_format(posting_date,'%%b-%%Y')"},
		{"key":"Year", "value": "year(posting_date)"},
		{"key":"Reservation Type", "value": "reservation_type"},
		{"key":"Business Source", "value": "business_source"},
		{"key":"Room Type", "value": "room_type_id"}
	]

def get_parent_group_by_record(filters):
	if filters.parent_row_group:
		sql =""
		if filters.parent_row_group == "Month":
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
	row_group = [d["parent_row_group"] for d in occupy_data]
	row_group = row_group +  [d["parent_row_group"] for d in folio_transaction_data]
	row_group = set(row_group)
	row_group =  [{"parent_row_group": d} for d in row_group]
	 
	return sorted(row_group, key=lambda k: k['parent_row_group'])