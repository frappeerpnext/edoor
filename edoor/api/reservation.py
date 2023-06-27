from datetime import datetime
import json
from edoor.edoor.doctype.reservation_stay.reservation_stay import change_room_occupy
from py_linq import Enumerable
import re
from edoor.api.frontdesk import get_working_day
from edoor.api.utils import update_reservation_stay,update_reservation
import frappe
from frappe.utils.data import add_to_date, getdate


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
def get_reservation_charge_summary(reservation = None, reservation_stay = None,folio_number = None):
    search_field = "reservation"
    search_value = reservation
    if reservation_stay:
        search_field = "reservation_stay"
        search_value = reservation_stay
    elif folio_number:
        search_field = "folio_number"
        search_value = folio_number

    
    sql = """
        select 
            account_category,
            account_category_sort_order, 
            sum(amount * if(type='Debit',1,-1)) as amount 
        from `tabFolio Transaction` 
        where 
            {} = '{}' 
        group by 
            account_category 
        order by account_category_sort_order
     """.format(
        search_field,
        search_value
    )
     
    return frappe.db.sql(sql, as_dict=1)

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
def check_room_type_availability(property,start_date=None,end_date=None,rate_type=None, business_source=None, room_type_id=None):
    end_date = add_to_date(end_date,days=-1)
    #get all room type and total room 

    room_type = frappe.db.sql("select room_type_id as name, room_type, count(name) as total_room, 0 as occupy from `tabRoom` where disabled = 0 and property='{}' group by room_type_id,room_type".format(property),as_dict=1)
    for t in room_type:
        # sql = "select coalesce(count(  distinct room_id),0) as total_room from `tabTemp Room Occupy` where room_type_id = '{}' and date between '{}' and '{}'".format(t["name"],start_date,end_date)
        sql = "SELECT COUNT(name) as total_room_type, date from `tabTemp Room Occupy` where room_type_id = '{}' and date between '{}' and '{}' GROUP BY date;".format(t["name"],start_date,end_date)
        room_type_occupy = frappe.db.sql(sql,as_dict=1)

        if room_type_occupy and room_type_id != t['name']:
            is_not_availible = Enumerable(room_type_occupy).where(lambda x:x.total_room_type >= t['total_room'])
            if is_not_availible:
                t["occupy"] = t["total_room"]
        # t["occupy"] = frappe.db.sql(sql,as_dict=1)[0]["total_room"]
        t["rate"] = get_room_rate(property, rate_type, t["name"], business_source, start_date)

    return  [d for d in room_type if d['total_room'] - d["occupy"] > 0]
@frappe.whitelist()
def check_room_occupy(property, room_id, start_date=None, end_date=None, reservation_stay=None):
    end_date = add_to_date(end_date,days=-1)
    except_stay = ""
    if reservation_stay:
        except_stay = " AND reservation_stay <> '{}'".format(reservation_stay)
    room_occupy = frappe.db.sql("SELECT COUNT(name) AS total FROM `tabTemp Room Occupy` WHERE property='{4}' AND room_id = '{0}' AND DATE BETWEEN '{1}' AND '{2}'{3}".format(room_id,start_date,end_date,except_stay,property))
    return room_occupy[0][0]


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
    if reservation:
        sql = """
                #select 'all' as name , 'All Folio' as folio
                #union
                select name, name as folio from `tabReservation Folio` where reservation='{}'
            """.format(reservation)
        return frappe.db.sql(sql, as_dict=1)
    else:
        sql = """
                #select 'all' as name , 'All Folio' as folio
                #union
                select name, name as folio from `tabReservation Folio` where reservation_stay='{}'
            """.format(reservation_stay)
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
def change_stay(data):
    room_occupy = check_room_occupy(property=data['property'],room_id=data['room_id'],start_date=data['start_date'],end_date=data['end_date'],reservation_stay=data['parent'])
    if room_occupy:
        frappe.throw("Room not avaible")
    else:
        doc = frappe.get_doc("Reservation Stay",data['parent'])
        doc.update_reservation_stay = True
        doc.update_room_occupy = True
        stays = Enumerable(doc.stays).order_by(lambda x:datetime.strptime(str(x.start_date), '%Y-%m-%d').date()).to_list()

        for s in stays:
            if s.name == data['name']:
                s.start_date = data['start_date']
                s.end_date = data['end_date']
            # change last stay room for start date
            index = stays.index(s) + 1
            if len(stays) > index and stays[index]:
                stays[index].start_date = s.end_date
        doc.save()
        frappe.db.commit()
        return doc

