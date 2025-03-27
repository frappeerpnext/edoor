# Copyright (c) 2025, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from edoor.api.frontdesk import get_working_day
from frappe.model.document import Document
from frappe import _


class CityLedgerInvoice(Document):
	pass



@frappe.whitelist(methods="POST")
def add_new_city_ledger_invoice(data):
    doc= data.get("doc")
    working_day = get_working_day(doc.get("property"))
    invoice_doc = frappe.get_doc({
            'doctype': 'City Ledger Invoice',
            **doc,
            "working_day":working_day.get("name"),
            "working_date":working_day.get("date_working_day"),
            "cashier_shift":working_day.get("cashier_shift").get("name")
        }).insert()
    
    if data.get("folio_transactions"):
        frappe.db.sql("update `tabFolio Transaction` set city_ledger_invoice = %(city_ledger_invoice)s where name in %(folio_transactions)s",{"city_ledger_invoice":invoice_doc.name, "folio_transactions":data.get("folio_transactions")})
        
    
    update_city_ledger_invoice_balance(invoice_doc.name, run_commit=False)
    frappe.db.commit()
    frappe.msgprint(_("Add city ledger invoice successfully"))
    return invoice_doc

def update_city_ledger_invoice_balance(name,run_commit = True):
    payment_status = get_payment_status(name)
    
    sql ="""
        update `tabCity Ledger Invoice` a
        join (
            select
                ft.city_ledger_invoice, 
                sum(transaction_amount * if(type='Debit',1,0)) as debit,
                sum(transaction_amount * if(type='Credit',1,0)) as credit 
            from `tabFolio Transaction` ft
            where
                ft.city_ledger_invoice = %(city_ledger_invoice)s and 
                ft.is_base_transaction = 1
        ) b on b.city_ledger_invoice = a.name
        SET 
            a.total_debit = b.debit,
            a.total_credit = b.credit,
            a.balance = b.debit - b.credit,
            a.payment_status = %(payment_status)s
        where
            a.name = %(city_ledger_invoice)s
    """
    frappe.db.sql(sql,{"city_ledger_invoice":name,"payment_status":payment_status})
    
    
    # update payment status to folio transaction
    sql = """
        update `tabFolio Transaction` 
        SET 
            payment_status = %(payment_status)s 
        where
            city_ledger_invoice = %(city_ledger_invoice)s and 
            account_group != '3000'
    """
    frappe.db.sql(sql,{"city_ledger_invoice":name,"payment_status":payment_status})
    
    if run_commit:
        frappe.db.commit()

        
def get_payment_status(name):
    sql = """
    SELECT 
        ft.account_group,
        SUM(ft.transaction_amount * IF(ft.type = 'debit', 1, -1)) AS total_amount
    FROM `tabFolio Transaction` ft
    WHERE ft.transaction_type = 'City Ledger' 
    AND ft.city_ledger_invoice = %(city_ledger_invoice)s
    GROUP BY ft.account_group
    """
    payment_data = frappe.db.sql(sql, {"city_ledger_invoice":name}, as_dict=True)
    payment = 0
    balance_value = 0
    
    if [d for d in payment_data if d.get("account_group") == '3000']:
        payment =abs( max([d.get("total_amount") for d in payment_data if d.get("account_group") == '3000']) )#payment account group
    
    balance_value = sum([d.get("total_amount") for d in payment_data])
    payment_status = ""
    
    if payment == 0:
        payment_status = "Unpaid"
    elif payment < 0 and balance_value != 0:
        payment_status = "Partially Paid"
    elif payment>0 and balance_value == 0:
        payment_status = "Paid"
    return payment_status

   
        
@frappe.whitelist(methods="POST")
def remove_folio_transaction_from_invoice(city_ledger_invoice, data):
    if data:
        transactions_with_empty_reference = frappe.db.get_list(
            "Folio Transaction",
            filters={"name": ["in", data], "reference_folio_transaction": ""},
            pluck="name" 
        )
        if len(transactions_with_empty_reference) >0: 
            frappe.throw("Can't remove payment from City Ledger Invoice")
        sql = "update `tabFolio Transaction` set payment_status = '', city_ledger_invoice ='' Where name in %(names)s"
        frappe.db.sql(sql, {"names":data})
        frappe.db.commit()
        update_city_ledger_invoice_balance(city_ledger_invoice)
        return frappe.get_doc("City Ledger Invoice", city_ledger_invoice)
@frappe.whitelist(methods="POST")
def add_city_ledger_transaction_invoice(city_ledger_invoice, data ):
    if data:
        sql = "update `tabFolio Transaction` set  city_ledger_invoice = %(city_ledger_invoice)s Where name in %(names)s"
        frappe.db.sql(sql, {"city_ledger_invoice":city_ledger_invoice,"names":data})
        frappe.db.commit()
        update_city_ledger_invoice_balance(city_ledger_invoice)
        return frappe.get_doc("City Ledger Invoice", city_ledger_invoice)    
    
        
        