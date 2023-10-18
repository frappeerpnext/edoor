import datetime 
import frappe
import json
from dateutil.rrule import rrule, MONTHLY
from py_linq import Enumerable
from frappe import local
from frappe.utils.data import getdate
import matplotlib.pyplot as plt
from PIL import Image
from frappe import _
import calendar

@frappe.whitelist()
def get_chart():
    labels = ["January", "February", "March", "April", "May", "June", "July"]
    values = [10, 20, 30, 40, 50, 60, 70]

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "name": _("Values"),
                "values": values,
                "chartType": "line"
            }
        ]
    }

    chart = frappe.Chart("My Chart", data=chart_data, type="line")
    chart_file_path = frappe.get_app_path("my_custom_app", "public", "charts", "my_chart.png")
    chart.save(chart_file_path)

def successful_login(login_manager):
    pass
 

def update_fetch_from_field(doc, method=None, *args, **kwargs):
    skip_doctypes = ["DocType","Temp Product Menu"]

    if not doc.doctype in skip_doctypes:
        #we need to run this in queue process 
        #for development we run casue need to track any error occure
        #get all doctype and link field reload to current doc.doctype field that 
        sql = "select parent,options,fieldname from `tabDocField` where options='{}'".format(doc.doctype)
        link_fiels = frappe.db.sql(sql, as_dict=1)
        # doctype =  set(d['parent'] for d in link_fiels)
        for d in link_fiels:
            sql = "select fieldname,options,fetch_from from `tabDocField` where  fetch_from <> '' and fetch_if_empty = 0 and parent='{}' and fetch_from like '{}.%'".format(d.parent, d["fieldname"])
            fetch_fields = frappe.db.sql(sql, as_dict=1)
            for  f in fetch_fields:
                sql = "update `tab{}` set {}=%(value)s where {}='{}'".format(d["parent"],f["fieldname"],f["fetch_from"].split(".")[0], doc.name)
                frappe.db.sql(sql,{"value":doc.get(f["fetch_from"].split(".")[1])})
                #frappe.msgprint(sql)


 

def update_keyword(doc, method=None, *args, **kwargs):
    meta = frappe.get_meta(doc.doctype)
    if meta.has_field("keyword"):
        fields = []
        fields.append("b.name")
        for d in meta.search_fields.split(","):
            fields.append("coalesce(b.{},'')".format(d))

        if fields:
            sql = "update `tab{0}` as a, `tab{0}` as b set a.keyword = concat({1}) where a.name = b.name and a.name='{2}'"
            sql = sql.format(doc.doctype, " , ' ',".join(fields), doc.name )
            frappe.db.sql(sql)
            # update keyword for searching in room chart
            if doc.doctype == 'Reservation Stay':
                rs = frappe.get_doc('Reservation Stay', doc.name)

                data_keyword = "update `tabRoom Occupy` set data_keyword = %(keyword)s where reservation_stay = %(reservation_stay)s"

                frappe.db.sql(data_keyword,{"keyword":rs.keyword,"reservation_stay":doc.name})
                #update to child table reservation stay room
                sql = "update `tabReservation Stay Room` set keyword =%(keyword)s where parent=%(reservation_stay)s"
                frappe.db.sql(sql,{"keyword":rs.keyword,"reservation_stay":doc.name})
            


