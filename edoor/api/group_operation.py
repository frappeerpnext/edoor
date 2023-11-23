from edoor.edoor.doctype.reservation_stay.reservation_stay import update_reservation_stay_room_rate_after_resize
from edoor.api.frontdesk import get_working_day
from edoor.api.reservation import check_room_type_availability
from edoor.api.utils import update_reservation, validate_role
from py_linq import Enumerable
import frappe
from frappe import _ 

from frappe.utils.data import add_to_date, getdate,now,date_diff

@frappe.whitelist(methods="POST")
def group_change_stay(data):
    #BASIC VALIDATION
    allow_back_date = frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")
    #check if user move from departure date and move behind current working date 
    working_day = get_working_day(data["property"])
    
    if getdate(data["departure"])< getdate(working_day["date_working_day"]) :
        if allow_back_date==1:
                validate_role("role_for_back_date_transaction","You don't have permission to add back date reservation")
        else:
            frappe.throw(_("Depature date must be greater then or equal to current working date"))
            
    note = ""
    if hasattr(data,"note") or "note" in data:
        note = data["note"]
    data_for_change_stays = []
    data_for_check_validation = []
    for s in data["stays"]:
        doc = frappe.get_doc("Reservation Stay",s)              
        if (getdate(data["arrival"]) != getdate(doc.arrival_date) or getdate(data["departure"]) != getdate(doc.departure_date)) and doc.is_active_reservation==1 and doc.allow_user_to_edit_information==1:
            #validate back date for reservation that is reserve and confrim
            if getdate(data["arrival"])<getdate(working_day["date_working_day"]):
                if doc.reservation_status in ["Reserved","Confirm"]:
                    if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")==1:
                        validate_role("role_for_back_date_transaction","You don't have permission to add back date reservation")
                    else:
                        frappe.throw("You cannot change arrival date to the back date")
                else:
                    for d in doc.stays:
                        if d.start_date != getdate(data["arrival"]):
                            frappe.throw("{} is not allow to change arrival date".format(doc.reservation_status))


            if len(doc.stays)>1:
                #check arrival date change for first stay room
                first_stay = doc.stays[0]
                if getdate(data["arrival"]) != getdate(first_stay.start_date):
                    data_for_check_validation.append({
                        "room_id": first_stay.room_id,
                        "property": doc.property,
                        "room_type_id": first_stay.room_type_id,
                        "start_date": data["arrival"],
                        "end_date": first_stay.end_date,
                        "parent": s,
                        "generate_rate_type": data["generate_new_stay_rate_by"],
                        "note": note,
                        "name": first_stay.name,
                        "ignore_check_room_occupy": 1, #TODO#
                        })
                
                #check departure change for last stay room 
                last_stay = doc.stays[len(doc.stays)-1]

                if getdate(data["departure"]) != getdate(last_stay.end_date):
                    data_for_check_validation.append({
                        "room_id": last_stay.room_id,
                        "property": doc.property,
                        "room_type_id": last_stay.room_type_id,
                        "start_date": last_stay.start_date,
                        "end_date": data["departure"],
                        "parent": s,
                        "generate_rate_type": data["generate_new_stay_rate_by"],
                        "note":note,
                        "name": last_stay.name,
                        "ignore_check_room_occupy": 1, #TODO#
                        })
            else:
                # when stay have only 1 room
                first_stay = doc.stays[0]
                data_for_check_validation.append({
                    "room_id": first_stay.room_id,
                    "property": doc.property,
                    "room_type_id": first_stay.room_type_id,
                    "start_date": data["arrival"],
                    "end_date": data["departure"],
                    "parent": s,
                    "generate_rate_type": data["generate_new_stay_rate_by"],
                    "note": note,
                    "name": first_stay.name,
                    "ignore_check_room_occupy": 1, #TODO#
                    })
                
    if len(data_for_check_validation)==0:
        frappe.throw("There is no record to change stay")
            
    for d in data_for_check_validation:
        data_for_change_stays.append(can_change_stay_date(d))
    
    can_change_stay_data = [d for d in data_for_change_stays if d["can_change_stay"]==True ]
    if len(can_change_stay_data)> 0:
        
        for d in can_change_stay_data:
            change_stay(d)


        #temporary update arrival date and departure date to reservation for data update in front end
        stay_date = frappe.db.sql("select min(arrival_date) as arrival_date, max(departure_date) as departure_date from `tabReservation Stay` where reservation='{}' and is_active_reservation=1".format(data["reservation"]),as_dict=1)
        if stay_date:
            frappe.db.sql("update `tabReservation` set arrival_date='{}', departure_date='{}' where name='{}'".format( stay_date[0]["arrival_date"],stay_date[0]["departure_date"],data["reservation"]))


        #commit data change to database
        frappe.db.commit()
        

        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"],reservation_stay=[d["parent"] for d in data_for_change_stays if d["can_change_stay"] == True]) 
        frappe.msgprint("Change stay successfully")


        
        return [d for d in data_for_change_stays if d["can_change_stay"]==False]
    else:
        return [d for d in data_for_change_stays if d["can_change_stay"]==False]


