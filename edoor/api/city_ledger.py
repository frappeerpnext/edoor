import frappe
import datetime
import json
from datetime import datetime
from frappe import _ 
from frappe import utils
from frappe.model.document import Document

@frappe.whitelist()
def get_city_ledger_account(property):
    sql = """
    SELECT 
    name, 
    city_ledger_name,
    city_ledger_type,
    business_source,
    company_name,
    phone_number,
    email_address,
    contact_name,
    contact_phone_number,
    total_debit,
    total_credit,
    balance
    FROM `tabCity Ledger`
    Where 
    property = %(property)s 
    ORDER BY modified DESC
    LIMIT 10
    """
    data = frappe.db.sql(sql, {"property":property} , as_dict=True)
    return data
@frappe.whitelist()
def get_city_ledger_invoice(property, status=None):
    condition = "AND status = %(status)s" if status else ""
    
    sql = f"""
    SELECT 
        name, 
        city_ledger,
        city_ledger_name,
        payment_status,
        owner,
        creation,
        modified,
        posting_date,
        status,
        total_debit,
        total_credit,
        balance
    FROM `tabCity Ledger Invoice`
    WHERE 
        property = %(property)s
        {condition}
    ORDER BY modified DESC
    LIMIT 10
    """

    params = {"property": property}
    if status:
        params["status"] = status
    
    data = frappe.db.sql(sql, params, as_dict=True)
    return data

@frappe.whitelist()
def get_top_debtor_company(property):
    sql = """
    SELECT city_ledger_name, balance
    FROM `tabCity Ledger`
    Where 
    property = %(property)s and
    balance > 0
    ORDER BY balance DESC
    LIMIT 10
    """
    data = frappe.db.sql(sql, {"property":property} , as_dict=True)
    return data
@frappe.whitelist()
def get_city_Ledger_jounal(property):
    sql = """
    SELECT 
    name , 
    is_auto_post,
    is_verify ,
    source_transaction_number ,
    guest,
    total_amount,
    amount,
    owner,
    note,
    posting_date , 
    city_ledger_name , 
    transaction_number , 
    account_code , 
    account_name , 
    type ,
    reference_number ,
    room_type , 
    modified,
    creation,
    room_number ,
    reservation_status ,
    reservation_status_color
    FROM `tabFolio Transaction`
    Where 
    property = %(property)s and
    transaction_type = "City Ledger"
    ORDER BY creation DESC
    LIMIT 10
    """
    data = frappe.db.sql(sql, {"property":property} , as_dict=True)
    return data
