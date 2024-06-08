
import frappe

def update_fetch_from_fields(self):
    data_for_updates = []

    data_for_updates = data_for_updates +  folio_type_change(self)
     

    if data_for_updates:
        for d in set([x["doctype"] for x in data_for_updates]):
            sql="update `tab{}` set {} where transaction_type='Reservation Folio' and transaction_number='{}' ".format(
                d,
                ",".join([x["update_field"] for x in data_for_updates if x["doctype"]==d]),
                self.name
            )
            frappe.db.sql(sql)

def folio_type_change(self):
    data_for_updates = []
    if self.has_value_changed("folio_type"):
        data_for_updates.append({"doctype":"Folio Transaction","update_field":"folio_type='{}'".format(self.folio_type)})
        
    return data_for_updates 
 