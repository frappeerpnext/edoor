import functools
import re

import requests
from edoor.api.utils import update_reservation, update_reservation_folio,update_reservation_folios, update_reservation_stay_and_reservation,submit_update_audit_trail_from_version,update_is_arrival_date_in_room_rate
from edoor.api.reservation import generate_room_occupies, post_charge_to_folio_afer_check_in,verify_reservation_stay
from edoor.edoor.doctype.reservation_stay.reservation_stay import generate_room_occupy, generate_temp_room_occupy
from frappe.utils import today,add_to_date,getdate
from rq.command import send_stop_job_command
from rq.exceptions import InvalidJobOperation, NoSuchJobError
from rq.job import Job
from rq.queue import Queue
import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	cint,
	compare,
	convert_utc_to_system_timezone,
	create_batch,
	make_filter_dict,
)
from frappe.utils.background_jobs import get_queues, get_redis_conn

QUEUES = ["default", "long", "short"]
JOB_STATUSES = ["queued", "started", "failed", "finished", "deferred", "scheduled", "canceled"]




@frappe.whitelist()
def get_job_by_job_name(job_name):
    args = {'doctype': 'RQ Job', 'fields': ['`tabRQ Job`.`name`', '`tabRQ Job`.`owner`', '`tabRQ Job`.`creation`', '`tabRQ Job`.`modified`', '`tabRQ Job`.`modified_by`', '`tabRQ Job`.`_user_tags`', '`tabRQ Job`.`_comments`', '`tabRQ Job`.`_assign`', '`tabRQ Job`.`_liked_by`', '`tabRQ Job`.`docstatus`', '`tabRQ Job`.`idx`', '`tabRQ Job`.`queue`', '`tabRQ Job`.`status`', '`tabRQ Job`.`job_name`'], 'filters': [['RQ Job', 'status', '=', 'queued']], 'order_by': '`tabRQ Job`.`modified` desc', 'start': '0', 'page_length': '20', 'group_by': '`tabRQ Job`.`name`', 'with_comment_count': '1', 'save_user_settings': True, 'strict': None}
    start = cint(args.get("start"))
    page_length = 1000



    matched_job_ids = get_matching_job_ids(args)[start : start + page_length]

    conn = get_redis_conn()
    jobs = [
        serialize_job(job) for job in Job.fetch_many(job_ids=matched_job_ids, connection=conn) if job
    ]
    
    return  [d for d in jobs if d["job_name"]==job_name]

@frappe.whitelist()
def get_runing_job_by_job_name(job_names):
    args = {'doctype': 'RQ Job', 'fields': ['`tabRQ Job`.`name`', '`tabRQ Job`.`owner`', '`tabRQ Job`.`creation`', '`tabRQ Job`.`modified`', '`tabRQ Job`.`modified_by`', '`tabRQ Job`.`_user_tags`', '`tabRQ Job`.`_comments`', '`tabRQ Job`.`_assign`', '`tabRQ Job`.`_liked_by`', '`tabRQ Job`.`docstatus`', '`tabRQ Job`.`idx`', '`tabRQ Job`.`queue`', '`tabRQ Job`.`status`', '`tabRQ Job`.`job_name`'], 
            'filters': [
                 ['RQ Job', 'status', 'in', ['queued','started']]
                 ], 'order_by': '`tabRQ Job`.`modified` desc', 'start': '0', 'page_length': '20', 'group_by': '`tabRQ Job`.`name`', 'with_comment_count': '1', 'save_user_settings': True, 'strict': None}
    start = cint(args.get("start"))
    page_length = 1000



    matched_job_ids = get_matching_job_ids(args)[start : start + page_length]

    conn = get_redis_conn()
    jobs = [
        serialize_job(job) for job in Job.fetch_many(job_ids=matched_job_ids, connection=conn) if job
    ]
    
    return  [d["job_name"] for d in jobs if d["job_name"] in job_names]

def can_run_job(job_name):
    
    if frappe.db.exists("Queue Job Configuration",job_name):   
             
        job = frappe.get_doc("Queue Job Configuration",job_name)
        
        if job.skip_if_these_job_running:
        
            job_names = job.skip_if_these_job_running.split()
            
            if len(get_runing_job_by_job_name(job_names=job_names))>0:
                frappe.log_error("This job is skip running. Job name: {}".format(job_name))
                return False
                
    return True
    
