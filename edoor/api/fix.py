from edoor.api.generate_room_rate import generate_forecast_revenue
import frappe
from edoor.api.utils import update_city_ledger



@frappe.whitelist()
def fix_update_account_code_show_hide_in_guest_folio_invoice():
    account_codes=[
        "10101",
        "10102",
        "10103",
        "50101",
        "50102"
        "50103"
        "50104",
        "10116"
    ]
    
    frappe.db.sql("update `tabAccount Code` set  hide_account_reservation_not_allow_see_rate= 1 where name in %(account_codes)s",{"account_codes":account_codes})
    
    frappe.db.commit()
    
@frappe.whitelist()
def fix_business_source_allow_see_room_rate():
    
    frappe.db.sql("update `tabBusiness Source` set show_room_rate_in_guest_folio =1")
    frappe.db.commit()
    
    
    
@frappe.whitelist()
def fix_update_total_room_charge_amount_and_total_other_charge_amount():
    sql = """
        update `tabReservation Stay` s 
        LEFT JOIN (
            select  
                source_reservation_stay,
                sum(if(parent_account_name = 'Room Charge' and is_base_transaction=1, total_amount * if(type='Debit',1,-1) , 0 )) as total_room_charge,
                sum(if(parent_account_name != 'Room Charge' and account_group_name ='Charge' and is_base_transaction=1, total_amount * if(type='Debit',1,-1) , 0 )) as total_other_charge
            from `tabFolio Transaction` 
            where
                transaction_type = 'Reservation Folio'
            group by 
                source_reservation_stay 
        ) as a on s.name = a.source_reservation_stay
        SET
            
            s.total_room_charge = coalesce(a.total_room_charge,0),
            s.total_other_charge = coalesce(a.total_other_charge,0)

    """
    frappe.db.sql(sql)
    
    stays = frappe.db.sql("select name from `tabReservation Stay`",as_dict=1)
    for s in stays:
        stay_names = [s["name"]]
        # stay_names = ["ST2024-1970"]
            
        use_room_rates = frappe.db.sql("select distinct reservation_room_rate from `tabFolio Transaction` where coalesce(reservation_room_rate,'') !='' and  transaction_type='Reservation Folio' and source_reservation_stay in %(stay_names)s", {"stay_names":stay_names},as_dict=1)
        if not use_room_rates:
            use_room_rates.append("dummy") # we use this for where statement in operator that not accepot empty array
        else:
            use_room_rates = [d["reservation_room_rate"] for d in use_room_rates]
        
         
        sql = """
            update `tabReservation Stay` s 
            LEFT JOIN (
                select  
                    reservation_stay,
                    sum(if(parent_account_name in ('Room Charge', 'Room Charge Discount','Room Charge Tax') and is_base_transaction=1, transaction_amount * if(type='Debit',1,-1) , 0 )) as total_room_charge,
                    sum(if(parent_account_name not in ('Room Charge', 'Room Charge Discount','Room Charge Tax') and account_group_name in ('Charge','Discount','Tax') and is_base_transaction=1, transaction_amount * if(type='Debit',1,-1) , 0 )) as total_other_charge
                from `tabRevenue Forecast Breakdown` 
                where
                    reservation_stay in %(stay_names)s  and 
                    room_rate_id not in %(use_room_rates)s
                group by 
                    reservation_stay 
            ) as a on s.name = a.reservation_stay
            SET
                s.total_room_charge = s.total_room_charge +  coalesce(a.total_room_charge,0),
                s.total_other_charge = s.total_other_charge  +  coalesce(a.total_other_charge,0)            
            where
                s.name in %(stay_names)s
        """
        frappe.db.sql(sql,{"stay_names":stay_names, "use_room_rates":use_room_rates})
    
    
    frappe.db.commit()


@frappe.whitelist()
def generate_revenue_forecast_breakdown():
    data = frappe.db.sql("select name from `tabReservation Stay` where is_active_reservation = 1",as_dict=1)
    for d in data:
        generate_forecast_revenue(stay_names=[d["name"]], run_commit=False)
    frappe.db.commit()

    return "done"
    
    
