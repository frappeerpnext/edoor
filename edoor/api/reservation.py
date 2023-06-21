import json
from py_linq import Enumerable
import re
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import update_reservation_stay,update_reservation
import frappe
from frappe.utils.data import add_to_date


@frappe.whitelist()
def test():
    data = frappe.db.get_all("Account Code", filters={"parent_account_code":"1000"}, order_by='lft')
    return data

@frappe.whitelist()
def get_reservation_detail(name):
    reservation= frappe.get_doc("Reservation",name)
    reservation_stays = frappe.get_list("Reservation Stay",filters={'reservation': name},fields=['name','room_type_alias','guest','total_charge','balance','total_payment','reservation_status','status_color','guest_name','pax','child','adult','adr_rate', 'reference_number','arrival_date','arrival_time','departure_date','departure_time','room_types','rooms'])
    master_guest = frappe.get_doc("Customer",reservation.guest)
    return {
        "reservation":reservation,
        "reservation_stays":reservation_stays,
        "master_guest": master_guest
    }


@frappe.whitelist()
def get_reservation_stay_detail(name):
    reservation_stay= frappe.get_doc("Reservation Stay",name)
    
    reservation = frappe.get_doc("Reservation",reservation_stay.reservation)
    total_reservation_stay = frappe.db.count("Reservation Stay", {'reservation': reservation.name})
    guest=frappe.get_doc("Customer",reservation_stay.guest)

    reservation_stay_names =frappe.get_all("Reservation Stay",filters={"reservation":reservation_stay.reservation},order_by="name", page_length=10000,pluck='name')
    

    master_guest = guest
    if reservation.guest != reservation_stay.guest:
        master_guest = frappe.get_doc("Customer",reservation.guest)
    return {
        "reservation":reservation,
        "total_reservation_stay": total_reservation_stay,
        "reservation_stay":reservation_stay,
        "guest":guest,
        "master_guest":master_guest,
        "reservation_stay_names":reservation_stay_names
    }

@frappe.whitelist()
def get_folio_detail(name):
    
    doc = frappe.get_doc("Folio Transaction",name)
    account_code = frappe.get_doc("Account Code", doc.account_code)
    return {"doc":doc, "account_code": account_code}

@frappe.whitelist()
def check_room_availability(property,room_type_id=None,start_date=None,end_date=None):
    end_date = add_to_date(end_date,days=-1)
    if not room_type_id:
        room_type_id = ''

    sql = """
        select 
            distinct
            room_type_id,
            room_type,
            name,
            room_number
        from `tabRoom` 
        where 
            property = '{0}' and 
            room_type_id = if('{1}'='', room_type_id, '{1}') and
            name not in (
                select 
                    distinct
                    coalesce(room_id,'') 
                from `tabTemp Room Occupy` 
                where
                    date between '{2}' and '{3}' 
            )   
    """

    sql = sql.format(property,room_type_id,start_date, end_date)
     
    data = frappe.db.sql(sql,as_dict=1)
    return data

@frappe.whitelist()
def check_room_type_availability(property,start_date=None,end_date=None,rate_type=None, business_source=None):
    end_date = add_to_date(end_date,days=-1)
    #get all room type and total room 

    room_type = frappe.db.sql("select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property='{}' group by room_type_id,room_type".format(property),as_dict=1)
    for t in room_type:
        sql = "select coalesce(count(  distinct room_id),0) as total_room from `tabTemp Room Occupy` where room_type_id = '{}' and date between '{}' and '{}'".format(t["name"],start_date,end_date)
        t["occupy"] = frappe.db.sql(sql,as_dict=1)[0]["total_room"]
        t["rate"] = get_room_rate(property, rate_type, t["name"], business_source, start_date)

    return  [d for d in room_type if d['total_room'] - d["occupy"] > 0]
 


