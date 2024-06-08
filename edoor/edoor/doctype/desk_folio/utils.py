
import frappe

def update_fetch_from_fields(self):
    data_for_updates = []

    data_for_updates = data_for_updates +  business_source_change(self)
    data_for_updates = data_for_updates +  guest_change(self)
    data_for_updates = data_for_updates +  room_id_change(self)

    if data_for_updates:
        for d in set([x["doctype"] for x in data_for_updates]):
            sql="update `tab{}` set {} where transaction_type='Desk Folio' and transaction_number='{}' ".format(
                d,
                ",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
                self.name
            )
            frappe.db.sql(sql)

def business_source_change(self):
    data_for_updates = []
    if self.has_value_changed("business_source"):
        business_source_type = frappe.db.get_value("Business Source",self.business_source, "business_source_type")
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"business_source='{}'".format(self.business_source)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"business_source_type='{}'".format(business_source_type)})


    return data_for_updates 
def guest_change(self):
    data_for_updates = []
    if self.has_value_changed("guest"):
        guest_name,guest_type,nationality = frappe.db.get_value("Customer",self.guest, ['customer_name_en','customer_group','country'])
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest='{}'".format(self.guest)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest_name='{}'".format(guest_name)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"guest_type='{}'".format(guest_type)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"nationality='{}'".format(nationality)})


    return data_for_updates 
def room_id_change(self):
    data_for_updates = []
    if self.has_value_changed("room_id"):
        if self.room_id:
            room_number,room_type_id,room_type,room_type_alias = frappe.db.get_value("Room",self.room_id, ['room_number','room_type_id','room_type','room_type_alias'])
        else:
            room_number,room_type_id,room_type,room_type_alias = ['','','','']
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_id='{}'".format(self.room_id)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_number='{}'".format(room_number)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type_id='{}'".format(room_type_id)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type='{}'".format(room_type)})
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"room_type_alias='{}'".format(room_type_alias)})


    return data_for_updates 
