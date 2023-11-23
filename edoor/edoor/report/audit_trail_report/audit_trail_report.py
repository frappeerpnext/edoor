# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff,today ,add_months, add_days
from frappe.utils.data import getdate, strip
import datetime
import uuid
from dateutil.rrule import rrule, MONTHLY
from datetime import datetime
import copy
import calendar


def execute(filters=None):
	report_data = get_report_data(filters)
	return get_columns(filters),report_data,None,None, None


def get_columns(filters):
	columns = [
		{'fieldname':'custom_posting_date','fieldtype':'Date','align':'left','label':'Audit Date',"width":90 ,"show_in_report":1, "css_class":"text-center"},
		{'fieldname':'reference_doctype','align':'left','label':'Ref Type #',"width":150 ,"show_in_report":1},
		{'fieldname':'reference_name','align':'left','label':'Ref Name #',"width":100 ,"show_in_report":1,"css_class":"text-center"},
		{'fieldname':'subject','align':'left','label':'Subject',"width":200 ,"show_in_report":1},
		{'fieldname':'content','align':'left','label':'Content',"width":550 ,"show_in_report":1},
		{'fieldname':'comment_by','align':'left','label':'By',"width":150 ,"show_in_report":1},
		{'fieldname':'modified','align':'left','fieldtype':'Datetime','label':'Date & Time',"width":200 ,"show_in_report":1,"css_class":"text-center"},
	]
	return columns
def get_filters(filters):
	sql = " and custom_is_audit_trail = 1 and custom_is_note = 0 and custom_property=%(property)s and custom_posting_date between %(start_date)s and %(end_date)s"

	if filters.get("select_user"):
		sql = sql + " and c.comment_email = %(select_user)s"
	if filters.get("select_filter"):
		sql = sql + " and c.reference_doctype in %(select_filter)s"

	sql = sql + " order by {} {}".format(
		[d for d in  get_order_field() if d["label"] == filters.order_by_audit][0]["field"],
		filters.sort_order
	)

	return sql

def get_order_field():
	return [
		{"label":"Created On","field":"c.creation"},
		{"label":"Reference Document","field":"c.reference_doctype"},
		{"label":"Reference Name","field":"c.reference_name"},
		{"label":"Audit Date","field":"c.custom_posting_date"},
		{"label":"Subject","field":"c.subject"},
		{"label":"Description","field":"c.content"},
		{"label":"Created By","field":"c.comment_email"},
		{"label":"Last Update On","field":"c.modified"},
		]

def get_report_data(filters):
	sql="""
			select 
				custom_posting_date,
				reference_doctype,
				subject,
				content,
				comment_by, 
				reference_name,
				comment_email,
				modified 
			from `tabComment` c
			where 
				1=1
				{}
		""".format(get_filters(filters))


	data =  frappe.db.sql(sql,filters,as_dict=1)
	return data