@frappe.whitelist()
def re_run_fail_jobs():
    if not can_run_job("edoor.api.schedule_task.re_run_fail_jobs"):
        return
    job_names=[
        "edoor.api.utils.update_reservation_stay_and_reservation",
        "edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy",
        "edoor.api.reservation.generate_room_occupies",
        "edoor.api.utils.update_reservation",
        "edoor.api.reservation.post_charge_to_folio_afer_check_in",
        "edoor.api.utils.update_is_arrival_date_in_room_rate",
        "edoor.api.reservation.verify_reservation_stay",
        "edoor.api.utils.update_reservation_folios"
    ]
    # append unwanted queue job from system
    job_names.append("frappe.model.delete_doc.delete_dynamic_links")
    job_names.append("build_index_for_all_routes")
    job_names.append("edoor.api.schedule_task.run_queue_job")
    job_names.append("upload_to_ftp")
    job_names.append("edoor.api.schedule_task.re_run_fail_jobs")
    job_names.append("erpnext_telegram_integration.erpnext_telegram_integration.doctype.telegram_notification.telegram_notification.evaluate_alert_queue")
    
    args = {'doctype': 'RQ Job', 'fields': ['`tabRQ Job`.`name`', '`tabRQ Job`.`owner`', '`tabRQ Job`.`creation`', '`tabRQ Job`.`modified`', '`tabRQ Job`.`modified_by`', '`tabRQ Job`.`_user_tags`', '`tabRQ Job`.`_comments`', '`tabRQ Job`.`_assign`', '`tabRQ Job`.`_liked_by`', '`tabRQ Job`.`docstatus`', '`tabRQ Job`.`idx`', '`tabRQ Job`.`queue`', '`tabRQ Job`.`status`', '`tabRQ Job`.`job_name`'], 
            'filters': [['RQ Job', 'status', '=', 'failed']], 
            'order_by': '`tabRQ Job`.`modified` desc', 'start': '0', 'page_length': '20', 'group_by': '`tabRQ Job`.`name`', 'with_comment_count': '1', 'save_user_settings': True, 'strict': None}
    start =0
    page_length = 100

    order_desc = "desc" in args.get("order_by", "")

    matched_job_ids = get_matching_job_ids(args)[start : start + page_length]
    
    conn = get_redis_conn()
    jobs = [
        serialize_job(job) for job in Job.fetch_many(job_ids=matched_job_ids, connection=conn) if job
    ]

    jobs =  sorted(jobs, key=lambda j: j.modified, reverse=order_desc)
    jobs = [d for d in jobs if "exc_info" in d]

    
    
    jobs = [d for d in jobs  if  (d["job_name"] in job_names)]
    job_ids = []

    for j in jobs:
        try:
            job =   json.loads(j["arguments"]) 
            if j["job_name"]  in "edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy":
                generate_room_occupy(self=None if "self" not in job["kwargs"] else job["kwargs"]["self"], stay_name=None if "stay_name" not in job["kwargs"] else job["kwargs"]["stay_name"])
            elif j["job_name"] == "edoor.api.reservation.generate_room_occupies":
                generate_room_occupies( stay_names=job["kwargs"]["stay_names"])
            elif j["job_name"] == "edoor.api.utils.update_reservation_folio":
                update_reservation_folio( doc=None if "doc" not in job["kwargs"] else job["kwargs"]["doc"], name=None if "name" not in job["kwargs"] else job["kwargs"]["name"], run_commit=True,ignore_validate=True)     
            elif j["job_name"] == "edoor.api.utils.update_reservation_folios":
                update_reservation_folios( folio_names =job["kwargs"]["folio_names"])     
            elif j["job_name"] == "edoor.api.utils.update_reservation":
                update_reservation(name=job["kwargs"]["name"], run_commit=True,ignore_validate=True)
            elif j["job_name"] == "edoor.api.utils.update_reservation_stay_and_reservation":
                update_reservation_stay_and_reservation(reservation=job["kwargs"]["reservation"],reservation_stay=job["kwargs"]["reservation_stay"],ignore_validate=True) 
            elif j["job_name"] == "edoor.api.reservation.post_charge_to_folio_afer_check_in":

                post_charge_to_folio_afer_check_in(
                    reservation=job["kwargs"]["reservation"],
                    stays=job["kwargs"]["stays"],
                    working_day=job["kwargs"]["working_day"],
                    master_folio=frappe.get_doc( job["kwargs"]["master_folio"]))
            elif j["job_name"]  =="edoor.api.utils.update_is_arrival_date_in_room_rate":
                update_is_arrival_date_in_room_rate(stay_name=job["kwargs"]["stay_name"])
            elif j["job_name"]  =="edoor.api.reservation.verify_reservation_stay":
                verify_reservation_stay(stay_name=job["kwargs"]["stay_name"])
            elif j["job_name"]  =="edoor.api.schedule_task.validate_opening_folio_balance":
                validate_opening_folio_balance()

                

            job_ids.append(j["job_id"])
        except Exception as e:
            return e
        
    
    remove_failed_jobs(job_ids)

    return job_ids


