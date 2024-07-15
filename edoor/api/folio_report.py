import frappe
# {% set data = frappe.call("edoor.api.reservation.get_folio_transaction", 
# transaction_type="Reservation Folio" ,transaction_number=frappe.form_dict.get("folio")) %}
@frappe.whitelist()
def get_data_for_folio_transaction_detail(
        transaction_type="Reservation Folio",
        transaction_number="",
        reservation="",
        reservation_stay="",
        show_package_breakdown = 1,
        show_account_code = 1,
        show_all_room_rate = 0
    ):
    
    show_all_room_rate = int(show_all_room_rate or 0)
    show_package_breakdown = int(show_package_breakdown or 0)
    
    if show_account_code=="-1":
        show_account_code = frappe.get_cached_value("eDoor Setting",None,"show_account_code_in_folio_transaction")==1
    else:
        show_account_code = int(show_account_code)

    data = get_data_from_folio_transaction(
        reservation=reservation,
        reservation_stay= reservation_stay,
        transaction_type=transaction_type,
        transaction_number=transaction_number,
        show_package_breakdown=show_package_breakdown
    )
    if show_all_room_rate==1:
        data = data +  get_uncharge_data_from_revenue_forecast_breakdown(
                            reservation=reservation,
                            reservation_stay=reservation_stay,
                            transaction_number=transaction_number,
                            show_package_breakdown=show_package_breakdown
                        )
    
    data = sorted(data, key=lambda x: (x['posting_date'], x["account_code_sort_order"] ))
    
    balance = 0
    folio_transactions = []
    for d in data: 
        #this is main transaction
        amount = d["amount"]
        balance = balance + (amount * (1 if d["type"]=="Debit" else -1))        
        folio_transactions.append({ 
            "reservation":d["reservation"],
            "name":"" if d["is_package_charge"]==1 else d["name"],
            "room_number":d["room_number"],
            "account_name": "{}-{}".format(d["account_code"], d["report_description"] or d["account_name"])  if show_account_code else (d["report_description"] or d["account_name"]) ,
            "quantity": d["report_quantity"],
            "note":d["note"],
            "posting_date": d["posting_date"],
            "debit": amount  if d["type"] == 'Debit' else 0,
            "credit": amount  if d["type"] == 'Credit' else 0,
            "balance":balance,
            "owner":d["owner"],
            "modified_by":d["modified_by"],
            "creation":d["creation"],
            "show_print_preview":d["show_print_preview"],
            "print_format":d["print_format"],
            "is_auto_post":d["is_auto_post"],
            "total_amount":d["total_amount"],
            "sale":d["sale"],
            "tbl_number":d["tbl_number"],
            "is_package":d["is_package"]
        })
  
    return folio_transactions

def get_data_from_folio_transaction(
        transaction_type="Reservation Folio",
        transaction_number="",
        show_package_breakdown=1,
        reservation="",
        reservation_stay=""
    ):
     
    amount_field = 'total_amount'
    if show_package_breakdown==1:
        amount_field = 'transaction_amount'
        
    sql = """
        select 
            reservation,
            name,
            room_number,
            account_code,
            report_description,
            account_name,
            quantity,
            report_quantity,
            note,
            posting_date,
            {amount_field} as  amount,
            type,
            0 as balance,
            owner,
            modified_by,
            creation,
            show_print_preview,
            print_format,
            is_auto_post,
            total_amount,
            sale,
            tbl_number,
            is_package,
            is_package_charge,
            account_code_sort_order
        from `tabFolio Transaction`
        where
            is_base_transaction = 1 and 
            transaction_type = %(transaction_type)s and 
            transaction_number = %(transaction_number)s and 
            reservation = if(%(reservation)s='',reservation,%(reservation)s) and  
            reservation_stay= if(%(reservation_stay)s='',reservation_stay,%(reservation_stay)s) and  
            is_package_charge = if(%(show_package_breakdown)s=0,0, is_package_charge )
        
    """.format(
        amount_field = amount_field
    )
    
    data = frappe.db.sql(sql, {
                                "transaction_type":transaction_type,
                                "transaction_number":transaction_number,
                                "reservation":reservation,
                                "reservation_stay":reservation_stay,
                                "show_package_breakdown":show_package_breakdown
                            },as_dict=1)
    return data



