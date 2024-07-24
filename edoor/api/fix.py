from edoor.api.generate_room_rate import generate_forecast_revenue
import frappe



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