import frappe 
from frappe.utils import add_to_date
import copy
import time
from decimal import Decimal
import json
@frappe.whitelist()
def dome():
    start_time = time.time()
    data = {"reservation": "RS2024-0830", "reservation_stay": ["ST2024-4488", "ST2024-4509", "ST2024-4466", "ST2024-4449", "ST2024-4501", "ST2024-4500", "ST2024-4499", "ST2024-4477", "ST2024-4506", "ST2024-4446", "ST2024-4448", "ST2024-4450", "ST2024-4494", "ST2024-4470", "ST2024-4505", "ST2024-4454", "ST2024-4498", "ST2024-4458", "ST2024-4487", "ST2024-4508", "ST2024-4489", "ST2024-4452", "ST2024-4507", "ST2024-4510", "ST2024-4474", "ST2024-4445", "ST2024-4461", "ST2024-4490", "ST2024-4451", "ST2024-4460", "ST2024-4463", "ST2024-4480", "ST2024-4482", "ST2024-4484", "ST2024-4464", "ST2024-4503", "ST2024-4478", "ST2024-4493", "ST2024-4495", "ST2024-4455", "ST2024-4475", "ST2024-4481", "ST2024-4492", "ST2024-4453", "ST2024-4472", "ST2024-4457", "ST2024-4465", "ST2024-4496", "ST2024-4473", "ST2024-4456", "ST2024-4459", "ST2024-4476", "ST2024-4491", "ST2024-4486", "ST2024-4504", "ST2024-4447", "ST2024-4462", "ST2024-4483", "ST2024-4444", "ST2024-4479", "ST2024-4502", "ST2024-4485", "ST2024-4497", "ST2024-4471"]}
    
    stay_names =[d["name"] for d in  frappe.db.sql("select name from `tabReservation Stay` where reservation='RS2024-0830'",as_dict=1)]
    
 
    update_reservation_stay(stay_names)
  
    end_time = time.time()

    duration = end_time - start_time
    return("Duration:", duration, "seconds")


 
