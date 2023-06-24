import datetime
import frappe
import json
from py_linq import Enumerable

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
                sql = "update `tab{}` set {}='{}' where {}='{}'".format(d["parent"],f["fieldname"],doc.get(f["fetch_from"].split(".")[1]),f["fetch_from"].split(".")[0], doc.name)
                frappe.db.sql(sql)
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

def update_deleted_document(doc, method=None, *args, **kwargs):
    if doc.comment_type == 'Deleted' and (doc.reference_doctype == "Folio Transaction" or doc.reference_doctype == "Reservation Folio"):
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
def update_reservation(name,doc=None, run_commit = True):
    if name:
        doc = frappe.get_doc("Reservation",name)
    
    sql = """select 
                min(if(is_active_reservation=0,'2050-01-01', arrival_date)) as arrival_date,
                max(if(is_active_reservation=0,'2000-01-01', departure_date)) as departure_date,
                count(name) as total_stay,
                sum(if(is_active_reservation =1,1,0)) as total_active_stay, 
                sum(if(is_active_reservation =1,adult,0)) as adult, 
                sum(if(is_active_reservation =1,child,0)) as child ,
                
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



    doc.total_debit = folio_data[0]["debit"]
    doc.total_credit= folio_data[0]["credit"]
    

    #update to reservation
    doc.total_reservation_stay = data[0][ "total_stay"]
    doc.total_active_reservation_stay = data[0][ "total_active_stay"]
    doc.arrival_date = data[0]["arrival_date"]
    doc.departure_date= data[0]["departure_date"]
    
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
     
    doc.total_checked_in= data[0]["total_checked_in"]
    doc.total_checked_out= data[0]["total_checked_out"]
    doc.total_cancelled= data[0]["total_cancelled"]
    doc.total_void= data[0]["total_void"]
    doc.total_no_show= data[0]["total_no_show"]
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
                folio_number = '{}'
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
def update_reservation_stay(name=None, doc=None,run_commit=True):
    if name:
        doc = frappe.get_doc("Reservation Stay",name)
                
    doc.update_reservation = False
    #1 update data to reservation stay room the rest will update from reservation stay validate event
    sql = """
        select 
            min(rate) as rate,
            avg(rate) as adr,
            sum(rate) as total_rate,
            sum(discount_amount) as discount_amount,
            sum(tax_1_amount) as tax_1_amount,
            sum(tax_2_amount) as tax_2_amount,
            sum(tax_3_amount) as tax_3_amount,
            sum(total_tax) as total_tax,
            sum(total_amount) as total_amount

        from `tabReservation Room Rate`
        where
        stay_room_id = '{}'
    """

    sql_folio = """
       select  
            account_category_name as label,
            abs(sum(amount * if(type='Debit',1,-1))) as amount ,
            sum(if(type='Debit',amount,0)) as debit,
            sum(if(type='Credit',amount,0)) as credit
        from `tabFolio Transaction` 
        where
            reservation_stay = '{}'
        group by account_category_name
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
    doc.summary_data  = json.dumps(folio_data)

    for stay in doc.stays:
        sql = sql.format(stay.name)
        data = frappe.db.sql(sql,as_dict=1)

        if data:
            d = data[0]
            stay.rate =  d["rate"]
            stay.total_rate =  d["total_rate"]
            stay.adr =  d["adr"]
            stay.discount_amount  =d["discount_amount"] or 0
            stay.tax_1_amount =d["tax_1_amount"] or  0
            stay.tax_2_amount =d["tax_2_amount"] or  0
            stay.tax_3_amount =d["tax_3_amount"] or  0
            stay.total_tax =d["total_tax"] or  0
            stay.total_amount =d["total_amount"] or  0
    doc.save()
    if run_commit:
        frappe.db.commit()
    return doc


def update_reservation_color(self=None):
    is_reservation_stay = hasattr(self, 'reservation')
    stays = []
    if is_reservation_stay:
        rs = frappe.get_doc('Reservation', self.reservation)
        rs.reservation_color = self.reservation_color
        if rs.total_active_reservation_stay > 1:
            stays = frappe.db.get_list('Reservation Stay', filters={'reservation':self.reservation, 'name': ['!=', self.name]})
        rs.save()
        frappe.db.commit()
    else:
        stays = frappe.db.get_list('Reservation Stay', filters={'reservation':self.name})
    for t in stays:
        frappe.db.set_value('Reservation Stay', t.name, 'reservation_color', self.reservation_color)





@frappe.whitelist()
def get_base_rate(amount,tax_rule,tax_1_rate, tax_2_rate,tax_3_rate):

	t1_r = (tax_1_rate or 0) / 100
	t2_r = (tax_2_rate or 0)  / 100
	t3_r = (tax_3_rate or 0)  / 100
	#frappe.throw("{}-{}-{}-{}-{}".format(amount,disc,t1_r,t2_r,t3_r))

	tax_1_amount = 0
	tax_2_amount = 0
	tax_3_amount = 0
	price = 0

	t1_af_disc = tax_rule.calculate_tax_1_after_discount
	t2_af_disc = tax_rule.calculate_tax_2_after_discount
	t2_af_add_t1 = tax_rule.calculate_tax_2_after_adding_tax_1
	t3_af_disc	= tax_rule.calculate_tax_3_after_discount
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
def clear_reservation():
    frappe.db.sql("delete from `tabReservation`")
    frappe.db.sql("delete from `tabReservation Stay`")
    frappe.db.sql("delete from `tabReservation Stay Room`")
    frappe.db.sql("delete from `tabReservation Room Rate`")
    frappe.db.sql("delete from `tabTemp Room Occupy`")
    frappe.db.sql("delete from `tabRoom Occupy`")
    frappe.db.commit()
    return "done"