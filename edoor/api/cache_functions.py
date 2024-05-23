from functools import lru_cache
import frappe

@lru_cache(maxsize=128)
def get_account_code_doc(name):
    return frappe.get_doc("Account Code",name)

@lru_cache(maxsize=128)
def get_rate_type_doc(name):
    return frappe.get_doc("Rate Type",name)

@lru_cache(maxsize=128)
def get_tax_rule_doc(name):
    return frappe.get_doc("Tax Rule",name)