def update_deleted_document(doc, method=None, *args, **kwargs):
    if doc.comment_type == 'Deleted' and (doc.reference_doctype == "Folio Transaction" or doc.reference_doctype == "Reservation Folio" or doc.reference_doctype == "Reservation Room Rate"):
        docname = doc.subject.replace((doc.reference_doctype + ' '), '')
        sql = "SELECT `name`,`data` FROM `tabDeleted Document` WHERE deleted_name = '{}'".format(docname)
        deleted = frappe.db.sql(sql, as_dict=1)

        if(deleted):
            data = json.loads(deleted[0]['data'])
            deleted_note = ""
          
            if "deleted_note" in data:
                
                deleted_note = data['deleted_note'] or ""
            
            
         
            reservation_folio = data['name']
            if doc.reference_doctype == "Folio Transaction":
                reservation_folio = data['folio_number']
            sql = """UPDATE `tabComment` 
                    SET  
                        reservation = '{0}', 
                        reservation_stay = '{1}', 
                        reservation_folio = '{2}', 
                        folio_number = '{3}',
                        deleted_document = '{4}',
                        reason = '{5}',
                        subject= concat(subject, ', Reason: ', '{5}' )
                    WHERE 
                        `name` = '{6}'
                    """.format(
                            data['reservation'],
                            data['reservation_stay'],
                            reservation_folio,
                            data['name'],
                            deleted[0]['name'],
                            deleted_note,
                            doc.name)
            frappe.db.sql(sql)

def update_insert_document(doc, method=None, *args, **kwargs):
    frappe.get_doc({
        "doctype":"Comment",
        "comment_type":'Created',
        "reference_doctype":doc.doctype,
        "reservation":doc.reservation,
        "reservation_stay":doc.reservation_stay,
        "folio_number":doc.name,
        "content": frappe.as_json(doc)
    }).insert()
    frappe.db.commit()

def check_field(doc, key):
    if key in doc.keys():
        if  doc[key].strip():
            return True
    return False 

def get_date_range(start_date, end_date, exlude_last_date=True):
 
    # Create an empty list to store the generated dates.
    dates = []
     
    for i in range((end_date - start_date).days + 1):
        
        if start_date + datetime.timedelta(days=i) == end_date:
            if not exlude_last_date:
                dates.append(start_date + datetime.timedelta(days=i))    
        else:
            dates.append(start_date + datetime.timedelta(days=i))

    # Return the generated dates.
    return dates