def serialize_job(job: Job) -> frappe._dict:
	modified = job.last_heartbeat or job.ended_at or job.started_at or job.created_at
	job_kwargs = job.kwargs.get("kwargs", {})
	job_name = job_kwargs.get("job_type") or str(job.kwargs.get("job_name"))
	if job_name == "frappe.utils.background_jobs.run_doc_method":
		doctype = job_kwargs.get("doctype")
		doc_method = job_kwargs.get("doc_method")
		if doctype and doc_method:
			job_name = f"{doctype}.{doc_method}"

	# function objects have this repr: '<function functionname at 0xmemory_address >'
	# This regex just removes unnecessary things around it.
	if matches := re.match(r"<function (?P<func_name>.*) at 0x.*>", job_name):
		job_name = matches.group("func_name")

	return frappe._dict(
		name=job.id,
		job_id=job.id,
		queue=job.origin.rsplit(":", 1)[1],
		job_name=job_name,
		status=job.get_status(),
		started_at=convert_utc_to_system_timezone(job.started_at) if job.started_at else "",
		ended_at=convert_utc_to_system_timezone(job.ended_at) if job.ended_at else "",
		time_taken=(job.ended_at - job.started_at).total_seconds() if job.ended_at else "",
		exc_info=job.exc_info,
		arguments=frappe.as_json(job.kwargs),
		timeout=job.timeout,
		creation=convert_utc_to_system_timezone(job.created_at),
		modified=convert_utc_to_system_timezone(modified),
		_comment_count=0,
		owner=job.kwargs.get("user"),
		modified_by=job.kwargs.get("user"),
	)


def get_matching_job_ids(args) -> list[str]:
    filters = make_filter_dict(args.get("filters"))

    queues = _eval_filters(filters.get("queue"), QUEUES)
    statuses = _eval_filters(filters.get("status"), JOB_STATUSES)

    matched_job_ids = []
    for queue in get_queues():
        if not queue.name.endswith(tuple(queues)):
            continue
        for status in statuses:
            matched_job_ids.extend(fetch_job_ids(queue, status))

    return filter_current_site_jobs(matched_job_ids)
    
def _eval_filters(filter, values: list[str]) -> list[str]:
	if filter:
		operator, operand = filter
		return [val for val in values if compare(val, operator, operand)]
	return values


def fetch_job_ids(queue: Queue, status: str) -> list[str]:
	registry_map = {
		"queued": queue,  # self
		"started": queue.started_job_registry,
		"finished": queue.finished_job_registry,
		"failed": queue.failed_job_registry,
		"deferred": queue.deferred_job_registry,
		"scheduled": queue.scheduled_job_registry,
		"canceled": queue.canceled_job_registry,
	}

	registry = registry_map.get(status)
	if registry is not None:
		job_ids = registry.get_job_ids()
		return [j for j in job_ids if j]

	return []

def filter_current_site_jobs(job_ids: list[str]) -> list[str]:
	site = frappe.local.site

	return [j for j in job_ids if j.startswith(site)]



