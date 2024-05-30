# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns = get_columns(filters)
	data = get_report_data(filters)
	
	return columns, data,"hello world",get_chart(),get_summary()
	

def get_chart():
    return {
		'data':{
			'labels':['d','o','g','s'],
			'datasets':[
				{'name':'Number','values':[3,6,4,7]},
				{'name':'Vowel','values':[0,1,0,0]}
			]
		},
		'type':'bar'
	}
def get_summary():
    return [
		{"label":"cats","value":2287,'indicator':'Red'},
		{"label":"dogs","value":3647,'indicator':'Blue',"datatype":"Currency","currency":"KHR"}
	]
    
def get_columns(filters):
    return [
		{"fieldname":"name", "label":"Reservation #","fieldtype":"Link","options":"Reservation"},
		{"fieldname":"arrival_date", "label":"Arrival", "fieldtype":"Date"},
		{"fieldname":"departure_date", "label":"Departure"},
		{"fieldname":"total_room_rate", "label":"Total Rate","fieldtype":"Currency"},
	]
    
def get_report_data(filters):
    sql = """select name, arrival_date, departure_date, total_room_rate from `tabReservation`
		where
			property = %(property)s and 
			arrival_date = %(arrival_date)s
    """
    data = frappe.db.sql(sql,filters,as_dict=1)
    return data 
    