import datetime
import frappe

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