@frappe.whitelist()
def remove_failed_jobs(failed_jobs):
    frappe.only_for("System Manager")

    for queue in get_queues():
        
        fail_registry = queue.failed_job_registry
         
        # Delete in batches to avoid loading too many things in memory
        conn = get_redis_conn()
        for job_ids in create_batch(failed_jobs, 100):
            for job in Job.fetch_many(job_ids=job_ids, connection=conn):
                job and fail_registry.remove(job, delete_job=True)
                    
@frappe.whitelist()
def five_minute_job():
    if not can_run_job("edoor.api.schedule_task.five_minute_job"):
        return
    
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
    
   



    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_status in ('Void','Cancelled')")
    frappe.db.sql("delete from `tabRoom Occupy` where reservation_status in ('Void','Cancelled')")

    frappe.db.commit()
    return "done"


@frappe.whitelist()
def ten_minute_job():
    if not can_run_job("edoor.api.schedule_task.ten_minute_job"):
        return
    

    if can_run_job("edoor.api.schedule_task.run_queue_job"):
        frappe.enqueue("edoor.api.schedule_task.run_queue_job",queue='long')

    if can_run_job("edoor.api.schedule_task.validate_opening_folio_balance"):
        frappe.enqueue("edoor.api.schedule_task.validate_opening_folio_balance",queue='default')
    
    
    if  can_run_job("edoor.api.schedule_task.validate_reservation_stay_balance"):
        frappe.enqueue("edoor.api.schedule_task.validate_reservation_stay_balance",queue='default')
    
    if can_run_job("edoor.api.schedule_task.validate_reservation_balance"):
        frappe.enqueue("edoor.api.schedule_task.validate_reservation_balance",queue='default')
    
    
    
    
    

@frappe.whitelist()
def run_queue_job():

    data = frappe.db.sql( "select distinct document_name, document_type, action from `tabQueue Job` limit 100",as_dict = 1)
    
    update_fetch_from_field([d for d in data if d["action"] =="update_fetch_from_field"])
    update_keyword([d for d in data if d["action"] =="update_keyword"])

    frappe.db.commit()


@frappe.whitelist()
def update_fetch_from_field(data):
    for x in data:
        try:
           if frappe.db.exists(x["document_type"],x["document_name"]):
            doc = frappe.get_doc(x["document_type"],x["document_name"])
            sql = "select parent,options,fieldname from `tabDocField` where options='{}'".format(doc.doctype)
            link_fiels = frappe.db.sql(sql, as_dict=1)
            # doctype =  set(d['parent'] for d in link_fiels)
            for d in link_fiels:
                sql = "select fieldname,options,fetch_from from `tabDocField` where  fetch_from <> '' and fetch_if_empty = 0 and parent='{}' and fetch_from like '{}.%'".format(d.parent, d["fieldname"])
                fetch_fields = frappe.db.sql(sql, as_dict=1)
                for  f in fetch_fields:
                    sql = "update `tab{}` set {}=%(value)s where {}=%(name)s".format(d["parent"],f["fieldname"],f["fetch_from"].split(".")[0])
                    frappe.db.sql(sql,{"value":doc.get(f["fetch_from"].split(".")[1]),"name":doc.name})
                    #frappe.msgprint(sql)
  
        except:
            pass
        
        frappe.db.sql("delete from `tabQueue Job` where document_type='{}' and document_name=%(name)s and action='{}'".format(x["document_type"],x["action"]),{"name":x["document_name"]})
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
            

