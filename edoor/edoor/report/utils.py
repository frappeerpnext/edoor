import frappe

def get_months(filters):
	sql="select datediff(max(date),min(date)) + 1 as total_days,    month(date) as month, year(date) as year, date_format(date, '%%b-%%Y') as str_month, min(date) as min_date,max(date) as max_date from `tabDates` where date between %(start_date)s and %(end_date)s group by month(date),year(date) order by year(date), month(date)"
	return frappe.db.sql(sql,filters, as_dict=1)
