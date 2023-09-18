import secrets
 
from edoor.api.utils import get_date_range, get_master_folio,add_room_charge_to_folio
import frappe
import datetime
import random
from datetime import datetime
from py_linq import Enumerable
from dateutil.relativedelta import relativedelta 
from frappe.utils import getdate,add_to_date

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

# Get the current date

@frappe.whitelist()
def get_dashboard_data(property = None,date = None):
    data = frappe.db.sql("select max(posting_date) as date from `tabWorking Day` where business_branch = '{}' limit 1".format(property),as_dict=1)
    working_date =  frappe.utils.today() 
    if data:
        working_date = data[0]["date"]

    if not date:
        date = working_date 
    
    # get total_room
    sql = "select count(name) as total from `tabRoom` where property='{}'".format(property)
    data = frappe.db.sql(sql, as_dict=1)
    total_room = 0
    if data:
        total_room = data[0]["total"] or 0

    #get total room occupy
    total_room_occupy = 0
    unassign_room = 0
    
    #check if past date 
    sql = ""
    if frappe.utils.getdate(date)>=frappe.utils.getdate(working_date):
        sql = "SELECT count(name) AS `total_room_occupy`, SUM(if(ifnull(room_id,'')='' and reservation_status in('Reserved', 'Confirmed'), 1, 0)) AS `unassign_room` FROM `tabTemp Room Occupy` WHERE `date` = '{0}' AND property = '{1}' and type='Reservation';".format(date,property)
    else:
        sql = "SELECT count(name) AS `total_room_occupy`, SUM(if(ifnull(room_id,'')='' and reservation_status in('Reserved', 'Confirmed'), 1, 0)) AS `unassign_room` FROM `tabRoom Occupy` WHERE `date` = '{0}' AND property = '{1}' and type='Reservation';".format(date,property)
    
    room_operation = frappe.db.sql(sql, as_dict=1)


    if room_operation:
        unassign_room = room_operation[0]["unassign_room"]
        total_room_occupy = room_operation[0]["total_room_occupy"]


    # get reservation stay
    #filter base on arrival date
    stay = []
    stay_sql = """SELECT 
                    SUM(if(reservation_status = 'No Show',1,0)) AS `total_no_show`, 
                    SUM(if(reservation_status = 'Cancelled',1,0)) AS `total_cancelled`, 
                    SUM(if(reservation_status in ('Reserved','Confirmed'),1,0)) AS `arrival_remaining`,
                    sum(if(reservation_status in ('Reserved','Confirmed','In-house') AND is_active_reservation = 1, 1, 0)) AS `total_arrival`,
                    sum(if(reservation_status in ('Reserved','Confirmed','In-house')   and reservation_type='GIT'  AND is_active_reservation = 1, 1, 0)) AS `total_git_stay_arrival`,
                    SUM(if(require_pickup = 1 AND  is_active_reservation = 1, 1, 0)) AS `pick_up`
                FROM `tabReservation Stay` WHERE  arrival_date='{0}' and property = '{1}';""".format(date,property)
    
    stay = frappe.db.sql(stay_sql, as_dict=1)
    

    #filter base on departure date
    stay_sql = """SELECT 
                    SUM(if(reservation_status in ('In-house','Reserved','Confirmed'),1,0)) AS `departure_remaining`,
                    sum(if(is_active_reservation = 1, 1, 0)) AS `total_departure`,
                    SUM(if(require_drop_off = 1  AND  is_active_reservation = 1, 1, 0)) AS `drop_off`
                FROM `tabReservation Stay` WHERE departure_date = '{0}' and  property = '{1}';""".format(date,property)
    
    stay =[stay[0] | frappe.db.sql(stay_sql, as_dict=1)[0]]


    #get stay over
    stay_sql = """SELECT 
                    sum(if( is_active_reservation = 1, 1, 0)) AS `total_stay_over`
                FROM `tabReservation Stay` WHERE   '{0}'> arrival_date and '{0}'< departure_date  AND  property = '{1}';""".format(date,property)
    
 

    stay = [stay[0] | frappe.db.sql(stay_sql, as_dict=1)[0]]
    

    git_reservation_sql = """
                        select 
                            count(distinct reservation)   as total
                        from `tabReservation Stay`
                        where 
                            is_active_reservation=1 and 
                            reservation_status   in ('Reserved','Confirmed','In-house') and
                            reservation_type = 'GIT' and 
                            arrival_date = '{0}' and
                            property = '{1}' 
                    """.format(date, property)
    
    
    #count upcommintg note
    upcoming_note = frappe.db.sql("select count(name) as total  from `tabFrontdesk Note` where note_date>='{}' and property='{}'".format(date,property), as_dict=1)
    
    #get total room block 
    sql = "SELECT count(name) AS `total_room_block` FROM `tabRoom Occupy` WHERE `date` = '{0}' AND property = '{1}' and type='Block';".format(date,property)
    total_room_block = frappe.db.sql(sql,as_dict=1)

    vacant_room = (total_room or 0) - (total_room_occupy or 0) - (total_room_block[0]["total_room_block"] or 0)
    if vacant_room<0:
        vacant_room = 0
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
        "total_no_show":stay[0]["total_no_show"] or 0,
        "total_cancelled":stay[0]["total_cancelled"] or 0,
        "stay_over":stay[0]["total_stay_over"] or 0,
        "git_reservation_arrival": frappe.db.sql(git_reservation_sql,as_dict=1)[0]["total"] or 0,
        "git_stay_arrival":stay[0]["total_git_stay_arrival"] or 0,
        "upcoming_note":upcoming_note[0]["total"] or 0,
        
        
    }

