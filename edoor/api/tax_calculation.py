from functools import lru_cache
from edoor.api.utils import get_base_rate
import frappe
import time

# @lru_cache(maxsize=128)
@frappe.whitelist()
def dome(n=10,rate=0):
    start_time = time.time()

    docs = []
    for i in range(0,int(n)):
        docs.append(get_tax_breakdown(
            tax_rule= "Room Charge Tax",
            tax_1_rate=5,
            tax_2_rate=2,
            tax_3_rate=10,
            rate_include_tax="Yes",
            rate=int(rate),
            discount_amount=10

        ))

    
    end_time = time.time()

    duration = end_time - start_time
    return("Duration:", duration, "seconds",docs)

     
@lru_cache(maxsize=128)
def get_tax_breakdown(tax_rule,rate_include_tax="Yes", tax_1_rate=0, tax_2_rate=0, tax_3_rate=0,discount_amount=0,rate=0):
    
    if tax_rule:
        tax_rule = frappe.get_doc("Tax Rule",tax_rule)
        
        data = {
            "tax_rule_data":tax_rule.tax_rule_data,
            "tax_1_name":tax_rule.tax_1_name or "",
            "tax_2_name":tax_rule.tax_2_name or "",
            "tax_3_name":tax_rule.tax_3_name or "",
            "tax_data_list":[]
        }
        data["rate"] = rate
        if rate_include_tax== "Yes" and (tax_1_rate + tax_2_rate + tax_3_rate) > 0:
            price = get_base_rate((rate or 0) - (discount_amount or 0),tax_rule,tax_1_rate,tax_2_rate, tax_3_rate)

            data["rate"] = price + (discount_amount or 0)

        else:
            data["rate"] = rate    
        #tax 1
        data["taxable_amount_1"] = data["rate"] * ((tax_rule.percentage_of_price_to_calculate_tax_1 or 100)/100)
        
        data["taxable_amount_1"] = data["taxable_amount_1"] if tax_rule.calculate_tax_1_after_discount == 0 and rate_include_tax== "No"   else data["taxable_amount_1"] - discount_amount

        data["tax_1_amount"] = data["taxable_amount_1"] * tax_1_rate / 100
        if data["tax_1_amount"]> 0:
            data["tax_data_list"].append({"tax_name":data["tax_1_name"],"amount":data["tax_1_amount"]})
        #tax 2
        data["taxable_amount_2"] = (data["rate"] or 0) * ((tax_rule.percentage_of_price_to_calculate_tax_2 or 100)/100)
        data["taxable_amount_2"] = data["rate"] * ((tax_rule.percentage_of_price_to_calculate_tax_2 or 100)/100)
        data["taxable_amount_2"] = data["taxable_amount_2"] if tax_rule.calculate_tax_2_after_discount == 0  and rate_include_tax== "No"  else data["taxable_amount_2"] - discount_amount
        data["taxable_amount_2"] = data["taxable_amount_2"]  if tax_rule.calculate_tax_2_after_adding_tax_1 == 0 else data["taxable_amount_2"]  + data["tax_1_amount"]
        
        data["tax_2_amount"] = data["taxable_amount_2"] * tax_2_rate / 100
        if data["tax_2_amount"]> 0:
            data["tax_data_list"].append({"tax_name":data["tax_2_name"],"amount":data["tax_2_amount"]})
        
        #tax 3

        data["taxable_amount_3"] = (data["rate"] or 0) * ((tax_rule.percentage_of_price_to_calculate_tax_3 or 100)/100)

        data["taxable_amount_3"] = data["taxable_amount_3"] if tax_rule.calculate_tax_3_after_discount == 0 and  rate_include_tax== "No"  else data["taxable_amount_3"] - discount_amount
        data["taxable_amount_3"] = data["taxable_amount_3"]  if tax_rule.calculate_tax_3_after_adding_tax_1 == 0 else data["taxable_amount_3"] +  data["tax_1_amount"]
        data["taxable_amount_3"] = data["taxable_amount_3"]  if tax_rule.calculate_tax_3_after_adding_tax_2 == 0 else data["taxable_amount_3"] + data["tax_2_amount"]
        data["tax_3_amount"] = data["taxable_amount_3"] * tax_3_rate / 100
        if data["tax_3_amount"]> 0:
            data["tax_data_list"].append({"tax_name":data["tax_3_name"],"amount":data["tax_3_amount"]})
        

        data["total_tax"] = (data["tax_1_amount"] or 0 ) + (data["tax_2_amount"] or 0 ) + (data["tax_3_amount"] or 0 ) 
        data["total_amount"] = data["rate"] - discount_amount + data["total_tax"] 
      
        return data
    else:
        return {
            "tax_1_amount": 0,
			"tax_2_amount" : 0,
			"tax_3_amount": 0,
			"taxable_amount_1": 0,
			"taxable_amount_2": 0,
			"taxable_amount_3": 0,
			"total_tax": 0,
            "tax_1_name":"",
            "tax_2_name":"",
            "tax_3_name":"",
            "rate": rate,
            "total_amount":0,
            "tax_rule_data":"{}"
        }