@frappe.whitelist()
def add_new_fit_reservation(doc):
    
    doc = json.loads(doc)
    #check if not have guest selected then create new guest

    if not check_field(doc["reservation"],"guest"):
        guest = frappe.get_doc(doc["guest_info"]).insert()
        doc["reservation"]["guest"] = guest.name
    else:
        guest = frappe.get_doc(doc["guest_info"]).save()
    
    #prevent code call on_pdate to reservation stay
    doc["update_reservation_stay"] = False
    reservation = frappe.get_doc(doc["reservation"]).insert()
    
    #start insert insert reservation stay
    i = 0
    stay_names = []
    # set first stay as master room 
    doc["reservation_stay"][0]["is_master"] = 1
    for   d in doc["reservation_stay"]:
      
        room = None
        if   'room_id' in d.keys():
            room = d["room_id"]
        #set virtural attribute field to update reservation after all stay is add to database
        
        update_reservation = False
        if i ==len(doc["reservation_stay"])-1:
            update_reservation = True

        stay = {
            "doctype":"Reservation Stay",
            "update_reservation":update_reservation,
            "reservation":reservation.name,
            "reservation_status":"Reserved",
            "arrival_time":reservation.arrival_time,
            "departure_time":reservation.departure_time,
            "note":reservation.note,
            "stays":[
                {
                    "doctype":"Reservation Stay Room",
                    "room_type_id": d["room_type_id"],
                    "room_id":room,
                    "rate":d["rate"] or 0,
                    "guest":reservation.guest,
                    "reservation_status":"Reserved",
                    
                    "start_date":reservation.arrival_date,
                    "end_date":reservation.departure_date,
                    "start_time":reservation.arrival_time,
                    "end_time":reservation.departure_time,

                    "is_manual_rate":d["is_manual_rate"]
                }
            ]
        }

        stay_doc = frappe.get_doc(stay).insert()
        stay_names.append(stay_doc.name)

        
        i=i+1

    #update summary to reservation stay
    for s in stay_names:
        update_reservation_stay(s, run_commit=False)

    #udpate summary to reservation 
    #pending todo
    frappe.db.commit()
    return reservation

@frappe.whitelist(methods="POST")
def check_in(reservation,reservation_stays=None):
    #reservation_stays is list of stay in a reservation separate by comma
    #reservation_stays is apply then we skip check reservation 
    doc = frappe.get_doc("Reservation",reservation)
    working_day = get_working_day(doc.property)
   
    if not working_day["cashier_shift"]:
        frappe.throw("There is no cashier shift open. Please open cashier shift first")

    
    
   
    stays = []
    if not reservation:
        frappe.throw("There is no reservation to check in")

    if reservation_stays:
        stays = reservation_stays.split(',')
    else:
        stays = frappe.get_list("Reservation Stay",filters={"reservation":reservation},limit=100) # limit 100 to prevent reservation that have more than 20 stay
    

    for s in stays:
        stay = frappe.get_doc("Reservation Stay", s)
        if stay.reservation_status=="Inhouse":
            frappe.throw("Stay #: {}. Room: {}. This room is already checkin.".format(stay.name, stay.rooms))

      
        if str(stay.arrival_date) != str(working_day["date_working_day"]):
            frappe.throw("Stay #: {}. Room: {}. Arrival date must be equal to current date.".format(stay.name, stay.rooms))

        stay.reservation_status = "Inhouse"
        stay.save()

    frappe.db.commit()

    return {
        "reservation":doc
    }



@frappe.whitelist()
def change_reservation_guest( guest, reservation='',reservation_stay='', is_apply_all_stays='false', is_apply_master_guest='false', is_only_master_guest='false'):
    doc_guest = json.loads(guest)
    #check if not have guest selected then create new guest
    if doc_guest.get("name") is None:
        guest_info = frappe.get_doc(doc_guest).insert()
    else:
        guest_info = frappe.get_doc(doc_guest).save()
    
    # update master guest
    if(is_apply_master_guest == 'true' or is_only_master_guest == 'true'):
        reservation_doc = frappe.get_doc('Reservation', reservation)
        reservation_doc.guest = guest_info.name
        reservation_doc.save()

    # update only stay
    if(is_only_master_guest == 'false'):
        if(is_apply_all_stays == 'false'):
            reservation_stay_doc = frappe.get_doc('Reservation Stay', reservation_stay)
            reservation_stay_doc.guest = guest_info.name
            reservation_stay_doc.save()
        else:
            reservation_stays = frappe.get_list('Reservation Stay',filters={"reservation":reservation})
            for s in reservation_stays:
                reservation_stay_doc = frappe.get_doc('Reservation Stay', s)
                reservation_stay_doc.guest = guest_info.name
                reservation_stay_doc.save()
    frappe.db.commit()
    return {
        'guest': guest_info
    }
    