@frappe.whitelist()
def get_house_keeping_status(property):
    #get house keeping status
    hk_data = frappe.db.get_list("Housekeeping Status",fields=["*"],  order_by='sort_order asc')
    housekeeping_status = []
    for d in hk_data:
        total  = frappe.db.sql("select count(name) as total from `tabRoom` where property='{}' and housekeeping_status='{}'".format(property,d.name),as_dict=1)[0]["total"] or 0

        housekeeping_status.append({
            "status":d.name,
            "color":d.status_color,
            "icon":d.icon,
            "total":total,
            "is_block_room":d.is_block_room
        })
 

    return housekeeping_status

@frappe.whitelist()
def get_mtd_room_occupany(property):
    total_room = frappe.db.sql("select count(name) from `tabRoom` where property='{}' and disabled=0".format(property))[0][0] 
    
    now = datetime.now()
    start_date = datetime(now.year, now.month, 1)
    
    end_date = now + relativedelta(day=1, months=1, days=-1)
    sql = "select date,0 as occupancy from `tabDates` where date between cast('{}' as date) and cast('{}' as date)"
    sql = sql.format(start_date, end_date)
    data_date = frappe.db.sql(sql,as_dict=1)
    
    sql = "select date, count(name) as  total from `tabRoom Occupy` where property='{}' and date between '{}' and '{}' and type='Reservation' group by date "
 
    data = frappe.db.sql(sql.format(property, start_date,end_date),as_dict=1)
    
    for r in data:
          [x for x in data_date if x["date"]==r["date"]][0]["occupancy"] = (r["total"]) 

    return data_date



@frappe.whitelist(allow_guest=True)
def get_server_port():
    return{"backend_port": frappe.get_doc('ePOS Settings').backend_port}

@frappe.whitelist()
def get_report():
    x = frappe.db.get_list("System Report")
    return x


