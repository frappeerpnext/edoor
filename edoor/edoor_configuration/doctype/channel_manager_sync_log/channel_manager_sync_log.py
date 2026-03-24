# Copyright (c) 2026, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_to_date, now_datetime



class ChannelManagerSyncLog(Document):
    pass 
    # def after_insert(self):
    #     if (
    #         self.request_type == "OTA_HotelAvailNotifRQ"
    #         and self.provider == "Exely"
    #         and self.can_sync
    #     ):
    #         frappe.enqueue(
    #             "edoor.channel_managers.exely.availability.update_room_availability",
    #             queue="long",
    #             docname=self.name
    #         )