@frappe.whitelist()
def update_reservation(name=None,doc=None, run_commit = True):
    if name or doc:
        if name:
            doc = frappe.get_doc("Reservation",name)

        sql = """select 
                    min(if(is_active_reservation=0,'2050-01-01', arrival_date)) as arrival_date,
                    max(if(is_active_reservation=0,'2000-01-01', departure_date)) as departure_date,
                    count(name) as total_stay,
                    sum(if(is_active_reservation =1,1,0)) as total_active_stay, 
                    sum(if(is_active_reservation =1,adult,0)) as adult, 
                    sum(if(is_active_reservation =1,child,0)) as child ,
                    
                    sum(if(is_active_reservation=1 and reservation_status='Reserved',1,0)) as total_reserved,
                    sum(if(is_active_reservation=1 and reservation_status='Confirmed',1,0)) as total_confirmed,
                    sum(if(is_active_reservation=1 and reservation_status='In-house',1,0)) as total_checked_in,
                    sum(if(is_active_reservation=1 and reservation_status='Checked Out',1,0)) as total_checked_out,
                    sum(if(is_active_reservation=0 and reservation_status='Cancelled',1,0)) as total_cancelled,
                    sum(if(is_active_reservation=0 and reservation_status='No Show',1,0)) as total_no_show,
                    sum(if(is_active_reservation=0 and reservation_status='Void',1,0)) as total_void,
                    
                    sum(if(is_active_reservation =1,room_nights,0)) as room_nights,
                    sum(if(is_active_reservation=1,total_room_rate,0)) as total_room_rate,
                    avg(if(is_active_reservation=1,adr,0)) as adr,
                    min(if(is_active_reservation=1,room_rate,0)) as room_rate,
                    sum(if(is_active_reservation=1,room_rate_discount,0)) as room_rate_discount,
                    sum(if(is_active_reservation=1,room_rate_tax_1_amount,0)) as room_rate_tax_1_amount,
                    sum(if(is_active_reservation=1,room_rate_tax_2_amount,0)) as room_rate_tax_2_amount,
                    sum(if(is_active_reservation=1,room_rate_tax_3_amount,0)) as room_rate_tax_3_amount,
                    sum(if(is_active_reservation=1,total_room_rate_tax,0)) as total_room_rate_tax

                from `tabReservation Stay`
                where 
                    reservation='{}'
                """.format(name)
        
        data = frappe.db.sql(sql,as_dict=1)

        #get folio summary
        sql_folio = """
            select  
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                reservation = '{}'
        """.format(
            doc.name
        )

        folio_data = frappe.db.sql(sql_folio, as_dict=1)
        
        #get room_numbers, room_type , and room_type alias
        sql_room_info = """
                    SELECT 
                        GROUP_CONCAT(rooms) as rooms,
                        GROUP_CONCAT(room_types) as room_types,
                        GROUP_CONCAT(room_type_alias) as room_type_alias,
                        GROUP_CONCAT(name) as room_stay 
                        FROM `tabReservation Stay`
                    where 
                        is_active_reservation = 1 and 
                        reservation = '{}'
        """.format(doc.name)
        room_info_data =frappe.db.sql(sql_room_info, as_dict=1)




        doc.total_debit = folio_data[0]["debit"]
        doc.total_credit= folio_data[0]["credit"]
        

        #update to reservation
        #get min and max active stay
        stay_date  =frappe.db.sql( "select min(arrival_date) as arrival_date, max(departure_date) as departure_date from `tabReservation Stay` where reservation='{}' and is_active_reservation=1".format(doc.name),as_dict=1)
        doc.arrival_date = stay_date[0]["arrival_date"]  or doc.arrival_date
        doc.departure_date= stay_date[0]["departure_date"] or   doc.departure_date

        
        doc.adult = data[0][ "adult"]
        doc.child = data[0][ "child"]

        doc.room_nights= data[0]["room_nights"]
        doc.total_room_rate= data[0]["total_room_rate"]
        doc.room_rate= data[0]["room_rate"]
        doc.adr= data[0]["adr"]
        doc.room_rate_discount= data[0]["room_rate_discount"]
        doc.room_rate_tax_1_amount= data[0]["room_rate_tax_1_amount"]
        doc.room_rate_tax_2_amount= data[0]["room_rate_tax_2_amount"]
        doc.room_rate_tax_3_amount= data[0]["room_rate_tax_3_amount"]
        doc.total_room_rate_tax= data[0]["total_room_rate_tax"]
        
        doc.total_reservation_stay = data[0][ "total_stay"]
        doc.total_active_reservation_stay = data[0][ "total_active_stay"]

        doc.reserved= data[0]["total_reserved"]
        doc.total_confirmed= data[0]["total_confirmed"]
        doc.total_checked_in= data[0]["total_checked_in"]
        doc.total_checked_out= data[0]["total_checked_out"]
        doc.total_cancelled= data[0]["total_cancelled"]
        doc.total_void= data[0]["total_void"]
        doc.total_no_show= data[0]["total_no_show"]


        #update room info
        
        doc.room_types ="" if not room_info_data[0]["room_types"] else  ",".join(set(room_info_data[0]["room_types"].split(',')))
        doc.room_numbers ="" if not room_info_data[0]["rooms"] else  ",".join(set(d for d in  room_info_data[0]["rooms"].split(',') if d !=''))
        doc.room_type_alias ="" if not room_info_data[0]["room_type_alias"] else ",".join(set(room_info_data[0]["room_type_alias"].split(','))) 
        # update room info json
        room_stays_list = []
        room_stay_data = []
        if room_info_data[0]["room_stay"]:
            room_stays_list = room_info_data[0]["room_stay"].split(",")
            room_stays = ','.join(f"'{x}'" for x in room_stays_list)
            sql_room_json = "SELECT `name`, room_number, room_type, room_type_alias,parent as reservation_stay FROM `tabReservation Stay Room` WHERE parent IN({})".format(room_stays)
            room_stay_data = frappe.db.sql(sql_room_json, as_dict=1)

        room_stay_json_list = []
        if len(room_stay_data) > 0:
            for s in room_stay_data:
                room_stay_json_list.append({
                    "name": s['name'],
                    "room_number": s['room_number'] or '',
                    "room_type_alias": s['room_type_alias'],
                    "room_type": s['room_type'],
                    "reservation_stay": s['reservation_stay']
                })
        doc.rooms_data = json.dumps(room_stay_json_list)
    
        #update reservation status
    
        if doc.total_confirmed>0:
            doc.reservation_status = 'Confirmed'
        elif doc.reserved>0:
            doc.reservation_status = 'Reserved'
        elif doc.total_checked_in>0 and  doc.reserved==0:
            doc.reservation_status = 'In-house'
        elif  doc.reserved == 0 and doc.total_checked_in==0 and doc.total_checked_out > 0:
            doc.reservation_status = 'Checked Out'
        elif (doc.total_no_show+ doc.total_cancelled + doc.total_void > 0 ) and doc.total_active_reservation_stay == 0:
            if doc.total_no_show > 0:
                doc.reservation_status = 'No Show'
            elif doc.total_cancelled > 0:
                doc.reservation_status = 'Cancelled'
            else:
                doc.reservation_status = "Void" 

    
        

        doc.update_reservation_stay = False

        doc.save()
        if run_commit:
            frappe.db.commit()
        return doc