def change_stay(data):
    #this method is do not have validation
    doc = frappe.get_doc("Reservation Stay",data['parent'])
    doc.is_override_rate = 'is_override_rate' in data and data['is_override_rate']

    for s in doc.stays:
        if s.name == data['name']:
            s.start_date = data['start_date']
            s.end_date = data['end_date']
            if  date_diff(s.end_date, s.start_date)<=0:
                frappe.db.sql("delete from `tabReservation Stay Room` where name='{}'".format(s.name))
                frappe.db.sql("delete from `tabTemp Room Occupy` where stay_room_id='{}'".format(s.name))
                frappe.db.sql("delete from `tabRoom Occupy` where stay_room_id='{}'".format(s.name))
                frappe.db.sql("delete from `tabReservation Room Rate` where stay_room_id='{}'".format(s.name))



    if hasattr(data,"note") or "note" in data:
        doc.change_stay_note = data["note"]  
        
    doc.save()

    if doc:
        #regenerate rate is base on field name generate_new_stay_rate_by in data object
        #there are 2 value
        #1. stay_rate get from last and first stay rate
        #2 is from rate plan
        # we not enqueue this because we want to get rate for update to reservation
 
        update_reservation_stay_room_rate_after_resize(data=data,stay_doc= doc)
        frappe.enqueue("edoor.edoor.doctype.reservation_stay.reservation_stay.change_room_occupy", queue='short', self = doc)

    return doc

