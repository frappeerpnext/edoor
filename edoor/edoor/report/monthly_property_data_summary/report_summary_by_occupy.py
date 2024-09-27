import frappe
from edoor.edoor.report.utils import get_months
from edoor.edoor.report.monthly_property_data_summary.utils import get_grand_total_row, get_total_row,get_total_room_group_by_month,row_group
from frappe.utils import getdate, add_to_date
import copy
from itertools import groupby
def get_report(filters,columns):
    months = get_months(filters)
    report_data = get_report_data(filters,columns)
    summary = get_summary_data(filters, report_data)
    chart = get_report_chart(filters,report_data,months)
    
    return {
        "data":report_data,
        "report_summary":summary,
        "report_chart":chart
    }

def get_report_data(filters,columns):
    report_data = []
    months = get_months(filters)
    room_occupy = get_room_occupy(filters)

    row_group = get_row_group(filters)
    for m in months:
        # frappe.throw(str(m))
        month_record = {
			"row_group": m["str_month"],
			"indent":0,
			"is_group":1
		}
        report_data.append(month_record)
      
        report_data = report_data + [{**d, "month": m["month"],"year":m["year"], "total_days":m["total_days"]}  for d in copy.deepcopy(row_group)]
        if 'Not Set' in [d["row_group"] for d in room_occupy]:
            report_data.append({
                "row_group":"Not Set",
                "indent":1,
                "month":m["month"],
                "year":m["year"],
                "total_days":m["total_days"]
            })
            
        
        # set blank total row 
        # and we assign value after render data complete
        report_data.append({
            "row_group":"Total",
            "indent":1,
            "is_total_row":1,
            "is_group":1,
            "month":m["month"],
            "year":m["year"]
        })

        
    for r in room_occupy:
        record = [d for d in report_data if d["row_group"] == r["row_group"] and int(d["month"])==int(r["month"])]
        if record:
            record[0]["col_" + str(r["day"])] = r["occupy"] 
            
            
    # total column
    room_occupy.sort(key=lambda x: (x['row_group'], x['month']))
    grouped_data = {}
    for key, group in groupby(room_occupy, key=lambda x: (x['row_group'], x['month'])):
    
        grouped_data[key] = list(group)
    
    for key, value in grouped_data.items():
        record = [d for d in report_data if d["row_group"] == key[0] and int(d["month"])==int(key[1])]
        if record:
            record[0]["total"] = sum([d["occupy"] for d in value])
            record[0]["total_block"] = sum([d["block"] for d in value])
    

    # calculate room occupy
    total_rooms = get_total_room_group_by_month (filters)
    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting","calculate_room_occupancy_include_room_block")
    
    for r in [d for d in report_data if "total" in d and  d["total"]>0]:
        total_room = 0
        if filters.row_group=="Room":
            total_room = r["total_days"]
            
        elif filters.row_group=="Room Type":
           
            total_room = sum([d["total_room"] for d in total_rooms if d["month"] == r["month"] and d["year"] ==r["year"] and r["row_group"]== d["room_type"]] )
        else:
            total_room = sum([d["total_room"] for d in total_rooms if d["month"] == r["month"] and d["year"] ==r["year"]])
        
        if calculate_room_occupancy_include_room_block==0:
            total_room = total_room  - (0 if not "total_block" in r else r["total_block"])
        r["occupancy"] = 100 *( r["total"] /  (1 if  (total_room or 0)==0 else total_room) )
    
    
    # update total row to the blank total row
    for r in [d for d in report_data if "is_total_row" in d and  d["is_total_row"]==1]:
        r = get_total_row(
            [d for d in report_data if "month" in d and "year" in d and d["month"]==r["month"] and d["year"]==r["year"]],
            r,
            columns,
            filters,
            sum([d["total_room"] for d in total_rooms if "month" in d  and d["month"]==r["month"]])
        )
    
    if len(months)>1:
        report_data.append({"indent":0, "is_group":1})
        report_data.append(
            get_grand_total_row(
                [d for d in report_data if "is_total_row" in d  ],
                columns,
                filters,
                sum([d["total_room"] for d in total_rooms])
            ))  
    
    if filters.hide_empty_record==1:
            # show hide emplty record
        report_data = [d for d in report_data if d["indent"] == 0 or ( "is_total_row" in d and d["is_total_row"] ==1) or ("total" in d and d["total"]> 0)]

    return report_data

