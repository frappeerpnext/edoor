
import frappe


def execute(filters=None):
	report_data =get_report_data(filters)
	summary = get_summary(filters,report_data)
	columns = get_report_columns(filters)
	 

	return  columns, report_data, None, None, summary




def get_report_columns(filters):
	columns = [
		{"fieldname":"room_number","label":"Room #", "width":100,"align":"center"},
		{"fieldname":"room_type","label":"Room Type", "width":250},
		{"fieldname":"room_charge","label":"Room Revenue", "width":125, "fieldtype":"Currency","align":"right"},
		{"fieldname":"room_charge_adjustment","label":"Room Adj", "width":125, "fieldtype":"Currency","align":"right"},
		{"fieldname":"other_room_charge","label":"Other Room Revenue", "width":150, "fieldtype":"Currency","align":"right"},
		{"fieldname":"service_charge","label":"Service Charge", "width":100, "fieldtype":"Currency","align":"right"},
		{"fieldname":"tax","label":"Tax", "width":75, "fieldtype":"Currency","align":"right"},
		{"fieldname":"total_revenue","label":"Total Revenue", "width":120, "fieldtype":"Currency","align":"right"},
		{"fieldname":"occupy","label":"Occupy", "width":75, "fieldtype":"Int","align":"center"},
		{"fieldname":"adr","label":"ADR", "width":100, "fieldtype":"Currency","align":"right"},
	]
	

	return columns

def get_report_data (filters):
	data = get_row_group(filters)
	# get charge data 
	report_data = data
	charge_data = get_room_charge_data(filters)
	for c in charge_data:
		row = [d for d in report_data if d["room_id"] == c["room_id"]]
		if row:
			row=row[0]
			row["room_charge"] = c["room_charge"] or 0
			row["room_charge_adjustment"] = c["room_charge_adjustment"] or 0
			row["other_room_charge"] = c["other_room_charge"] or 0
			row["service_charge"] = c["service_charge"] or 0
			row["tax"] = c["tax"] or 0
			row["total_revenue"] = c["room_charge"] + c["room_charge_adjustment"] +  c["other_room_charge"]  + c["service_charge"] + c["tax"]


	#occupy data 
	occupy_data = get_occupy_data(filters)
	for occ in occupy_data:
		row = [d for d in report_data if d["room_id"] == occ["room_id"]]
		if row:
			row=row[0]
			row["occupy"] = occ["occupy"]
	total_adr = 0
	for d in report_data:
		if "occupy" in d and d["occupy"]>0 and "total_revenue" in d:
			d["adr"] = d["total_revenue"] / d["occupy"]
			total_adr += d['adr']	
	total_revenue = sum([d["room_charge"] for d in charge_data]) + sum([d["room_charge_adjustment"] for d in charge_data]) + sum([d["other_room_charge"] for d in charge_data]) + sum([d["service_charge"] for d in charge_data]) + sum([d["tax"] for d in charge_data])
	
	report_data.append({
		"indent":0,
		"room_number": "Total",
		"room_charge":sum([d["room_charge"] for d in charge_data]),
		"room_charge_adjustment":sum([d["room_charge_adjustment"] for d in charge_data]),
		"other_room_charge":sum([d["other_room_charge"] for d in charge_data]),
		"service_charge":sum([d["service_charge"] for d in charge_data]),
		"tax":sum([d["tax"] for d in charge_data]),
		"total_revenue":total_revenue,
		"occupy":sum([d["occupy"] for d in occupy_data]),
		"adr":total_adr,
	})
	return report_data


def get_room_charge_data(filters):
	sql="""
		select
			room_id,
			sum(if(account_category='Room Charge',a.amount, 0)) as room_charge,
			sum(if(account_category='Room Charge Adjustment',a.amount, 0)) as room_charge_adjustment,
			sum(if(account_category='Other Room Charge',a.amount, 0)) as other_room_charge,
			sum(if(account_category='Service Charge',a.amount, 0)) as service_charge,
			sum(if(account_category='Room Tax',a.amount, 0)) as tax
		from `tabFolio Transaction` a
		where 
			property=%(property)s

		"""
	if filters.business_source:
		sql=sql +" and a.business_source=%(business_source)s "
	if filters.room_types:
		sql=sql +" and a.room_type_id in  %(room_types)s"
	
	sql= sql + " group by a.room_id"

	data = frappe.db.sql(sql,filters,as_dict=1)
	return data

def get_occupy_data(filters):
	sql="""
		select
			room_id,
			count(name) as occupy

		from `tabRoom Occupy` a
		where 
			is_active=1 and
			type='Reservation' and
			property=%(property)s

		"""
	if filters.business_source:
		sql=sql +" and a.business_source=%(business_source)s "
	if filters.room_types:
		sql=sql +" and a.room_type_id in  %(room_types)s"
	
	sql= sql + " group by a.room_id"

	data = frappe.db.sql(sql,filters,as_dict=1)

	return data

def get_row_group(filters):
	return get_room_number(filters)
	
def get_room_number(filters):
	rooms= []
	if filters.room_types:
		rooms= frappe.db.sql("select name as room_id, room_number, room_type,room_type from `tabRoom` where property=%(property)s and room_type_id in %(room_type_id)s order by sort_order, room_number",filters,as_dict=1)
	else:
		rooms= frappe.db.sql("select name as room_id, room_number, room_type,room_type from `tabRoom` where property=%(property)s order by sort_order, room_number",filters,as_dict=1)
	return rooms




def get_summary(filters,data):
	report_data = get_report_data(filters)
	# get charge data 
	total_adr = 0
	for d in report_data:
		if "occupy" in d and d["occupy"]>0 and "total_revenue" in d:
			d["adr"] = d["total_revenue"] / d["occupy"]
			total_adr += d['adr']	
	total_revenue = sum([d["room_charge"] for d in get_room_charge_data(filters)]) + sum([d["room_charge_adjustment"] for d in get_room_charge_data(filters)]) + sum([d["other_room_charge"] for d in get_room_charge_data(filters)]) + sum([d["service_charge"] for d in get_room_charge_data(filters)]) + sum([d["tax"] for d in get_room_charge_data(filters)])
	if filters.show_summary:
		return [
			{ "label":"Total Room","value":len(data),"indicator":"red"},
			{ "label":"Total Room Revenue","value":sum([d["room_charge"] for d in get_room_charge_data(filters) ]),"datatype": "Currency","indicator":"red"},
			{ "label":"Total Room Adj","value":sum([d["room_charge_adjustment"] for d in get_room_charge_data(filters) ]),"datatype": "Currency","indicator":"blue"},
			{ "label":"Total Other Room Revenue","value":sum([d["other_room_charge"] for d in get_room_charge_data(filters) ]),"datatype": "Currency","indicator":"green"},
			{ "label":"Total Service Charge","value":sum([d["service_charge"] for d in get_room_charge_data(filters) ]),"datatype": "Currency","indicator":"red"},
			{ "label":"Total Tax","value":sum([d["tax"] for d in get_room_charge_data(filters)]),"datatype": "Currency","indicator":"blue"},
			{ "label":"Total Revenue","value":total_revenue,"datatype": "Currency","indicator":"blue"},
			{ "label":"Total Occ.","value":sum([d["occupy"] for d in get_occupy_data(filters)]),"indicator":"green"},
			{ "label":"Total ADR","value":total_adr,"datatype": "Currency","indicator":"green"},
			
		]