@frappe.whitelist()
def update_reservation_folio(name=None, doc=None,run_commit=True):
    if name:
        doc = frappe.get_doc("Reservation Folio",name)
    sql_folio = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'Reservation Folio' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql_folio, as_dict=1)

    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.save()
    if run_commit:
        frappe.db.commit()
        
    return doc

@frappe.whitelist()
def update_reservation_stay(name=None, doc=None,run_commit=True,is_save=True):
   
    if name or doc:
        if name:
            doc = frappe.get_doc("Reservation Stay",name)

        #1 update data to reservation stay room the rest will update from reservation stay validate event
    

        sql_folio = """
        select  
                account_category as label,
                abs(sum(amount * if(type='Debit',1,-1))) as amount ,
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                reservation_stay = '{}' and 
                transaction_type = 'Reservation Folio'
            group by account_category
        """.format(
                doc.name
            )

        folio_data = frappe.db.sql(sql_folio, as_dict=1)


        
        doc.total_debit =  Enumerable(folio_data).sum(lambda x: x.debit or 0)
        doc.total_credit=  Enumerable(folio_data).sum(lambda x: x.credit or 0)
        #REMOVE credit and debit from dict
        for  d in folio_data:
            del d["credit"]
            del d["debit"]
        
        for stay in doc.stays:
            sql = """
                select 
                    min(rate) as rate,
                    avg(rate) as adr,
                    sum(discount_amount) as discount_amount,
                    sum(tax_1_amount) as tax_1_amount,
                    sum(tax_2_amount) as tax_2_amount,
                    sum(tax_3_amount) as tax_3_amount,
                    sum(total_tax) as total_tax,
                    sum(total_rate) as total_amount

                from `tabReservation Room Rate`
                where
                stay_room_id = '{}'
            """.format(stay.name)
        
            data = frappe.db.sql(sql,as_dict=1)
            
            if data:
                d = data[0]
                stay.rate =  d["rate"]
                stay.total_rate =  d["total_amount"] or  0
                stay.adr =  d["adr"]
                stay.discount_amount =d["discount_amount"] or 0
                stay.tax_1_amount =d["tax_1_amount"] or  0
                stay.tax_2_amount =d["tax_2_amount"] or  0
                stay.tax_3_amount =d["tax_3_amount"] or  0
                stay.total_tax =d["total_tax"] or  0
    
        if is_save:
            doc.save()
            if run_commit:
                frappe.db.commit()
        return doc