@frappe.whitelist()
def get_balance_city_ledger(property, date=None, city_leger=None):
    # Aging Balance Query
    aging_balance_sql = """
    SELECT 
        SUM(CASE WHEN DATEDIFF(DATE(%(date)s), ft.posting_date) < 1 THEN ft.amount * IF(ft.type='Debit',1,-1) ELSE 0 END) AS current_amount,
        SUM(CASE WHEN DATEDIFF(DATE(%(date)s), ft.posting_date) BETWEEN 1 AND 30 THEN ft.amount * IF(ft.type='Debit',1,-1) ELSE 0 END) AS `30_day`,
        SUM(CASE WHEN DATEDIFF(DATE(%(date)s), ft.posting_date) BETWEEN 31 AND 60 THEN ft.amount * IF(ft.type='Debit',1,-1) ELSE 0 END) AS `60_day`,
        SUM(CASE WHEN DATEDIFF(DATE(%(date)s), ft.posting_date) BETWEEN 61 AND 90 THEN ft.amount * IF(ft.type='Debit',1,-1) ELSE 0 END) AS `90_day`,
        SUM(CASE WHEN DATEDIFF(DATE(%(date)s), ft.posting_date) > 90 THEN ft.amount * IF(ft.type='Debit',1,-1) ELSE 0 END) AS `120_day_plus`
    FROM `tabFolio Transaction` ft
    INNER JOIN `tabCity Ledger` cl ON cl.name = ft.transaction_number
    WHERE 
        ft.transaction_type = 'City Ledger' 
        AND ft.property = %(property)s 
        AND ft.posting_date <= DATE(%(date)s)
    """

    # Pending Balance Query
    pending_balance_sql = """
    SELECT 
        SUM(ft.amount * IF(ft.type='Debit',1,-1)) AS total_pending,
        SUM(
            CASE 
                WHEN (ft.city_ledger_invoice IS NULL OR ft.city_ledger_invoice = '') 
                THEN ft.amount * CASE WHEN ft.type = 'Debit' THEN 1 ELSE -1 END
                ELSE 0
            END
        ) AS city_ledger_invoice_pending,
        SUM(
            CASE 
                WHEN ft.city_ledger_invoice IS NOT NULL  
                THEN ft.amount * CASE WHEN ft.type = 'Debit' THEN 1 ELSE -1 END
                ELSE 0
            END
        ) AS city_ledger_uninvoice
    FROM `tabFolio Transaction` ft
    WHERE 
        ft.transaction_type = 'City Ledger' 
        AND ft.property = %(property)s
    """

    # SQL Query Parameters
    params = {"property": property, "date": date}

    # Add city ledger filter if provided
    count_pending = 0
    if city_leger:
        aging_balance_sql += " AND ft.transaction_number = %(city_leger)s"
        pending_balance_sql += " AND ft.transaction_number = %(city_leger)s"
        params["city_leger"] = city_leger  # Include in parameters
        count_pending = frappe.db.count("City Ledger Invoice", {
        "city_ledger": city_leger,
        "status": "Open"
        })
        

    # Execute queries using Frappe ORM
    aging_data = frappe.db.sql(aging_balance_sql, params, as_dict=True)
    pending_data = frappe.db.sql(pending_balance_sql, params, as_dict=True)
    result = {
        "aging_balance": [
            {"label": "Current Amount", "value": aging_data[0].get("current_amount", 0)},
            {"label": "30 Day", "value": aging_data[0].get("30_day", 0)},
            {"label": "60 Day", "value": aging_data[0].get("60_day", 0)},
            {"label": "90 Day", "value": aging_data[0].get("90_day", 0)},
            {"label": "120 Day Plus", "value": aging_data[0].get("120_day_plus", 0)}
        ],
        "pending_balance": {
            "total_pending": pending_data[0].get("total_pending", 0),
            "city_ledger_invoice_pending": pending_data[0].get("city_ledger_invoice_pending", 0),
            "city_ledger_uninvoice": pending_data[0].get("city_ledger_uninvoice", 0),
            "count_pending":count_pending
        }
    }
    
    return result
@frappe.whitelist()
def get_balance_city_ledger_transaction(property,city_ledger_invoice = None):
    sql = """
        SELECT 
          ft.account_group , ft.account_group_name , SUM(ft.amount * IF(ft.type = 'debit', 1, -1)) AS total_amount
        FROM `tabFolio Transaction` ft
        WHERE ft.transaction_type = 'City Ledger' 
        AND ft.property = %(property)s 
        AND ft.city_ledger_invoice = %(city_ledger_invoice)s
       GROUP BY ft.account_group 

    """
    data = frappe.db.sql(sql, {"property": property, "city_ledger_invoice": city_ledger_invoice}, as_dict=True)
    return data
@frappe.whitelist()
def get_city_Ledger_payment_received(filters):
    filters = json.loads(filters)
    sql_today = """
    SELECT 
        account_code,
        account_name,
        SUM(amount * CASE WHEN type = 'Debit' THEN 1 ELSE -1 END) AS total_amount
    FROM `tabFolio Transaction`
    WHERE 
        property = %(property)s
        AND transaction_type = "City Ledger"
        AND account_group = "30000"
        AND posting_date = %(date)s
    """

    sql_mtd = """
    SELECT 
        account_code,
        account_name,
        SUM(amount * CASE WHEN type = 'Debit' THEN 1 ELSE -1 END) AS total_amount
    FROM `tabFolio Transaction`
    WHERE 
        property = %(property)s
        AND transaction_type = "City Ledger"
        AND account_group = "30000"
        AND posting_date BETWEEN DATE_FORMAT(%(date)s, '%%Y-%%m-01') AND %(date)s
    """
    params = {"property": filters.get("property"), "date": filters.get("date")}

    if "city_ledger" in filters and filters["city_ledger"]:
        sql_today += " AND transaction_number = %(city_ledger)s"
        sql_mtd += " AND transaction_number = %(city_ledger)s"
        params["city_ledger"] = filters["city_ledger"]

    sql_today += " GROUP BY account_group ORDER BY creation DESC"
    sql_mtd += " GROUP BY account_group ORDER BY creation DESC"
    today_data = frappe.db.sql(sql_today, params, as_dict=True)
    mtd_data = frappe.db.sql(sql_mtd, params, as_dict=True)

    return {
        "today_payment": today_data,
        "mtd_payment": mtd_data
    }