@frappe.whitelist()
def validate_property_data():
    if not can_run_job("edoor.api.schedule_task.validate_property_data"):
        return
    
    #check if data have duplicate reservation
    fix_generate_duplicate_room_occupy()

    #fix folio transaction that dont have reservation status color
    frappe.db.sql("update `tabFolio Transaction` set reservation_status_color=(select color from `tabReservation Status` where name=`tabFolio Transaction`.reservation_status ) where transaction_type='Reservation Folio' and coalesce(reservation_status_color,'')=''")
    frappe.db.sql("update `tabFolio Transaction` set reservation_type=(select reservation_type from `tabReservation Stay` where name=`tabFolio Transaction`.reservation_stay ) where transaction_type='Reservation Folio' and coalesce(reservation_type,'')=''")

    #fix folio transaction have reservation room rate but not have source reservation stay
    data = frappe.db.sql("select name from `tabFolio Transaction` where coalesce(reservation_room_rate)!='' and coalesce(source_reservation_stay,'')=''  limit 1",as_dict=1)
    
    if len(data)>0:
            frappe.db.sql("""
                update `tabFolio Transaction` 
                set 
                    source_reservation_stay = (select x.reservation_stay from `tabReservation Room Rate` x where x.name = `tabFolio Transaction`.reservation_room_rate) 
                where
                    coalesce(reservation_room_rate,'') !='' and 
                    coalesce(source_reservation_stay,'') = ''
                """)

    #fix folio transaction have reservation room rate but not have stay room_id
    data = frappe.db.sql("select name from `tabFolio Transaction` where coalesce(reservation_room_rate)!='' and coalesce(stay_room_id,'')=''   limit 1",as_dict=1)
    
    if len(data)>0:
            frappe.db.sql("""
                update `tabFolio Transaction` 
                set 
                    stay_room_id = (select x.stay_room_id from `tabReservation Room Rate` x where x.name = `tabFolio Transaction`.reservation_room_rate) 
                where
                    coalesce(reservation_room_rate,'') !='' and 
                    coalesce(stay_room_id,'') = ''
                """)
         
         
    frappe.db.commit()
    

def fix_generate_duplicate_room_occupy():
    sql = "select reservation_stay,date,count(name) as total from `tabRoom Occupy` where date>='{}' group by reservation_stay,date having count(name)>1".format(add_to_date(getdate(today()),days=-7))

    data = frappe.db.sql(sql,as_dict=1)
    if len(data)> 0:
        for s in set([d["reservation_stay"] for d  in data]):
            generate_room_occupy(stay_name=s)
    #temp room occupy
    sql = "select reservation_stay,date,count(name) as total from `tabTemp Room Occupy` where date>='{}' group by reservation_stay,date having count(name)>1".format(add_to_date(getdate(today()),days=-7))
    data = frappe.db.sql(sql,as_dict=1)
    if len(data)> 0:
        for s in set([d["reservation_stay"] for d  in data]):
            generate_temp_room_occupy(stay_name=s)

    # find count room occupy by stay and compare to room night in reservation 
    # if differenct then update run script update room occupy
    sql=""" select 
            a.name
        from `tabReservation Stay` a
        where 
            a.reservation_status in ('Reserved','In-house','Confirmed')  and
            (select count(x.name)-1  from `tabRoom Occupy` x where x.reservation_stay =a.name) != a.room_nights
        """
    data = frappe.db.sql(sql,as_dict=1)

    for d in data:
            generate_room_occupy(stay_name=d["name"])
            generate_temp_room_occupy(stay_name=d["name"])



    # clear 
    sql="select name from `tabReservation Stay` where arrival_date>='{}' and reservation_status='No Show' and is_reserved_room=0".format(add_to_date(getdate(today()),days=-7))
    data = frappe.db.sql(sql,as_dict=1) 
    sql="select name from `tabReservation Stay` where arrival_date>='{}' and reservation_status in ('Cancelled', 'Void')".format(add_to_date(getdate(today()),days=-7))
    data = data +  frappe.db.sql(sql,as_dict=1)

    if len(data)>0:
        frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay in %(stays)s", {"stays":set([d["name"] for d in data])})
        frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay in %(stays)s", {"stays":set([d["name"] for d in data])})
        
    frappe.db.commit()

   


    

@frappe.whitelist()
def generate_audit_trail_from_version():
    if not can_run_job("edoor.api.schedule_task.generate_audit_trail_from_version"):
        return
    

    audit_trail_documents = frappe.db.get_list("Audit Trail Document", pluck='name',filters={"is_epos_audit_trail":0})
    version_data = frappe.db.get_list('Version',
                        filters={
                            'ref_doctype': ["in",audit_trail_documents],
                            "custom_is_converted_to_audit_trail":0
                        },
                        fields=['name','ref_doctype', 'docname',"creation"],
                        page_length=100
                    )
 
    if len(version_data)> 0:
        for v in version_data:
            
            if frappe.db.exists(v.ref_doctype, v.docname):
                doc = frappe.get_doc("Version", v.name)
                submit_update_audit_trail_from_version(doc)
        
        #update is converted
        frappe.db.sql("update `tabVersion` set custom_is_converted_to_audit_trail=1 where name in %(names)s", {"names":set([d.name for d in version_data])})
        frappe.db.commit()
        return version_data




