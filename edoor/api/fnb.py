import frappe
import datetime
import json
from datetime import datetime
from frappe import _ 
from frappe import utils

@frappe.whitelist(allow_guest=True)
def get_fnb_revenue_and_payment_data(property, date):
	data = {
		"fnb_revenue":get_fnb_revenue(property, date),
		"fnb_payment":get_fnb_payment(property, date)
	}
	return data

@frappe.whitelist(allow_guest=True)
def get_fnb_revenue(property, date=None):
	sql = """select 
            sp.revenue_group,
			sum(sp.total_revenue) as total_revenue,
			r.color,
			r.background
		from `tabSale Product` sp 
		inner join `tabSale` s on s.name = sp.parent
		inner join `tabRevenue Group` r on sp.revenue_group = r.name
		where
            s.business_branch = %(property)s and
			s.posting_date=%(date)s and 
			s.docstatus=1 and 
			coalesce(sp.is_combo_menu,0) = 0
		group by 
			sp.revenue_group"""
	data = frappe.db.sql(sql,{'property':property,'date':date},as_dict=1)
	labels = []
	datasets = []
	result = data + get_combo_menu_revenue(property, date)
	
	for d in set([r["revenue_group"] for r in result]):
		labels.append(d)
		datasets.append({
			"type":"bar",
			"name":d,
			"values": sum([x["total_revenue"] for x in result if x["revenue_group"]==d]),	
			"color":[x["color"] for x in result if x["revenue_group"]==d][0]
		})
	return {"labels":labels,"datasets":datasets}


@frappe.whitelist(allow_guest=True)
def get_fnb_payment(property, date=None):
	sql="""select 
		sp.payment_type,
		sum(sp.payment_amount + sp.fee_amount) as total_payment,
		pt.color,
		pt.background
	from `tabSale Payment` as sp
	inner join `tabSale` as s on s.name = sp.sale
	inner join `tabPayment Type` as pt on sp.payment_type = pt.name
	where
		s.business_branch = %(property)s and
		sp.posting_date=%(date)s and 
		sp.transaction_type = 'Payment' and
		sp.docstatus = 1 
	group by
		payment_type
	"""
	data = frappe.db.sql(sql,{'property':property,'date':date},as_dict=1)
	labels = []
	datasets = []
	for d in data:
		labels.append(d["payment_type"])
		datasets.append({
			"type":"bar",
			"name":d["payment_type"],
			"values": d["total_payment"],	
			"color":d["color"]
		})
	return {"labels":labels,"datasets":datasets}


def get_combo_menu_revenue(property, date):
	sql="""select 
			sp.revenue_group,
			sp.sub_total,
			sp.total_discount as discount,
			sp.tax_1_amount,
			sp.tax_2_amount,
			sp.tax_3_amount,
			sp.combo_menu_data,
			sp.quantity,
			sp.total_revenue
		from `tabSale Product` sp 
		inner join `tabSale` s on s.name = sp.parent
		where
			s.business_branch = %(property)s and
			s.posting_date=%(date)s and 
			s.docstatus=1  and 
			sp.is_combo_menu = 1
		
		"""
	
	
 
	data = frappe.db.sql(sql, {'property':property,'date':date},as_dict=1)
	revenue_data = []
	for d in data:
		revenue_data = revenue_data  + get_combo_menu_data_revenue_breakdown(d)
		
	revenue_group = frappe.db.sql("""select name, color,background from `tabRevenue Group`""", as_dict=1)

	group_revenue_data = []
	for r in set([d["revenue_group"] for d in revenue_data]): 
		group_revenue_data.append({
			"revenue_group":r,
			"total_revenue":sum([d["total_revenue"] for d in revenue_data if d["revenue_group"] == r]),
			"color": [rg["color"] for rg in revenue_group if rg["name"]==r][0],
			"background": [rg["background"] for rg in revenue_group if rg["name"]==r][0]
		})
	return group_revenue_data

def get_combo_menu_data_revenue_breakdown(revenue_data):
	data = json.loads(revenue_data["combo_menu_data"])
	combo_item_revenues  =[]
	for c in data:
		combo_revenue ={"product_code":c["product_code"], 
						"revenue_group": frappe.db.get_value("Product",c["product_code"],"revenue_group") ,
						"sub_total":revenue_data["quantity"] * c["quantity"] * c["price"],
						"discount":0,
						"tax_1_amount":0,
						"tax_2_amount":0,
						"tax_3_amount":0,
						"total_revenue":0
					} 
		# calculate discount
		if revenue_data["discount"] > 0:
			combo_revenue["discount"] = combo_revenue["sub_total"] * (revenue_data["discount"] / revenue_data["sub_total"])
   
		if revenue_data["tax_1_amount"] > 0:
			combo_revenue["tax_1_amount"] = combo_revenue["tax_1_amount"] * (revenue_data["tax_1_amount"] / revenue_data["sub_total"])
   
		if revenue_data["tax_2_amount"] > 0:
			combo_revenue["tax_2_amount"] = combo_revenue["tax_2_amount"] * (revenue_data["tax_2_amount"] / revenue_data["sub_total"])
   
		if revenue_data["tax_3_amount"] > 0:
			combo_revenue["tax_3_amount"] = combo_revenue["tax_3_amount"] * (revenue_data["tax_3_amount"] / revenue_data["sub_total"])
			
		if revenue_data["total_revenue"] > 0:
			combo_revenue["total_revenue"] = combo_revenue["sub_total"]   - combo_revenue["discount"] + combo_revenue["tax_1_amount"] +  combo_revenue["tax_2_amount"]+ combo_revenue["tax_3_amount"]
	
		combo_item_revenues.append(combo_revenue)

  
	base_revenue ={"revenue_group":revenue_data.revenue_group}
	base_revenue["sub_total"] = revenue_data["sub_total"] -  sum(d["sub_total"] for d in combo_item_revenues)
	base_revenue["discount"] = revenue_data["discount"] -  sum(d["discount"] for d in combo_item_revenues)
	base_revenue["tax_1_amount"] = revenue_data["tax_1_amount"] -  sum(d["tax_1_amount"] for d in combo_item_revenues)
	base_revenue["tax_2_amount"] = revenue_data["tax_2_amount"] -  sum(d["tax_2_amount"] for d in combo_item_revenues)
	base_revenue["tax_3_amount"] = revenue_data["tax_3_amount"] -  sum(d["tax_3_amount"] for d in combo_item_revenues)
	base_revenue["total_revenue"] = revenue_data["total_revenue"] -  sum(d["total_revenue"] for d in combo_item_revenues)
	
	return   [base_revenue] + combo_item_revenues