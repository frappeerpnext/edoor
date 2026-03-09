import frappe

def update_fetch_from_fields(self):
    data_for_updates = []
    condiction_keys = [
        {
            "key": "name",
            "doctypes": ["Reservation Stay"]
        }
    ]

    # reservation_status changes
    if self.has_value_changed("reservation_status"):
        if self.reservation_status == 'In-house' and self.reservation_color:
            # used to be reservation_color='' -> we store empty string value
            data_for_updates.append({"doctype": "Reservation Stay", "field": "reservation_color", "value": ""})
            data_for_updates.append({"doctype": "Reservation Stay", "field": "reservation_color_code", "value": ""})

        status_color = frappe.db.get_value("Reservation Status", self.reservation_status, "color")

        data_for_updates.append({"doctype": "Folio Transaction", "field": "reservation_status", "value": self.reservation_status})
        data_for_updates.append({"doctype": "Folio Transaction", "field": "reservation_status_color", "value": status_color})

        data_for_updates.append({"doctype": "Reservation Folio", "field": "reservation_status", "value": self.reservation_status})
        data_for_updates.append({"doctype": "Reservation Folio", "field": "reservation_status_color", "value": status_color})

        data_for_updates.append({"doctype": "Room Occupy", "field": "reservation_status", "value": self.reservation_status})

    # business_source changed
    if self.has_value_changed("business_source"):
        data_for_updates.append({"doctype": "Revenue Forecast Breakdown", "field": "business_source", "value": self.business_source})

    # guest changed
    if self.has_value_changed("guest"):
        # Revenue Forecast Breakdown
        data_for_updates.append({"doctype": "Revenue Forecast Breakdown", "field": "guest", "value": self.guest})
        data_for_updates.append({"doctype": "Revenue Forecast Breakdown", "field": "guest_type", "value": self.guest_type})
        data_for_updates.append({"doctype": "Revenue Forecast Breakdown", "field": "nationality", "value": self.nationality})

        # Reservation Room Rate
        data_for_updates.append({"doctype": "Reservation Room Rate", "field": "guest", "value": self.guest})
        data_for_updates.append({"doctype": "Reservation Room Rate", "field": "guest_name", "value": self.guest_name})
        data_for_updates.append({"doctype": "Reservation Room Rate", "field": "guest_type", "value": self.guest_type})
        data_for_updates.append({"doctype": "Reservation Room Rate", "field": "nationality", "value": self.nationality})

        # Room Occupy
        data_for_updates.append({"doctype": "Room Occupy", "field": "guest", "value": self.guest})
        data_for_updates.append({"doctype": "Room Occupy", "field": "guest_name", "value": self.guest_name})
        data_for_updates.append({"doctype": "Room Occupy", "field": "guest_type", "value": self.guest_type})
        data_for_updates.append({"doctype": "Room Occupy", "field": "nationality", "value": self.nationality})

    if not data_for_updates:
        return

    # group updates by doctype
    doctypes = set([x["doctype"] for x in data_for_updates])
    for d in doctypes:
        # determine key column for WHERE clause
        key_list = [f["key"] for f in condiction_keys if d in f["doctypes"]]
        key = "reservation_stay" if not key_list else key_list[0]

        # build parameterized SET clause
        fields_for_doctype = [x for x in data_for_updates if x["doctype"] == d]
        # protect against empty
        if not fields_for_doctype:
            continue

        set_clauses = []
        values = []
        for item in fields_for_doctype:
            field_name = item.get("field")
            # ignore invalid entries
            if not field_name:
                continue
            set_clauses.append(f"`{field_name}` = %s")
            # convert None to empty string if you prefer, otherwise keep None to set NULL
            val = item.get("value")
            # if you want empty string instead of NULL for missing values, uncomment next line:
            # if val is None: val = ""
            values.append(val)

        if not set_clauses:
            continue

        sql = f"UPDATE `tab{d}` SET {', '.join(set_clauses)} WHERE `{key}` = %s"
        # append key value at the end
        values_tuple = tuple(values) + (self.name,)

        # execute parameterized query
        frappe.db.sql(sql, values_tuple)