@frappe.whitelist(methods="DELETE")
def delete_stay_room(parent,name, note):
    stay = frappe.get_doc('Reservation Stay', parent)
    deleted_row = None
    for p in stay.stays:
        if p.name == name:
            p.deleted_note = note or ""
            deleted_row = p
    stay.save()
    stay.remove(deleted_row)
    stay.update_reservation_stay = True
    stay.update_room_occupy = True
    stay.save()
    frappe.db.commit()
    return stay
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
    # stay room rate
    stay_room_rates = []
    meta_room_rate = None
    stay_names = "'{}'".format(docname)
    if doctype == 'Reservation':
        reservation_stays = frappe.db.get_list('Reservation Stay', filters={'reservation': docname})
        for r in reservation_stays:
            stay_names = stay_names + ",'{}'".format(r.name)
            room_rate = frappe.db.get_list('Reservation Room Rate',fields=['name', 'reservation','reservation_stay'], filters={'reservation_stay': r.name})
            stay_room_rates = stay_room_rates + room_rate
    else:
        room_rate = frappe.db.get_list('Reservation Room Rate',fields=['name', 'reservation','reservation_stay'], filters={'reservation_stay': docname})
        stay_room_rates = stay_room_rates + room_rate
    sql_room_rate = ""
    if len(stay_room_rates) > 0:
        meta_room_rate = frappe.get_meta("Reservation Room Rate")
        for rr in stay_room_rates:
            sql_room_rate = sql_room_rate + "'{}',".format(rr.name)
    if sql_room_rate:
        sql_room_rate = ",{}".format(sql_room_rate[:-1])
    sql = """
        SELECT `name`,docname AS `docname`, ref_doctype AS `doctype`, 'Version' AS `type`, '' AS comment_type, creation,`owner`,`data` AS `content`   FROM `tabVersion` WHERE docname IN({0}{1})
        UNION
        SELECT `name`,reference_name AS `docname`,reference_doctype AS `doctype`, 'Frontdesk Note' AS `type`, '' AS comment_type, creation,`owner`, `content` AS `content` FROM `tabFrontdesk Note` WHERE reference_name IN({0})
        UNION
        SELECT `name`,reference_name AS `docname`, reference_doctype AS `doctype`, 'Comment' AS `type`, comment_type, creation, COALESCE(comment_by,modified_by) AS `owner`, `content` AS `content` FROM `tabComment` WHERE reference_name IN({0})
        UNION
        SELECT `name`,reservation_stay AS `docname`, '' AS `doctype`, 'Folio Transaction' AS `type`, '' AS comment_type, creation, `owner`, CONCAT('Add ', account_name) AS `content` FROM `tabFolio Transaction` WHERE reservation_stay IN({0})
        UNION
        SELECT `name`,reference_name AS `docname`, reference_doctype AS `doctype`, 'Comment' AS `type`, 'Deleted Folio' AS comment_type, creation,COALESCE(comment_by,modified_by) AS `owner`, CONCAT(reservation,'|',reservation_stay,'|',reservation_folio,'|',folio_number,'|',deleted_document,'|',reason) AS `content` FROM `tabComment` WHERE comment_type = 'Deleted' AND reservation_stay IN({0})
    """

    sql = sql.format(stay_names,sql_room_rate)
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
    def get_option(key):
        if(meta.fields and len(meta.fields) > 0):
            field = Enumerable(meta.fields).single_or_default(lambda r:r.fieldname == key)
            if field:
                return field.options
            return ''
        
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
                changed_other_doc = ''
                meta_fields = []
                if record['doctype'] == 'Reservation Room Rate':
                    changed_other_doc = " in <b>#{}</b>".format(record['doctype'])
                    meta_fields = meta_room_rate.fields
                else:
                    meta_fields = meta.fields
                for c in content['changed']:
                    meta_key = Enumerable(meta_fields).single_or_default(lambda r:r.fieldname == c[0])
                    if hasattr(meta_key,'fieldtype') and (meta_key.fieldtype != 'JSON' and meta_key.fieldtype != 'Code' and meta_key.fieldtype != 'HTML') and not meta_key.hidden:
                        count_result = count_result + 1
                        pro_list.append({
                            'property': meta_key.label,
                            'original_value': c[1],
                            'new_value': c[2],
                        })
                        if count_result <= 3:
                            description = description + "{0} from {1} to {2}, ".format(meta_key.label, get_text(c[1]), get_text(c[2]))

                record['changed'] = pro_list 
                record['description'] = "{0} changed the value of {1}{2}".format(prefix, description[:-2],changed_other_doc)
            elif len(content['row_changed']) > 0:
                pro_list = []
                for r in content['row_changed']:
                    pro_list.append({
                        'property': r[0],
                        'index': r[1],
                        'name': r[2],
                        'feilds': r[3]
                    })
                
                groups = Enumerable(pro_list).distinct(lambda x: x['property'])
                group_list = [] 
                for g in groups: 
                    group_list.append({
                        'property': g['property'],
                        'rows': Enumerable(pro_list).where(lambda x: x['property'] == g['property'])
                    })
                description = "{} changed the values for ".format(prefix)
                for g in group_list:
                    description = description + "{} in row ".format(get_label(g['property']))
                    for r in g['rows']:
                        description = description + "#{}, ".format(r['index'])
                record['row_changed'] = group_list
                record['description'] = description[:-2]
            elif len(content['removed']) > 0:
                description = prefix + " removed rows for "
                
                for r in content['removed']:
                    pro_list = []
                    description = description + "{}, ".format(get_label(r[0]))
                    objs = []
                    for key, value in r[1].items():
                        objs.append({'property': key, 'value': value})
                    pro_list.append({
                        'property': get_label(r[0]),
                        'options': get_option(r[0]),
                        'value': objs
                    })
                record['removed'] = pro_list
                record['description'] = description.rstrip(description[-2]) if len(description) > 2 else description
            result.append(record)
        else:
            result.append(record)
    return result


