# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime
from epos_restaurant_2023.custom_socket_client import emit_event


class ChannelManagerSyncLog(Document): 
    def after_insert(self): 
        # get last sync log list
        get_sync_log_list = get_all_cm_sync_status(self.property)

        emit_event("ChannelManagerUpdate",{
            "action":"update_last_sync_log",
            "property":self.property,
            "data": {
                "creation":self.creation,
                "request_type":self.request_type,
                "status":self.status,
                "response_text":self.response_text,
                "name": self.name
                },
            "sync_log_list": get_sync_log_list
            })

        
@frappe.whitelist()  
def get_all_cm_sync_status(property):
    methods = [
        "Get Reservation","Prices update","Restriction update","Availabilty update"
    ]

    data = []

    for m in methods:
        _data = {
            "title": m
        }

        sql = """
            select name, sync_action, provider, sync_until, is_retry_sync, response_text, status, creation
            from `tabChannel Manager Sync Log`
            where 
                property=%(property)s
                and request_type = %(title)s
            order by creation desc
            limit 1
        """

        log = frappe.db.sql(sql, {
            "property": property,
            "title": m
        }, as_dict=1)

        if log:
            log = log[0]
            # convert datetime
            if log.creation:
                log.creation = str(log.creation)

            if log.sync_until:
                log.sync_until = str(log.sync_until)

            _data = {**_data, **log}

        data.append(_data)

    return data