@frappe.whitelist(allow_guest=True)
def get_edoor_setting(property = None):

    edoor_menus = frappe.db.get_list("eDoor Menu", fields=["name","parent_edoor_menu", "is_group", "menu_name","menu_text","icon",'move_to_more','sub_menu_icon'],order_by="sort_order asc")
    
    currency = frappe.get_doc("Currency",frappe.db.get_default("currency"))
 
    
    housekeeping_status = frappe.get_list("Housekeeping Status",filters={"is_block_room":0}, fields=['status','status_color','icon','sort_order','is_room_occupy'],  order_by='sort_order asc')
    reservation_status = frappe.get_list("Reservation Status", fields=['reservation_status','name','color','is_active_reservation','show_in_reservation_list','show_in_room_chart','sort_order'],  order_by='sort_order asc')
    
    edoor_setting_doc = frappe.get_doc("eDoor Setting")
     
    epos_setting = frappe.get_doc('ePOS Settings')
    custom_print_format = frappe.db.sql("select name, print_format from `tabCustom Print Format` where ifnull(property,'')='' or property='{}'".format(property),as_dict=1)
    
    edoor_setting  =  {
        "edoor_menu": edoor_menus,
        "folio_transaction_style_credit_debit":edoor_setting_doc.folio_transaction_style_credit_debit,
        "guest_ledger_report_name":edoor_setting_doc.guest_ledger_report_name,
        "guest_ledger_transaction_report":edoor_setting_doc.guest_ledger_transaction_report,
        "city_ledger_report_name":edoor_setting_doc.city_ledger_report_name,
        "allow_user_to_add_back_date_transaction":edoor_setting_doc.allow_user_to_add_back_date_transaction,
        "role_for_back_date_transaction":edoor_setting_doc.role_for_back_date_transaction,
        "show_account_code_in_folio_transaction":edoor_setting_doc.show_account_code_in_folio_transaction,
        "backend_port":epos_setting.backend_port,
        "custom_print_format":custom_print_format,
        "currency":{
            "name":currency.name,
            "locale":currency.custom_locale,
            "precision":  currency.custom_currency_precision,
            "symbol": currency.symbol,
            "pos_currency_format": currency.custom_pos_currency_format
        },
        "housekeeping_status":housekeeping_status,
        'reservation_status':reservation_status,
    }

    
    
    user = get_logged_user()
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
        "default_letter_head":property.default_letter_head
    }


    pos_profile = frappe.get_doc("POS Profile",property.default_pos_profile)
    
    edoor_setting["pos_profile"] = {
        "name":pos_profile.name,
        "stock_location":pos_profile.stock_location
    }
    pos_config = frappe.get_doc("POS Config", pos_profile.pos_config)
    edoor_setting["payment_type"] = pos_config.payment_type
    edoor_setting["account_group"] = frappe.db.get_list("Account Code", filters={"parent_account_code":"All Account Code"},fields=["name","account_name","show_in_shortcut_menu","show_in_folio_tab","show_in_deposit_tab","show_in_city_ledger","icon","is_city_ledger_account"], order_by="sort_order")


    return {
        "user":get_logged_user(),
        "working_day": working_day,
        "edoor_setting":edoor_setting,
         
    }

@frappe.whitelist()
def get_logged_user():
    data = frappe.get_doc('User',frappe.session.user)
 
    property = frappe.get_list("Business Branch",fields=["name","property_code","province","email","phone_number_1","photo"])
     
    return {
        "name":data.name,
        "full_name":data.full_name,
        "role":data.role_profile_name,
        "phone_number":data.phone,
        "photo":data.user_image,
        "property":property,
        "roles":frappe.get_roles(frappe.session.user),
        "language":data.language
    }

@frappe.whitelist()
def get_room_chart_data(property,group_by,start_date,end_date):

    


    return []


@frappe.whitelist()
def get_working_day(property = ''):
    working_day = frappe.db.sql("select  posting_date as date,name,pos_profile from `tabWorking Day` where business_branch = '{0}' order by creation desc limit 1".format(property),as_dict=1)
    cashier_shift = None
    if len(working_day)>0:
        data = frappe.db.sql("select creation, shift_name,name from `tabCashier Shift` where business_branch = '{}' and working_day='{}' and pos_profile='{}' ORDER BY creation desc limit 1".format(property,working_day[0]["name"],working_day[0]["pos_profile"]),as_dict=1)
        
        if len(data)>0:
            cashier_shift = data[0]
        
    return {
        "date_working_day": working_day[0]["date"] if len(working_day)>0 else '',
        "name":working_day[0]["name"] if len(working_day)>0 else '',
        "cashier_shift":cashier_shift
    }