@frappe.whitelist()
def fix_revenue_forecast_breadown():
    # fix total sub package charger
    sql = """
         update `tabRevenue Forecast Breakdown` a
         join (
                select 
                parent_reference,
                sum(total_amount) as amount
                from `tabRevenue Forecast Breakdown` 
                where     
                    is_package_charge = 1 and 
                    is_base_transaction = 1
                group by parent_reference
         ) b 
         on a.name = b.parent_reference
         SET 
            a.total_sub_package_charge = b.amount
    """
    frappe.db.sql(sql)
    
    # 2 update total transaction amount
    sql ="""
        update `tabRevenue Forecast Breakdown` set transaction_amount = total_amount - coalesce(total_sub_package_charge,0)
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    
    
    return "done"
    #2 fix transaction_amount
    
@frappe.whitelist()
def fix_folio_transaction():
    # fix total sub package charger
    sql = """
         update `tabFolio Transaction` a
         join (
                select 
                parent_reference,
                sum(total_amount) as amount
                from `tabFolio Transaction` 
                where     
                    is_package_charge = 1 and 
                    is_base_transaction = 1
                group by parent_reference
         ) b 
         on a.name = b.parent_reference
         SET 
            a.total_sub_package_charge = b.amount
    """
    frappe.db.sql(sql)
    
    # 2 update total transaction amount
    sql ="""
        update `tabFolio Transaction` set transaction_amount = total_amount - coalesce(total_sub_package_charge,0)
    """
    frappe.db.sql(sql)

    # 4 update total transaction amount
    sql ="""
        update `tabFolio Transaction` set is_base_transaction = 1 where coalesce(parent_reference,'') = ''
    """
    frappe.db.sql(sql)
    
    # update reservation status to folio
    sql ="""
        update `tabFolio Transaction` a
        join `tabReservation Stay` b on b.name = a.reservation_stay
        set a.reservation_status = b.reservation_status,
            a.reservation_status_color = b.status_color

    """
    
    
    frappe.db.sql(sql)
    
    # update pax
    sql = """
        update `tabFolio Transaction` a 
        inner join `tabReservation Stay` rs on rs.name = a.reservation_stay
        Set
            a.adult= rs.adult,
            a.child=rs.child,
            a.total_pax = rs.pax
        where
            a.account_code = '10101' and 
            a.adult = 0 
    """
    frappe.db.commit()
    
    
    return "done"
    

# update stay
@frappe.whitelist()
def update_reservation_stay():
    # update stay that have room rate 0
    stays = frappe.db.sql("select name from `tabReservation Stay`")
    for s in stays:
        sql = """
            UPDATE `tabReservation Stay` st
            JOIN 
                (
                select 
                    reservation_stay,
                    count(name) as total_night,
                    MIN(CASE WHEN rate <> 0 THEN rate END) as rate,
                    MIN(CASE WHEN input_rate <> 0 THEN input_rate END)   as input_rate,
                    sum(total_rate)/count(name) as adr,
                    sum(discount_amount) as discount_amount,
                    sum(total_tax) as total_tax,
                    sum(total_rate) as total_amount
                from `tabReservation Room Rate`
                where
                    reservation_stay = %(stay)s
                group by reservation_stay
                ) as a
            ON st.name = a.reservation_stay
            SET 
                st.room_nights = coalesce(a.total_night,0), 
                st.room_rate = coalesce(a.input_rate,0), 
                st.adr = coalesce(a.adr,0), 
                st.total_discount= coalesce(a.discount_amount,0), 
                st.total_tax = coalesce(a.total_tax,0),
                st.total_amount =coalesce(a.total_amount,0)
            where
                st.name in %(stay)s
        """
        frappe.db.sql(sql,{"stay":s})
    frappe.db.commit()
    
    
    return "Done"
    
    
# update reservation
@frappe.whitelist()
def update_reservation():
    # update stay that have room rate 0
    stays = frappe.db.sql("select name from `tabReservation`")
  
    for s in stays:
        sql = """
            UPDATE `tabReservation` st
            JOIN 
                (
                select 
                    reservation,
                    count(name) as total_night,
                    sum(total_rate)/count(name) as adr,
                    sum(discount_amount) as discount_amount,
                    sum(total_tax) as total_tax,
                    sum(total_rate) as total_amount
                from `tabReservation Room Rate`
                where
                    reservation = %(reservation)s and 
                    is_active_reservation = 1
                group by reservation
                ) as a
            ON st.name = a.reservation
            SET 
                st.room_nights = coalesce(a.total_night,0), 
                st.adr = coalesce(a.adr,0), 
                st.total_discount= coalesce(a.discount_amount,0), 
                st.total_tax = coalesce(a.total_tax,0),
                st.total_amount =coalesce(a.total_amount,0)
            where
                st.name in %(reservation)s
        """
        frappe.db.sql(sql,{"reservation":s})
    frappe.db.commit()
    
    
    return "Done"
    

@frappe.whitelist()
def update_pax_to_room_occupy():
    sql ="""
        update `tabRoom Occupy` a
        join `tabReservation Stay` b on b.name = a.reservation_stay
        SET 
            a.adult = b.adult,
            a.child = b.child,
            a.pax = b.adult + b.child
        
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    return "done"

@frappe.whitelist()
def update_balance_to_city_ledger():
    sql="select name from `tabCity Ledger`"
    data = frappe.db.sql(sql,as_dict=1)
    for d in data:
        update_city_ledger(name= d["name"],run_commit=False, ignore_on_update= True, ignore_validate= True )    
    frappe.db.commit()
    return "done"
    
    
@frappe.whitelist()
def update_room_type_info_reservation():
    sql="""
        update `tabReservation Stay Room` a
        join `tabRoom` b on b.name = a.room_id
        set
            a.room_type_id = b.room_type_id,
            a.room_type = b.room_type,
            a.room_type_alias = b.room_type_alias
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    # update stay
    sql ="""
        update `tabReservation Stay` a 
        join (
           select 
                parent,
                GROUP_CONCAT(DISTINCT  room_number SEPARATOR ',') as rooms,
                GROUP_CONCAT(DISTINCT  room_type SEPARATOR ',') as room_types,
                GROUP_CONCAT(DISTINCT  room_type_alias SEPARATOR ',') as room_type_alias
                from `tabReservation Stay Room` 
            group by parent 
        ) b on b.parent = a.name
        set
            a.rooms = b.rooms,
            a.room_types = b.room_types,
            a.room_type_alias = b.room_type_alias
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    
    # update reservation
    sql ="""
        update `tabReservation` a 
        join (
           select 
                reservation,
                GROUP_CONCAT(DISTINCT  room_number SEPARATOR ',') as rooms,
                GROUP_CONCAT(DISTINCT  room_type SEPARATOR ',') as room_types,
                GROUP_CONCAT(DISTINCT  room_type_alias SEPARATOR ',') as room_type_alias
                from `tabReservation Stay Room` 
            group by reservation 
        ) b on b.reservation = a.name
        set
            a.room_numbers= b.rooms,
            a.room_types = b.room_types,
            a.room_type_alias = b.room_type_alias
    """
    frappe.db.sql(sql)
    frappe.db.commit()
    
    
    