@frappe.whitelist()
def validate_opening_folio_balance():
    data_folios = frappe.db.sql("select name, total_credit,total_debit,balance from `tabReservation Folio` where status = 'Open'",as_dict=1)
    if data_folios:
        sql = """
        select 
            transaction_number,
            sum(if(type='Debit',amount,0)) as debit,
            sum(if(type='Credit',amount,0)) as credit
        from `tabFolio Transaction`
        where 
            transaction_type='Reservation Folio' and 
            transaction_number in %(folio_numbers)s    
        group by
            transaction_number
    """
        data_folio_transaction =frappe.db.sql(sql, {"folio_numbers":set([d["name"] for d in data_folios])},as_dict=1)
        do_commit = False
        for f in data_folios:
            t =  [d for d in data_folio_transaction if d["transaction_number"] ==f["name"]]
            if t:
                t=t[0]
                if t["debit"] != f["total_debit"] or t["credit"] != f["total_credit"]:
                    do_commit = True
                    sql="update `tabReservation Folio` set total_debit={0},total_credit={1}, balance={0}-{1} where name='{2}'".format(
                        t["debit"], 
                        t["credit"],
                        f["name"]
                    )
                    frappe.db.sql(sql)
        if do_commit:
            frappe.db.commit()


@frappe.whitelist()
def validate_reservation_stay_balance():
    data_folios = frappe.db.sql("""
                                select name as reservation_stay, total_credit,total_debit,balance from `tabReservation Stay` 
                                where 
                                    name in (
                                        select reservation_stay from `tabReservation Folio` where status='Open'
                                    ) 
                                """,as_dict=1)
    if data_folios:

        sql = """
        select 
            reservation_stay,
            sum(if(type='Debit',amount,0)) as debit,
            sum(if(type='Credit',amount,0)) as credit
        from `tabFolio Transaction`
        where 
            transaction_type='Reservation Folio' and 
            reservation_stay in %(reservation_stays)s    
        group by
            reservation_stay
    """
        data_folio_transaction =frappe.db.sql(sql, {"reservation_stays":set([d["reservation_stay"] for d in data_folios])},as_dict=1)
        do_commit = False
        for f in data_folios:
            t =  [d for d in data_folio_transaction if d["reservation_stay"] ==f["reservation_stay"]]
            if t:
                t=t[0]
                if t["debit"] != f["total_debit"] or t["credit"] != f["total_credit"]:
                    do_commit = True
                    sql="update `tabReservation Stay` set total_debit={0},total_credit={1}, balance={0}-{1} where name='{2}'".format(
                        t["debit"], 
                        t["credit"],
                        f["reservation_stay"]
                    )
                    frappe.db.sql(sql)
        if do_commit:
            frappe.db.commit()

    return "Done"


    

@frappe.whitelist()
def validate_reservation_balance():
    data_folios = frappe.db.sql("""
                                select name as reservation, total_credit,total_debit,balance from `tabReservation` 
                                where 
                                    name in (
                                        select reservation from `tabReservation Folio` where status='Open'
                                    ) 
                                """,as_dict=1)
    if data_folios:
        sql = """
        select 
            reservation,
            sum(if(type='Debit',amount,0)) as debit,
            sum(if(type='Credit',amount,0)) as credit
        from `tabFolio Transaction`
        where 
            transaction_type='Reservation Folio' and 
            reservation in %(reservations)s    
        group by
            reservation
    """
        data_folio_transaction =frappe.db.sql(sql, {"reservations":set([d["reservation"] for d in data_folios])},as_dict=1)
        do_commit = False
        for f in data_folios:
            t =  [d for d in data_folio_transaction if d["reservation"] ==f["reservation"]]
            if t:
                t=t[0]
                if t["debit"] != f["total_debit"] or t["credit"] != f["total_credit"]:
                    do_commit = True
                    sql="update `tabReservation` set total_debit={0},total_credit={1}, balance={0}-{1} where name='{2}'".format(
                        t["debit"], 
                        t["credit"],
                        f["reservation"]
                    )
                    frappe.db.sql(sql)
        if do_commit:
            frappe.db.commit()

    return "Done"