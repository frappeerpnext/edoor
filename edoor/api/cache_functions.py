from functools import lru_cache
import frappe
import json

@lru_cache(maxsize=128)
def get_account_code_doc(name):
    return frappe.get_doc("Account Code",name)

@lru_cache(maxsize=128)
def get_rate_type_doc(name):
    return frappe.get_doc("Rate Type",name)

@lru_cache(maxsize=128)
def get_tax_rule_doc(name):

    return frappe.get_doc("Tax Rule",name)


@lru_cache(maxsize=128)
def get_rate_type_info_with_cache(name):
    doc = frappe.get_doc("Rate Type", name)
    if not doc.account_code:
        frappe.throw("This account does not have account code")
    
    account_doc =frappe.get_doc("Account Code", doc.account_code)
    tax_rule=None
    if account_doc.tax_rule:
        tax_rule = frappe.get_doc("Tax Rule",account_doc.tax_rule)
    

    if doc.is_house_use==1 or doc.is_complimentary==1:
        tax_rule = None
    package_data = []
    if account_doc.is_package:
        if account_doc.packages:
            package_data = [{
                "account_code":d.account_code,
                "posting_rule":d.posting_rule,
                "charge_rule":d.charge_rule,
                "rate":d.rate,
                "adult_rate":d.adult_rate,
                "child_rate":d.child_rate,
                "breakdown_account_code": d.breakdown_account_code,
                "discount_breakdown_account_code": d.discount_breakdown_account_code or "",
                "tax_1_breakdown_account_code": d.tax_1_breakdown_account_code or "",
                "tax_2_breakdown_account_code": d.tax_2_breakdown_account_code or "",
                "tax_3_breakdown_account_code": d.tax_3_breakdown_account_code or "",
             } for d in account_doc.packages]
            
            
    return {
        "name": name,
        "tax_rule":tax_rule,
        "allow_discount": account_doc.allow_discount,
        "allow_user_to_change_tax": account_doc.allow_user_to_change_tax,
        "allow_user_to_edit_rate": doc.allow_user_to_edit_rate,
        "is_house_use":doc.is_house_use,
        "is_complimentary":doc.is_complimentary,
        "is_package":doc.is_package,
        "package_charge_data":json.dumps(package_data)
    }
