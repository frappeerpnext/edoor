import frappe


@frappe.whitelist()
def get_summary_folio_transaction(property, cashier_shift=None ):
    sql = """
        select 
            parent_account_name,
            account_group_name,
            concat(account_code, ' - ',account_name) as account_name,
            sum(amount * if(type='Debit',1,-1)) as amount,
            sum(quantity) as quantity
        from `tabFolio Transaction` 
        where
            transaction_type = 'Reservation Folio'
        group by
            parent_account_name,
            account_group_name,
            account_name
        order by
            account_code_sort_order
    """
    