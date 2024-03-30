def get_room_occupy_group_by_field(filters):
    if filters.parent_row_group:
        return [d["value"] for d in room_occupy_group_by_fields() if d["key"] == filters.row_group][0]
    else:
        return "''"

def room_occupy_group_by_fields():
	# a. is base table alias
	return [
		{"key":"Business Source", "value": "business_source"},
		{"key":"Business Source Type", "value": "business_source_type"},
		{"key":"Reservation Type", "value": "reservation_type"},
		{"key":"Room Type", "value": "room_type_id"},
		{"key":"Room", "value": "room_id"},
		{"key":"Guest", "value": "guest"},
		{"key":"Guest Type", "value": "guest_type"},
	]

def get_columns(filters):
	columns = []
	for n in range(1,32):
		columns.append(
			{'fieldname':str(n),'align':'center','label':str(n),"width":55 ,"show_in_report":1,"is_date":1},
		)
	return columns

def get_filters(filters):
	sql = " and property=%(property)s "
	if filters.building:
		sql = sql + " and r.building in %(building)s "

	return sql