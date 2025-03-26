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
            a.balance = b.debit - b.credit
        where
            a.name = %(city_ledger_invoice)s
    """
    frappe.db.sql(sql,{"city_ledger_invoice":name})
    if run_commit:
        frappe.db.commit()
    sql = """
    SELECT 
        SUM(ft.amount * IF(ft.type = 'debit', 1, -1)) AS total_amount
    FROM `tabFolio Transaction` ft
    WHERE ft.transaction_type = 'City Ledger' 
    AND ft.city_ledger_invoice = %(city_ledger_invoice)s
    AND ft.account_group = '30000' 
    GROUP BY ft.account_group
    """
    payemnt_data = frappe.db.sql(sql, {"property": property, "city_ledger_invoice": name}, as_dict=True)
    payment = payemnt_data[0]["total_amount"] if payemnt_data else 0
    balance_value = frappe.get_value("City Ledger Invoice", {"name": name}, "balance")
    if payment == 0:
        payment_status = "Unpaid"
    elif payment < 0 and balance_value > 0:
        payment_status = "Partially Paid"
    else:
        payment_status = "Paid"
    sql_update_payment_status = """
        update `tabCity Ledger Invoice` a set
        a.payment_status = %(payment_status)s 
        where
            a.name = %(city_ledger_invoice)s
    """
    frappe.db.sql(sql_update_payment_status,{"city_ledger_invoice":name,"payment_status":payment_status})
    if run_commit:
        frappe.db.commit()
    