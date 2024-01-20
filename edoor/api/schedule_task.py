import functools
import re
from edoor.api.utils import update_reservation, update_reservation_folio,submit_update_audit_trail_from_version, update_reservation_stay_and_reservation
from edoor.api.reservation import generate_room_occupies, post_charge_to_folio_afer_check_in
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
def re_run_fail_jobs():
    args = {'doctype': 'RQ Job', 'fields': ['`tabRQ Job`.`name`', '`tabRQ Job`.`owner`', '`tabRQ Job`.`creation`', '`tabRQ Job`.`modified`', '`tabRQ Job`.`modified_by`', '`tabRQ Job`.`_user_tags`', '`tabRQ Job`.`_comments`', '`tabRQ Job`.`_assign`', '`tabRQ Job`.`_liked_by`', '`tabRQ Job`.`docstatus`', '`tabRQ Job`.`idx`', '`tabRQ Job`.`queue`', '`tabRQ Job`.`status`', '`tabRQ Job`.`job_name`'], 'filters': [['RQ Job', 'status', '=', 'failed']], 'order_by': '`tabRQ Job`.`modified` desc', 'start': '0', 'page_length': '20', 'group_by': '`tabRQ Job`.`name`', 'with_comment_count': '1', 'save_user_settings': True, 'strict': None}
    start = cint(args.get("start"))
    page_length = cint(args.get("page_length")) or 20

    order_desc = "desc" in args.get("order_by", "")

    matched_job_ids = get_matching_job_ids(args)[start : start + page_length]

    conn = get_redis_conn()
    jobs = [
        serialize_job(job) for job in Job.fetch_many(job_ids=matched_job_ids, connection=conn) if job
    ]

    jobs =  sorted(jobs, key=lambda j: j.modified, reverse=order_desc)

    # jobs = [d for d in jobs if d["job_name"] =='edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy']
    jobs = [d for d in jobs  if  ['Deadlock found when trying', 'Lock wait timeout exceeded'] in  d["exc_info"] ]
    job_ids = []
    for j in jobs:
        job =   json.loads(j["arguments"]) 
        if j["job_name"]  in "edoor.edoor.doctype.reservation_stay.reservation_stay.generate_room_occupy":
            generate_room_occupy(self=None if "self" not in job["kwargs"] else job["kwargs"]["self"], stay_name=None if "stay_name" not in job["kwargs"] else job["kwargs"]["stay_name"])
        elif j["job_name"] == "edoor.api.reservation.generate_room_occupies":
            generate_room_occupies( stay_names=job["kwargs"]["stay_names"])    
        elif j["job_name"] == "edoor.api.utils.update_reservation_folio":
            update_reservation_folio( doc=None if "doc" not in job["kwargs"] else job["kwargs"]["doc"], name=None if "name" not in job["kwargs"] else job["kwargs"]["name"], run_commit=True)     
        elif j["job_name"] == "edoor.api.utils.update_reservation":
            update_reservation(name=job["kwargs"]["name"], run_commit=True)
        elif j["job_name"] == "edoor.api.utils.update_reservation_stay_and_reservation":
            update_reservation_stay_and_reservation(reservation=job["kwargs"]["reservation"],reservation_stay=job["kwargs"]["reservation_stay"], run_commit=True) 
        elif j["job_name"] == "edoor.api.reservation.post_charge_to_folio_afer_check_in":
            post_charge_to_folio_afer_check_in(
                 reservation=job["kwargs"]["reservation"],
                 stays=job["kwargs"]["stays"],
                 working_day=job["kwargs"]["working_day"],
                 run_commit=True)
            

        job_ids.append(j["job_id"])
    
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
            

@frappe.whitelist()
def validate_property_data():
    #check if data have duplicate reservation
    fix_generate_duplicate_room_occupy()



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


    # clear 
    sql="select name from `tabReservation Stay` where arrival_date>='{}' and reservation_status='No Show' and is_reserved_room=0".format(add_to_date(getdate(today()),days=-7))
    data = frappe.db.sql(sql,as_dict=1) 
    sql="select name from `tabReservation Stay` where arrival_date>='{}' and reservation_status in ('Cancelled', 'Void')".format(add_to_date(getdate(today()),days=-7))
    data = data +  frappe.db.sql(sql,as_dict=1)

    frappe.db.sql("delete from `tabRoom Occupy` where reservation_stay in %(stays)s", {"stays":set([d["name"] for d in data])})
    frappe.db.sql("delete from `tabTemp Room Occupy` where reservation_stay in %(stays)s", {"stays":set([d["name"] for d in data])})
    frappe.db.commit()

    

@frappe.whitelist()
def generate_audit_trail_from_version():
    audit_trail_documents = frappe.db.get_list("Audit Trail Document", pluck='name')
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
        frappe.db.sql("update `tabVersion` set custom_is_converted_to_audit_trail=1 where name in %(names)s", {"names":[d.name for d in version_data]})
        frappe.db.commit()
        return version_data