@frappe.whitelist()
def update_city_ledger(name=None,doc=None, run_commit = True):
    if name:
        doc = frappe.get_doc("City Ledger",name)
    sql = """
        select 
                sum(if(type='Debit',amount,0)) as debit,
                sum(if(type='Credit',amount,0)) as credit
            from `tabFolio Transaction` 
            where
                transaction_type = 'City Ledger' and 
                transaction_number = '{}'
        """.format(
                doc.name
            )

    folio_data = frappe.db.sql(sql, as_dict=1)

    doc.total_debit =  folio_data[0]["debit"]
    doc.total_credit=folio_data[0]["credit"]
    doc.balance= (doc.total_debit or 0) - (doc.total_credit or 0)
    
    doc.save()
    if run_commit:
        frappe.db.commit()
        
    return doc

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
            #check rate from rate that dont have business source
            sql = "{} and ifnull(business_source,'') = '' ".format(sql) 
            data = frappe.db.sql(sql, as_dict=1)
            rate = data[0]["rate"] or 0

            
    if rate == 0:
        #if still rate = 0 the  get rate from room type
        rate = room_type_rate
    return rate



@frappe.whitelist()
def get_base_rate(amount,tax_rule,tax_1_rate, tax_2_rate,tax_3_rate):

	t1_r = (tax_1_rate or 0) / 100
	t2_r = (tax_2_rate or 0)  / 100
	t3_r = (tax_3_rate or 0)  / 100
 


	price = 0

	t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1

	t3_af_add_t1 =  tax_rule.calculate_tax_3_after_adding_tax_1
	t3_af_add_t2 =   tax_rule.calculate_tax_3_after_adding_tax_2


	tax_rate_con = 0


	tax_rate_con = (1 + t1_r + t2_r 
						+ (t1_r * t2_af_add_t1 * t2_r) 
						+ t3_r + (t1_r * t3_af_add_t1 * t3_r) 
						+ (t2_r * t3_af_add_t2 * t3_r)
						+ (t1_r * t2_af_add_t1 * t2_r * t3_af_add_t2 * t3_r))


 
	tax_rate_con = tax_rate_con or 0


	price = amount /  tax_rate_con


	return  price

@frappe.whitelist(methods="DELETE")
def delete_doc(doctype, name, note):
    doc = frappe.get_doc(doctype,name)
    if hasattr(doc,"deleted_note"):
        frappe.db.sql("update `tab{}` set deleted_note = '{}' where name='{}'".format(doctype,note or "",name))
    frappe.delete_doc(doctype,name)

@frappe.whitelist()
def remove_temp_room_occupy(reservation):
    frappe.db.sql(""" 
                    delete from `tabTemp Room Occupy` 
                    where  
                        reservation_stay in (
                                select 
                                    name 
                                from `tabReservation Stay` 
                                where reservation = '{0}' and 
                                (is_active_reservation = 0 or reservation_status ='Checked Out') 
                        ) and 
                        reservation = '{0}'
                  """.format(reservation))
    frappe.db.commit()

def add_room_charge_to_folio(folio,rate):
    rate_type_doc = frappe.get_doc("Rate Type", rate.rate_type)
 
    frappe.get_doc({
        "doctype":"Folio Transaction",
        "transaction_type":"Reservation Folio",
        "posting_date":rate.date,
        "transaction_number":folio.name,
        "room_type_id":rate.room_type_id,
        "room_id":rate.room_id,
        "room_id":rate.room_id,
        "input_amount":rate.input_rate,
        "account_code":rate_type_doc.account_code,
        "tax_rule":rate.tax_rule,
        "discount_type":rate.discount_type,
        "discount":rate.discount,
        "tax_1_rate":rate.tax_1_rate,
        "tax_2_rate":rate.tax_2_rate,
        "tax_3_rate":rate.tax_3_rate,
        "rate_include_tax":rate.rate_include_tax,
        "is_auto_post":1,
        "valiate_input_amount": False
    }).insert()


def get_master_folio(reservation):
    master_stay = frappe.db.get_list("Reservation Stay", filters={"reservation":reservation, "is_master":"1"})
    if master_stay:
        master_folio = frappe.db.get_list("Reservation Folio", fields=["*"], filters={"reservation_stay":master_stay[0].name, "is_master":1})
        if master_folio:
            return master_folio[0]
    return None