def can_change_stay_date(data):
    
    room_id = ""
    
    if 'room_id' in data and data["room_id"]:
        room_id = data["room_id"]

    
    # when we change stay date from drap and drop in room chart calendar we allow to overlap

    if frappe.db.get_single_value("eDoor Setting","enable_over_booking")==0: 
        if room_id:        
            check_room_occupy = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy` where is_departure = 0 and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                {"start_date":data["start_date"],"end_date":add_to_date(data["end_date"],days=-1),"stay_room_id":data["name"],"room_id":data["room_id"]},
                as_dict = 1
                )
            
            if check_room_occupy:
                return {
                        "can_change_stay": False, 
                        "reservation_stay": data["parent"],
                        "message":_("You cannot change stay of this reservation. Because this room is not available or block on {}".format(frappe.format(check_room_occupy[0]["date"]),{"fieldtype":"Date"}) )
                    }
            
                


        #check room type occupy
        available_room = check_room_type_availability(
            property=data["property"],
            room_type_id=data["room_type_id"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            exclude_stay_room_id=data["name"]
        )

         
        if available_room[0]["total_vacant_room"]<=0:
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":"You cannot change stay of this reservation. Because you don't have enough room for room type {}".format(available_room[0]["room_type"])
                }
            
    else:
        #check if the room is block
        if room_id:        
            check_room_occupy = frappe.db.sql("select stay_room_id, date from `tabTemp Room Occupy` where type='Block' and date between %(start_date)s and %(end_date)s and stay_room_id<>%(stay_room_id)s and room_id=%(room_id)s limit 1",
                {"start_date":data["start_date"],"end_date":add_to_date(data["end_date"],days=-1),"stay_room_id":data["name"],"room_id":data["room_id"]},
                as_dict = 1
                )
            
            if check_room_occupy:
                return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":_("You cannot change stay of this reservation. Because this room is not available or block on {}".format(frappe.format(check_room_occupy[0]["date"]),{"fieldtype":"Date"}) )
                }
            
    
    doc = frappe.get_doc("Reservation Stay",data['parent'])
    
    #validate move room that have mulltiple stay is not allow to change stay date
    stay_room = [d for d in  doc.stays if d.name ==data["name"]][0]


        

    # validate if reservation is check in and they and they already stay so we cannot 

    working_day  =get_working_day(doc.property)
    if doc.stays.index(stay_room)==0:
        if getdate( stay_room.start_date) != getdate(data["start_date"]) and  getdate(  working_day["date_working_day"])>= getdate( stay_room.start_date) and doc.reservation_status =='In-house':
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":_("Checked-In reservation is not allow to change arrival date")
                }
            
        
        if  getdate(working_day["date_working_day"])>=getdate( stay_room.start_date) and doc.reservation_status =='In-house' and getdate(stay_room.start_date) !=getdate(data["start_date"]) :
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":_("Checked-In reservation is not allow to change arrival date")
            }
        
        
   
    #check if current dsate date range have room block
    if (hasattr(data,"room_id") or "room_id" in data) and data["room_id"]: 
        block_data =frappe.db.sql("select name from `tabTemp Room Occupy` Where  type='Block' and room_id=%(room_id)s and date between %(start_date)s and %(end_date)s",
                                {
                                    "room_id":data["room_id"],
                                    "start_date":data["start_date"],
                                    "end_date":add_to_date(getdate(  data["end_date"]),days=-1)
                                },as_dict=1)
        if block_data:
            return {
                    "can_change_stay": False, 
                    "reservation_stay": data["parent"],
                    "message":"You cannot change stay or extend stay on a block room"
            }
    
    data["can_change_stay"] = True
    return data

@frappe.whitelist(methods="POST")
def group_change_rate_type(data):
    #data is 
    # {
    #     "start_date", "end_date", "rate_type", "is_override_rate"
    # }
    working_day = get_working_day(data["property"])
    #get active stay
    sql = "select name from `tabReservation Stay` where name in %(stays)s and is_active_reservation=1 and allow_user_to_edit_information=1 and departure_date>= %(working_date)s"
    active_stays = frappe.db.sql(sql, {
        "stays":data["stays"],
        "working_date":working_day["date_working_day"]
    },as_dict=1)


    #get all room rate list to change rate
    sql = "select name,reservation_stay,date from `tabReservation Room Rate` where reservation_stay in %(stays)s and date>=%(working_date)s and date between %(start_date)s and %(end_date)s"
    room_rate_names = frappe.db.sql(sql,{
        "stays":[d["name"] for d in active_stays ],
        "working_date":working_day["date_working_day"],
        "start_date":data["start_date"],
        "end_date":data["end_date"]
    }, as_dict=1)



    for d in room_rate_names:
        if frappe.db.get_value("Reservation Stay", d["reservation_stay"],"reservation_status")=='In-house' and  getdate(d["date"]) == getdate(working_day["date_working_day"]): 
            pass
        else:
            doc = frappe.get_doc("Reservation Room Rate",d["name"])
            if data["is_override_rate"] ==1:
                doc.is_manual_rate = 0
                doc.regenerate_rate =1
            doc.rate_type = data["rate_type"]
            if "tax_rule" in data:
                doc.tax_rule = data["tax_rule"]
                doc.tax_1_rate = data["tax_1_rate"]
                doc.tax_2_rate = data["tax_2_rate"]
                doc.tax_3_rate = data["tax_3_rate"]
                doc.rate_include_tax = data["rate_include_tax"]
            doc.save()

    frappe.db.commit()
    if len(room_rate_names) :
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"], reservation_stay=[d["name"] for d in active_stays])
    else:
        frappe.throw("There are no data change")

    frappe.msgprint("Change rate type successfully")




@frappe.whitelist(methods="POST")
def group_change_rate(data):
    #data is 
    # {
    #     "start_date", "end_date", "rate_type", "is_override_rate"
    # }
    working_day = get_working_day(data["property"])
    #get active stay
    sql = "select name from `tabReservation Stay` where name in %(stays)s and is_active_reservation=1 and allow_user_to_edit_information=1 and departure_date>= %(working_date)s"
    active_stays = frappe.db.sql(sql, {
        "stays":data["stays"],
        "working_date":working_day["date_working_day"]
    },as_dict=1)


    #get all room rate list to change rate
    sql = "select name,reservation_stay,date from `tabReservation Room Rate` where reservation_stay in %(stays)s and date>=%(working_date)s and date between %(start_date)s and %(end_date)s"
    room_rate_names = frappe.db.sql(sql,{
        "stays":[d["name"] for d in active_stays ],
        "working_date":working_day["date_working_day"],
        "start_date":data["start_date"],
        "end_date":data["end_date"]
    }, as_dict=1)



    for d in room_rate_names:
        if frappe.db.get_value("Reservation Stay", d["reservation_stay"],"reservation_status")=='In-house' and  getdate(d["date"]) == getdate(working_day["date_working_day"]): 
            pass
        else:
            doc = frappe.get_doc("Reservation Room Rate",d["name"])
        
            doc.is_manual_rate = 1
            doc.regenerate_rate =0
            doc.rate_include_tax = data["rate_include_tax"]
            doc.input_rate = data["rate"] or 0

            doc.save()

    frappe.db.commit()
    if len(room_rate_names) :
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"], reservation_stay=[d["name"] for d in active_stays])
    else:
        frappe.throw("There are no data change")

    frappe.msgprint("Change new rate  successfully")





@frappe.whitelist(methods="POST")
def group_room_rate_discount(data):
    #data is 
    # {
    #     "start_date", "end_date", "rate_type", "is_override_rate"
    # }
    working_day = get_working_day(data["property"])
    #get active stay
    sql = "select name from `tabReservation Stay` where name in %(stays)s and is_active_reservation=1 and allow_user_to_edit_information=1 and departure_date>= %(working_date)s"
    active_stays = frappe.db.sql(sql, {
        "stays":data["stays"],
        "working_date":working_day["date_working_day"]
    },as_dict=1)


    #get all room rate list to change rate
    sql = "select name,reservation_stay,date from `tabReservation Room Rate` where reservation_stay in %(stays)s and date>=%(working_date)s and date between %(start_date)s and %(end_date)s and allow_discount = 1"
    room_rate_names = frappe.db.sql(sql,{
        "stays":[d["name"] for d in active_stays ],
        "working_date":working_day["date_working_day"],
        "start_date":data["start_date"],
        "end_date":data["end_date"]
    }, as_dict=1)



    for d in room_rate_names:
        if frappe.db.get_value("Reservation Stay", d["reservation_stay"],"reservation_status")=='In-house' and  getdate(d["date"]) == getdate(working_day["date_working_day"]): 
            pass
        else:
            doc = frappe.get_doc("Reservation Room Rate",d["name"])
            doc.regenerate_rate =0
            doc.discount_type = data["discount_type"]
            doc.discount = data["discount"]
            doc.save()

    frappe.db.commit()
    if len(room_rate_names) :
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"], reservation_stay=[d["name"] for d in active_stays])
    else:
        frappe.throw("There are no data change discount")

    frappe.msgprint("Change group discount successfully")


@frappe.whitelist(methods="POST")
def group_change_tax(data):
    
    working_day = get_working_day(data["property"])
    #get active stay
    sql = "select name from `tabReservation Stay` where name in %(stays)s and is_active_reservation=1 and allow_user_to_edit_information=1 and departure_date>= %(working_date)s"
    active_stays = frappe.db.sql(sql, {
        "stays":data["stays"],
        "working_date":working_day["date_working_day"]
    },as_dict=1)


    #get all room rate list to change rate
    sql = "select name,reservation_stay,date from `tabReservation Room Rate` where reservation_stay in %(stays)s and date>=%(working_date)s and date between %(start_date)s and %(end_date)s and allow_discount = 1"
    room_rate_names = frappe.db.sql(sql,{
        "stays":[d["name"] for d in active_stays ],
        "working_date":working_day["date_working_day"],
        "start_date":data["start_date"],
        "end_date":data["end_date"]
    }, as_dict=1)


    tax_rules = data["tax_rules"]
    tax_rule_names =[d["name"] for d in  data["tax_rules"]]

    for d in room_rate_names:
        if frappe.db.get_value("Reservation Stay", d["reservation_stay"],"reservation_status")=='In-house' and  getdate(d["date"]) == getdate(working_day["date_working_day"]): 
            pass
        else:
            doc = frappe.get_doc("Reservation Room Rate",d["name"])
            if doc.tax_rule in tax_rule_names:
                
                tax_rule =[d for d in  tax_rules if d["name"] == doc.tax_rule][0]

                doc.rate_include_tax = "Yes" if tax_rule["is_rate_include_tax"] == 1 else "No"
                doc.tax_1_rate = tax_rule["use_tax_1_rate"]
                doc.tax_2_rate = tax_rule["use_tax_2_rate"]
                doc.tax_3_rate = tax_rule["use_tax_3_rate"]

                doc.regenerate_rate =0
                doc.save()


    frappe.db.commit()
    if len(room_rate_names) :
        frappe.enqueue("edoor.api.utils.update_reservation_stay_and_reservation", queue='short', reservation = data["reservation"], reservation_stay=[d["name"] for d in active_stays])
    else:
        frappe.throw("There are no data change tax")

    frappe.msgprint("Change group tax successfully")



@frappe.whitelist(methods="POST")
def group_change_arrival_time(data):
    frappe.db.set_value('Reservation', data["reservation"], {
        'arrival_time': data["arrival_time"],
        'departure_time': data["departure_time"]
    })

    #update to reservation stay active
    stays = frappe.db.sql("select name from `tabReservation Stay` where is_active_reservation=1 and allow_user_to_edit_information=1 and  reservation='{}'".format(data["reservation"]),as_dict=1)
    for s in stays:
        frappe.db.set_value('Reservation Stay', s["name"], {
            'arrival_time': data["arrival_time"],
            'departure_time': data["departure_time"]
        })

    return frappe.get_doc("Reservation", data["reservation"])


@frappe.whitelist(methods="POST")
def get_group_tax_rules(stays):
     
    sql = """
        with a as(
            select distinct rate_type from `tabReservation Room Rate`  where reservation_stay in %(stays)s
        ),
        b as (
            select distinct account_code from `tabRate Type` where name in (select rate_type  from a)
        ),
        c as (
            select tax_rule, allow_user_to_change_tax,rate_include_tax from `tabAccount Code` where name in (select account_code from b) and allow_tax =1
        )
        select 
            t.name, 
            if(c.rate_include_tax='Yes',1,0) as is_rate_include_tax, 
            t.tax_1_rate, 
            t.tax_2_rate, 
            t.tax_3_rate,
            t.tax_1_rate as use_tax_1_rate, 
            t.tax_2_rate as use_tax_2_rate, 
            t.tax_3_rate as use_tax_3_rate, 
            t.tax_1_name, 
            t.tax_2_name, 
            t.tax_3_name,
            c.allow_user_to_change_tax
        from `tabTax Rule` t 
        inner join c on c.tax_rule = t.name
    """
 
    tax_rules = frappe.db.sql(sql, {"stays":stays}, as_dict = 1)
    return tax_rules


@frappe.whitelist(methods="POST")
def group_transfer_stay_to_other_reservation(data):
    #update selected stays reservation to taget reservation
    update_fields = []
    target_doc = frappe.get_doc("Reservation", data["target_reservation"])
    
    update_fields.append("reservation='{}'".format(data["target_reservation"]))
    update_fields.append("group_color='{}'".format(target_doc.group_color))

    update_fields.append("reservation_type='{}'".format(target_doc.reservation_type))
    update_fields.append("business_source='{}'".format(target_doc.business_source))
    update_fields.append("business_source_type='{}'".format(target_doc.business_source_type))
    update_fields.append("is_master=0")
    
    sql = "update `tabReservation Stay` set {} where name in %(stays)s".format(",".join(update_fields))
    frappe.db.sql(sql,{"stays":data["stays"]})

    #update reservation stay room
    update_fields = []
    update_fields.append("reservation='{}'".format(data["target_reservation"]))
    update_fields.append("business_source='{}'".format(target_doc.business_source))
    update_fields.append("reservation_type='{}'".format(target_doc.reservation_type))
    update_fields.append("group_color='{}'".format(target_doc.group_color))
    update_fields.append("is_master=0")
    
    
    sql = "update `tabReservation Stay Room` set {} where parent in %(stays)s".format(",".join(update_fields))
    frappe.db.sql(sql,{"stays":data["stays"]})
    

    #update to room occupy 
    update_fields = []
    update_fields.append("reservation='{}'".format(data["target_reservation"]))
    update_fields.append("business_source='{}'".format(target_doc.business_source))
    
    sql = "update `tabRoom Occupy` set {} where reservation_stay in %(stays)s".format(",".join(update_fields))
    frappe.db.sql(sql,{"stays":data["stays"]})
    
    #temp room occupy
    sql = "update `tabTemp Room Occupy` set {} where reservation_stay in %(stays)s".format(",".join(update_fields))
    frappe.db.sql(sql,{"stays":data["stays"]})

    #update room rate
    sql = "update `tabReservation Room Rate` set {} where reservation_stay in %(stays)s".format(",".join(update_fields))
    frappe.db.sql(sql,{"stays":data["stays"]})


    #update to folio 
    update_fields = []
    update_fields.append("reservation='{}'".format(data["target_reservation"]))
    update_fields.append("business_source='{}'".format(target_doc.business_source))
    sql = "update `tabReservation Folio` set {} where reservation_stay in %(stays)s".format(",".join(update_fields))
    frappe.db.sql(sql,{"stays":data["stays"]})

    #update to folio transaction



    update_reservation(name=data["source_reservation"]) 
    if not frappe.db.exists("Reservation Stay", {"reservation": data["source_reservation"],"is_master":1,"is_active_reservation":1}):
        stay_name   = frappe.db.sql("select name from `tabReservation Stay` where reservation='{}' limit 1".format(data["source_reservation"]),as_dict=1)
        if len(stay_name)>0:
            stay_doc = frappe.get_doc("Reservation Stay", stay_name[0]["name"])
            stay_doc.is_master = 1
            if len(stay_doc.stays)>0:
                stay_doc.stays[0].is_master = 1
            stay_doc.save()

    frappe.db.commit()
    
        



    frappe.enqueue("edoor.api.utils.update_reservation", queue='short', name = data["target_reservation"])     
    frappe.msgprint("Transfer stay to {} successfully".format(data["target_reservation"]))

 