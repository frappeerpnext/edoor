import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import strip
import datetime

def execute(filters=None): 
	data = get_report_data(filters)
	return get_columns(),data


def get_columns():
	return [
		{"fieldname":"name", "label":"Stay #", "fieldtype":"Link","options":"Reservation Stay"},
		{"fieldname":"reservation_date", "label":"Res. Date", "fieldtype":"Date"},
		{"fieldname":"arrival_date", "label":"Arrival", "fieldtype":"Date"},
		{"fieldname":"departure_date", "label":"Departure", "fieldtype":"Date"}
	]

def get_report_data(filters):
	sql="""
		select 
			name,
			reservation_date,
			arrival_date,
			departure_date
		from `tabReservation Stay`
	"""
	data = frappe.db.sql(sql,as_dict=1)
	return data