def create_folio(stay):
    doc = frappe.get_doc({
        "doctype":"Reservation Folio",
        "reservation_stay":stay.name,
        "guest":stay.guest
    }).insert()
    return doc


@frappe.whitelist()
def five_minute_job():
    #delete void and cancel from temp room occupy
    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_status in ('Void','Cancelled')")
    frappe.db.sql("delete from `tabRoom Occupy` where reservation_status in ('Void','Cancelled')")


@frappe.whitelist()
def clear_reservation():
    frappe.db.sql("delete from `tabReservation`")
    frappe.db.sql("delete from `tabReservation Stay`")
    frappe.db.sql("delete from `tabReservation Stay Room`")
    frappe.db.sql("delete from `tabReservation Room Rate`")
    frappe.db.sql("delete from `tabTemp Room Occupy`")
    frappe.db.sql("delete from `tabRoom Occupy`")
    frappe.db.sql("delete from `tabFolio Transaction`")
    frappe.db.sql("delete from `tabReservation Folio`")
    frappe.db.sql("update `tabRoom` set housekeeping_status = 'Vacant Clean', reservation_stay='',guest='' , guest_name=''")
    
    frappe.db.sql("delete from `tabSale Product`")
    frappe.db.sql("delete from `tabSale Payment`")
    frappe.db.sql("delete from `tabSale`")
    frappe.db.sql("delete from `tabWorking Day`")
    frappe.db.sql("delete from `tabCashier Shift`")
    frappe.db.sql("delete from `tabFrontdesk Note`")
    frappe.db.sql("delete from `tabRoom Block`")

    room_list = frappe.db.get_all("Room")

    for r in room_list:

        room_doc = frappe.get_doc("Room", r.name)
        room_doc.housekeeping_status = "Vacant Clean"
        
        room_doc.save()
    
    
    frappe.db.commit()

    
    return "done"

@frappe.whitelist()
def get_rate_type_info(name):
    doc = frappe.get_doc("Rate Type", name)
    if not doc.account_code:
        frappe.throw("This account does not have account code")
    
    account_doc =frappe.get_doc("Account Code", doc.account_code)
    tax_rule=None
    if account_doc.tax_rule:
        tax_rule = frappe.get_doc("Tax Rule",account_doc.tax_rule)
    
    return {
        "name": name,
        "tax_rule":tax_rule
    }

@frappe.whitelist("POST")
def rename_doc(data):
    doc = frappe.rename_doc(data['doctype'], data['old_name'], data['new_name'])
    if doc:
        return {
            'name': data['new_name']
        }
    
@frappe.whitelist()
def get_city_ledger_amount_summary(filters):
    filters = json.loads(filters)
    filters["start_date"] =getdate(filters["end_date"]).replace(day=1)
 
    sql = """
            select 
                sum(total_amount*(if(type='Debit',1,-1))) as amount 
            from `tabFolio Transaction`
            where
                transaction_type='City Ledger' and 
                transaction_number = %(city_ledger)s and 
                posting_date < %(start_date)s  
        """
    data = frappe.db.sql(sql,filters,as_dict=1)
    opening_balance = 0
    if data:
        opening_balance = data[0]["amount"] or 0
    debit = 0
    credit = 0
    sql = """
            select 
                sum(if(type='Debit',total_amount,0 )) as debit,
                sum(if(type='Credit',total_amount,0 )) as credit 
            from `tabFolio Transaction`
            where
                transaction_type='City Ledger' and 
                transaction_number = %(city_ledger)s and 
                posting_date between  %(start_date)s and %(end_date)s  
        """
    data = frappe.db.sql(sql,filters,as_dict=1)
    if data:
        debit = data[0]["debit"] or 0
        credit= data[0]["credit"] or 0

    return {
        "opening_balance": opening_balance,
        "debit":debit,
        "credit":credit,
        "balance": opening_balance + (debit - credit)
    }