@frappe.whitelist()
def get_room_chart_resource(property = '',room_type_group = '', room_type = '',room_number = "",floor="", building = '', view_type='room_type'):
     
    resources = []
    filters = ""
    if room_number:
        filters = filters + " AND `room_number` like '%{}%'".format(room_number)
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
        
        sql = """
            select 
            name,
            room_type,
            sort_order,
            alias,
            (select count(name) from `tabRoom` where room_type_id=rt.name) as total_room
            from 
                `tabRoom Type` rt
            where 
                rt.name in (select room_type_id from `tabRoom` where building=if(%(building)s="",building,%(building)s)) and
                rt.name in (select room_type_id from `tabRoom` where floor=if(%(floor)s="",floor,%(floor)s)) and
                property='{0}'{1}
            
        """
        sql=sql.format(property,filter_room_type)      
        

        filter = {
            "building":building or "",
            "floor":floor or ""
        }
        room_types = frappe.db.sql(sql,filter, as_dict=1)
        
       
        for t in room_types:
            rooms = frappe.db.sql("select name as id, room_number as title, sort_order, housekeeping_status,status_color,housekeeping_icon, 'room' as type from `tabRoom` where room_type_id='{0}' and property='{1}' and disabled = 0 {2}   order by room_number".format(t["name"],property, filters),as_dict=1)
            resources.append({
                "id":t["name"],
                "title":t["room_type"],
                "sort_order":t["sort_order"],
                "alias":t["alias"],
                "type":"room_type",
                "total_room": t["total_room"],
                "children": rooms
            })
    else:
        resources = frappe.db.sql("select name as id,room_type,room_type_alias, room_type_id, room_number as title,sort_order, housekeeping_status,status_color,housekeeping_icon, 'room' as type from `tabRoom` where property='{0}' and  disabled = 0 {1} {2} order by room_number".format( property, filters, ("AND room_type_id = '{}'".format(room_type) if room_type else "")),as_dict=1)
    


    return resources
 


@frappe.whitelist()
def get_room_inventory_resource(property = ''):
    
    resources = []

    resources = frappe.db.sql("select name as id,room_type as title,alias,(select count(name) from `tabRoom` where room_type_id=t.name) as total_room ,sort_order from `tabRoom Type` t where property='{0}'  order by sort_order".format(property),as_dict=1)
    
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
        "id": "arrival_departure",
        "title": "Arrival/Departure",
        "sort_order":1003
    })
    resources.append({
        "id": "pax",
        "title": "PAX (A/C)",
        "sort_order":1004
    })


    return resources
 