@frappe.whitelist()
def change_reservation_additional_guest(guest,reservation_stay):
 
    doc_guest = json.loads(guest)
    guest_name = ''
    if doc_guest.get("name") is None:
        doc_guest = json.loads(guest)
        doc_guest = frappe.get_doc(doc_guest).insert()
        guest_name = doc_guest.name
    else:
        guest_info = frappe.get_doc(doc_guest).save()
        guest_name = guest_info.name
    doc_stay = frappe.get_doc('Reservation Stay', reservation_stay)
    if doc_stay.guest == guest_name:
        frappe.throw('This guest is already selected.')
    for i in doc_stay.additional_guests:
        if i.guest ==guest_name or i.guest == doc_stay.guest:
            frappe.throw('This guest is already selected.')
            # return {
            #     'status': 406,
            #     'message': 'This guest is already selected.'
            # }
    
    doc_stay.append('additional_guests',{'guest':guest_name})
    doc_stay = doc_stay.save()
    frappe.db.commit()
    return {
        'result': doc_stay
    }


def check_field(doc, key):
    if key in doc.keys():
        if  doc[key].strip():
            return True
    return False 



@frappe.whitelist()
def get_reservation_guest(reservation=None, reservation_stay=None):
    sql = """
            select guest as name, guest_name from `tabReservation` where name='{0}'
            union 
            select guest as name, guest_name from `tabReservation Stay` where name='{1}' 
            union 
            select guest as name, guest_name from `tabAdditional Stay Guest` where parent='{1}' 
        """
    sql = sql.format((reservation or ''), (reservation_stay or ''))
    return frappe.db.sql(sql, as_dict=1)

@frappe.whitelist()
def get_reservation_folio(reservation=None, reservation_stay=None):
    sql = """
            select 'all' as name , 'All Folio' as folio
            union
            select name, name as folio from `tabReservation Folio`
            union 
            select name, name as folio from `tabReservation Folio`
        """
    # sql = sql.format((reservation or ''), (reservation_stay or ''))
    return frappe.db.sql(sql, as_dict=1)


@frappe.whitelist()
def get_room_rate(property, rate_type, room_type, business_source, date):
    sql = "select name from `tabSeason` where '{}' between start_date and end_date limit 1".format(date)
    season = frappe.db.sql (sql, as_dict=1)

    room_type_rate  = frappe.get_value("Room Type", room_type,"rate")
    rate = 0
   
    if season and rate_type:
        season_id = season[0]["name"]
       
        sql = """select 
                    max(rate) as rate 
                from `tabRate Plan` 
                where 
                    property='{}' and
                    season = '{}' and 
                    rate_type = '{}' 
                """.format(property, season_id, rate_type)
     
        if business_source:
            sql_with_business_source = "{} and business_source = '{}'".format(sql, business_source)
            data = frappe.db.sql(sql_with_business_source, as_dict=1)
            rate = data[0]["rate"] or 0
            
        if rate ==0:
            data = frappe.db.sql(sql, as_dict=1)
            rate = data[0]["rate"] or 0
            
    if rate == 0:
        rate = room_type_rate
    return rate