def get_uncharge_data_from_revenue_forecast_breakdown(
    reservation="",
    reservation_stay="",
    transaction_number="",
    show_package_breakdown=0
):
    use_stay_room_ids = frappe.db.sql("select reservation_room_rate from `tabFolio Transaction` where reservation_stay='{reservation_stay}' and transaction_number='{transaction_number}' and  reservation_room_rate !='' ".format(reservation_stay=reservation_stay, transaction_number=transaction_number),as_dict=1)
    use_stay_room_ids = list(set([d["reservation_room_rate"] for d in use_stay_room_ids]))
    
    
    if not use_stay_room_ids:
        use_stay_room_ids.append("dummy")
        # we add this to prevent error when use in operator in sql statment
    
    
    amount_field = 'total_amount'
    if show_package_breakdown==1:
        amount_field = 'transaction_amount'

    sql = """
        select 
            a.reservation,
            a.name,
            a.room_number,
            a.account_code,
            b.account_name as report_description,
            b.account_name as account_name,
            a.quantity,
            a.quantity as report_quantity,
            '' as note,
            a.date as posting_date,
            {amount_field} as  amount,
            a.type,
            0 as balance,
            a.owner,
            a.modified_by,
            a.creation,
            '' as show_print_preview,
            '' as print_format,
            0 as is_auto_post,
            a.total_amount,
            '' as sale,
            '' as tbl_number,
            a.is_package,
            a.is_package_charge,
            b.sort_order as account_code_sort_order
        from `tabRevenue Forecast Breakdown` a 
            inner join `tabAccount Code` b on b.name = a.account_code
        where
            a.is_base_transaction = 1 and 
            reservation = if(%(reservation)s='',reservation,%(reservation)s) and  
            reservation_stay= if(%(reservation_stay)s='',reservation_stay,%(reservation_stay)s) and  
            is_package_charge = if(%(show_package_breakdown)s=0,0, is_package_charge ) and 
            room_rate_id not in %(room_rate_ids)s
        
    """.format(
        amount_field = amount_field
    )

    data = frappe.db.sql(sql, {
                               
                                "transaction_number":transaction_number,
                                "reservation":reservation,
                                "reservation_stay":reservation_stay,
                                "show_package_breakdown":show_package_breakdown,
                                "room_rate_ids":use_stay_room_ids
                            },as_dict=1)
    return data


@frappe.whitelist()
def get_folio_transaction_summary_amount(
    transaction_number , 
    show_package_breakdown=0,
    reservation_stay="",
    show_all_room_rate=1
    ):
    show_package_breakdown = int(show_package_breakdown or 0)

    summary_data =frappe.db.sql("""
        select 
            account_category,
            account_category_sort_order,
            sum(report_quantity) as quantity, 
            sum({amount_field} * if(type='Debit',1,-1)) as amount 
        from `tabFolio Transaction` 
        where 
            transaction_number = '{transaction_number}' and 
            is_base_transaction = 1 and 
            is_package_charge = if({show_package_breakdown}=0,0,is_package_charge) 
        group by 
            account_category 
        order by 
            account_category_sort_order
        """.format(
            show_package_breakdown = show_package_breakdown,
            amount_field = "total_amount" if show_package_breakdown == 0 else "transaction_amount",
            transaction_number = transaction_number
        ),as_dict=1)
    
    if int(show_all_room_rate) ==1:
        room_rate_summary = get_uncharge_room_rate_summary_amount_group_by_account_category(
            reservation_stay=reservation_stay,
            transaction_number=transaction_number,
            show_package_breakdown=show_package_breakdown
        )
       
        if room_rate_summary :
            for r in room_rate_summary:
                charge = [d for d in summary_data  if d["account_category"] == r["account_category"]]
                
                if charge:
                    
                    charge=charge[0]
                    charge["quantity"] = charge["quantity"] + r["quantity"]
                    charge["amount"] = charge["amount"] + r["amount"]
                else:
                    
                    summary_data.append(r)
                    
    summary_data = sorted(summary_data, key=lambda x: x['account_category_sort_order'])

    return  summary_data 




def get_uncharge_room_rate_summary_amount_group_by_account_category(
    reservation_stay="",
    transaction_number="",
    show_package_breakdown=1
):
    room_rate_ids = frappe.db.sql("select reservation_room_rate from `tabFolio Transaction` where reservation_stay='{reservation_stay}' and transaction_number='{transaction_number}' and reservation_room_rate!=''".format(reservation_stay=reservation_stay, transaction_number=transaction_number),as_dict=1)
    room_rate_ids = list(set([d["reservation_room_rate"] for d in room_rate_ids]))
    if not room_rate_ids:
        room_rate_ids.append("dummy")
        
    sql ="""
        select 
            a.account_category,
            c.sort_order as account_category_sort_order,
            sum(a.quantity) as quantity, 
            sum({amount_field} * if(a.type='Debit',1,-1)) as amount 
        from `tabRevenue Forecast Breakdown` a
            inner join `tabAccount Code` b on b.name = a.account_code 
            inner join `tabAccount Category` c on c.name = b.account_category
        where
            a.reservation_stay = '{reservation_stay}'  and 
            a.room_rate_id not in %(room_rate_ids)s and 
            a.is_base_transaction = 1 and 
            a.is_package_charge = if({show_package_breakdown}=1,a.is_package_charge, 0)
        group by
            a.account_category,
            c.sort_order
    """.format(
        reservation_stay=reservation_stay,
        amount_field ="transaction_amount" if show_package_breakdown ==1 else "total_amount" ,
        show_package_breakdown = show_package_breakdown
    )

    return  frappe.db.sql(sql,{"room_rate_ids":room_rate_ids},as_dict =1)