def update_reservation_stay(stay_names,run_commit=True):
    #1 update stay_room rate information like rate, tax, discount...
    sql = """
        UPDATE `tabReservation Stay Room` sr
        JOIN 
            (
            select 
                stay_room_id,
                MIN(CASE WHEN rate <> 0 THEN rate END) as rate,
                MIN(CASE WHEN input_rate <> 0 THEN input_rate END)   as input_rate,
                sum(total_rate)/count(name) as adr,
                sum(discount_amount) as discount_amount,
                sum(tax_1_amount) as tax_1_amount,
                sum(tax_2_amount) as tax_2_amount,
                sum(tax_3_amount) as tax_3_amount,
                sum(total_tax) as total_tax,
                sum(total_rate) as total_rate,
                max(is_complimentary) as is_complimentary,
                max(is_house_use) as is_house_use
                from `tabReservation Room Rate`
                where
                    reservation_stay in %(stay_names)s
                group by stay_room_id
            ) as a
        ON sr.name = a.stay_room_id
        SET 
            sr.input_rate = coalesce(a.input_rate,0), 
            sr.total_rate = coalesce(a.total_rate,0), 
            sr.rate = coalesce(a.rate,0), 
            sr.adr = coalesce(a.adr,0), 
            sr.discount_amount = coalesce(a.discount_amount,0), 
            sr.tax_1_amount = coalesce(a.tax_1_amount,0), 
            sr.tax_2_amount = coalesce(a.tax_2_amount,0), 
            sr.tax_3_amount = coalesce(a.tax_3_amount,0), 
            sr.total_tax = coalesce(a.total_tax,0)
        where
            sr.parent in %(stay_names)s
    """
 
    frappe.db.sql(sql,{"stay_names":stay_names})
    
    # update rate information to reseration stay
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
                max(is_complimentary) as is_complimentary,
                max(is_house_use) as is_house_use
            from `tabReservation Room Rate`
            where
                reservation_stay in %(stay_names)s
            group by reservation_stay
            ) as a
        ON st.name = a.reservation_stay
        SET 
            st.room_nights = coalesce(a.total_night,0), 
            st.room_rate = coalesce(a.rate,0), 
            st.adr = coalesce(a.adr,0), 
            st.total_discount= coalesce(a.discount_amount,0), 
            st.total_tax = coalesce(a.total_tax,0)
        where
            st.name in %(stay_names)s
    """
    frappe.db.sql(sql,{"stay_names":stay_names})
    
    #3 update credit debit and balance
    sql = """
        update `tabReservation Stay` s 
        LEFT JOIN (
            select  
                reservation_stay,
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit,
                sum(amount* (if(type='Debit',1,-1))) as balance
            from `tabFolio Transaction` 
            where
                reservation_stay in %(stay_names)s and 
                transaction_type = 'Reservation Folio'
            group by 
                reservation_stay 
        ) as a on s.name = a.reservation_stay
        SET
            s.total_debit = coalesce(a.debit,0),
            s.total_credit = coalesce(a.credit,0),
            s.balance = coalesce(a.balance,0)
            
        where
            s.name in %(stay_names)s
    """
    frappe.db.sql(sql,{"stay_names":stay_names})
    
    
    #03 update is complimentary and house use get form reservtion room rate list
    sql = """
        update `tabReservation Stay` s
        JOIN (
            select 
                reservation_stay,
                coalesce(max(is_complimentary),0) as is_complimentary, 
                coalesce(max(is_house_use),0) as is_house_use 
            from `tabReservation Room Rate`    
            where name in %(stay_names)s
            group by
            reservation_stay
        ) as a 
        ON s.name = a.reservation_stay
        SET 
            s.is_complimentary = a.is_complimentary,
            s.is_house_use = a.is_house_use
    """
    frappe.db.sql(sql,{"stay_names":stay_names})
    
    
    # update field like room type, is com, and is house from room rate to room occupy
    sql = """
        UPDATE `tabRoom Occupy` a
        JOIN (
            SELECT 
                reservation_stay, 
                rate_type,
                date,
                is_complimentary,
                is_house_use ,
                is_breakfast_include,
                adult,
                child
            FROM `tabReservation Room Rate` 
            WHERE reservation_stay IN %(stay_names)s
        ) AS b
        ON a.reservation_stay = b.reservation_stay AND a.date = b.date
        SET 
            a.rate_type = b.rate_type,
            a.is_complimentary = b.is_complimentary,
            a.is_house_use = b.is_house_use,
            a.is_breakfast_include = b.is_breakfast_include,
            a.adult=b.adult,
            a.child = b.child,
            a.pax = b.adult + b.child
    """
    frappe.db.sql(sql,{"stay_names":stay_names})
    
    # room occupy have row more thant room rate 1 record 
    # so we need to update last record of room occupy room type, is com, and is house  
    # from last record of reservation room rate group by reservatio stay

    sql ="""
        UPDATE `tabRoom Occupy` AS occ
        JOIN (
            SELECT 
                a.reservation_stay,
                DATE_ADD(MAX(rrr.date), INTERVAL 1 DAY) AS date,
                rrr.rate_type,
                rrr.is_complimentary,
                rrr.is_house_use,
                rrr.is_breakfast_include,
                rrr.adult,
                rrr.child
            FROM `tabReservation Room Rate` AS rrr
            JOIN (
                SELECT 
                    reservation_stay,
                    MAX(date) AS date
                FROM `tabReservation Room Rate`
                WHERE reservation_stay IN %(stay_names)s
                GROUP BY reservation_stay
            ) AS a ON rrr.date = a.date AND rrr.reservation_stay = a.reservation_stay
            GROUP BY a.reservation_stay
        ) AS b ON occ.reservation_stay = b.reservation_stay AND occ.date = b.date
        SET
            occ.rate_type = b.rate_type,
            occ.is_complimentary = b.is_complimentary,
            occ.is_house_use = b.is_house_use,
            occ.is_breakfast_include = b.is_breakfast_include,
            occ.adult = b.adult,
            occ.child = b.child,
            occ.pax = b.adult + b.child
        WHERE occ.reservation_stay IN %(stay_names)s;

    """
 
    frappe.db.sql(sql,{"stay_names":stay_names})
    if run_commit:
        frappe.db.commit()
   
