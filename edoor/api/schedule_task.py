import frappe

@frappe.whitelist()
def five_minute_job():
    
    #delete void and cancel from temp room occupy
    sql="""
        update `tabRoom Occupy` a 
        inner join `tabCustomer` b on a.guest = b.name
        set 
            a.guest_name = b.customer_name_en,
            a.guest_type = b.customer_group,
            a.nationality = b.country
        where 
            ifnull(a.guest_name,'') != ifnull(b.customer_name_en,'') or 
            ifnull(a.guest_type,'') != ifnull(b.customer_group,'') or
            ifnull(a.nationality,'') != ifnull(b.country,'');
    """
    frappe.db.sql(sql)

    sql="""
        update `tabFolio Transaction` a 
        inner join `tabCustomer` b on a.guest = b.name
        set 
            a.guest_name = b.customer_name_en,
            a.guest_type = b.customer_group,
            a.nationality = b.country
        where 
            ifnull(a.guest_name,'') != ifnull(b.customer_name_en,'') or 
            ifnull(a.guest_type,'') != ifnull(b.customer_group,'') or
            ifnull(a.nationality,'') != ifnull(b.country,'');
    """
    frappe.db.sql(sql)

    sql="""
        update `tabFolio Transaction` a 
        inner join `tabBusiness Source` b on a.business_source = b.name
        set 
            a.business_source_type = b.business_source_type
        where 
            ifnull(a.business_source_type,'') != ifnull(b.business_source_type,'') """
    frappe.db.sql(sql)
    
    #update account category
    sql="""
        update `tabFolio Transaction` a 
        inner join `tabAccount Code` b on a.account_code = b.name
        set 
            a.account_category = b.account_category
        where 
            ifnull(a.account_category,'') != ifnull(b.account_category,'') """
    frappe.db.sql(sql)
    
    #update rate type in room occupy
    sql="""
        update `tabRoom Occupy` a 
        inner join `tabReservation Room Rate` b on a.reservation_stay = b.reservation_stay and a.date = b.date and a.room_type_id = b.room_type_id
        set 
            a.rate_type = b.rate_type
        where 
            ifnull(a.rate_type,'') != ifnull(b.rate_type,'') 
        """
    
    frappe.db.sql(sql)



    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_status in ('Void','Cancelled')")
    frappe.db.sql("delete from `tabRoom Occupy` where reservation_status in ('Void','Cancelled')")

    frappe.db.commit()
    return "done"


@frappe.whitelist()
def ten_minute_job():
    frappe.enqueue("edoor.api.schedule_task.run_queue_job",queue='long')

@frappe.whitelist()
def run_queue_job():
    data = frappe.db.sql( "select distinct document_name, document_type, action from `tabQueue Job`",as_dict = 1)
    
    update_fetch_from_field([d for d in data if d["action"] =="update_fetch_from_field"])
    update_keyword([d for d in data if d["action"] =="update_keyword"])

@frappe.whitelist()
def update_fetch_from_field(data):
    for x in data:
        if frappe.db.exists(x["document_type"],x["document_name"]):
            doc = frappe.get_doc(x["document_type"],x["document_name"])
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

        frappe.db.sql("delete from `tabQueue Job` where document_type='{}' and document_name='{}' and action='{}'".format(x["document_type"],x["document_name"],x["action"]))
    frappe.db.commit()
            


def update_keyword(data):
    for x in data:
        if frappe.db.exists(x["document_type"],x["document_name"]):
            doc = frappe.get_doc(x["document_type"],x["document_name"])

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

        frappe.db.sql("delete from `tabQueue Job` where document_type='{}' and document_name='{}' and action='{}'".format(x["document_type"],x["document_name"],x["action"]))
            