@frappe.whitelist()
def get_folio_transaction(folio_number):
    show_account_code = frappe.db.get_default("show_account_code_in_folio_transaction") ==1
    
    data = frappe.db.sql("select * from `tabFolio Transaction` where folio_number='{}' and coalesce(parent_reference,'')=''".format(folio_number),as_dict=1)

    balance = 0
    folio_transactions = []
    for d in data:
        if  d.bank_fee_amount > 0:
            balance = balance + d.bank_fee_amount
          
            folio_transactions.append({ 
                "name":d["name"],
                "room_number":d.room_number,
                "account_name": "{}-{}".format(d.bank_fee_account, d.bank_fee_description)  if show_account_code else d.bank_fee_description,
                "quantity": d["quantity"],
                "note":d["note"],
                "posting_date": d["posting_date"],
                "debit": d.bank_fee_amount,
                "credit": 0,
                "balance":balance,
                "owner":d["owner"],
                "modified_by":d["modified_by"],
                "creation":d.creation,

            })


        balance = balance + (d.amount * (1 if d.type=="Debit" else -1))
        folio_transactions.append({ 
            "name":d["name"],
            "room_number":d.room_number,
            "account_name": "{}-{}".format(d.account_code, d.account_name)  if show_account_code else d.account_name,
            "quantity": d["quantity"],
            "note":d["note"],
            "posting_date": d["posting_date"],
            "debit": d["amount"]  if d["type"] == 'Debit' else 0,
            "credit": d["amount"]  if d["type"] == 'Credit' else 0,
            "balance":balance,
            "owner":d["owner"],
            "modified_by":d["modified_by"],
            "creation":d.creation,

        })

        if  d.discount_amount > 0:
            balance = balance - d.discount_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.discount_account, d.discount_description)  if show_account_code else d.discount_description,
                "credit":d.discount_amount,
                "debit":0,
                "balance":balance
            })
        
        if  d.tax_1_amount > 0:
            balance = balance + d.tax_1_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.tax_1_account, d.tax_1_description)  if show_account_code else d.tax_1_description,
                "debit":d.tax_1_amount,
                "credit":0,
                "balance":balance
            })

        if  d.tax_2_amount > 0:
            balance = balance + d.tax_2_amount
            folio_transactions.append({
                "account_name": " {}-{}".format(d.tax_2_account, d.tax_2_description)  if show_account_code else d.tax_2_description,
                "debit":d.tax_2_amount,
                "credit":0,
                "balance":balance
            })

        if  d.tax_3_amount > 0:
            balance = balance + d.tax_3_amount
            folio_transactions.append({
                "account_name": "{}-{}".format(d.tax_3_account, d.tax_3_description)  if show_account_code else d.tax_3_description,
                "debit":d.tax_3_amount,
                "credit":0,
                "balance":balance
            })
        
        
    return folio_transactions


@frappe.whitelist(methods="POST")
def update_room_rate(room_rate_names= None,data=None):
 
    if  len(room_rate_names) ==0:
        room_rate_names.append(data["name"])
    for d in room_rate_names:
        doc = frappe.get_doc("Reservation Room Rate",d)
        doc.is_manual_rate = 1
        doc.rate_type = data["rate_type"]
        doc.input_rate = data["input_rate"]
        doc.discount_type = data["discount_type"] 
        doc.discount = data["discount"] 
        doc.tax_rule = data["tax_rule"]
        doc.tax_1_rate = data["tax_1_rate"]
        doc.tax_2_rate = data["tax_2_rate"]
        doc.tax_3_rate = data["tax_3_rate"]
        doc.rate_include_tax = data["rate_include_tax"]
        doc.save()

    #update to reservation stay
    #using enqure process 
    update_reservation_stay(name=data["reservation_stay"], run_commit=False)

    frappe.db.commit()
    #update to reservation
    # #using enqure process  
    return frappe.get_list("Reservation Room Rate",fields=["*"], filters={"reservation_stay":data["reservation_stay"]},limit_page_length=1000,order_by="date")
        


