import frappe

@frappe.whitelist()
def get_folio_total_summary(transaction_type, transaction_number,reservation_stay):
    data = frappe.db.sql("select account_category,account_category_sort_order,sum(report_quantity) as quantity, sum(amount * if(type='Debit',1,-1)) as amount from `tabFolio Transaction` where transaction_type='{}' and transaction_number = '{}' group by account_category order by account_category_sort_order".format(transaction_type, transaction_number),as_dict=1)
    return data
    
    
