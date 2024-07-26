import secrets
import time
 
from edoor.api.folio_transaction import get_master_folio, post_charge_to_folio_afer_after_run_night_audit
from edoor.api.utils import get_date_range,add_room_charge_to_folio, get_months, validate_role,get_breakdown_package_charge_code,add_package_inclusion_charge_to_folio

import frappe
import datetime
import random
from datetime import datetime
from py_linq import Enumerable
from dateutil.relativedelta import relativedelta 
from frappe.utils import getdate,add_to_date
from frappe.desk.search import search_link
from frappe import _ 

@frappe.whitelist(methods="POST")
def search(doctypes=None, txt="" ,filters=None):
    search_tables = frappe.get_doc("eDoor Setting").search_table
    results = []
    
    if txt:
        
        for t in search_tables:
            if t.table_name in doctypes:
                search_fields = ["name"]
                for k in t.search_field.split(","):
                    search_fields.append("ifnull({}, ' ')".format(k))
                if len(search_fields)>0:
                    search_fields = ", ' ',".join(search_fields)
                
                return_fields = "name,modified"
                if t.return_fields:
                    return_fields = return_fields + "," + t.return_fields
                
                # default condition
                default_condition = ""
                if t.default_condition:
                    default_condition = " and " + t.default_condition

                sql = "select '{0}' as doctype, {1} from `tab{0}` where concat({2}) like %(txt)s {4} order by modified desc limit {3}".format(t.table_name,return_fields,search_fields,t.limit_result,default_condition)
        
                
                data = frappe.db.sql(sql,{"txt":"%{}%".format(txt)},as_dict=1)
                # frappe.throw(sql)
                results = results + data
                results.sort(key=lambda x: x.modified, reverse=True)
    else:
        for t in search_tables:
            if t.table_name in doctypes:
                search_fields = ["name"]
                for k in t.search_field.split(","):
                    search_fields.append("ifnull({}, ' ')".format(k))
                if len(search_fields)>0:
                    search_fields = ", ' ',".join(search_fields)
                
                return_fields = "name,modified"
                if t.return_fields:
                    return_fields = return_fields + "," + t.return_fields
                
                # default condition
                default_condition = ""
                if t.default_condition:
                    default_condition = " and " + t.default_condition

                sql = "select '{0}' as doctype, {1} from `tab{0}` where modified>=(NOW() - INTERVAL 1 HOUR) and concat({2}) like %(txt)s {4} order by modified desc limit {3}".format(t.table_name,return_fields,search_fields,t.limit_result,default_condition)
        
                
                data = frappe.db.sql(sql,{"txt":"%{}%".format(txt)},as_dict=1)
                results = results + data
                results.sort(key=lambda x: x.modified, reverse=True)

                # sql = "select '{0}' as doctype, {1} from `tab{0}` where modified>=(NOW() - INTERVAL 1 HOUR)  {3} order by modified desc limit {2}".format(t.table_name,return_fields,t.limit_result,default_condition)

    return results



@frappe.whitelist(allow_guest=True)
def test_socket():
    frappe.publish_realtime('test_socket', {'helo': 'world'})
    return "xx"

@frappe.whitelist(allow_guest=True)
def get_config_data():
    backend_port = frappe.db.get_default("backend_port")
    return {
        "backend_port":backend_port
    }

@frappe.whitelist()
def get_meta(doctype=None):
    data =  frappe.get_meta(doctype)
    return data


@frappe.whitelist()
def get_dashboard_data_by_timespan(property,timespan="today"):
    # time.sleep(3)
    working_day = get_working_day(property)
    data = None
    hk_status = get_house_keeping_status(property, working_day["date_working_day"])
    if timespan=="today":
        data =  get_dashboard_data(property=property, date=working_day['date_working_day'])
    elif timespan=="tomorrow":
        data =  get_dashboard_data(property=property, date=add_to_date(getdate(working_day['date_working_day']),days=1))
    else:
        data =  get_dashboard_data(property=property, date=add_to_date(getdate(working_day['date_working_day']),days=-1))
    data["housekeeping_status"] = hk_status
    return  data