#@frappe.whitelist(methods="POST")
@frappe.whitelist()
def change_rate_type(property=None,reservation=None, reservation_stay=None, rate_type = None, apply_to_all_stay = None,regenerate_new_rate=None):
    working_day = get_working_day(property)
    #get reservation room rate
    #udpate to reservation room rate
    room_rates = []
    active_stays = []
    if reservation_stay:
        stay = frappe.get_doc("Reservation Stay", reservation_stay)
        if not stay.is_active_reservation:
            frappe.throw("Reservation stay # {} is not an active reservation".format(reservation_stay))
        
        if   stay.reservation_status=='Checked Out':
            frappe.throw("Reservation stay # {} is already checked out".format(reservation_stay))
        
        active_stays.append(reservation_stay)

    if apply_to_all_stay:
        active_stays = frappe.get_all("Reservation Stay",filters={"is_active_reservation":1,"reservation":reservation}, page_length=10000,pluck='name')
        
    room_rates = frappe.get_all("Reservation Room Rate",
                                filters={
                                            "reservation_stay":['in',active_stays],
                                            "date":['>=',working_day["date_working_day"]]
                                }, page_length=10000)
    for r in room_rates:
        
        doc = frappe.get_doc("Reservation Room Rate",r.name)
        doc.rate_type = rate_type
        doc.regenerate_rate = regenerate_new_rate
        doc.save()

    #update rate type to reservation stay
    for s in active_stays:
        if s != stay.name:
            doc = frappe.get_doc("Reservation Stay",s)
            doc.rate_type = rate_type
            doc.update_reservation = False
            update_reservation_stay(doc=doc, run_commit = False)

        
    stay.rate_type = rate_type
    #disable update to reservation when update stay
    stay_doc = update_reservation_stay(doc=stay, run_commit = False)
     
    #update rate type to reservation 
    reservation_doc = update_reservation(name=reservation,run_commit=False)
    

    frappe.db.commit()
    if reservation_stay:
        return stay_doc
    else:
        return reservation_doc


@frappe.whitelist()
def get_current_room_reservation(room_id):

    sql = "select parent from `tabReservation Stay Room` where room_id='{}' and '{}' between start_date and end_date and is_active_reservation=1"
    sql = sql.format(room_id,frappe.utils.today() )
    data = frappe.db.sql(sql, as_dict=1)

@frappe.whitelist()
def get_reservation_comment_note(doctype, docname):
    sql = """
        SELECT `name`, creation, reference_doctype, reference_name,`owner`, content, 'Notice' AS note_type FROM `tabFrontdesk Note` WHERE reference_doctype ='{0}' AND reference_name = '{1}'
        UNION
        SELECT `name`, creation, reference_doctype, reference_name,comment_by AS owner, content, 'Comment' AS note_type FROM `tabComment` WHERE comment_type = 'Comment' AND reference_doctype ='{0}' AND reference_name = '{1}'
    """
    sql = sql.format(doctype, docname)
    data = frappe.db.sql(sql, as_dict=1)
    return data

@frappe.whitelist(methods="POST")
def update_note(data):
    note = '' if data.get("note") is None else data['note']
    housekeeping_note = '' if data.get("housekeeping_note") is None else data['housekeeping_note']

    doc = frappe.get_doc(data['doctype'], data['name'])
    doc.note = note
    doc.housekeeping_note = housekeeping_note
    doc.save()

    # apply reservation
 
    if(data['is_apply_reseration']):
        reseration = frappe.get_doc('Reservation', data['reservation'])
        reseration.note = note
        reseration.housekeeping_note = housekeeping_note
        reseration.save() 
        
    # apply all stays
    if(data['is_apply_all_stays']):
        reservation_stays = frappe.get_list('Reservation Stay',filters={"reservation":data['reservation']})
        for s in reservation_stays:
            reservation_stay_doc = frappe.get_doc('Reservation Stay', s)
            reservation_stay_doc.note = note
            reservation_stay_doc.housekeeping_note = housekeeping_note
            reservation_stay_doc.save()

    frappe.db.commit()
    return doc
    
