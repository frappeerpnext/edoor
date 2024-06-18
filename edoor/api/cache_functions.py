from functools import lru_cache
import frappe
import json

@lru_cache(maxsize=128)
def get_account_code_doc(name):
    return frappe.get_doc("Account Code",name)

@lru_cache(maxsize=128)
def get_account_code_sub_account_information(account_code):
    account_code_doc = get_account_code_doc(account_code)
    account_category_doc = get_account_category_doc(account_code_doc.account_category)
     
    data = {
        "account_code":account_code,
        "account_name":account_code_doc.account_name,
        "account_code_sort_order": account_code_doc.sort_order,
        "parent_account_code": account_code_doc.parent_account_code,
        "parent_account_name":account_code_doc.parent_account_name,
        "account_category": account_category_doc.name,
        "account_category_sort_order": account_category_doc.sort_order,
        "allow_discount": account_code_doc.allow_discount,
        "discount_account": account_code_doc.discount_account,
        "allow_enter_quantity":account_code_doc.allow_enter_quantity,
        "sort_order":account_code_doc.sort_order,
        "flash_report_revenue_group":account_code_doc.flash_report_revenue_group
    }
    
    if account_code_doc.allow_tax and account_code_doc.tax_rule:
        tax_rule_doc = get_tax_rule_doc(account_code_doc.tax_rule)
        if tax_rule_doc.tax_1_rate>0 and tax_rule_doc.tax_1_account:
            data["tax_1_account"] = tax_rule_doc.tax_1_account
            data["tax_1_description"] =  get_doctype_value_cache("Account Code", tax_rule_doc.tax_1_account,"account_name")
        if tax_rule_doc.tax_2_rate>0 and tax_rule_doc.tax_2_account:
            data["tax_2_account"] = tax_rule_doc.tax_2_account
            data["tax_2_description"] =  get_doctype_value_cache("Account Code", tax_rule_doc.tax_2_account,"account_name")
            
        if tax_rule_doc.tax_3_rate>0 and tax_rule_doc.tax_3_account:
            data["tax_3_account"] = tax_rule_doc.tax_3_account
            data["tax_3_description"] =  get_doctype_value_cache("Account Code", tax_rule_doc.tax_3_account,"account_name")
            
         
    
    if account_code_doc.discount_account:
        data["discount_account_name"] = get_doctype_value_cache("Account Code", account_code_doc.discount_account,"account_name")
    
    
    # accunt group and name
    parent_account_doc = get_account_code_doc(account_code_doc.parent_account_code)
    data["account_group"] = parent_account_doc.parent_account_code
    data["account_group_name"] = parent_account_doc.parent_account_name
    return data
    
    

@lru_cache(maxsize=128)
def get_doctype_value_cache(doctype,doc_name, fieldname):
    return frappe.db.get_value(doctype,doc_name,fieldname)




@lru_cache(maxsize=128)
def get_account_category_doc(name):
    return frappe.get_doc("Account Category",name)

@lru_cache(maxsize=128)
def get_rate_type_doc(name):
    return frappe.get_doc("Rate Type",name)

@lru_cache(maxsize=128)
def get_tax_rule_doc(name):
    return frappe.get_doc("Tax Rule",name)

@lru_cache(maxsize=128)
def get_master_folio_name_cache(reservation):
    master_stay = frappe.db.get_list("Reservation Stay",  filters={"reservation":reservation, "is_master":"1"})
    if master_stay:
        master_folio = frappe.db.get_list("Reservation Folio", filters={"reservation_stay":master_stay[0].name, "is_master":1})
        if master_folio:
            folio_doc = frappe.get_doc("Reservation Folio", master_folio[0].name)
            
            return  folio_doc
    
    
    return None

@lru_cache(maxsize=128)
def get_rate_type_info_with_cache(name):
    doc = frappe.get_doc("Rate Type", name)
    if not doc.account_code:
        frappe.throw("This rate type does not have account code")
    
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



@lru_cache(maxsize=128)
def get_base_rate_cache(amount,tax_rule,tax_1_rate, tax_2_rate,tax_3_rate):

	t1_r = (tax_1_rate or 0) / 100
	t2_r = (tax_2_rate or 0)  / 100
	t3_r = (tax_3_rate or 0)  / 100
 


	price = 0

	t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1

	t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
	t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


	tax_rate_con = 0


	tax_rate_con = (1 + t1_r + t2_r 
						+ (t1_r * t2_af_add_t1 * t2_r) 
						+ t3_r + (t1_r * t3_af_add_t1 * t3_r) 
						+ (t2_r * t3_af_add_t2 * t3_r)
						+ (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r)
                )

	tax_rate_con = tax_rate_con or 0
	price = amount /  tax_rate_con

	return  price

@lru_cache(maxsize=128)
def get_doctype_tree_name(doctype, parent=None, parent_field='parent', name_field='name'):
    tree = []
    filters = {}
    if parent:
        filters[parent_field] = parent
    else:
        filters[parent_field] = ('is', 'null')  # Root nodes typically have no parent
    children = frappe.get_all(doctype, filters=filters, fields=[name_field])
    
    for child in children:
        node =child[name_field]
        
        tree.append(node)
        tree = tree + get_doctype_tree_name(doctype, child[name_field], parent_field, name_field)
    
    return tree