@frappe.whitelist()
def get_room_chart_calendar_event(property, start=None,end=None, keyword=None,view_type=None,business_source="",room_type="",room_type_group=None,room_number=None,floor=None,building=None):
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
            concat(start_date,'T',start_time) as start ,
            concat(end_date,'T',end_time) as end,
            guest_name as title,
            status_color as color,
            adult,
            adr,
            child,
            pax,
            reference_number,
            internal_reference_number,
            reservation,
            reservation_color,
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
            total_room_rate,
            note
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
    """
    if room_number:
        sql = sql + " and room_number like   concat('%%' ,  %(room_number)s ,'%%') "
    if keyword:
        # sql = sql + " and ifnull(keyword,'') like  concat('%%' +   %(keywords)s ,'%%') "
        sql = sql + " and concat(ifnull(keyword,''),' ', guest_name) like concat('%%' ,  %(keywords)s ,'%%') "



  
    filter = {
                "property":property, 
                "start":add_to_date( start, days=-1),
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
    occupy_data = []
    if view_type =="room_type":
        sql = """select 
                    room_type_id, 
                    date, 
                    count(name) as total, 
                    sum(if(type='Block',1,0)) as block, 
                    sum(if(type='Reservation' and coalesce(room_id,'')='',1,0)) as unassign_room, 
                    sum(is_arrival) as arrival, 
                    sum(is_departure) as departure,
                    sum(adult) as adult, 
                    sum(child) as child 
                    from `tabRoom Occupy` 
                where 
                    property=%(property)s and 
                    date between %(start)s and %(end)s and 
                    room_type_id = if(%(room_type_id)s='',room_type_id, %(room_type_id)s)  and 
                    room_type_id in (select name from `tabRoom Type` where room_type_group=if(%(room_type_group)s='',room_type_group,%(room_type_group)s)) 


                group by 
                    room_type_id, 
                date"""
        occupy_data = frappe.db.sql(sql,filter,as_dict=1)
         

    #get event from room block
    events = events +  get_room_block_event(add_to_date(start, days=-1),end,property)
    

    return {"events":events,"occupy_data":occupy_data}

@frappe.whitelist()
def get_room_inventory_calendar_event(property, start=None,end=None, keyword=None):
     
    sql = "select room_type_id, date, count(name) as total, sum(if(type='Block',1,0)) as block, sum(is_arrival) as arrival, sum(is_departure) as departure,sum(adult) as adult, sum(child) as child from `tabRoom Occupy` where property='{}' and date between '{}' and '{}' group by room_type_id, date".format(property,start,end)
    data = {
        "room_occupy": frappe.db.sql(sql,as_dict=1)
    }
    return data
   

@frappe.whitelist()
def get_room_block_event(start,end,property):
    sql = """
        select 
            name as id, 
            room_id as resourceId,
            room_number,
            concat(start_date,'T12:00:00') as start ,
            concat(end_date,'T12:00:00') as end,
            'Room Block' as title,
            status_color as color,
            reason,
            'room_block' as type,
            owner as block_by,
            0 as editable

        from 
            `tabRoom Block` 
        where 
            docstatus = 1   and 
            is_unblock = 0 and
            name in (
                select distinct stay_room_id from `tabRoom Occupy` where date between '{}' and '{}' 
            ) and 
            property = '{}'

    """
    sql = sql.format(
            getdate(start), 
            getdate(end)
            ,property)
  
    data = frappe.db.sql(sql, as_dict=1)
    
    for d in data:
        d["editable"] = d["editable"]  == 1
    
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

        future_arrival_data = get_future_arrival_data(
                                property,
                                future_dates[0].strftime('%Y-%m-%d'),
                                future_dates[len(future_dates)-1].strftime('%Y-%m-%d')
                            )
        
        future_departure_data = get_future_departure_data(
                                property,
                                future_dates[0].strftime('%Y-%m-%d'),
                                future_dates[len(future_dates)-1].strftime('%Y-%m-%d')
                            )

    return events

 
def get_future_arrival_data(property,start,end):
    #get arrival and departure event
    sql = """
            select 
                arrival_date as date,
                count(name) as total_room
            from `tabReservation Stay` 
            where 
                is_active_reservation = 1 and 
                property = '{}' and 
                arrival_date between '{}' and '{}'  
            group by
                arrival_date

        """
    sql = sql.format(
            property, 
            start,
            end
        )
    
def get_future_departure_data(property,start,end):
    #get arrival and departure event
    sql = """
            select 
                departure_date as date,
                count(name) as total_room
            from `tabReservation Stay` 
            where 
                is_active_reservation = 1 and 
                property = '{}' and 
                departure_date between '{}' and '{}'  
            group by
                departure_date

        """
    sql = sql.format(
            property, 
            start,
            end
        )
    
 

    
    return  frappe.db.sql(sql,as_dict=1)
@frappe.whitelist(methods="POST")
def validate_run_night_audit(property,step):
    working_day = get_working_day(property)
    if step ==2:
        #valdate if have check room vaivable
        sql="select name from `tabReservation Stay` where is_active_reservation=1 and reservation_status in ('Confirmed','Reserved') and arrival_date='{}' and property='{}' limit 1".format(working_day["date_working_day"],property)
        data = frappe.db.sql(sql, as_dict=1)
        if data:
            frappe.throw("Please check in or cancel the Confirmed and Reserved")
    elif step==3:
        #validate check out guest
        sql="select name from `tabReservation Stay` where is_active_reservation=1 and reservation_status in ('In-house','Reserved','Confirmed') and departure_date='{}' and property='{}' limit 1".format(working_day["date_working_day"], property)
        data = frappe.db.sql(sql, as_dict=1)
        if data:
            frappe.throw("Please check out all reservation")
    elif step==4:
        sql="select name from `tabReservation Room Rate` where date = date_add('{}', interval 1 day) and property='{}' limit 1".format(working_day["date_working_day"], property)
        data = frappe.db.sql(sql, as_dict=1)
        return True if data else False
    elif step == 5:
        sql="select name from `tabFolio Transaction` where posting_date = '{}'  and property='{}' and ifnull(parent_reference,'') = '' and is_auto_post = 0 limit 1".format(working_day["date_working_day"], property)
        data = frappe.db.sql(sql, as_dict=1)
        return True if data else False
    elif step == 6:
        sql="select name from `tabCashier Shift` where posting_date = '{}'  and business_branch='{}' and is_closed = 0 limit 1".format(working_day["date_working_day"], property)
        data = frappe.db.sql(sql, as_dict=1)
        if  data:
            frappe.throw("Please close all cashier shift")
    return False

@frappe.whitelist(methods="POST")
def run_night_audit(property, working_day):
    
    #1. Validate working day is still open
    #2. Validate cashier shift open
    #3. validate arrival to check in 
    #3. validate departure to check out 
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
     

    doc_cashier_shift = frappe.get_doc(  {
            "doctype":"Cashier Shift",
            "working_day": new_working_day.name,
            "shift_name": frappe.db.get_default("shift_name_after_run_night_audit"),
            "pos_profile": doc_property.default_pos_profile,
            "cash_float":cash_float
        }
    ).insert()

    #Remove room occupy for no show folio that reserved room

    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_status='No Show' and property=%(property)s and date<=%(date)s", {"property":property, "date":doc_working_day.posting_date})
    frappe.db.sql("delete from `tabRoom Occupy` where reservation_status='No Show' and property=%(property)s and date<=%(date)s", {"property":property, "date":doc_working_day.posting_date})

    #queue post room change to folio

    #post_room_change_to_folio(new_working_day)
    frappe.enqueue("edoor.api.frontdesk.post_room_change_to_folio", queue='short', working_day=new_working_day)

    #update room status after runight auit
    # update_room_status(new_working_day)
    frappe.enqueue("edoor.api.frontdesk.update_room_status", queue='short', working_day=new_working_day)

    
    return property

@frappe.whitelist()
def update_room_status(working_day=None):
    #1. update stay over guesty
    stay_over_room = frappe.db.sql("""
                            select 
                                name 
                            from `tabRoom` 
                            where 
                                ifnull(reservation_stay,'')<>'' and 
                                property='{}' 
                    """.format(working_day.business_branch),as_dict=1)
    room_status = frappe.db.get_default("housekeeping_status_after_run_night_audit")
    
    for r in stay_over_room:
        room_doc = frappe.get_doc("Room", r["name"])
        room_doc.housekeeping_status = room_status
        room_doc.save()

    #update room status that end block
    sql = "select room_id from `tabRoom Block` where docstatus=1 and is_unblock=0 and end_date='{}' and property='{}'".format(working_day.posting_date ,working_day.business_branch)
    data = frappe.db.sql(sql,as_dict=1)


    for d in data:
        room_doc = frappe.get_doc("Room", d["room_id"])
        room_doc.housekeeping_status = frappe.db.get_default("hk_status_rb_release_after_audit")
        room_doc.save()
    

    #2 update room status of room block
    room_block = frappe.db.sql("select room_id from `tabTemp Room Occupy` where type='Block' and property='{}' and date='{}'".format(working_day.business_branch, working_day.posting_date),as_dict=1)
    
    room_status = frappe.db.get_default("room_block_status")
    for r in room_block:
        room_doc = frappe.get_doc("Room", r["room_id"])
        room_doc.housekeeping_status = room_status
        room_doc.save()

    

    
   
    frappe.db.commit()
    

@frappe.whitelist()
def post_room_change_to_folio(working_day):
    
    room_rates = frappe.db.get_list("Reservation Room Rate",fields=["*"] , filters={"property":working_day.business_branch,"date":working_day.posting_date})

    for r in room_rates:
        stay_doc = frappe.get_doc("Reservation Stay",r.reservation_stay)
        if stay_doc.is_active_reservation==1:
            folio = None
            if stay_doc.paid_by_master_room == 0:
                master_folios = frappe.db.get_list("Reservation Folio",fields=["*"],filters={"reservation_stay":r.reservation_stay,"is_master":1})
                if master_folios:
                    folio = master_folios[0]
            else:
                folio = get_master_folio(r.reservation)
            
            if folio:
                add_room_charge_to_folio(folio, r)

    
    #verify if reservation stay and and reservation is update balance