@frappe.whitelist()
def get_audit_trail(doctype, docname):
    sql = """
        SELECT `name`,'Version' AS `type`, '' AS comment_type, creation,`owner`,`data` AS `content`   FROM `tabVersion` WHERE ref_doctype = '{0}' AND docname = '{1}'
        UNION
        SELECT `name`,'Frontdesk Note' AS `type`, '' AS comment_type, creation,`owner`, `content` AS `content` FROM `tabFrontdesk Note` WHERE reference_doctype = '{0}' AND reference_name = '{1}'
        UNION
        SELECT `name`,'Comment' AS `type`, comment_type, creation, COALESCE(comment_by,modified_by) AS `owner`, `content` AS `content` FROM `tabComment` WHERE reference_doctype = '{0}' AND reference_name = '{1}'
        UNION
        SELECT `name`, 'Folio Transaction' AS `type`, '' AS comment_type, creation, `owner`, CONCAT('Add ', account_name) AS `content` FROM `tabFolio Transaction` WHERE reservation_stay = '{1}'
    """
    sql = sql.format(doctype, docname)
    data = frappe.db.sql(sql, as_dict=1)
    return data

@frappe.whitelist()
def get_audit_test(doctype, docname):
    sql = """
        SELECT `name`,'Version' AS `type`, '' AS comment_type, creation,`owner`,`data` AS `content`   FROM `tabVersion` WHERE ref_doctype = '{0}' AND docname = '{1}'
        UNION
        SELECT `name`,'Frontdesk Note' AS `type`, '' AS comment_type, creation,`owner`, `content` AS `content` FROM `tabFrontdesk Note` WHERE reference_doctype = '{0}' AND reference_name = '{1}'
        UNION
        SELECT `name`,'Comment' AS `type`, comment_type, creation, COALESCE(comment_by,modified_by) AS `owner`, `content` AS `content` FROM `tabComment` WHERE reference_doctype = '{0}' AND reference_name = '{1}'
        UNION
        SELECT `name`, 'Folio Transaction' AS `type`, '' AS comment_type, creation, `owner`, CONCAT('Add ', account_name) AS `content` FROM `tabFolio Transaction` WHERE reservation_stay = '{1}'
    """
    sql = sql.format(doctype, docname)
    data = frappe.db.sql(sql, as_dict=1)

    meta = frappe.get_meta(doctype)
    def get_label(key):
        if(meta.fields and len(meta.fields) > 0):
            field = Enumerable(meta.fields).single_or_default(lambda r:r.fieldname == key)
            if field:
                return field.label
            return ''
    def get_text(t):
        tag = re.compile(r'<[^>]+>')
        text = tag.sub('',str(t))
        text = text if len(text) <= 20 else text.rstrip(text[-20]) + '...'
        return "<b>{}</b>".format(text)

    result = []
    for record in data:
        prefix = 'You' if record.owner == frappe.session.user else record.owner
        if(record.type == 'Version'):
            content = json.loads(record.content)
            
            if(len(content['added']) > 0):
                addeds = []
                description = ''
                for add in content['added']:
                    pro_list = []
                    for key, value in add[1].items():
                        pro_list.append({'property': key, 'value': value})
                    property = get_label(add[0])
                    description = description + property + ', '
                    addeds.append({'property':property, 'value': pro_list})
                record['added'] = addeds
                record['description'] = "{0} added rows for {1}".format(prefix, description)
            elif len(content['changed']) > 0:
                pro_list = []
                description = ''
                count_result = 0
                for c in content['changed']:
                    meta_key = Enumerable(meta.fields).single_or_default(lambda r:r.fieldname == c[0])
                    if meta_key.fieldtype != 'JSON' and meta_key.fieldtype != 'Code' and meta_key.fieldtype != 'HTML' and not meta_key.hidden:
                        count_result = count_result + 1
                        pro_list.append({
                            'property': meta_key.label,
                            'original_value': c[1],
                            'new_value': c[2],
                        })
                        if count_result <= 3:
                            description = description + "{0} from {1} to {2}, ".format(meta_key.label, get_text(c[1]), get_text(c[2]))
                    return pro_list
                    c['changed'] = json.dumps(json.loads(pro_list))
                    # c['description'] = "{0} changed the value of {1}".format(prefix, description.rstrip(description[-2]))
                    return c
    return 1