def get_summary_data(filters,report_data):
    if filters.show_summary:
        return [
            {"label": "Total Occupy","value": sum(d["total"] for d in report_data if 'total' in d and "is_total_row" in d), "indicator":"red","datatype":"Int"},
            {"label": "Total Occ(%)","value": sum(d["occupancy"] for d in report_data if 'occupancy' in d and "is_total_row" in d), "indicator":"green","datatype":"Percent"},
            
        ]
def get_row_group(filters):
    sql=""
    if filters.row_group=="Business Source":
        sql="select name as row_group,1 as indent  from `tabBusiness Source` where property =%(property)s order by name"
    elif filters.row_group=="Business Source Type":
        sql="select name as row_group,1 as indent  from `tabBusiness Source Type` order by name"
    
    elif filters.row_group=="Guest Type":
        sql="select name as row_group,1 as indent  from `tabCustomer Group` order by name"
    
    elif filters.row_group=="Room":
        sql="select coalesce(room_number,'Not Set') as row_group,1 as indent  from `tabRoom` where property=%(property)s order by room_number"
    
    elif filters.row_group=="Reservation Type":
        return [{"row_group":"FIT", "indent":1},{"row_group":"GIT", "indent":1}]
    
    elif filters.row_group=="Nationality":
         sql="select distinct coalesce(nationality,'Not Set') as row_group,1 as indent  from `tabRoom Occupy` where property=%(property)s and date between %(start_date)s and %(end_date)s order by nationality"
     
    elif filters.row_group=="Room Type":
         sql="select distinct room_type as row_group,1 as indent  from `tabRoom Type` where property=%(property)s  order by room_type"
     
    
    data = frappe.db.sql(sql,filters,as_dict=1)
    
    return data


def get_room_occupy(filters):
    sql = """select 
				day(date) as day,
                month(date) as month, 
				coalesce({0},'Not Set') as row_group,
				sum(type='Reservation') as occupy, 
				sum(type='Block') as block 
			from `tabRoom Occupy` 
			where 
				property=%(property)s and 
                date between %(start_date)s and %(end_date)s and 
				is_active=1  and 
                type='Reservation'
			group by 
				day(date) ,
                month(date),
				coalesce({0},'Not Set') """.format(
                    min( [d["fieldname"] for d in row_group() if d["label"] == filters.row_group])
                )
    
    
    
    return frappe.db.sql(sql,filters, as_dict=1)
def get_report_chart(filters,data,months):
    if not filters.chart_type in ["pie", "donut"]:
        min_day = min([d["min_date"].day for d in months])
        max_day = max([d["max_date"].day for d in months])
        precision = frappe.db.get_single_value("System Settings","currency_precision")
        columns = []
        row_group = get_row_group(filters)
        
        datasets = []
        # frappe.throw(str(datasets))
        for n in range(min_day, max_day +1):
            columns.append(n)
                
        for s in row_group:
        
            values = []
            for n in range(min_day, max_day +1):
                col_name= "col_" + str(n)
            
                values.append(sum([d[col_name] for d in data if "row_group" in d and d["row_group"]==s["row_group"] and col_name in d]))
            s["values"] = values
            datasets.append({"name":s["row_group"],"values":s["values"]})

        datasets = [d for d in datasets if any(value > 0 for value in d["values"]) ]
        chart = {
            'data':{
                'labels':columns,
                'datasets':datasets
            },
            "type": filters.chart_type,
            "lineOptions": {
                "regionFill": 1,
            },
            'valuesOverPoints':1,
            "axisOptions": {"xIsSeries": 1}
        }
    else:

        labels=list(set([d.get("row_group") for d in data if d.get("is_group",0) == 0]))
        
        values = [ sum([x.get("total",0) for x in data if x.get("row_group") == d ])  for d in  labels ]
        
        chart = {
            'data':{
                'labels':labels,
                'datasets':[{
                    "name": "Occupy",
                    "values":values   
                }]
            },
            "type": filters.chart_type,
            "lineOptions": {
                "regionFill": 1,
            },
            'valuesOverPoints':1,
            "axisOptions": {"xIsSeries": 1}
        }
    return chart