@frappe.whitelist(methods="POST")
def update_photo(data):
    frappe.db.sql("update `tab{}` set photo=%(photo)s where name=%(name)s".format(data["doctype"]), data)
    frappe.msgprint("Upload photo successfully")

@frappe.whitelist()
def update_reservation_stay_and_reservation(reservation_stay, reservation, reservation_folio=None):
    if reservation_folio:
        update_reservation_folio(name=reservation_folio, doc=None, run_commit=True)
    #check if user pass array
    if isinstance(reservation_stay, list):
        for s in reservation_stay:
            update_reservation_stay ( name=s, doc=None, run_commit=True)
    else:
        update_reservation_stay ( name=reservation_stay, doc=None, run_commit=True)

    update_reservation(name=reservation, doc=None, run_commit=True)



    
def validate_role(role_name, message = None,is_backdate_transaction =True):

    if is_backdate_transaction==True:
        #check if edoor setting config allow enter back date transaction
        if frappe.db.get_single_value("eDoor Setting","allow_user_to_add_back_date_transaction")==1: 
            #check user permission if have permission for back date
            role = frappe.db.get_single_value("eDoor Setting",role_name)
            if role:
                if not role in frappe.get_roles(frappe.session.user):
                    frappe.throw(message or "You don't have permission to perform this action")
            else:
                frappe.throw(message or "You don't have permission to perform this action")

       
    
def check_user_permission(role_field_name,message = None):
    role = frappe.db.get_single_value("eDoor Setting",role_field_name)
    if role:
        if not role in frappe.get_roles(frappe.session.user):
            frappe.throw(message or "You don't have permission to perform this action")
    else:
        frappe.throw(message or "You don't have permission to perform this action")

def validate_backdate_permission():
    check_user_permission("role_for_back_date_transaction","Sorry you don't have permission to perform back date transaction")

@frappe.whitelist()
def can_view_rate():
    can_see_rate_role = frappe.db.get_single_value("eDoor Setting","can_see_rate_and_amount_role")
    roles = frappe.get_roles(frappe.session.user)
    
    return 1 if can_see_rate_role in roles else 0


def generate_temp_room_occupy_after_undo_check_out(stay_doc):
    #get stay date to temp room occupy. we get from room occupy cause room occupy is not clear
    room_occupy_list = frappe.db.sql("select date,room_type_id, room_id,stay_room_id,is_arrival,is_departure from `tabRoom Occupy` where reservation_stay='{}'".format(stay_doc.name),as_dict=1)

    for r in room_occupy_list:
        frappe.get_doc({
            "doctype":"Temp Room Occupy",
            "reservation":stay_doc.reservation,
            "reservation_stay":stay_doc.name,
            "room_type_id":r["room_type_id"],
            "room_id":r["room_id"],
            "date":r["date"],
            "type":"Reservation",
            "property":stay_doc.property,
            "stay_room_id":r["stay_room_id"],
            "adult":stay_doc.adult,
            "child":stay_doc.child,
            "pax":stay_doc.pax,
            "is_arrival": r["is_arrival"],
            "is_departure": r["is_departure"]
        }).insert()

    frappe.db.commit()
    
@frappe.whitelist(methods="POST")
def update_doctype_data(data):
    data["modified_by"] = frappe.session.user
    data["modified"] = frappe.utils.now()
    

    keys = data.keys()
    data_keys = []
    for k in [d for d in keys if d not in ["name","doctype"]]:
        data_keys.append("{0}=%({0})s".format(k))
    if len(data_keys)>0:
        sql ="update `tab{}` set {} where name=%(name)s".format(data["doctype"],",".join(data_keys))
        frappe.db.sql(sql, data)
        frappe.db.commit()

    return frappe.get_doc(data["doctype"],data["name"])

    
def get_months(start_date,end_date):
	months = [{'month_number': dt.month, 'month_name': dt.strftime('%B'),"year": dt.year, "total_day":  calendar.monthrange(dt.year, dt.month)[1]} for dt in rrule(MONTHLY, dtstart=start_date, until=end_date)]
	return months