# Get the current date
@frappe.whitelist()
def get_dashboard_data(property = None,date = None,room_type_id=None,include_reservation_by_business_source=0,include_reservation_by_room_type=0):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 

    if data:
        working_date = data[0]["date"]

    if not date:
        date = working_date 

    # get total_room
    sql = "select count(name) as total from `tabRoom` where property=%(property)s and room_type_id=if('{0}'='',room_type_id,'{0}')".format(room_type_id or '')
    data = frappe.db.sql(sql,{"property":property}, as_dict=1)
    total_room = 0
    if data:
        total_room = data[0]["total"] or 0

    #get total room occupy
    total_room_occupy = 0
    unassign_room = 0

    sql = """
        SELECT 
            count(name) AS `total_room_occupy`, 
            SUM(if(ifnull(room_id,'')='' and reservation_status in('Reserved', 'Confirmed'), 1, 0)) AS `unassign_room` 
        FROM `tabRoom Occupy` 
        WHERE 
            is_active = 1 and
            `date` = %(date)s AND 
            property = %(property)s and 
            type='Reservation' and 
            room_type_id=if('{0}'='',room_type_id,'{0}');
    """.format( room_type_id or '')
 

    #get all totoal unassign room

    total_unassign_room = frappe.db.sql("""
        select count(name) as total from `tabReservation Stay` 
        where name in (  
            SELECT 
              distinct  reservation_stay
            FROM `tabRoom Occupy` 
            WHERE 
                is_active= 1 and  
                `date` >= %(date)s AND 
                property = %(property)s and 
                type='Reservation' and 
                room_type_id=if('{0}'='',room_type_id,'{0}') and 
                ifnull(room_id,'') = ''
        ) and is_active_reservation = 1
        """.format( room_type_id or ''),{"property":property,"date":date}, as_dict =1)

    
    if total_unassign_room:
        total_unassign_room = total_unassign_room[0]["total"]
    else:
        total_unassign_room = 0
    
   
 
    
    room_operation = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)



    if room_operation:
        unassign_room = room_operation[0]["unassign_room"]
        total_room_occupy = room_operation[0]["total_room_occupy"]


    # get reservation stay
    #filter base on arrival date
    stay = []
    stay_sql = """SELECT
                    SUM(if(reservation_status = 'Cancelled' and arrival_date=%(date)s,1,0)) AS `total_cancelled`, 
                    SUM(if(reservation_status = 'Void' and arrival_date=%(date)s,1,0)) AS `total_void`
                FROM `tabReservation Stay` 
                WHERE  
                    name in (
                        select reservation_stay from `tabReservation Room Rate`
                        where
                            date = %(date)s and 
                            property = %(property)s and 
                            room_type_id = if('{0}'='',room_type_id,'{0}')
                    )  and
                    property = %(property)s;""".format(room_type_id or '')
    
    
    stay = frappe.db.sql(stay_sql,{"property":property,"date":date}, as_dict=1)
    
    #get data from occupy data 
    stay_sql = """SELECT

                    SUM(reservation_status = 'No Show' and is_active=1 and is_active_reservation=0) AS `total_no_show`, 
                    SUM( type='Reservation' and  is_active=1 and is_active_reservation=1 and is_arrival=1 and reservation_status in ('Reserved','Confirmed')) AS `arrival_remaining`,
                    sum( type='Reservation' and  is_active=1 and is_active_reservation=1 and is_arrival=1) AS `total_arrival`,
                    sum( type='Reservation' and  is_active=1 and is_active_reservation=1 and is_arrival=1 and reservation_type='GIT') AS `total_git_stay_arrival`,
                    sum( type='Reservation' and  is_active=1 and is_active_reservation=1 and is_arrival=1 and reservation_type='FIT') AS `total_fit_stay_arrival`,
                    sum( type='Reservation' and  is_active=1 and reservation_type='GIT') AS `total_git_stay`,
                    sum( type='Reservation' and  is_active=1 and reservation_type='FIT') AS `total_fit_stay`,

                    SUM( type='Reservation' and  is_active=1 and is_active_reservation=1 and is_arrival=1 and pick_up=1 ) AS `pick_up`,
                    SUM( type='Reservation' and   is_active_reservation=1 and drop_off=1 ) AS `drop_off`,
                    SUM( type='Reservation' and  is_active_reservation=1 and reservation_status = 'In-house' ) AS `total_in_house`,
                    SUM( type='Reservation' and  is_active_reservation=1 and is_stay_over=1 ) AS `total_stay_over`
                FROM `tabRoom Occupy` 
                WHERE  
                    date = %(date)s and 
                    property = %(property)s  and 
                    room_type_id = if('{0}'='',room_type_id,'{0}')
        """.format(room_type_id or '')

    stay =[stay[0] | frappe.db.sql(stay_sql,{"property":property,"date":date}, as_dict=1)[0]]
    
    # get today cancell by cannel date

    stay_sql = """SELECT 
                    SUM(if(a.reservation_status = 'No Show',1,0)) AS `today_no_show`, 
                    SUM(if(a.reservation_status = 'Cancelled',1,0)) AS `today_cancelled`, 
                    SUM(if(a.reservation_status = 'Void',1,0)) AS `today_void`
                FROM `tabReservation Stay` a
                    inner join `tabReservation Stay Room` b on b.parent = a.name
                    
                WHERE  
                    b.room_type_id = if('{0}'='',room_type_id,'{0}') and 
                    a.cancelled_date = %(date)s and 
                    a.property = %(property)s;""".format( room_type_id or '')
    
    
    stay =[stay[0] | frappe.db.sql(stay_sql,{"property":property,"date":date}, as_dict=1)[0]]

    #filter base on departure date
    stay_sql = """SELECT 
                    SUM(if(reservation_status in ('In-house','Reserved','Confirmed'),1,0)) AS `departure_remaining`,
                    sum(if(is_active_reservation = 1, 1, 0)) AS `total_departure`
                FROM `tabReservation Stay` 
                WHERE 
                     name in (
                        select reservation_stay from `tabRoom Occupy`
                        where
                            date = %(date)s and 
                            room_type_id = if('{0}'='',room_type_id,'{0}') and 
                            property=%(property)s and 
                            is_departure = 1 and 
                            is_active_reservation= 1

                    ) and 
                    
                    property = %(property)s;""".format(room_type_id or '')
    
 
    stay =[stay[0] | frappe.db.sql(stay_sql,{"property":property,"date":date}, as_dict=1)[0]]



    

    git_reservation_sql = """
                        select 
                            count(distinct reservation)   as total
                        from `tabReservation Stay`
                        where 
                            is_active_reservation=1 and 
                            reservation_status   in ('Reserved','Confirmed','In-house','Checked Out') and
                            reservation_type = 'GIT' and 
                            arrival_date = %(date)s and
                            property = %(property)s
                    """
    fit_reservation_sql = """
                        select 
                            count(distinct reservation)   as total
                        from `tabReservation Stay`
                        where 
                            is_active_reservation=1 and 
                            reservation_status   in ('Reserved','Confirmed','In-house','Checked Out') and
                            reservation_type = 'FIT' and 
                            arrival_date = %(date)s and
                            property = %(property)s
                    """
    daily_reservation_sql = """
                        select 
                            count(distinct reservation)   as total
                        from `tabReservation Stay`
                        where 
                            reservation_date = %(date)s and
                            property = %(property)s
                    """
    daily_reservation_stay_sql = """
                        select 
                            count( reservation)   as total
                        from `tabReservation Stay`
                        where 
                            reservation_date = %(date)s and
                            property = %(property)s
                    """ 
    in_house_guest = """
                        select 
                            count(reservation)   as total
                        from `tabReservation Stay`
                        where 
                            property = %(property)s and
                            reservation_status = 'In-house'
                    """    
    
    
    #count upcommintg note
    upcoming_note = frappe.db.sql("select count(name) as total  from `tabComment` where custom_is_note=1 and  custom_note_date>=%(date)s and custom_property=%(property)s",{"property":property,"date":date}, as_dict=1)
    
    #count desk folio
    desk_folio = frappe.db.sql("select count(name) as total  from `tabDesk Folio` where posting_date = %(date)s and property=%(property)s",{"property":property,"date":date}, as_dict=1)
    
    #get total room block 
    sql = "SELECT count(name) AS `total_room_block` FROM `tabRoom Occupy` WHERE `date` = %(date)s AND property = %(property)s and type='Block' and room_type_id = if('{0}'='',room_type_id,'{0}');".format(room_type_id or '')
    total_room_block = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)
    total_room_block = total_room_block[0]["total_room_block"] or 0
    
    vacant_room =  frappe.db.sql("""select count(name) as total_room from `tabRoom` where name not in (
            select 
                ifnull(room_id,'') 
            from `tabRoom Occupy` 
            where 
                is_active = 1 and
                is_departure = 0 and 
                `date` = %(date)s AND 
                room_type_id = if('{0}'='',room_type_id,'{0}') and 
                property = %(property)s
        ) and 
        room_type_id = if('{0}'='',room_type_id,'{0}')                      
        """.format(room_type_id or ''),{"property":property,"date":date},as_dict=1)
    
    if len(vacant_room)>0:
        vacant_room = vacant_room[0]["total_room"]
    else:
        vacant_room = 0
    occupancy = 0
    
    if int(frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")) ==1:

        occupancy = round( (total_room_occupy or 0)   / (total_room or 1) * 100,2)
    else:
        occupancy = round( (total_room_occupy or 0)  / ((total_room or 1) - total_room_block) * 100,2)
    
    reservation_by_business_source= []
    if include_reservation_by_business_source:
        reservation_by_business_source =  get_total_reservation_by_business_source(property, date, room_type_id)
    
    reservation_by_room_type= []
    if include_reservation_by_room_type:
        reservation_by_room_type =  get_total_reservation_by_room_type(property, date, room_type_id)

    return {
        "working_date":working_date,
        "total_room":total_room or 0,
        "total_room_occupy":total_room_occupy or 0,
        "total_room_vacant": vacant_room,
        "arrival":stay[0]["total_arrival"] or 0,
        "arrival_remaining": stay[0]["arrival_remaining"] or 0,
        "departure":stay[0]["total_departure"] or 0,
        "departure_remaining": stay[0]["departure_remaining"] or 0,
        "pick_up":stay[0]["pick_up"] or 0,
        "drop_off":stay[0]["drop_off"] or 0,
        "unassign_room":unassign_room or 0,
        "today_no_show":stay[0]["today_no_show"] or 0,
        "today_cancelled":stay[0]["today_cancelled"] or 0,
        "today_void":stay[0]["today_void"] or 0,
        "total_no_show":stay[0]["total_no_show"] or 0,
        "total_cancelled":stay[0]["total_cancelled"] or 0,
        "total_void":stay[0]["total_void"] or 0,
        "stay_over":stay[0]["total_stay_over"] or 0,
        "git_reservation_arrival": frappe.db.sql(git_reservation_sql,{"property":property, "date":date},as_dict=1)[0]["total"] or 0,
        "fit_reservation_arrival": frappe.db.sql(fit_reservation_sql,{"property":property, "date":date},as_dict=1)[0]["total"] or 0,
        "git_stay_arrival":stay[0]["total_git_stay_arrival"] or 0,
        "upcoming_note":upcoming_note[0]["total"] or 0,
        "desk_folio":desk_folio[0]["total"] or 0,
        "total_unassign_room":total_unassign_room,
        "total_room_block": total_room_block,
        "in_house": frappe.db.sql(in_house_guest,{"property":property, "date":date},as_dict=1)[0]["total"] or 0,
        "occupancy":occupancy,
        "fit_stay_arrival":stay[0]["total_fit_stay_arrival"] or 0,
        "total_git_stay":stay[0]["total_git_stay"] or 0,
        "total_fit_stay":stay[0]["total_fit_stay"] or 0,
        "daily_reservation": frappe.db.sql(daily_reservation_sql,{"property":property, "date":date},as_dict=1)[0]["total"] or 0 ,
        "daily_reservation_stay":frappe.db.sql(daily_reservation_stay_sql,{"property":property, "date":date},as_dict=1)[0]["total"] or 0 ,
        "reservation_by_business_source":reservation_by_business_source,
        "reservation_by_room_type":reservation_by_room_type,
        "total_in_house":stay[0]["total_in_house"] or 0,
    }

@frappe.whitelist()
def get_owner_dashboard_current_revenue_data(property = None,end_date = None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 
    
    if data:
        working_date = data[0]["date"]

    if not end_date:
        end_date = working_date
    day_end = get_day_end_summary_report(property, end_date)
    revenue_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as room_revenue 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date = %(date)s and
            flash_report_revenue_group in ('Room Charge')
        """
    today_revenue = frappe.db.sql(revenue_sql,{"property":property,"date":end_date}, as_dict=1)[0]["room_revenue"] or 0
    other_room_revenue_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as other_room_revenue 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date = %(date)s and
            flash_report_revenue_group in ('Other Room Revenue')
        """
    today_room_other_revenue = frappe.db.sql(other_room_revenue_sql,{"property":property,"date":end_date}, as_dict=1)[0]["other_room_revenue"] or 0
    other_revenue_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as other_revenue 
            from `tabFolio Transaction` 
            where 
            property= %(property)s and posting_date = %(date)s and
            flash_report_revenue_group in ('Other Revenue')
        """
    today_other_revenue = frappe.db.sql(other_revenue_sql,{"property":property,"date":end_date}, as_dict=1)[0]["other_revenue"] or 0

    payment_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as payment 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date = %(date)s and
            account_group_name in ('Payment & Refund')
        """
    today_payment = frappe.db.sql(payment_sql,{"property":property,"date":end_date}, as_dict=1)[0]["payment"] or 0

    exp_revenue_sql = "select sum(amount * if(type='Debit',1,-1)) as expected_revenue from `tabRevenue Forecast Breakdown` where property = %(property)s and date = %(date)s"
    today_exp_revenue = frappe.db.sql(exp_revenue_sql,{"property":property,"date":end_date}, as_dict=1)[0]["expected_revenue"] or 0
    expense_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as expense 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date = %(date)s and
            transaction_type = 'Payable Ledger'
        """
    today_expense = frappe.db.sql(expense_sql,{"property":property,"date":end_date}, as_dict=1)[0]["expense"] or 0
    total_rooms =frappe.db.count('Room', {'property': property, "disabled":0})
    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
    if calculate_room_occupancy_include_room_block==0:
        total_rooms = total_rooms - day_end['room_block'] 
    revpar = (today_revenue + today_room_other_revenue)/(1 if total_rooms==0 else total_rooms)
    exp_revpar = (today_exp_revenue)/(1 if total_rooms==0 else total_rooms)
    ##Get MTD Data

    start_date = getdate(end_date).replace(day=1)
    mtd_revenue_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as room_revenue 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date between '{}' and '{}' and
            flash_report_revenue_group in ('Room Charge')
        """.format(start_date ,end_date)
    mtd_room_revenue = frappe.db.sql(mtd_revenue_sql,{"property":property}, as_dict=1)[0]["room_revenue"] or 0
    mtd_other_room_revenue_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as other_room_revenue 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date between '{}' and '{}' and
            flash_report_revenue_group in ('Other Room Revenue')
        """.format(start_date,end_date)
    mtd_other_room_revenue = frappe.db.sql(mtd_other_room_revenue_sql,{'property':property}, as_dict=1)[0]["other_room_revenue"] or 0
    mtd_other_revenue_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as other_revenue 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date between '{}' and '{}' and
            flash_report_revenue_group in ('Other Revenue')
        """.format(start_date,end_date)
    mtd_other_revenue = frappe.db.sql(mtd_other_revenue_sql,{'property':property}, as_dict=1)[0]["other_revenue"] or 0

    mtd_payment_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as payment 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date between '{}' and '{}' and
            account_group_name in ('Payment & Refund')
        """.format(start_date,end_date)
    mtd_payment = frappe.db.sql(mtd_payment_sql, {'property':property},as_dict=1)[0]["payment"] or 0
    mtd_expense_sql = """select 
                sum(amount * if(type='Debit',1,-1)) as expense 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date between '{}' and '{}' and
            transaction_type = 'Payable Ledger'
        """.format(start_date,end_date)
    mtd_expense = frappe.db.sql(mtd_expense_sql,{'property':property}, as_dict=1)[0]["expense"] or 0

    sql = """select 
                sum(is_active=1 and type='Reservation') as total_room_sold ,
                sum(is_active=1 and type='Reservation' and is_complimentary=1) as total_complimentary_room ,
                sum(is_active=1 and type='Reservation' and is_house_use=1) as total_house_use_room ,
                sum(type='Block') as total_block
            from `tabRoom Occupy` 
            where 
            property=%(property)s and date between '{}' and '{}'  
        """.format( start_date,end_date)
    
    occupy_data = frappe.db.sql(sql,{'property':property},as_dict=1)
    calculate_adr_include_all_room_occupied = frappe.db.get_single_value("eDoor Setting", "calculate_adr_include_all_room_occupied")
    room_sold = 0
    complimentary = 0
    house_use = 0
    room_block = 0
    if len(occupy_data)>0:
        room_sold = occupy_data[0]["total_room_sold"] or 0
        complimentary = occupy_data[0]["total_complimentary_room"] or 0
        house_use = occupy_data[0]["total_house_use_room"] or 0
        room_block = occupy_data[0]["total_block"] or 0
    if calculate_adr_include_all_room_occupied == 1:
        mtd_adr = (mtd_room_revenue) / (1 if room_sold==0 else room_sold)
    else:
        mtd_adr = (mtd_room_revenue) / ((1 if room_sold==0 else room_sold) - (complimentary + house_use))
    #occupancy
    sql = "select sum(total_room) as total_room from `tabDaily Property Data` where property='{}' and date between '{}' and '{}'".format(property, start_date,end_date)
    mtd_total_room= frappe.db.sql(sql,as_dict=1)[0]["total_room"] or 0
    total_room = 0
    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
    if calculate_room_occupancy_include_room_block==0:
        total_room = mtd_total_room - room_block 
    mtd_revpar = (mtd_room_revenue + mtd_other_revenue)/(1 if total_room==0 else total_room or 0)

    
    return {
        "working_date":working_date,
        "room_revenue": today_revenue,
        "adr":day_end['adr'],
        "revpar":revpar,
        "other_room_revenue": today_room_other_revenue,
        "other_revenue": today_other_revenue,
        "today_payment": today_payment,
        "today_exp_revenue": today_exp_revenue,
        "today_exp_adr": today_exp_revenue/(1 if day_end['room_night']==0 else day_end['room_night']) or 0,
        "today_exp_revpar":exp_revpar,
        "today_expense": today_expense,
        "total_room":total_room,
        "room_block":room_block,
        "room_sold":room_sold,
        "mtd_room_revenue":mtd_room_revenue,
        "mtd_adr":mtd_adr,
        "mtd_revpar":mtd_revpar,
        "mtd_other_room_revenue":mtd_other_room_revenue,
        "mtd_other_revenue":mtd_other_revenue,
        "mtd_payment":mtd_payment,
        "mtd_expense":mtd_expense,
        "end_day":day_end,
        
    }
@frappe.whitelist()
def get_chart_list_data(property=None,date=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 
    
    if data:
        working_date = data[0]["date"]

    if not date:
        date = working_date
    #payment breakdown
    sql="""
            select 
                sum(amount) as payment ,
                account_code,
                account_name 
            from `tabFolio Transaction` 
            where 
                property = %(property)s and
                posting_date = %(date)s and
                account_group_name in ('Payment & Refund')
            group by
                account_code,account_name
        """
    payment_breakdown = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)

    # Charge List
    charge_sql="""
            select 
                sum(amount) as charge ,
                parent_account_name
            from `tabFolio Transaction`
            where 
                property = %(property)s and
                posting_date = %(date)s and
                account_group_name in ('Charge')
            group by
                parent_account_name
        """
    charge_list = frappe.db.sql(charge_sql,{"property":property,"date":date}, as_dict=1)

    # Business Source List
    sql="""
            select 
                sum(amount * if(type='Debit',1,-1)) as amount,
                business_source
            from `tabFolio Transaction`
            where 
                property = %(property)s and
                posting_date = %(date)s and
                business_source != ''
            group by
                business_source
        """
    business_source_list = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    return {
        "payment_breakdown":payment_breakdown,
        "charge_list":charge_list,
        "business_source":business_source_list
    }
@frappe.whitelist()
def get_paymet_chart_data(property=None,date=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 

    if data:
        working_date = data[0]["date"]

    if not date :
        date = working_date
    sql="""
            select 
                sum(amount) as payment ,
                account_code,
                account_name 
            from `tabFolio Transaction` 
            where 
                property = %(property)s and
                posting_date = %(date)s and
                account_group_name in ('Payment & Refund')
            group by
                account_code,account_name
        """
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    chart_data = {
            "labels":[d['account_name'] for d in data],
            "datasets":[d['payment'] for d in data]
            # "colors": ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    }
    colors = ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    chart_data["datasets"] = []

    for i, d in enumerate(data):
        dataset = {
            "type": 'pie',
            "name": d['account_name'],
            "values": d['payment'],
            "color": colors[i % len(colors)]
        }
        chart_data["datasets"].append(dataset)
  
    return chart_data
@frappe.whitelist()
def get_charge_chart_data(property=None,date=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 

    if data:
        working_date = data[0]["date"]

    if not date :
        date = working_date
    sql="""
            select 
                sum(amount) as charge ,
                parent_account_name
            from `tabFolio Transaction`
            where 
                property = %(property)s and
                posting_date = %(date)s and
                account_group_name in ('Charge')
            group by
                parent_account_name
        """
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    chart_data = {
            "labels":[d['parent_account_name'] for d in data],
            "datasets":[d['charge'] for d in data],
            
    }
    colors = ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    chart_data["datasets"] = []

    for i, d in enumerate(data):
        dataset = {
            "type": 'bar',
            "name": d['parent_account_name'],
            "values": d['charge'],
            "color": colors[i % len(colors)]
        }
        chart_data["datasets"].append(dataset)
  
    return chart_data
@frappe.whitelist()
def get_f_and_b_chart_data(property=None,date=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 

    if data:
        working_date = data[0]["date"]

    if not date :
        date = working_date
    sql="""
            select 
                sum(amount) as charge ,
                parent_account_name
            from `tabFolio Transaction`
            where 
                property = %(property)s and
                posting_date = %(date)s and
                account_group_name in ('Charge')
            group by
                parent_account_name
        """
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    chart_data = {
            "labels":[d['parent_account_name'] for d in data],
            "datasets":[d['charge'] for d in data],
            
    }
    colors = ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    chart_data["datasets"] = []

    for i, d in enumerate(data):
        dataset = {
            "type": 'bar',
            "name": d['parent_account_name'],
            "values": d['charge'],
            "color": colors[i % len(colors)]
        }
        chart_data["datasets"].append(dataset)
  
    return chart_data
@frappe.whitelist()
def get_business_source_chart_data(property=None,date=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 

    if data:
        working_date = data[0]["date"]

    if not date :
        date = working_date
    sql="""
            select 
                sum(amount * if(type='Debit',1,-1)) as amount,
                business_source
            from `tabFolio Transaction`
            where 
                property = %(property)s and
                posting_date = %(date)s and
                coalesce(business_source,'') !=''
            group by
                business_source
        """
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    epx_sql="""
            select 
                sum(amount * if(type='Debit',1,-1)) as amount,
                business_source
            from `tabRevenue Forecast Breakdown`
            where 
                property = %(property)s and
                date = %(date)s and
                coalesce(business_source,'') !=''
            group by
                business_source
        """
    epx_data = frappe.db.sql(epx_sql,{"property":property,"date":date}, as_dict=1)
    chart_data = {
            "labels":[d['business_source'] for d in data]
            # "colors": ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    }
    colors = ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    chart_data["datasets_actual"] = []

    for i, d in enumerate(data):
        datasets_actual = {
            "type": 'pie',
            "name": d['business_source'],
            "values": d['amount'],
            "color": colors[i % len(colors)]
        }
        chart_data["datasets_actual"].append(datasets_actual)

    chart_data["datasets_expected"] = []
    for i, d in enumerate(epx_data):
        datasets_expected = {
            "type": 'pie',
            "name": d['business_source'],
            "values": d['amount'],
            "color": colors[i % len(colors)]
        }
        chart_data["datasets_expected"].append(datasets_expected)
  
    return chart_data
@frappe.whitelist()
def get_owner_dashboard_current_mount_chart(property=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 
    currency_precision = frappe.db.get_single_value("System Settings","currency_precision")
    working_day = get_working_day(property)
    now = getdate(working_day["date_working_day"])
    start_date = getdate( datetime(now.year, now.month, 1))
    end_date = getdate( now + relativedelta(day=1, months=1, days=-1))
    group_by_field =  "date"
    group_by_field_actual =  "posting_date"
    series_label =  [{"series_label":getdate(d)} for d in  get_date_range(start_date, end_date, False)]
    forcast_revenue_sql = "select {0} as group_by, sum(amount * if(type='Debit',1,-1)) as forcast_revenue from `tabRevenue Forecast Breakdown` where property = %(property)s and date between %(start_date)s and %(end_date)s group by {0}"    
    forcast_data = frappe.db.sql(forcast_revenue_sql.format(group_by_field),{"property":property,"start_date":start_date,"end_date":end_date},as_dict=1)
    actual_revenue_sql = """select 
                {0} as group_by,
                sum(amount * if(type='Debit',1,-1)) as actual_revenue 
            from `tabFolio Transaction` 
            where 
            property=%(property)s and posting_date between %(start_date)s and %(end_date)s
            group by
                {0}
        """.format(group_by_field_actual)
    actual_data = frappe.db.sql(actual_revenue_sql,{"property":property,"start_date":start_date,"end_date":end_date}, as_dict=1)
    actual_revenue = []
    forcast_revenue = []
    for d in series_label:
        actual_revenue.append(sum([x["actual_revenue"] for x in actual_data if x["group_by"] == d["series_label"]]))
        forcast_revenue.append(sum([x["forcast_revenue"] for x in forcast_data if x["group_by"] == d["series_label"]]))
    chart_data = {
            "labels":[getdate(x["series_label"]).strftime('%d/%b') for x in series_label]
            # "colors": ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    }
    colors = ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    chart_data["datasets"] = []

    datasets_actual = {
        "chartType": 'bar',
        "name": 'Actual Revenue',
        "values": actual_revenue,
        "colors":'#306ec5',
    }
    chart_data["datasets"].append(datasets_actual)

    datasets_forcast = {
        "chartType": 'bar',
        "name": 'Forcast Revenue',
        "values": forcast_revenue,
        "colors":'#e0453a',
    }
    chart_data["datasets"].append(datasets_forcast)
  
    return chart_data
@frappe.whitelist()
def get_room_type_chart_data(property=None,date=None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = %(property)s limit 1",{"property":property},as_dict=1)
    working_date =  frappe.utils.today() 

    if data:
        working_date = data[0]["date"]

    if not date :
        date = working_date
    sql="""
            select 
                sum(amount * if(type='Debit',1,-1)) as amount,
                room_type
            from `tabFolio Transaction`
            where 
                property = %(property)s and
                posting_date = %(date)s and
                room_type != '' and
                flash_report_revenue_group in ('Room Charge')
            group by
                room_type
        """
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    epx_sql="""
            select 
                sum(amount * if(type='Debit',1,-1)) as amount,
                room_type
            from `tabRevenue Forecast Breakdown`
            where 
                property = %(property)s and
                date = %(date)s and
                room_type != ''
            group by
                room_type
        """
    epx_data = frappe.db.sql(epx_sql,{"property":property,"date":date}, as_dict=1)

    #get total room in each room type
    sql = """
            select 
            count(name) as total_room, 
            room_type 
        from `tabRoom` 
        where 
            property = %(property)s and
            disabled != 1 
        group by room_type        
        """.format(property)
    room_type = frappe.db.sql(sql,{"property":property}, as_dict=1)
    sql = """
            select 
                count(room_id) as total_room_sold,
                room_type 
            from `tabRoom Occupy` 
            where 
                property = %(property)s and
                date=%(date)s and 
                is_departure = 0 
            group by room_type      
        """
    room_sold = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    chart_data = {
            "labels":[d['room_type'] for d in data]
            # "colors": ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    }
    colors = ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    chart_data["datasets_actual"] = []
  
    for i, d in enumerate(data):
        total_room = [g['total_room'] for g in room_type if g['room_type'] == d['room_type']][0]
        total_room_sold = [g['total_room_sold'] for g in room_sold if g['room_type'] == d['room_type']][0]
        datasets_actual = {
            "name": d['room_type'],
            "values": d['amount'],
            "total_room":total_room,
            "room_sold":total_room_sold,
            "color": colors[i % len(colors)]
        }
        chart_data["datasets_actual"].append(datasets_actual)

    chart_data["datasets_expected"] = []
    for i, d in enumerate(epx_data):
        total_room = [g['total_room'] for g in room_type if g['room_type'] == d['room_type']][0]
        total_room_sold = [g['total_room_sold'] for g in room_sold if g['room_type'] == d['room_type']][0]
        datasets_expected = {
            "type": 'pie',
            "name": d['room_type'],
            "values": d['amount'],
            "total_room":total_room,
            "room_sold":total_room_sold,
            "color": colors[i % len(colors)]
        }
        chart_data["datasets_expected"].append(datasets_expected)
  
    return chart_data
def get_total_reservation_by_business_source(property = None ,date =None,room_type=None):
 
    return   frappe.db.sql("""select 
                            business_source, 
                            count(name) as total 
                         from `tabRoom Occupy`
                         where
                            property = %(property)s and 
                            date = %(date)s and 
                            room_type_id = if(coalesce(%(room_type_id)s,'')='', room_type_id,%(room_type_id)s) and 
                            is_active=1 and 
                            type='Reservation'
                        group by business_source    
                         """, {
                             "property":property,
                             "date":date,
                             "room_type_id":room_type or ""
                         },as_dict =1)

def get_total_reservation_by_room_type(property = None ,date =None,room_type=None):
 
    return   frappe.db.sql("""select 
                            room_type_id,
                            room_type, 
                            count(name) as total 
                         from `tabRoom Occupy`
                         where
                            property = %(property)s and 
                            date = %(date)s and 
                            room_type_id = if(coalesce(%(room_type_id)s,'')='', room_type_id,%(room_type_id)s) and 
                            is_active=1 and 
                            type='Reservation'
                        group by 
                           room_type_id,
                            room_type   
                         """, {
                             "property":property,
                             "date":date,
                             "room_type_id":room_type or ""
                         },as_dict =1)

@frappe.whitelist()
def get_daily_property_data_detail(property=None, date=None, room_type=None):
    filter = {"property":property, "date":date, "room_type":room_type or ""}
    # arrival
    arrival_guest = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            room_rate_discount,
            status_color
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_arrival = 1 and 
                    c.is_active=1 and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)

    # stay over guest
    stay_over = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            status_color,
            room_rate_discount
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_stay_over = 1 and 
                    c.is_active=1 and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)
    # departure guest
    departure = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            status_color,
            room_rate_discount
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_departure = 1 and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)
    # unassign room
    unassign_room = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            status_color
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_active = 1   and 
                    coalesce(c.room_id,'') = '' and 
                    c.is_active_reservation = 1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)
    # pickup drop off
    pickup_drop_off = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            pickup_time as time,
            arrival_mode as mode,
            arrival_flight_number as flight_number,
            pickup_location as location,
            pickup_driver as driver,
            pickup_driver_name as driver_name,
            pickup_driver_phone_number as driver_phone_number,
            pickup_note as note,
            'Pickup' as type
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_active = 1   and 
                    c.is_active_reservation = 1 and 
                    c.pick_up=1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)
    drop_off = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            drop_off_time as time,
            departure_mode as mode,
            departure_flight_number as flight_number,
            drop_off_location as location,
            drop_off_driver as driver,
            drop_off_driver_name as driver_name,
            drop_off_driver_phone_number as driver_phone_number,
            drop_off_note as note,
            'Drop Off' as type
        from `tabReservation Stay`
        where
            name in (
                select distinct c.reservation_stay from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_active_reservation = 1 and 
                    c.drop_off=1
            ) and 
            property = %(property)s
    """,filter, as_dict=1)

    pickup_drop_off = pickup_drop_off + drop_off


    inactive_reservation = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            status_color,
            cancelled_date,
            cancelled_by,
            cancelled_note,
            is_reserved_room
        from `tabReservation Stay`
        where
            property = %(property)s and 
            is_active_reservation = 0 and 
            name in (
            select distinct c.reservation_stay from `tabRoom Occupy` c
            where
                c.date = %(date)s and 
                c.property = %(property)s and 
                c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                c.is_active_reservation = 0
            )
    """,filter, as_dict=1)
    #get cancell and void by today obly
    cancelled_void_and_no_show = frappe.db.sql("""
        select 
            reservation,
            name,
            reference_number,
            adult,
            child,
            reservation_type,
            reservation_date,
            arrival_date,
            departure_date,
            room_nights,
            rooms,
            room_type_alias,
            guest,
            guest_name,
            business_source,
            adr,
            total_amount as total_room_rate,
            reservation_status,
            status_color,
            cancelled_date,
            cancelled_by,
            cancelled_note,
            is_reserved_room
        from `tabReservation Stay`
        where
            property = %(property)s and 
            is_active_reservation = 0 and
            reservation_status in ('Cancelled','Void','No Show') and 
            cancelled_date =%(date)s and 
            name in (
                select distinct c.parent from `tabReservation Stay Room` c
                where
                    %(date)s between start_date and end_date and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.is_active_reservation = 0 and 
                    c.reservation_status in ('Cancelled','Void','No Show') 
            )
    """,filter, as_dict=1)

    cancelled_void_and_no_show = [d for d in cancelled_void_and_no_show if d["is_reserved_room"]==0]



    #if room type is set 
    
    if room_type: 
        filter["parents"] = [d["name"] for d in inactive_reservation]
        sql = """
            select 
                distinct parent 
            from `tabReservation Stay Room` 
            where 
                room_type_id=%(room_type)s  
        """
        if  'parent' in filter and  len(filter["parent"])>0:
            sql = sql + " and parent in %(parents)s "

        stay_name_list = frappe.db.sql(sql,filter, as_dict=1)
        
        inactive_reservation = [d for d in inactive_reservation if d["name"] in [x["parent"] for x in stay_name_list]]
        

    #room block 
    room_block = frappe.db.sql("""
        select 
           name,
            block_date,
            start_date,
            end_date,
            total_night_count,
            is_unblock,
            room_number,
            room_type,
            reason,
            owner

        from `tabRoom Block`
        where
            name in (
                select distinct stay_room_id from `tabRoom Occupy` c
                where
                    c.date = %(date)s and 
                    c.property = %(property)s and 
                    c.room_type_id = if(%(room_type)s='',c.room_type_id,%(room_type)s) and 
                    c.type='Block' 
            ) and 
            property = %(property)s and 
            room_type_id =  if(%(room_type)s='',room_type_id,%(room_type)s) 
    """,filter, as_dict=1)
    data = {
        "arrival": arrival_guest,
        "stay_over": stay_over,
        "departure":departure,
        "unassign_room":unassign_room,
        "pickup_drop_off":pickup_drop_off,
        "inactive_reservation":inactive_reservation,
        "room_block":room_block,
        "cancelled_void_and_no_show":cancelled_void_and_no_show
    }

    return data




@frappe.whitelist()
def get_daily_property_summary():
    property = frappe.defaults.get_user_default("business_branch")
    
    if not property:
        data = frappe.db.get_list("Business Branch")
        if len(data)>0:
            property = data[0].name
    if property:
        working_day = get_working_day(property)
        if working_day:
            date = working_day["date_working_day"] 
            if not date:
                date = frappe.utils.today()
            doc = frappe.get_doc("Business Branch",property)
            
            data =  get_dashboard_data(property, date)
            data["property"] = doc.name
            data["property_code"] = doc.property_code or ""
            data["photo"] = doc.photo 
            data["property_background_banner"] = doc.property_background_banner 
            data["phone_number"] = doc.phone_number_1 or ""
            data["province"] = doc.province or ""
            data["address"] = doc.address_en or ""
            data["pattern_background"] = doc.pattern_background or ""
            return data


    return {}
            



@frappe.whitelist()
def get_daily_summary_by_room_type(property = None,date = None,room_type_id=None):
    sql="select room_type_id,room_type,room_type_alias, count(name) as total_room from `tabRoom` where disabled = 0 group by room_type_id order by room_type_id,room_type,room_type_alias"


    data =  frappe.db.sql(sql,as_dict=1)
    sql="""
        select 
            room_type_id,
            sum(type='Reservation' and is_active =1 ) as total_room_sold,
            sum(if(type='Reservation' and  is_active =1 and  is_active_reservation = 1,adult,0) ) as adult,
            sum(if(type='Reservation' and is_active =1 and  is_active_reservation = 1 ,child,0) ) as child,
            sum(type='Reservation' and is_active=1  and reservation_type='FIT') as fit,
            sum(type='Reservation' and is_active=1  and reservation_type='GIT') as git,
            sum(type='Reservation' and is_active=1 and is_active_reservation=1 and pick_up=1) as pick_up,
            sum(type='Reservation' and is_active_reservation=1  and is_departure=1 and drop_off=1) as drop_off,
            sum(type='Reservation' and is_active = 1 and is_active_reservation = 1 and is_arrival=1) as arrival,
            sum(type='Reservation' and is_active=1 and  is_arrival=1 and is_active_reservation = 1 and reservation_status in ('In-house','Checked Out') ) as checked_in,
            sum(type='Reservation' and is_active=1 and is_active_reservation = 1 and is_stay_over = 1) as stay_over,
            sum(type='Reservation' and is_active_reservation = 1 and is_departure=1 ) as departure,
            sum(type='Reservation' and is_active_reservation = 1 and is_departure=1 and reservation_status='Checked Out' ) as checked_out ,
            sum(type='Reservation' and is_active=1  and reservation_status='No Show' ) as no_show ,
            sum(type='Reservation' and is_active=1 and reservation_status='Void' ) as void ,
            sum(is_departure=0 and reservation_status='Cancelled' ) as cancelled ,
            sum(type='Block') as block ,
            0 as adr,
            0 as total_rate
        from `tabRoom Occupy`
        WHERE 
            `date` = %(date)s AND 
            property = %(property)s and 
            is_active=1 and 
            room_type_id=if('{0}'='',room_type_id,'{0}')
        group by
            room_type_id
    """.format(room_type_id or '') 

    occupy_data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    
    #get room rate 
    sql="""
        select 
            room_type_id,
            sum(total_rate) as total_rate
        from `tabReservation Room Rate`
        WHERE 
            is_active = 1 and 
            `date` = %(date)s AND 
            property = %(property)s and 
            room_type_id=if('{0}'='',room_type_id,'{0}')
        group by
            room_type,
            room_type_id,
            room_type_alias
    """.format( room_type_id or '')
    room_rate_data = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)


    calculate_room_occupancy_include_room_block = int(frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block"))

    for d in data:
        d["total_room_sold"] = sum([r["total_room_sold"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["adult"] = sum([r["adult"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["child"] = sum([r["child"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["git"] = sum([r["git"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["fit"] = sum([r["fit"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["pick_up"] = sum([r["pick_up"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["drop_off"] = sum([r["drop_off"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["arrival"] = sum([r["arrival"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["checked_in"] = sum([r["checked_in"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["stay_over"] = sum([r["stay_over"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["departure"] = sum([r["departure"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["checked_out"] = sum([r["checked_out"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["no_show"] = sum([r["no_show"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["void"] = sum([r["void"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["cancelled"] = sum([(r["cancelled"] if r["cancelled"] is not None else 0) for r in occupy_data if r["room_type_id"] == d["room_type_id"]])
        d["block"] = sum([r["block"] for r in occupy_data if r["room_type_id"] == d["room_type_id"]]) or 0

        d["total_rate"] = sum([r["total_rate"] for r in room_rate_data if r["room_type_id"] == d["room_type_id"]]) or 0
        d["adr"] = d["total_rate"] /  (d["total_room_sold"] if d["total_room_sold"] > 0 else 1) 

        total_room = d["total_room"] 
        if  calculate_room_occupancy_include_room_block==0:
            total_room = total_room - d["block"]
        if total_room==0:
            total_room = 1
        d["occupancy_room"] = total_room #we use this field to calculate occupancy 
        d["occupancy"] = round(  d["total_room_sold"] / total_room * 100, 2)
    return data


@frappe.whitelist()
def get_daily_summary_by_business_source(property = None,date = None,room_type_id=None):
    
    data =  []
    sql="""
        select 
            business_source,
            sum(type='Reservation' and is_active =1 ) as total_room_sold,
            sum(if(type='Reservation' and  is_active =1 and  is_active_reservation = 1,adult,0) ) as adult,
            sum(if(type='Reservation' and is_active =1 and  is_active_reservation = 1 ,child,0) ) as child,
            sum(type='Reservation' and is_active=1 and  reservation_type='FIT') as fit,
            sum(type='Reservation' and is_active=1 and  reservation_type='GIT') as git,
            sum(type='Reservation' and is_active=1 and is_active_reservation=1 and pick_up=1) as pick_up,
            sum(type='Reservation' and is_active_reservation=1  and is_departure=1 and drop_off=1) as drop_off,
            sum(type='Reservation' and is_active = 1 and is_active_reservation = 1 and is_arrival=1) as arrival,
            sum(type='Reservation' and is_active=1 and is_arrival=1 and is_active_reservation = 1 and reservation_status in ('In-house','Checked Out') ) as checked_in,
            sum(type='Reservation' and is_active=1 and is_active_reservation = 1 and is_stay_over = 1) as stay_over,
            sum(type='Reservation' and is_active_reservation = 1 and is_departure=1 ) as departure,
            sum(type='Reservation' and is_active_reservation = 1 and is_departure=1 and reservation_status='Checked Out' ) as checked_out ,
            sum(type='Reservation' and is_active=1  and reservation_status='No Show' ) as no_show ,
            sum(type='Reservation' and is_active=1 and reservation_status='Void' ) as void ,
            sum(is_departure=0 and reservation_status='Cancelled' ) as cancelled ,
            0 as adr,
            0 as total_rate
        from `tabRoom Occupy`
        WHERE 
            `date` = %(date)s AND 
            property = %(property)s and 
            type='Reservation' and
            is_active=1 and 
            room_type_id=if('{0}'='',room_type_id,'{0}')
        group by
            business_source
    """.format(room_type_id or '') 

    
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    
    #get room rate 
    sql="""
        select 
            business_source,
            sum(total_rate) as total_rate
        from `tabReservation Room Rate`
        WHERE 
            is_active = 1 and 
            `date` = %(date)s AND 
            property = %(property)s and 
            room_type_id=if('{0}'='',room_type_id,'{0}')
        group by
           business_source
    """.format( room_type_id or '')
    room_rate_data = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)


    calculate_room_occupancy_include_room_block = int(frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block"))
    #get total room from daily property data 
    sql = "select sum(total_room) as total from `tabDaily Property Data` where  `date` = %(date)s AND property = %(property)s and room_type_id=if('{0}'='',room_type_id,'{0}')"
    total_rooms  = frappe.db.sql(sql.format( room_type_id or ''),{"property":property,"date":date},as_dict=1)[0]["total"]
    
    #get total room block
    sql = "select count(name) as total from `tabRoom Occupy` where type='Block' and  `date` = %(date)s AND property = %(property)s and room_type_id=if('{0}'='',room_type_id,'{0}')"
    room_block  = frappe.db.sql(sql.format( room_type_id or ''),{"property":property,"date":date},as_dict=1)[0]["total"]
    
    for d in data:
        d["total_room"] = total_rooms
        
        d["total_rate"] = sum([r["total_rate"] for r in room_rate_data if r["business_source"] == d["business_source"]]) or 0
        d["adr"] = d["total_rate"] /  (d["total_room_sold"] if d["total_room_sold"] > 0 else 1) 
        d["block"] = room_block
        total_room = d["total_room"] 
        if  calculate_room_occupancy_include_room_block==0:
            total_room = total_room - d["block"]
        if total_room==0:
            total_room = 1
        d["occupancy_room"] = total_room #we use this field to calculate occupancy 
        d["occupancy"] = round(  d["total_room_sold"] / total_room * 100, 2)

    return data


@frappe.whitelist()
def get_daily_summary_by_reservation_type(property = None,date = None,room_type_id=None):
    
    data =  []
    sql="""
        select 
            reservation_type,
            sum(type='Reservation' and is_active =1 ) as total_room_sold,
            sum(if(type='Reservation' and  is_active =1 and  is_active_reservation = 1,adult,0) ) as adult,
            sum(if(type='Reservation' and is_active =1 and  is_active_reservation = 1 ,child,0) ) as child,
            sum(type='Reservation' and is_active=1 and reservation_type='FIT') as fit,
            sum(type='Reservation' and is_active=1 and reservation_type='GIT') as git,
            sum(type='Reservation' and is_active=1 and is_active_reservation=1 and pick_up=1) as pick_up,
            sum(type='Reservation' and is_active_reservation=1  and is_departure=1 and drop_off=1) as drop_off,
            sum(type='Reservation' and is_active = 1 and is_active_reservation = 1 and is_arrival=1) as arrival,
            sum(type='Reservation' and is_active=1 and  is_arrival=1 and is_active_reservation = 1 and reservation_status in ('In-house','Checked Out') ) as checked_in,
            sum(type='Reservation' and is_active=1 and is_active_reservation = 1 and is_stay_over = 1) as stay_over,
            sum(type='Reservation' and is_active_reservation = 1 and is_departure=1 ) as departure,
            sum(type='Reservation' and is_active_reservation = 1 and is_departure=1 and reservation_status='Checked Out' ) as checked_out ,
            sum(type='Reservation' and is_active=1  and reservation_status='No Show' ) as no_show ,
            sum(type='Reservation' and is_active=1 and reservation_status='Void' ) as void ,
            sum(is_departure=0 and reservation_status='Cancelled' ) as cancelled ,
            0 as adr,
            0 as total_rate
        from `tabRoom Occupy`
        WHERE 
            `date` = %(date)s AND 
            property = %(property)s and 
            type='Reservation' and 
            is_active=1 and 
            room_type_id=if('{0}'='',room_type_id,'{0}')
        group by
            reservation_type
    """.format( room_type_id or '') 

    
    data = frappe.db.sql(sql,{"property":property,"date":date}, as_dict=1)
    
    #get room rate 
    sql="""
        select 
            reservation_type,
            sum(total_rate) as total_rate
        from `tabReservation Room Rate`
        WHERE 
            is_active = 1 and 
            `date` = %(date)s AND 
            property = %(property)s and 
            room_type_id=if('{0}'='',room_type_id,'{0}')
        group by
           reservation_type
    """.format(room_type_id or '')
    room_rate_data = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)


    calculate_room_occupancy_include_room_block = int(frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block"))
    #get total room from daily property data 
    sql = "select sum(total_room) as total from `tabDaily Property Data` where  `date` = %(date)s AND property = %(property)s and room_type_id=if('{0}'='',room_type_id,'{0}')"
    total_rooms  = frappe.db.sql(sql.format( room_type_id or ''),{"property":property,"date":date},as_dict=1)[0]["total"]
        
    #get total room block
    sql = "select count(name) as total from `tabRoom Occupy` where type='Block' and  `date` = %(date)s AND property = %(property)s and room_type_id=if('{0}'='',room_type_id,'{0}')"
    room_block  = frappe.db.sql(sql.format(  room_type_id or ''),{"property":property,"date":date},as_dict=1)[0]["total"]
    

    for d in data:
        d["total_room"] = total_rooms
        d["total_rate"] = sum([r["total_rate"] for r in room_rate_data if r["reservation_type"] == d["reservation_type"]]) or 0
        d["adr"] = d["total_rate"] /  (d["total_room_sold"] if d["total_room_sold"] > 0 else 1) 

        d["block"] = room_block
        total_room = d["total_room"] 
        if  calculate_room_occupancy_include_room_block==0:
            total_room = total_room - d["block"]
        if total_room==0:
            total_room = 1
        d["occupancy_room"] = total_room #we use this field to calculate occupancy 
        d["occupancy"] = round(  d["total_room_sold"] / total_room * 100, 2)

    return data



@frappe.whitelist()
def get_house_keeping_status(property, working_day):
    #get house keeping status
    hk_data = frappe.db.get_list("Housekeeping Status",fields=["*"],  order_by='sort_order asc')
    housekeeping_status = []
    for d in hk_data:
        total  = frappe.db.sql("select count(name) as total from `tabRoom` where property=%(property)s and housekeeping_status='{}'".format(d.name),{"property":property},as_dict=1)[0]["total"] or 0
        
        total_room_block  = frappe.db.sql("select count(name) as total from `tabRoom Block` where property=%(property)s and end_date >= %(end_date)s and is_unblock = 0 and docstatus = 1",{"property":property,"end_date":working_day},as_dict=1)[0]["total"] or 0

        housekeeping_status.append({
            "status":d.name,
            "color":d.status_color,
            "icon":d.icon,
            "total":total,
            "is_block_room":d.is_block_room,
            "total_block_room":total_room_block
        })
 

    return housekeeping_status

@frappe.whitelist()
def get_mtd_room_occupany(property,duration_type="Daily", view_chart_by="Time Series",show_occupancy_only=False,view_chart_type="line"):
    working_day = get_working_day(property)

    now = getdate(working_day["date_working_day"])

    start_date = getdate( datetime(now.year, now.month, 1))

    end_date = getdate( now + relativedelta(day=1, months=1, days=-1))
    group_by_field =  "date"
    if duration_type=="Daily":
        group_by_field = "date"
    else:
        start_date = datetime(now.year,1, 1)
        end_date = add_to_date(start_date, years=1,days=-1)
       
        group_by_field = "monthname(date)"
    months= get_months(start_date,end_date)

    series_label =[]
     #get series label
    if view_chart_by=="Time Series":
        if duration_type=="Daily":
            series_label =  [{"series_label":getdate(d)} for d in  get_date_range(start_date, end_date, False)]
        else:
            series_label =  [{'series_label': 'January'},
                            {'series_label': 'February'},
                            {'series_label': 'March'},
                            {'series_label': 'April'},
                            {'series_label': 'May'},
                            {'series_label': 'June'},
                            {'series_label': 'July'},
                            {'series_label': 'August'},
                            {'series_label': 'September'},
                            {'series_label': 'October'},
                            {'series_label': 'November'},
                            {'series_label': 'December'}]

    elif view_chart_by =="Business Source":
        group_by_field = "business_source"
        series_label =  frappe.db.sql("select distinct business_source as series_label from  `tabRoom Occupy` where property='{}' and  date between '{}' and '{}' and ifnull(business_source,'') !=''  order by business_source".format(property, start_date, end_date),as_dict=1)

    elif view_chart_by =="Room Type":
        group_by_field = "room_type"
        series_label =  frappe.db.sql("select distinct room_type_id, room_type as series_label from  `tabRoom Occupy` where property='{}' and  date between '{}' and '{}' order by room_type".format(property, start_date, end_date),as_dict=1)
       
        

    sql = """select 
                {0} as group_by, 
                sum(type='Reservation' and  is_active=1) as  total ,
                sum(type='Reservation' and is_arrival=1 and is_active = 1  and is_active_reservation=1) as  arrival ,
                sum(type='Reservation' and is_departure=1 and is_active_reservation=1) as  departure ,
                sum(type='Reservation' and is_stay_over = 1 and is_active_reservation=1) as  stay_over ,
                sum(type='Reservation' and is_active = 1 and is_active_reservation=0 and reservation_status='No Show') as  no_show ,
                sum(type='Block') as  block 
            from `tabRoom Occupy` where property=%(property)s and date between '{1}' and '{2}'  group by {0} """
    
    data = frappe.db.sql(sql.format(group_by_field, start_date,end_date),{"property":property},as_dict=1) 
 
    
    occupancy_data = []
    arrival_data = []
    departure_data = []
    stay_over_data = []
    block_data = []
    no_show_data = []
    calculate_room_occupancy_include_room_block = int(frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block"))
    #get total room by room type
    total_rooms_list= []
    if view_chart_by == "Room Type":
        total_rooms_list = frappe.db.sql("select room_type_id ,sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between '{}' and '{}' group by room_type_id".format( start_date,end_date),{"property":property}, as_dict=1)
    elif view_chart_by == "Time Series":
        if duration_type=="Daily":
            total_rooms_list = frappe.db.sql("select date ,sum(total_room) as total_room from `tabDaily Property Data` where property=%(property)s and date between '{}' and '{}' group by date".format( start_date,end_date),{"property":property}, as_dict=1)
        else:
            total_rooms_list = frappe.db.sql("select date_format(date,'%M') as date ,sum(total_room) as total_room from `tabDaily Property Data` where property='{}' and date between '{}' and '{}' group by date_format(date,'%M')".format(property, start_date,end_date), as_dict=1)

    elif view_chart_by == "Business Source":
        total_rooms_list =  frappe.db.sql("select sum(total_room) as total_room from `tabDaily Property Data` where property='{}' and date between '{}' and '{}'".format(property, start_date,end_date), as_dict=1)
         


    for d in series_label:
        occupancy = sum([x["total"] for x in data if x["group_by"] == d["series_label"]])
        block= sum([x["block"] for x in data if x["group_by"] == d["series_label"]])
        
        #check if duration tyope is monthly then we set total room = total room x total day of month

        total_rooms = 0
        if view_chart_by=="Time Series":
            total_rooms = sum([x["total_room"]  for x in total_rooms_list if str(x["date"]) == str(d["series_label"])])
        elif view_chart_by=='Room Type':
            total_rooms =sum([x["total_room"]  for x in total_rooms_list if x["room_type_id"] == d["room_type_id"]])
        elif  view_chart_by=='Business Source':
           
            total_rooms = sum([x["total_room"] for x in total_rooms_list])
        
        if  calculate_room_occupancy_include_room_block==1:
          
            occupancy = round(occupancy /  total_rooms * 100,2)
           
        else:
            
            occupancy =round( occupancy /   (total_rooms - (block or 0))  * 100,2)
        
        occupancy_data.append(occupancy or 0.00)
 
        if int(show_occupancy_only)==0:
            arrival_data.append(sum([x["arrival"] for x in data if x["group_by"] == d["series_label"]]))
            departure_data.append(sum([x["departure"] for x in data if x["group_by"] == d["series_label"]]))
            stay_over_data.append(sum([x["stay_over"] for x in data if x["group_by"] == d["series_label"]]))
            block_data.append(sum([x["block"] for x in data if x["group_by"] == d["series_label"]]))
            no_show_data.append(sum([x["no_show"] for x in data if x["group_by"] == d["series_label"]]))

    chart_data = {
            "labels":[getdate(x["series_label"]).strftime('%d/%b') for x in series_label] if view_chart_by=="Time Series" and duration_type=="Daily" else [x["series_label"] for x in series_label],
            "datasets":[]
            # "colors": ['#f7e7a9', '#d1a4ff', '#f5b3b3', '#c8e6c9', '#f2d8d8', '#c5e1a5', '#f0f4c3', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#ffccbc', '#dcedc8', '#ffe0b2', '#b3e5fc', '#ffcdd2', '#d7ccc8', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#f0f4c3', '#dcedc8', '#ffcdd2', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c', '#b2ebf2', '#f5b3b3', '#d1a4ff', '#f7e7a9', '#c5e1a5', '#f2d8d8', '#b3e5fc', '#ffe0b2', '#dcedc8', '#ffcdd2', '#fff9c4', '#e0f7fa', '#ffebee', '#c8e6c9', '#ffecb3', '#d7ccc8', '#b2dfdb', '#e6ee9c','#000000','#000080','#00008B','#0000CD','#0000FF','#006400','#008000','#008080','#008B8B','#00BFFF','#00CED1','#00FA9A','#00FF00','#00FF7F','#00FFFF','#191970','#1E90FF','#20B2AA','#228B22','#240F04','#27408B','#282828','#292421','#292D44','#2980B9','#29AB87','#29C4A9','#29C4AF','#29C4C5','#29C4D0','#29C4F0','#29C4F1','#29C4F3','#29C4F4']
    }
    if int(show_occupancy_only)==0:
        
        chart_data["datasets"] =[
                {
                    "chartType": 'bar',
                    "name": _('Room Block'),
                    "values": block_data,
                },
                {
                    "chartType": 'bar',
                    "name": _('No-Show'),
                    "values": no_show_data,
                },

                {
                    "chartType": 'bar',
                    "name": _('Departure'),
                    "values": departure_data,
                },
                {
                    "chartType": 'bar',
                    "name": _('Stay Over'),
                    "values": stay_over_data,
                },
                {
                    "chartType": 'bar',
                    "name": _('Arrival'),
                    "values": arrival_data,
                },
            

        ]
    chart_data["datasets"].append({
                "chartType": "line" if int(show_occupancy_only)==0 else  view_chart_type,
                "name": _('Occupancy') + ' (%)',
                "values": occupancy_data,
                
    })
  
    return chart_data
   


@frappe.whitelist(allow_guest=True)
def get_server_port():
    return{"backend_port": frappe.get_doc('ePOS Settings').backend_port}

@frappe.whitelist()
def get_report():
    x = frappe.db.get_list("System Report")
    return x


@frappe.whitelist(allow_guest=True)
def get_edoor_setting(property = None):

    edoor_menus = frappe.db.get_list("eDoor Menu", fields=["name","parent_edoor_menu", "is_group", "menu_name","menu_text","icon",'move_to_more','sub_menu_icon'],filters={"name":["!=","All Menus"]},order_by="sort_order asc")
    
    currency = frappe.get_doc("Currency",frappe.db.get_single_value("ePOS Settings","currency"))
    second_currency = frappe.get_doc("Currency",frappe.db.get_single_value("ePOS Settings","second_currency"))
 
    
    housekeeping_status = frappe.get_list("Housekeeping Status",filters={"is_block_room":0}, fields=['status','status_color','icon','sort_order','is_room_occupy'],  order_by='sort_order asc')
    housekeeping_status_code = frappe.get_list("Housekeeping Status Code", fields=['status'],ignore_permissions = True )

    reservation_status = frappe.get_list("Reservation Status", fields=['reservation_status','name','color','is_active_reservation','show_in_reservation_list','show_in_room_chart','sort_order',"allow_reinstate"],  order_by='sort_order asc')
    
    edoor_setting_doc = frappe.get_doc("eDoor Setting")
     
    epos_setting = frappe.get_doc('ePOS Settings')
    custom_print_format = frappe.db.sql("select   print_format as name, custom_print_format as print_format from `tabCustom Print Format` where (ifnull(property,'')='' or property=%(property)s) and ifnull(attach_to_doctype,'')!='' and ifnull(custom_print_format,'')!=''",{"property":property},as_dict=1)
    


    edoor_setting  =  {
        "edoor_menu": edoor_menus,
        "folio_transaction_style_credit_debit":edoor_setting_doc.folio_transaction_style_credit_debit,
        "guest_ledger_report_name":edoor_setting_doc.guest_ledger_report_name,
        "guest_ledger_transaction_report":edoor_setting_doc.guest_ledger_transaction_report,
        "city_ledger_report_name":edoor_setting_doc.city_ledger_report_name,
        "allow_user_to_add_back_date_transaction":edoor_setting_doc.allow_user_to_add_back_date_transaction,
        "role_for_back_date_transaction":edoor_setting_doc.role_for_back_date_transaction,
        "show_account_code_in_folio_transaction":edoor_setting_doc.show_account_code_in_folio_transaction,
        "enable_over_booking":edoor_setting_doc.enable_over_booking,
        "backend_port":epos_setting.backend_port,
        "room_conflict_background_color":edoor_setting_doc.room_conflict_background_color,
        "run_night_audit_role":edoor_setting_doc.run_night_audit_role,
        "custom_print_format":custom_print_format,
        "powered_by_text": edoor_setting_doc.powered_by_text,
        "calculate_room_occupancy_include_room_block": edoor_setting_doc.calculate_room_occupancy_include_room_block,
        "search_table": [{"doctype":d.table_name,"title":d.title,"template":d.template} for d in edoor_setting_doc.search_table],
        "room_block_color":edoor_setting_doc.room_block_color,
        "show_additional_guest_name_in_room_chart_calendar":edoor_setting_doc.show_additional_guest_name_in_room_chart_calendar,
        "help_url":edoor_setting_doc.help_url,
        "default_folio_print_format":edoor_setting_doc.default_folio_print_format,
        "room_chart_calendear_slot_duration":edoor_setting_doc.room_chart_calendear_slot_duration,
        
        "currency":{
            "name":currency.name,
            "locale":currency.custom_locale,
            "precision":  currency.custom_currency_precision,
            "symbol": currency.symbol,
            "pos_currency_format": currency.custom_pos_currency_format
        },
        "second_currency":{
            "name":second_currency.name,
            "locale":second_currency.custom_locale,
            "precision":  second_currency.custom_currency_precision,
            "symbol": second_currency.symbol,
            "pos_currency_format": second_currency.custom_pos_currency_format
        },
        "housekeeping_status":housekeeping_status,
        "housekeeping_status_code":housekeeping_status_code,
        'reservation_status':reservation_status
    }

    
    
    user = get_logged_user()
    if not property:
        if len(user["property"])==1:
            property = user["property"][0]["name"]

            
    if not frappe.db.exists("Business Branch", property):
        return {"user":user,"property":"Invalid Property", "edoor_setting":edoor_setting}
     
 
    working_day = None 
     
    if property:
        working_day = get_working_day(property)
    else:
        if len(user["property"])==1:
             
             working_day = get_working_day(user["property"][0]["name"])
 

    property = frappe.get_doc("Business Branch", property)
    
    if  not property.default_pos_profile:
        frappe.throw("Please assign default pos profile to your current property")

    edoor_setting["property"] = {
        "name":property.name,
        "property_code":property.property_code,
        "province":property.province,
        "address_en":property.address_en,
        "address_kh":property.address_kh,
        "phone_number_1":property.phone_number_1,
        "phone_number_2":property.phone_number_1,
        "pos_profile":property.default_pos_profile,
        "default_letter_head":property.default_letter_head,
        "default_walk_in_business_source":property.default_walk_in_business_source,
        "edoor_letterhead":[d.letterhead for d in property.edoor_letterhead],
        "allow_generate_tax_invoice":property.allow_generate_tax_invoice
    }


    pos_profile = frappe.get_doc("POS Profile",property.default_pos_profile)
    
    edoor_setting["pos_profile"] = {
        "name":pos_profile.name,
        "stock_location":pos_profile.stock_location,
        "price_rule":pos_profile.price_rule
    }
    pos_config = frappe.get_doc("POS Config", pos_profile.pos_config)
    edoor_setting["payment_type"] = pos_config.payment_type
    edoor_setting["account_group"] = frappe.db.get_list("Account Code", filters={"parent_account_code":"All Account Code"},fields=["name","account_name","show_in_shortcut_menu","icon","is_city_ledger_account","is_guest_folio_account","is_guest_desk_folio_account","is_deposit_ledger_account","show_in_guest_folio","show_in_desk_folio","show_in_city_ledger","show_in_deposit_ledger","show_in_payable_ledger"], order_by="sort_order")

    
    frappe.enqueue("edoor.api.schedule_task.ten_minute_job",queue='short')
    
 

    return {
        "user":get_logged_user(),
        "working_day": working_day,
        "edoor_setting":edoor_setting,
         
    }

@frappe.whitelist()
def get_logged_user():
    data = frappe.get_doc('User',frappe.session.user)
 
    property = frappe.get_list("Business Branch",fields=["name","property_code","province","email","phone_number_1","photo"])
        # can see rate role 
    
    can_see_rate_role = frappe.db.get_single_value("eDoor Setting","can_see_rate_and_amount_role")
    roles = frappe.get_roles(frappe.session.user)
    
    return {
        "name":data.name,
        "full_name":data.full_name,
        "role":data.role_profile_name,
        "phone_number":data.phone,
        "photo":data.user_image,
        "property":property,
        "roles":roles,
        "can_view_rate": True if can_see_rate_role in roles else False, 
        "language":data.language
    }

@frappe.whitelist()
def get_room_chart_data(property,group_by,start_date,end_date):
    return []


@frappe.whitelist()
def get_working_day(property = ''):
    
    working_day = frappe.db.sql("select  posting_date as date,name,pos_profile from `tabWorking Day` where business_branch = %(property)s  order by posting_date desc, creation desc limit 1",{"property":property},as_dict=1)

    cashier_shift = None
    
    if len(working_day)>0:
        data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = %(property)s and working_day='{}' and pos_profile='{}' and is_closed =0 and is_edoor_shift =1  ORDER BY posting_date desc, creation desc limit 1".format(working_day[0]["name"],working_day[0]["pos_profile"]),{"property":property},as_dict=1)
    
        
        if len(data)>0:
            cashier_shift = data[0]


    return {
        "date_working_day": working_day[0]["date"] if len(working_day)>0 else '',
        "name":working_day[0]["name"] if len(working_day)>0 else '',
        "cashier_shift":cashier_shift,
        "stock_location": frappe.db.get_value("POS Profile", working_day[0]["pos_profile"] if len(working_day)>0 else '',"stock_location")
    }



@frappe.whitelist()
def get_room_chart_resource_and_event(property, start=None,end=None, keyword=None,view_type=None,business_source="",room_type="",room_type_group=None,room_number=None,floor=None,building=None):
    return {
        "resources": get_room_chart_resource(
            property=property,
            room_type_group = room_type_group,
            room_type = room_type,
            room_number = room_number,
            floor=floor,
            building=building,
            view_type=view_type
        ),
        "events":get_room_chart_calendar_event(
                property=property, 
                start=start,
                end=end, 
                keyword=keyword,
                view_type=view_type,
                business_source=business_source,
                room_type=room_type,
                room_type_group=room_type_group,
                room_number=room_number,
                floor=floor,
                building=building
            ),
        
    }

def get_conflict_room(filter):
    sql="""
        select 
            distinct
            room_id  
        from `tabTemp Room Occupy` 
        where
            is_departure = 0 and
            ifnull(room_id,'') <> '' and 
            property = %(property)s and 
            date between %(start)s and %(end)s and 
            room_type_id = if(%(room_type_id)s='',room_type_id, %(room_type_id)s) and 
            ifnull(floor,'') = if(%(floor)s='',ifnull(floor,''), %(floor)s) and 
            ifnull(building,'') = if(%(building)s='',ifnull(building,''), %(building)s) and 
            room_type_id in (select name from `tabRoom Type` where room_type_group=if(%(room_type_group)s='',room_type_group,%(room_type_group)s)) 
        group by date, room_id
        having count(name)>1
        """

 
    data = frappe.db.sql(sql,filter, as_dict=1)
    return [d["room_id"] for d in data]


@frappe.whitelist()
def get_room_chart_resource(property = '',room_type_group = '', room_type = '',room_number = "",floor="", building = '', view_type='room_type'):
     
    resources = []
    #set first resource = summary by for current property
    total_room = frappe.db.sql("select count(name) as total_room from `tabRoom` where property=%(property)s",{"property":property}, as_dict=1)
    resources.append({
        "id":"property_summary",
        "title":property,
        "sort_order":-1000,
        "alias":"",
        "type":"property_summary",
        "total_room": 0 if  not total_room else total_room[0]["total_room"]
    })    

    filters = ""
    if room_number:
        filters = filters + " AND `room_number` like '%%{}%%'".format(room_number)
    if building:
        filters = filters + " AND building = '{}'".format(building)
    if floor:
        filters = filters + " AND floor = '{}'".format(floor)
    if room_type_group:
        filters = filters + " AND room_type_group = '{}'".format(room_type_group)
    if view_type == 'room_type':
        filter_room_type = ""
        if room_type:
            filter_room_type = filter_room_type + " AND name = '{}'".format(room_type)
        if room_type_group:
            filter_room_type = filter_room_type + " AND room_type_group = '{}'".format(room_type_group)
        
        if room_number:
            filter_room_type = filter_room_type + " AND rt.name in (select room_type_id from `tabRoom` where room_number like '%%{}%%')".format(room_number or '')

        
        sql = """
            select 
            name,
            room_type,
            sort_order,
            alias,
            coalesce(room_type_color,'#FFFFFF') as room_type_color,
            (select count(name) from `tabRoom` where room_type_id=rt.name) as total_room
            from 
                `tabRoom Type` rt
            where 
                rt.name in (select room_type_id from `tabRoom` where building=if(%(building)s="",building,%(building)s)) and
                rt.name in (select room_type_id from `tabRoom` where floor=if(%(floor)s="",floor,%(floor)s)) and
                
                property=%(property)s {0}
            
        """
        sql=sql.format(filter_room_type)      
        
        

        filter = {
            "building":building or "",
            "floor":floor or "",
            "property":property
        }
        room_types = frappe.db.sql(sql,filter, as_dict=1)
        
         
        for t in room_types:
            rooms = frappe.db.sql("select name as id,coalesce(room_type_color,'#FFFFFF') as room_type_color, room_number as title, sort_order, housekeeping_status,status_color,housekeeping_icon, 'room' as type,room_type_id, room_type,room_type_alias from `tabRoom` where room_type_id='{0}' and property=%(property)s and disabled = 0 {1}   order by room_number".format(t["name"], filters),{"property":property},as_dict=1)
            resources.append({
                "id":t["name"],
                "room_type_color":t["room_type_color"],
                "title":t["room_type"],
                "sort_order":t["sort_order"],
                "alias":t["alias"],
                "type":"room_type",
                "total_room": t["total_room"],
                "children": rooms
            })
    else:
        resources = resources +  frappe.db.sql("select name as id,coalesce(room_type_color,'#FFFFFF') as room_type_color,room_type,room_type_alias, room_type_id, room_number as title,sort_order, housekeeping_status,status_color,housekeeping_icon, 'room' as type,room_type_id, room_type from `tabRoom` where property=%(property)s and  disabled = 0 {0} {1} order by room_number".format(  filters, ("AND room_type_id = '{}'".format(room_type) if room_type else "")),{"property":property},as_dict=1)
    


    return resources
 


@frappe.whitelist()
def get_room_inventory_resource(property = ''):
    
    resources = []

    resources = frappe.db.sql("select name as id,room_type as title,alias,(select count(name) from `tabRoom` where room_type_id=t.name) as total_room ,sort_order from `tabRoom Type` t where property=%(property)s order by sort_order",{'property':property},as_dict=1)
    
    resources.append({
        "id": "vacant_room",
        "title": "Vacant Room",
        "sort_order":1000
    })
    
    resources.append({
        "id": "occupany",
        "title": "Occupancy",
        "sort_order":1001
    })
  
    resources.append({
        "id": "out_of_order",
        "title": "Out of Order",
        "sort_order":1002
    })
    
    resources.append({
        "id": "arrival",
        "title": "Arrival",
        "sort_order":1003
    })
    resources.append({
        "id": "stay_over",
        "title": "Stay Over",
        "sort_order":1004
    })
    
    resources.append({
        "id": "departure",
        "title": "Departure",
        "sort_order":1005
    })

    resources.append({
        "id": "pax",
        "title": "Pax(A/C)",
        "sort_order":1006
    })
    resources.append({
        "id": "dummy",
        "title": " ",
        "sort_order":1007
    })


    return resources
 

@frappe.whitelist()
def get_room_chart_calendar_event(property, start=None,end=None, keyword=None,view_type=None,business_source="",room_type="",room_type_group=None,room_number=None,floor=None,building=None):
    slot_duration = frappe.db.get_single_value("eDoor Setting","room_chart_calendear_slot_duration")
    
    events = []   
    sql = """
        select 
            name as id, 
            room_id as resourceId,
            room_id,
            room_type_id,
            room_type,
            room_type_alias,
            room_number,
            concat(start_date,'T','{0}') as start ,
            concat(end_date,'T','{1}') as end,
            guest_name as title,
            additional_guest_name,
            if(reservation_status in('Reserved','In-house'),if(ifnull(reservation_color,'')='',status_color,reservation_color),status_color) as color,
            adult,
            reservation_stay_adr,
            child,
            pax,
            reference_number,
            internal_reference_number,
            reservation,
            reservation_color,
            reservation_color_code,
            is_master,
            parent as reservation_stay,
            'stay' as type,
            allow_user_to_edit_information as can_resize,
            arrival_date,
            departure_date,
            start_time,
            end_time,
            business_source,
            rooms,
            reservation_type,
            group_color,
            group_name,
            group_code,
            paid_by_master_room,
            total_debit,
            balance,
            total_credit,
            total_amount,
            note,
            reservation_status,
            can_change_start_date,
            can_change_end_date,
            stay_rooms
        from 
            `tabReservation Stay Room` 
        where 
            show_in_room_chart = 1   and 
            name in (
                select 
                    distinct stay_room_id 
                from `tabRoom Occupy` 
                where 
                    date between %(start)s and %(end)s  and 
                    room_type_id = if(%(room_type_id)s='',room_type_id, %(room_type_id)s) and 
                    ifnull(floor,'') = if(%(floor)s='',ifnull(floor,''), %(floor)s) and 
                    ifnull(building,'') = if(%(building)s='',ifnull(building,''), %(building)s) and 
                    business_source = if(%(business_source)s='',business_source, %(business_source)s) and 
                    room_type_id in (select name from `tabRoom Type` where room_type_group=if(%(room_type_group)s='',room_type_group,%(room_type_group)s)) 
                    


            ) and 
            property = %(property)s 
    """.format(
        "12:00:00" if slot_duration=="12" else "00:00:00",
        "12:00:00" if slot_duration=="12" else "00:00:00"
    )
    if room_number:
        sql = sql + " and room_number like   concat('%%' ,  %(room_number)s ,'%%') "
    if keyword:
        # sql = sql + " and ifnull(keyword,'') like  concat('%%' +   %(keywords)s ,'%%') "
        sql = sql + " and concat(ifnull(keyword,''),' ', guest_name, ' ' + parent) like concat('%%' ,  %(keywords)s ,'%%') "



  
    filter = {
                "property":property, 
                "start":add_to_date( start, days=-1),#we set start -1 to get the last event to show in room chart
                "end":end,
                "room_type_id":room_type or "",
                "room_type_group":room_type_group or '',
                "business_source":business_source,
                "room_number":room_number or '',
                "floor":floor or '',
                "keywords":keyword or "",
                "building":building or ""
            }
 
    data = frappe.db.sql(sql,filter, as_dict=1)

    for d in data:
        d["can_resize"]  = d["can_resize"] == 1
        
    events = data
   

    # check if room chart view is group by room type then add event to room type resource
    occupy_data =  get_occupy_data(view_type, filter)
         

    #get event from room block
    events = events +  get_room_block_event(add_to_date(start, days=-1),end,property)
    

    return {
        "events":events,
        "occupy_data":occupy_data,
        "conflig_rooms":get_conflict_room(filter),
        }

@frappe.whitelist()
def get_room_inventory_calendar_event(property, start=None,end=None, keyword=None):
 
    sql = """
        select 
            room_type_id, 
            date,
            sum(type='Reservation' and is_active=1 and is_departure=0) as total, 
            sum(if(type='Block',1,0)) as block, 
            sum(type='Reservation' and coalesce(room_id,'')='' and is_active=1 and is_active_reservation=1) as unassign_room, 
            sum(is_arrival=1 and is_active=1 and is_active_reservation=1) as arrival,
            sum(is_departure=1 and is_active=1 and is_active_reservation=1) as departure,
            sum(type='Reservation' and is_stay_over=1 and is_active=1 and is_active_reservation = 1) as stay_over,
            sum(adult) as adult, 
            sum(child) as child 
        from `tabRoom Occupy` 
        where 
            property=%(property)s and 
            date between %(start)s and %(end)s  
        group by 
            room_type_id, 
            date
        """
    data = {
        "room_occupy": frappe.db.sql(sql,{'property':property,'start':start,'end':end},as_dict=1)
    }
    return data
   

@frappe.whitelist()
def get_occupy_data(view_type, filter):
    occupy_data = []
    if view_type =="room_type":
        sql = """select 
                    room_type_id, 
                    date, 
                    sum(is_active=1 and is_departure=0) as total,
                    sum(type='Block') as block, 
                    sum(type='Reservation' and coalesce(room_id,'')='' and is_active=1 and is_active_reservation = 1) as unassign_room, 
                    sum(type='Reservation' and is_arrival=1 and is_active=1 and is_active_reservation=1 ) as arrival, 
                    sum(type='Reservation' and is_departure=1  and is_active_reservation = 1)  as departure,
                    sum(type='Reservation' and is_stay_over=1 and is_active=1 and is_active_reservation = 1) as stay_over,
                    sum(if(is_active=1 and is_active_reservation=1, adult,0)) as adult, 
                    sum(if(is_active=1 and is_active_reservation=1, child,0)) as child,
                    sum(type='Reservation' and is_active=1) as total_room_sold
                from `tabRoom Occupy`  
                where 
                    
                    property=%(property)s and 
                    date between %(start)s and %(end)s and 
                    room_type_id = if(%(room_type_id)s='',room_type_id, %(room_type_id)s)  and 
                    room_type_id in (select name from `tabRoom Type` where room_type_group=if(%(room_type_group)s='',room_type_group,%(room_type_group)s)) 
                group by 
                    room_type_id, 
                    date
                """
        
        occupy_data = frappe.db.sql(sql,filter,as_dict=1)
    else: 
        #get summary by date only without room type
        sql = """select 
                    date, 
                    sum(is_active=1 and is_departure=0) as total,
                    sum(type='Block') as block, 
                    sum(type='Reservation' and coalesce(room_id,'')='' and is_active=1 and is_active_reservation = 1) as unassign_room, 
                    sum(type='Reservation' and is_arrival=1 and is_active=1 and is_active_reservation=1 ) as arrival, 
                    sum(type='Reservation' and is_departure=1 and  is_active_reservation = 1)  as departure,
                    sum(type='Reservation' and is_stay_over=1 and is_active=1 and is_active_reservation = 1) as stay_over,
                    sum(if(is_active=1 and is_active_reservation=1, adult,0)) as adult, 
                    sum(if(is_active=1 and is_active_reservation=1, child,0)) as child,
                    sum(type='Reservation' and is_active=1) as total_room_sold
                    from `tabRoom Occupy` 
                where 
                    property=%(property)s and 
                    date between %(start)s and %(end)s and 
                    room_type_id = if(%(room_type_id)s='',room_type_id, %(room_type_id)s)  and 
                    room_type_id in (select name from `tabRoom Type` where room_type_group=if(%(room_type_group)s='',room_type_group,%(room_type_group)s)) 
                group by 
                    date
                """
        
        occupy_data = frappe.db.sql(sql,filter,as_dict=1)

    return occupy_data

@frappe.whitelist()
def get_room_block_event(start,end,property):
    slot_duration = frappe.db.get_single_value("eDoor Setting","room_chart_calendear_slot_duration")
    sql = """
        select 
            name as id, 
            room_id as resourceId,
            room_number,
            concat(start_date,'T','{0}') as start ,
            concat(end_date,'T','{1}') as end,
            'Room Block' as title,
            status_color as color,
            reason,
            'room_block' as type,
            owner as block_by

        from 
            `tabRoom Block` 
        where 
            docstatus = 1   and 
            is_unblock = 0 and
            name in (
                select distinct stay_room_id from `tabRoom Occupy` where date between '{2}' and '{3}' 
            ) and 
            property = %(property)s

    """
    sql = sql.format(
            "12:00:00" if slot_duration=="12" else "00:00:00",
            "12:00:00" if slot_duration=="12" else "00:00:00",
            getdate(start), 
            getdate(end)
            )
    
        
    data = frappe.db.sql(sql,{"property":property}, as_dict=1)
    
    for d in data:
        d["can_resize"] = True
    
    return data

@frappe.whitelist()
def get_calendar_event_for_room_type_resource(start,end,property):
    """
        There are 2 place to get room type resource event and other resource event
        1. From temp room occupy for current and future date 
        2. From room type Daily Property Data for past date

    """
    events = []
    working_day = get_working_day(property=property)
    dates = get_date_range( getdate(start),getdate(end),False)



    future_dates =  [d for d in dates if d >= working_day["date_working_day"]]
    past_dates =  [d for d in dates if d < working_day["date_working_day"]]
    
    #1. get date for future date by from temp room occupy
    if future_dates:
        #get all room type with total room
        sql = "select room_type_id, room_type, count(name) as total_room from `tabRoom` where property='{}' and disabled = 0 group by room_type_id, room_type".format(property)
        room_type_data = frappe.db.sql(sql,as_dict=1)
    

         
        sql = """
                select 
                    room_type_id, 
                    date, 
                    sum(if(type='Reservation',1,0)) as total_occupy,
                    sum(if(type='Block',1,0)) as total_block,
                    sum(if(coalesce(room_id,'')='',1,0)) as total_unassign_room,
                    sum(pax) as pax
                from 
                    `tabTemp Room Occupy` 
                where 
                    property='{}' and 
                    date between '{}' and '{}' 
                group by 
                    room_type_id, 
                    date 
            """
        sql = sql.format(
            property,
            future_dates[0].strftime('%Y-%m-%d'),
            future_dates[len(future_dates)-1].strftime('%Y-%m-%d'),
        )
         
        temp_occupy_data = frappe.db.sql(sql,as_dict=1)
        #get temp room occupy 
        
        for d in room_type_data:
            for x in future_dates:
                events.append(      
                {
                    "resourceId": d["room_type_id"],
                    "start": "{}T00:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title": d["total_room"] - Enumerable(temp_occupy_data).where(lambda r:r.room_type_id==d["room_type_id"] and r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: (r.total_occupy or 0) + (r.total_block or 0)),
                    "color": "#29CD42",
                    "type":"available_room"
                })

                #add event for unssign room
                events.append(      
                {
                    "resourceId": d["room_type_id"],
                    "start": "{}T12:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "end": "{}T0:00:00.000000".format(x.strftime('%Y-%m-%d')),
                    "title":  Enumerable(temp_occupy_data).where(lambda r:r.room_type_id==d["room_type_id"] and r.date.strftime('%Y-%m-%d') == x.strftime('%Y-%m-%d')).sum(lambda r: r.total_unassign_room or 0),
                    "color": "#cccccc",
                    "type":"unassign_room"
                })

        #add event for Vacant Room 
        total_room = Enumerable(room_type_data).sum(lambda r:r.total_room)

      
 

    return events
 
 
@frappe.whitelist(methods="POST")
def validate_run_night_audit(property,step):
    working_day = get_working_day(property)
    if step ==2:
        #valdate if have check room vaivable
        sql="select name from `tabReservation Stay` where is_active_reservation=1 and reservation_status in ('Confirmed','Reserved') and arrival_date='{}' and property=%(property)s limit 1".format(working_day["date_working_day"])
        data = frappe.db.sql(sql,{"property":property}, as_dict=1)
        if data:
            frappe.throw("Please check in or cancel the Confirmed and Reserved")
    elif step==3:
        #validate check out guest
        sql="select name from `tabReservation Stay` where is_active_reservation=1 and reservation_status in ('In-house','Reserved','Confirmed') and departure_date='{}' and property=%(property)s limit 1".format(working_day["date_working_day"])
        data = frappe.db.sql(sql,{"property":property}, as_dict=1)
        if data:
            frappe.throw("Please check out all reservation")
    elif step==4:
        # update is arrival to reservation room rate
        # we need to filter this in step 5
        sql="select distinct reservation_stay from `tabReservation Room Rate` where property=%(property)s and date=%(date)s"
        stay_names = frappe.db.sql(sql,{"property":property,"date":working_day["date_working_day"]})
        # reset all room rate record with is_arrival = 0
        stay_names = stay_names or []
        if stay_names: 
            frappe.db.sql("update `tabReservation Room Rate` set is_arrival=0 where reservation_stay in %(stay_names)s and is_arrival=1",{"stay_names":stay_names})
            # get min date from room rate group by reservation stay then update is_arrival =1 
            sql = """
                update `tabReservation Room Rate` r 
                join (
                    select
                        reservation_stay,
                        min(date) as date
                    from `tabReservation Room Rate` 
                    where
                        reservation_stay in %(stay_names)s
                    group by
                        reservation_stay
                ) b 
                on r.reservation_stay = b.reservation_stay and  r.date = b.date
                set
                    r.is_arrival = 1
                
            """
            frappe.db.sql(sql,{"stay_names":stay_names})
            frappe.db.commit()
    elif step == 6:
        sql="select name from `tabFolio Transaction` where posting_date = '{}'  and property=%(property)s and ifnull(parent_reference,'') = '' and is_auto_post = 0 limit 1".format(working_day["date_working_day"])
        data = frappe.db.sql(sql,{"property":property}, as_dict=1)
        return True if data else False
    elif step == 7:
        sql="select name from `tabCashier Shift` where posting_date = '{}'  and business_branch=%(property)s and is_closed = 0 limit 1".format(working_day["date_working_day"])
        data = frappe.db.sql(sql,{"property":property}, as_dict=1)
        if  data:
            frappe.throw("Please close all cashier shift.")
    return False

@frappe.whitelist(methods="POST")
def run_night_audit(property, working_day):
    #1. Validate working day is still open
    #2. Validate cashier shift open
    #3. validate arrival to check in 
    #3. validate departure to check out 
    #validate permission
    old_working_day_data = get_working_day(property)
    validate_role("run_night_audit_role")
    
    doc_property = frappe.get_doc("Business Branch", property)
    doc_working_day = frappe.get_doc("Working Day", working_day)

    if doc_working_day.is_closed==1:
        frappe.throw("Working day # {}, Date {} is already closed by {}. Please refresh your browser to get update.".format(working_day, doc_working_day.posting_date.strftime("%d-%m-%Y"), doc_working_day.modified_by))
    
    # if frappe.db.exists("Cashier Shift",{"working_day":working_day, "is_closed":0}):
    #     frappe.throw("Please close all cashier shift before run night audit")
    #validate room to check in
    
    if frappe.db.exists("Reservation Stay",{"property":property, "reservation_status":["in",["Confirmed","Reserved"],], "arrival_date": doc_working_day.posting_date}):
        frappe.throw("Please check in all arrival reservation")

    if frappe.db.exists("Reservation Stay",{"property":property, "reservation_status":"In-house", "departure_date": doc_working_day.posting_date}):
        frappe.throw("Please check out all departure reservation")
    
    #Close working
    doc_working_day.is_closed = 1
    doc_working_day.closed_date = datetime.now()
    doc_working_day.save()

    #create new working day
    new_working_day = frappe.get_doc(
                    {
                        "doctype":"Working Day",
                        "posting_date": add_to_date(getdate(doc_working_day.posting_date), days=1),
                        "business_branch":property,
                        "pos_profile": doc_property.default_pos_profile,

                    }
                    ).insert()
    
    #create a new cashier shift
    doc_pos_profile = frappe.get_doc("POS Profile", doc_property.default_pos_profile)
    doc_pos_config = frappe.get_doc("POS Config", doc_pos_profile.pos_config)
    cash_float = []
    for d in doc_pos_config.payment_type:

        if d.allow_cash_float == 1:
            cash_float.append({
                "payment_method":d.payment_type,
                "exchange_rate":d.exchange_rate,
                "input_amount":0,
                "opening_amount":0
            })
     
    if frappe.get_cached_value("eDoor Setting", None, "create_next_cashier_shift_after_close_shift"):
        frappe.get_doc(  {
                "doctype":"Cashier Shift",
                "working_day": new_working_day.name,
                "shift_name": frappe.db.get_default("shift_name_after_run_night_audit"),
                "pos_profile": doc_property.default_pos_profile,
                "cash_float":cash_float
            }
        ).insert()

    #queue post room change to folio

    
    # get last edoor cashier shift 
    last_shift = frappe.db.sql("select name from `tabCashier Shift` where working_day=%(working_day)s and is_edoor_shift=1 order by creation desc limit 1",{"working_day":old_working_day_data["name"]},as_dict=1)
    if not last_shift:
        frappe.throw(_("There is edoor shift to posting nightly charge."))
    old_working_day_data["cashier_shift"] = {"name": last_shift[0]["name"]}
    
    post_charge_to_folio_afer_after_run_night_audit(property=property, working_day=old_working_day_data)  
    
    # update_room_status(new_working_day)
    frappe.enqueue("edoor.api.frontdesk.update_room_status", queue='long', working_day=new_working_day)
    
    # update daily property data 
    frappe.enqueue("edoor.api.frontdesk.update_daily_property_data", queue='long', working_date=doc_working_day.posting_date, property = property)
    
    working_day = get_working_day(property)
    frappe.db.commit()
    return working_day



@frappe.whitelist()
def update_room_status(working_day=None,working_day_name=None):
    if not working_day:
        working_day = frappe.get_doc("Working Day", working_day_name)
    
    #0 update all vacant room 
    sql = """
        select name from `tabRoom`
        where 
            name not in (
                select room_id from `tabRoom Occupy` 
                where
                    property = %(property)s and 
                    date = %(date)s and 
                    is_active=1 and 
                    ifnull(room_id,'') !=''
            )  and
            property = %(property)s
    """
    room_list = frappe.db.sql(sql,{"property":working_day.business_branch,"date":working_day.posting_date},as_dict=1)
    for d in room_list:
        room_doc = frappe.get_doc("Room", d["name"])
        room_doc.room_status = "Vacant" 
        room_doc.save()
    frappe.db.commit()

    #1. update stay over guesty
    stay_over_room = frappe.db.sql("""
                            select 
                                room_id  
                            from `tabRoom Occupy` 
                            where 
                                is_active = 1 and 
                                property='{}' and
                                date = '{}' and 
                                ifnull(room_id,'') !=''
                    """.format( working_day.business_branch,working_day.posting_date),as_dict=1)
    
    for r in stay_over_room:
        room_doc = frappe.get_doc("Room", r["room_id"])
        room_doc.housekeeping_status_code = "Dirty"
        room_doc.room_status = "Occupy" 
        room_doc.save()

    #update room status that end block
    sql = "select room_id from `tabRoom Block` where docstatus=1 and is_unblock=0 and end_date='{}' and property='{}'".format(working_day.posting_date ,working_day.business_branch)
    data = frappe.db.sql(sql,as_dict=1)


    for d in data:
        room_doc = frappe.get_doc("Room", d["room_id"])
        room_doc.room_status = "Vacant"
        room_doc.housekeeping_status_code = "Dirty"
        room_doc.save()
    

    #2 update room status of room block
    room_block = frappe.db.sql("select room_id from `tabTemp Room Occupy` where type='Block' and property='{}' and date='{}'".format(working_day.business_branch, working_day.posting_date),as_dict=1)
   
  
    for r in room_block:
        room_doc = frappe.get_doc("Room", r["room_id"])
        room_doc.room_status = "Room Block"
        room_doc.save()
    frappe.db.commit()
    
@frappe.whitelist()
def update_daily_property_data(property, working_date):

    sql = "delete from `tabDaily Property Data` where date='{}' and property='{}'".format(working_date,property)
    frappe.db.sql(sql)

    sql = "select room_type_id, count(name) as total_rooms from `tabRoom` where disabled=0 and property='{}' group by room_type".format(property)
    data = frappe.db.sql(sql,as_dict=1)
    for d in data:
        frappe.get_doc({
            "property":property,
            "doctype":"Daily Property Data",
            "date":working_date,
            "room_type_id":d["room_type_id"],
            "total_room":d["total_rooms"]
        }).insert(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist()
def post_room_change_to_folio(working_day): 
    folio_names=[] 
    cashier_shift = frappe.db.sql( "select name from `tabCashier Shift` where working_day='{}' and pos_profile='{}' order by creation desc limit 1".format(working_day.name,working_day.pos_profile),as_dict=1)
    
    
    room_rates = frappe.db.get_all("Reservation Room Rate", fields=["*"] , filters={"property":working_day.business_branch,"date": working_day.posting_date,"is_arrival":0 },page_length=1000)
    
    for r in room_rates:
        stay_doc = frappe.get_doc("Reservation Stay",r.reservation_stay)
        if stay_doc.is_active_reservation==1 and stay_doc.reservation_status=="In-house":
            folio = None
            if stay_doc.paid_by_master_room == 0:
                master_folios = frappe.db.get_all("Reservation Folio",fields=["*"],filters={"reservation_stay":r.reservation_stay,"is_master":1},page_length=1000)
                if master_folios:
                    folio = master_folios[0]
            else:
                folio = get_master_folio(r.reservation)

            
            if folio:
                if not stay_doc.inclusion_items:
                    # get folio name to update after post room charge to folio
                    folio_names.append(folio.name)
                    add_room_charge_to_folio(
                        folio= folio,
                        rate= r,
                        is_night_audit_posing=1,
                        working_day=working_day.name,
                        cashier_shift=cashier_shift[0]["name"],
                        ignore_validateion_cashier_shift=True,
                        ignore_validate_back_date_transaction=True
                    )
                else:
                    # pos room charge exclude package charge 
                    posting_rules = ["Everyday","Everyday Except Checked Out Date"]
                    package_charges = get_breakdown_package_charge_code(stay_doc, r, posting_rules)
                    
                    
                    # get discount percentage if have discount amount
                    
                    # Discount for sub package charge code is percent only 
                    # we calculate this percentage from base account code charge and pacage charge amount
                        
                    if r.discount and r.discount_type=='Amount':
                        r.discount_type = "Percent"
                        r.discount = r.discount / r.input_rate 
                    
                    
                    r.input_rate = r.input_rate - sum([d["rate"] *d["quantity"]  for d in package_charges]) 
                    # get folio name to update after post room charge to folio
                    folio_names.append(folio.name)
                    folio_tran_doc = add_room_charge_to_folio( folio= folio,rate = r, is_package=1,ignore_validateion_cashier_shift=True,ignore_validate_back_date_transaction=True,ignore_update_reservation_folio=True )
                    if folio_tran_doc:
                        # check if room rate have discount then minute discount from package room rate
                        for p in package_charges: 
                            rate_data = {
                                "account_code":p["account_code"],
                                "reference_folio_transaction":folio_tran_doc.name,
                                "parent_reference":"",
                                "date":r["date"],
                                "room_type_id":r["room_type_id"],
                                "room_id":r["room_id"],
                                "input_rate":p["rate"],
                                "tax_rule":frappe.db.get_value("Account Code",p["account_code"],"tax_rule"),
                                "is_auto_post":1,
                                "name":r.name,
                                "reservation_stay":r["reservation_stay"],
                                "stay_room_id":r.stay_room_id,
                                "adult":p["adult"],
                                "child":p["child"],
                                "quantity":p["quantity"],
                                "note": "This folio transaction is package charge breakdown from folio transaction number " + folio_tran_doc.name
                                
                            }   
                            if rate_data["tax_rule"]:
                                tax_rule_doc = frappe.get_doc("Tax Rule", rate_data["tax_rule"])
                                
                                rate_data["tax_1_rate"] = tax_rule_doc.tax_1_rate
                                rate_data["tax_2_rate"] = tax_rule_doc.tax_2_rate
                                rate_data["tax_3_rate"] = tax_rule_doc.tax_3_rate
                                rate_data["rate_include_tax"] =  'Yes' if tax_rule_doc.is_rate_include_tax else 'No'
                            else:
                                rate_data["tax_1_rate"] =0
                                rate_data["tax_2_rate"] = 0
                                rate_data["tax_3_rate"] = 0
                                rate_data["rate_include_tax"] =  'No'
                            
                            rate_data["discount_type"] ="Percent"
                            rate_data["discount"] = r.discount
                            
                            add_package_inclusion_charge_to_folio(
                                folio= folio,
                                rate= rate_data ,
                                ignore_update_reservation_folio=True,
                                ignore_validateion_cashier_shift=True,
                                ignore_validate_back_date_transaction=True,
                                is_night_audit_posing=1,
                                working_day=working_day.name,
                                cashier_shift=cashier_shift[0]["name"]

                            )
                        
                
    if folio_names:  
        frappe.enqueue("edoor.api.reservation.update_sub_package_charge_to_folio_transaction",queue="short",reservation_folios = folio_names)           
    frappe.enqueue("edoor.api.frontdesk.update_transaction_balance_after_run_night_audit", queue='long', working_day=working_day)
    


@frappe.whitelist()
def update_transaction_balance_after_run_night_audit(working_day):
    #verify if reservation stay and and reservation is update balance
    # post enque job to update update folio balance
    sql= "select distinct reservation,reservation_stay, transaction_number from `tabFolio Transaction` where transaction_type='Reservation Folio' and posting_date = '{}' and property='{}'".format(working_day.posting_date, working_day.business_branch)
    data = frappe.db.sql(sql,as_dict=1)
    
    frappe.enqueue("edoor.api.frontdesk.update_ledger_balance_after_run_night_audit", queue='long', ledger_type='Reservation Folio', names = set([d["transaction_number"] for d in data]))
    frappe.enqueue("edoor.api.frontdesk.update_reservation_stay_credit_debit_balance", queue='long', names = set([d["reservation_stay"] for d in data]))
    frappe.enqueue("edoor.api.frontdesk.update_reservation_credit_debit_balance", queue='long',  names = set([d["reservation"] for d in data]))


@frappe.whitelist()
def update_ledger_balance_after_run_night_audit(ledger_type, names):
    if names:
        sql = """
            select 
                    transaction_type,
                    transaction_number,
                    coalesce(sum(if(type='Debit',amount,0)),0) as debit,
                    coalesce(sum(if(type='Credit',amount,0)),0) as credit
                from `tabFolio Transaction` 
                where
                    transaction_type = %(ledger_type)s and 
                    transaction_number in  %(names)s
                group by
                    transaction_type,
                    transaction_number 
        """
        data_folio_balance = frappe.db.sql(sql, {
            "names":names,
            "ledger_type":ledger_type,
        }, as_dict =1)

        for d in data_folio_balance:
            frappe.db.sql("update `tab{0}` set total_debit={1}, total_credit={2}, balance={1}-{2} where name='{3}'".format(
                ledger_type,
                d["debit"],
                d["credit"],
                d["transaction_number"],
            ))
        frappe.db.commit()

 
@frappe.whitelist()
def update_reservation_credit_debit_balance(names):
    if names:
        sql = """
            select 
                    reservation,
                    coalesce(sum(if(type='Debit',amount,0)),0) as debit,
                    coalesce(sum(if(type='Credit',amount,0)),0) as credit
                from `tabFolio Transaction` 
                where
                    transaction_type = 'Reservation Folio' and 
                    reservation in  %(names)s
                group by
                    reservation
        """
        data_folio_balance = frappe.db.sql(sql, {
            "names":names,
        }, as_dict =1)

        for d in data_folio_balance:
            frappe.db.sql("update `tabReservation` set total_debit={0}, total_credit={1}, balance={0}-{1} where name='{2}'".format(
                d["debit"],
                d["credit"],
                d["reservation"],
            ))
        frappe.db.commit()
 
@frappe.whitelist()
def update_reservation_stay_credit_debit_balance(names):
    if names:
        sql = """
            select 
                    reservation_stay,
                    coalesce(sum(if(type='Debit',amount,0)),0) as debit,
                    coalesce(sum(if(type='Credit',amount,0)),0) as credit
                from `tabFolio Transaction` 
                where
                    transaction_type = 'Reservation Folio' and 
                    reservation_stay in  %(names)s
                group by
                    reservation_stay 
        """
        data_folio_balance = frappe.db.sql(sql, {
            "names":names,
        }, as_dict =1)

        for d in data_folio_balance:
            frappe.db.sql("update `tabReservation Stay` set total_debit={0}, total_credit={1}, balance={0}-{1} where name='{2}'".format(
                d["debit"],
                d["credit"],
                d["reservation_stay"],
            ))
            
            frappe.db.sql("update `tabReservation Stay Room` set total_debit={0}, total_credit={1}, balance={0}-{1} where parent='{2}'".format(
                d["debit"],
                d["credit"],
                d["reservation_stay"],
            ))
        frappe.db.commit()






@frappe.whitelist()
def check_room_config_and_over_booking(property):
    working_day = get_working_day(property)
    sql="select count(name) from `tabTemp Room Occupy` where type='Reservation' and is_departure=0  and ifnull(room_id,'') <> '' and date>='{}'   group by room_id,date   having count(name)>1".format(working_day["date_working_day"])
    data = frappe.db.sql(sql)
    if data:
        return data[0][0]
    return 0

@frappe.whitelist()
def get_day_end_summary_report(property="ESTC  & HOTEL's", date=None,show_package_breakdown=0): 
    amount_field = "total_amount"
    if int(show_package_breakdown)==1:
        amount_field = "transaction_amount"
        
    # room revneue 
    sql = """select 
                sum({} * if(type='Debit',1,-1)) as room_revenue 
            from `tabFolio Transaction` 
            where 
            {} and 
            property=%(property)s and posting_date = '{}' and
            account_category in ('Room Charge','Room Tax','Room Discount','Service Charge') and
            is_base_transaction=1
        """.format(
            amount_field, 
            " coalesce(parent_reference,'') ='' " if int(show_package_breakdown)==0 else "  1=1  " ,
            date)
    
    
       

    data = frappe.db.sql(sql,{'property':property},as_dict=1)
    room_revenue = 0
    if len(data)>0:
        room_revenue = data[0]["room_revenue"]
 
    #room nitht
    sql = """select 
                sum(is_active=1 and type='Reservation') as total_room_sold ,
                sum(is_active=1 and type='Reservation' and is_complimentary=1) as total_complimentary_room ,
                sum(is_active=1 and type='Reservation' and is_house_use=1) as total_house_use_room ,
                sum(type='Block') as total_block ,
                sum(is_active=1 and type='Reservation' and is_arrival=1) as arrival,
                sum(if(is_active=1 and type='Reservation' and is_arrival=1,adult,0)) as arrival_adult,
                sum(if(is_active=1 and type='Reservation' and is_arrival=1,child,0)) as arrival_child,
                sum(is_active=1 and type='Reservation' and is_arrival=0 and is_departure=0) as stay_over,
                sum(if(is_active=1 and type='Reservation' and is_arrival=0 and is_departure=0,adult,0)) as stay_over_adult,
                sum(if(is_active=1 and type='Reservation' and is_arrival=0 and is_departure=0,child,0)) as stay_over_child,
                sum(type='Reservation' and is_departure=1) as departure,
                sum(if(type='Reservation' and is_departure=1,adult,0)) as departure_adult,
                sum(if(type='Reservation' and is_departure=1,child,0)) as departure_child
            from `tabRoom Occupy` 
            where 
            property=%(property)s and date= '{}'  
        """.format(date)
    
    occupy_data = frappe.db.sql(sql,{'property':property},as_dict=1)
    calculate_adr_include_all_room_occupied = frappe.db.get_single_value("eDoor Setting", "calculate_adr_include_all_room_occupied")
    room_sold = 0
    complimentary = 0
    house_use = 0
    room_block = 0
    if len(occupy_data)>0:
        room_sold = occupy_data[0]["total_room_sold"] or 0
        complimentary = occupy_data[0]["total_complimentary_room"] or 0
        house_use = occupy_data[0]["total_house_use_room"] or 0
        room_block = occupy_data[0]["total_block"] or 0
    if calculate_adr_include_all_room_occupied == 1:
        adr = (room_revenue or 0) / (1 if room_sold==0 else room_sold)
    else:
        adr = (room_revenue or 0) / ((1 if room_sold==0 else room_sold) - (complimentary + house_use))
    #occupancy
    total_rooms =frappe.db.count('Room', {'property': property, "disabled":0})
    
    vacant_room = total_rooms - (room_sold + room_block)
    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")


    if calculate_room_occupancy_include_room_block==0:
        total_rooms = total_rooms - room_block 

    
    occupancy = round( (room_sold or 0) / (1 if total_rooms == 0 else total_rooms)*100,2)

    ledger_types = [
        {"label":"Guest Ledger", "value":"Reservation Folio"},
        {"label":"Deposit Ledger", "value":"Deposit Ledger"},
        {"label":"Desk Folio", "value":"Desk Folio"},
        {"label":"City Ledger", "value":"City Ledger"},
        {"label":"Payable Ledger", "value":"Payable Ledger"},
        {"label":"F&B Revenue", "value":"Cashier Shift"},
    ]
    #get opening balance
    sql = """
        select
            transaction_type,
            sum(amount * if(type='Debit',1,-1)) as opening
        from `tabFolio Transaction`
        where
            property = %(property)s and 
            posting_date<%(date)s
        group by
            transaction_type
    """

    opening_data = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)

    #get current date transaction

    sql = """
        select
            transaction_type,
            sum({0} * if(type='Debit',1,0)) as debit,
            sum({0} * if(type='Debit',0,1)) as credit
        from `tabFolio Transaction`
        where
            {1} and 
            property = %(property)s and 
            posting_date = %(date)s and
            is_base_transaction=1
        group by
            transaction_type
    """.format( amount_field, " coalesce(parent_reference,'') ='' " if int(show_package_breakdown)==0  else "  1=1 " )
    

    current_date_transaction  = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)

    for l in ledger_types:
        opening_record = [d for d in opening_data if d["transaction_type"] == l["value"]]
        if len(opening_record)>0:
            l["opening"] = opening_record[0]["opening"]
            if l["value"] == "Cashier Shift":
                l["opening"] = 0
        else:
            l["opening"] = 0

        current_date_data  = [d for d in current_date_transaction if d["transaction_type"] == l["value"]]
        if len(current_date_data)>0:
            l["debit"] =current_date_data[0]["debit"]
            l["credit"] =current_date_data[0]["credit"]
        else:
            l["debit"] = 0
            l["credit"] = 0

    #room sold by room type
    sql = """
        select 
            rate_type,
            count(name) as total_room
        from `tabRoom Occupy` 
        where  
            property= %(property)s and 
            date = '{}' and
            is_active = 1  and 
            type='Reservation'
        group by
            rate_type 
    """.format(date)
    room_sold_by_rate_type = frappe.db.sql(sql,{'property':property},as_dict=1)

    data = {
        "room_revenue": room_revenue,
        "room_night": room_sold,
        "adr":adr,
        "occupancy":occupancy,
        "check_in":occupy_data[0]["arrival"] or 0,
        "check_in_adult":occupy_data[0]["arrival_adult"] or 0,
        "check_in_child":occupy_data[0]["arrival_child"] or 0,
        "stay_over":occupy_data[0]["stay_over"] or 0,
        "stay_over_adult":occupy_data[0]["stay_over_adult"] or 0,
        "stay_over_child":occupy_data[0]["stay_over_child"] or 0,
        "departure":occupy_data[0]["departure"] or 0,
        "departure_adult":occupy_data[0]["departure_adult"] or 0,
        "departure_child":occupy_data[0]["departure_child"] or 0,
        "room_block":room_block,
        "vacant_room":vacant_room,
        "ledger_summary":ledger_types,
        "room_sold_by_rate_type":room_sold_by_rate_type
    }

    return data

@frappe.whitelist()
def get_recent_audit_trail():
    property = frappe.defaults.get_user_default("business_branch")
    if not property:
        data = frappe.db.get_list("Business Branch")
        if len(data)>0:
            property = data[0].name
    if property:
        sql = "select name,creation,comment_by,content,reference_doctype,reference_name,subject,custom_comment_by_photo from `tabComment` where custom_property = %(property)s and custom_is_audit_trail=1 order by creation desc limit 20"

        data =  frappe.db.sql(sql,{"property":property}, as_dict=1)
        for d in data:
            d["creation"] = frappe.utils.pretty_date(d["creation"])
        return data
    return []

@frappe.whitelist()
def get_house_keeping_status_backend():
    property = frappe.defaults.get_user_default("business_branch")
    if not property:
        data = frappe.db.get_list("Business Branch")
        if len(data)>0:
            property = data[0].name
    if property:
        working_day = get_working_day(property)

        #get house keeping status
        
        hk_data = frappe.db.get_list("Housekeeping Status",fields=["*"],  order_by='sort_order asc')
        housekeeping_status = []
        for d in hk_data:
            total  = frappe.db.sql("select count(name) as total from `tabRoom` where property=%(property)s and housekeeping_status='{}'".format(d.name),{"property":property},as_dict=1)[0]["total"] or 0
            total_room  = frappe.db.sql("select count(name) as total_room from `tabRoom` where property=%(property)s ".format(d.name),{"property":property},as_dict=1)[0]["total_room"] or 0
            housekeeping_status.append({
                "status":d.name,
                "color":d.status_color,
                "total":total,
                "is_block_room":d.is_block_room,
                "total_room":total_room,
                "property":property,
                "working_date":working_day["date_working_day"] 
            })
        return housekeeping_status
    return []




@frappe.whitelist()
def get_arrival_stay_over_departure_backend():
    property = frappe.defaults.get_user_default("business_branch")
    
    if not property:
        data = frappe.db.get_list("Business Branch")
        if len(data)>0:
            property = data[0].name

    data = {'arrival':[],'stay_over':[],'departure':[]}
    if property:
        working_day = get_working_day(property)
        if working_day:
            date = working_day["date_working_day"] 
            if not date:
                date = frappe.utils.today()
            doc = frappe.get_doc("Business Branch",property)
            
            sql = "SELECT name,reference_number,room_type_alias,rooms,arrival_date,departure_date,business_source,room_nights,reservation_type,reservation_status,guest,guest_name,status_color from `tabReservation Stay` where property = %(property)s and is_active_reservation = 1 and arrival_date = %(date)s"
            data["arrival"] = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)
            sql = """SELECT 
                        name,
                        reference_number,
                        room_type_alias,
                        rooms,
                        arrival_date,
                        departure_date,
                        business_source,
                        room_nights,
                        reservation_type,
                        reservation_status,
                        guest,
                        guest_name,
                        status_color
                    from `tabReservation Stay` 
                    where 
                        name in (
                        select reservation_stay from `tabRoom Occupy`
                        where
                            date = %(date)s and 
                            property=%(property)s and 
                            is_departure = 1 and 
                            is_active_reservation= 1 
                        )
                    """
            data["departure"] = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)
             
            sql = """SELECT 
                        name,
                        reference_number,
                        room_type_alias,
                        rooms,
                        arrival_date,
                        departure_date,
                        business_source,
                        room_nights,
                        reservation_type,
                        reservation_status,
                        guest,
                        guest_name,
                        status_color
                    from `tabReservation Stay` 
                    where 
                        property = %(property)s and 
                        name in (
                            select reservation_stay from `tabRoom Occupy`
                            where
                            type='Reservation' and  
                            is_stay_over = 1 and 
                            is_active_reservation= 1 and 
                            date = %(date)s
                        ) 
                    """
            data["stay_over"] = frappe.db.sql(sql,{"property":property,"date":date},as_dict=1)


    
    return data
            