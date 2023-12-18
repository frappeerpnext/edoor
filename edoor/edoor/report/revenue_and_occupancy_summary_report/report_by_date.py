# Copyright (c) 2023, Tes Pheakdey and contributors
# For license information, please see license.txt
import copy
from edoor.edoor.report.revenue_and_occupancy_summary_report.utils import get_parent_group_by_record,get_room_occupy_group_by_field,get_folio_transaction_group_by_field,get_parent_group_row_from_result_data,get_parent_row_group_label
from edoor.api.frontdesk import get_working_day
import frappe

def get_report(filters, report_config):
    report_data = get_report_data(filters,report_config)
    return {
        "columns":get_report_columns(filters,report_config),
        "data": report_data["report_data"],
        "report_summary": report_data["report_summary"],
        "report_chart": report_data["report_chart"]
    }


def get_report_columns(filters,report_config):
	columns = [
		{'key': "Date","fieldname":"row_group","label":"Date","width":125},
		
		{"fieldname":"room_available","label":"Room Avai","width":100,"align":"center"},
	]
	for g in report_config.report_fields:
		if g.show_in_report==1:
			columns.append({"fieldname":g.fieldname,"label":g.label,"width":g.width,"fieldtype":g.fieldtype,"align": g.align })
	 
	return columns

def get_report_data(filters,report_config):
    calculate_room_occupancy_include_room_block = frappe.db.get_single_value("eDoor Setting", "calculate_room_occupancy_include_room_block")
    
 
    data = get_occupy_data(filters,report_config)
    folio_transaction_data = get_folio_transaction_data(filters,report_config)
    
    parent_row_group_data =[{"parent_row_group":""}]
    if filters.parent_row_group in ["Date","Month","Year"]:
        parent_row_group_data = get_parent_group_by_record(filters)
    else:
        parent_row_group_data = get_parent_group_row_from_result_data(data, folio_transaction_data)

    
    report_group_data = get_row_group_report_data(filters)



    room_available_datas= get_room_available(filters)
	#assign value for data
    report_data = []

    for parent in parent_row_group_data:

        if parent["parent_row_group"] !="":
            report_data.append({
                 "indent":0,
                 "is_total_row":0,
                 "is_group":1,
                 "row_group": get_parent_row_group_label(filters,parent["parent_row_group"])
            })
            

        sub_report_data  = []
        if filters.parent_row_group in ["Date","Month","Year"]:
            sub_report_data = [d for d in report_group_data if d["parent_row_group"]== parent["parent_row_group"]]
        else:
            sub_report_data =copy.deepcopy( report_group_data)

  
        for row in sub_report_data:
            row["is_group"] = 0 
            row["is_total_row"] = 0 
            row["indent"] = 1 

            #set default value 0 for field that dont have value
            for d in  report_config.report_fields:
                row[d.fieldname] = 0
            #room available
            room_available_record = []
            if filters.parent_row_group == "Room Type":    
                room_available_record = [d for d in room_available_datas if str(d["row_group"])==str(row["row_group"]) and str(d["parent_row_group"])==str(parent["parent_row_group"]) ]
            else:
                room_available_record = [d for d in room_available_datas if str(d["row_group"])==str(row["row_group"]) ]

            if len(room_available_record)>0:
                row["room_available"] = room_available_record[0]["total_rooms"]

            occupy_records = [d for d in data if str(d["row_group"]) == str(row["row_group"]) and str(d["parent_row_group"]) == str(parent["parent_row_group"])]
 
            
            if len(occupy_records)> 0:
                    
                    #occupy
                    occupy_record = occupy_records[0]
                    
                    
                    # set value occupy dynamic field
                    for f in report_config.report_fields :
                        if f.show_in_report==1 and f.reference_doctype=="Room Occupy":
                            #set static field
                            #room occupy
                            if f.fieldname=='occupancy':
                                
                                if calculate_room_occupancy_include_room_block==1:
                                    row["occupancy"] = (row["occupy"] or 0) / (1 if row["room_available"] <=0 else row["room_available"]) 
                                else:
                                    row["occupancy"] = (row["occupy"] or 0) / (1 if (row["room_available"]  - row["room_block"])<=0 else (row["room_available"]  - row["room_block"]))
                                row["occupancy"] = row["occupancy"] * 100
                            else:
                                row[f.fieldname] =   occupy_record[f.fieldname]
            # end reed occupy data
                                
            # get data from folio folio transaction
                                
            if len(folio_transaction_data)> 0:
                folio_transaction_records  = [d for d in folio_transaction_data if str(d["row_group"]) == str(row["row_group"]) and str(d["parent_row_group"]) == str(parent["parent_row_group"])]
                 
                if len(folio_transaction_records)> 0:
                    folio_transaction_record  = folio_transaction_records[0]
                    for f in report_config.report_fields :
                        if f.show_in_report==1 and f.reference_doctype=="Folio Transaction":
                            #f.fildname is from report config
                            if f.fieldname=='adr':
                                occupy = row["occupy"] or 0
                                occupy = occupy -  row["complimentary"] or 0 
                                occupy = occupy -  row["house_use"] or 0 
                                if occupy<=0:
                                    occupy =1
                                row['adr'] = (row["room_charge"] or 0) /  occupy
                            else:
                                row[f.fieldname] =   folio_transaction_record[f.fieldname]

  
        # add sub report data to report data
        report_data = report_data + sub_report_data

        #total row for sub group data
        if parent["parent_row_group"] !="":
            if len(sub_report_data):
                report_data.append( get_sub_group_total_record(sub_report_data, report_config, calculate_room_occupancy_include_room_block))
                

    #show total row 
    report_summary=[]
    if len(report_data)>0:
        total_record = {
            "is_total_row":1,
            "is_group" : 0, 
            "row_group": "Grand Total",
        }

        if filters.parent_row_group in ["Date", "Month","Year"]:
            total_record["room_available"] =  sum([d['room_available'] for d in report_data if  d["is_group"]==0 and d["is_total_row"]==0])
        else:
            total_record["room_available"] = sum([d["total_rooms"] for d in room_available_datas])

        for f in report_config.report_fields :
            total_record[f.fieldname] = sum([d[f.fieldname] for d in report_data if d["is_group"]==0 and d["is_total_row"]==0])
        
        if calculate_room_occupancy_include_room_block==1:
            total_record["occupancy"] = (total_record["occupy"] or 0) / (1 if total_record["room_available"] <=0 else total_record["room_available"]) 
        else:
            total_record["occupancy"] = (total_record["occupy"] or 0) / (1 if (total_record["room_available"]  - total_record["room_block"])<=0 else (total_record["room_available"]  - total_record["room_block"]))
        total_record["occupancy"] = total_record["occupancy"] * 100

        #adr
        
        total_record['adr'] = (total_record["room_charge"] or 0) / (1 if  (total_record["occupy"] or 0) == 0 else (total_record["occupy"] or 0) -(total_record["complimentary"] + total_record["house_use"] ))

        report_data.append(total_record)


        #get report summaryt
        if filters.show_summary ==1:
            report_summary = get_report_summary(total_record,report_config)

        report_chart = None
        if filters.chart_type!="None":
            report_chart = get_report_chart(filters, report_data,report_config)
        
 
    return  {"report_data":report_data, "report_summary": report_summary,"report_chart":report_chart}

def get_sub_group_total_record(data,report_config,calculate_room_occupancy_include_room_block):
    
    total_record = {
            "is_total_row":1,
            "is_group" : 0, 
            "row_group": "Total",
            "is_group_total":1,
            "room_available":  sum([d['room_available'] for d in data if 'room_available' in d])
        }
    for f in report_config.report_fields :
        total_record[f.fieldname] = sum([d[f.fieldname] for d in data if 'is_group' in d and  d["is_group"]==0 ])

    if calculate_room_occupancy_include_room_block==1:
        total_record["occupancy"] = (total_record["occupy"] or 0) / (1 if total_record["room_available"] <=0 else total_record["room_available"]) 
    else:
        total_record["occupancy"] = (total_record["occupy"] or 0) / (1 if (total_record["room_available"]  - total_record["room_block"])<=0 else (total_record["room_available"]  - total_record["room_block"]))
    total_record["occupancy"] = total_record["occupancy"] * 100

    #adr

    total_record['adr'] = (total_record["room_charge"] or 0) / (1 if  (total_record["occupy"] or 0) == 0 else (total_record["occupy"] or 0) -(total_record["complimentary"] + total_record["house_use"] ))
    return total_record



def get_row_group_report_data(filters):
    sql = ""
    if not filters.parent_row_group: 
        sql ="select date_format(date,'%%d-%%m-%%Y') as row_group,'' as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date_format(date,'%%d-%%m-%%Y')"
    elif filters.parent_row_group =='Month':
         sql ="select date_format(date,'%%d-%%m-%%Y') as row_group,date_format(date,'%%b-%%Y') as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date_format(date,'%%d-%%m-%%Y')"      
    elif filters.parent_row_group =='Year':
         sql ="select date_format(date,'%%d-%%m-%%Y') as row_group,date_format(date,'%%Y') as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date_format(date,'%%d-%%m-%%Y')" 
    else:
        sql ="select date_format(date,'%%d-%%m-%%Y') as row_group,'' as parent_row_group from `tabDates` where date between %(start_date)s and %(end_date)s order by date_format(date,'%%d-%%m-%%Y')" 
    
    data = frappe.db.sql(sql,filters,as_dict=1)

    return data
	
def get_occupy_data(filters,report_config):
    sql = "select date_format(date,'%%d-%%m-%%Y') as row_group, "
    sql = "{} {} as parent_row_group,".format(sql,get_room_occupy_group_by_field(filters))

    #other aggregate field
    sql = "{} {}".format(sql,','.join([d.sql_expression for d in report_config.report_fields if d.reference_doctype =='Room Occupy' and d.sql_expression]) )
    #filter
    sql = sql+ " from `tabRoom Occupy` a  where 1=1 "
    sql = sql + " and date between %(start_date)s and %(end_date)s and property=%(property)s "
    if filters.room_type:
        sql = "{} and room_type_id=%(room_type)s".format(sql)   
    if filters.business_source:
        sql = "{} and business_source=%(business_source)s".format(sql)

    if filters.guest_type:
        sql = "{} and guest_type=%(guest_type)s".format(sql)

    # group by
    
    sql = "{} group by date_format(date,'%%d-%%m-%%Y')".format(sql)

    #add parent row group
    if filters.parent_row_group:
        sql = "{}, {}".format(sql, get_room_occupy_group_by_field(filters)) 
 

    data = frappe.db.sql(sql,filters,as_dict = 1)
    return data

def get_report_summary(total_record,report_config):
    report_summary = []
    
    
    report_summary.append({"label":"Room Avai","value":total_record["room_available"],"indicator":"blue"})
    for f in report_config.report_fields:
         if f.show_in_summary==1:
              report_summary.append({"label":f.label,"value":frappe.format_value(total_record[f.fieldname],f.fieldtype),"indicator":f.summary_indicator or "blue"})

    return report_summary



def get_room_available(filters):
    sql = ""
    if filters.parent_row_group=="Room Type":
        sql="""select 
            date_format(date,'%%d-%%m-%%Y')  as row_group ,
            room_type_id as parent_row_group,
            sum(total_room) as total_rooms 
        from `tabDaily Property Data` where """
    else:
        sql="""select 
            date_format(date,'%%d-%%m-%%Y')  as row_group , 
            sum(total_room) as total_rooms 
        from `tabDaily Property Data` where """

    sql = sql + " property=%(property)s and date between %(start_date)s and %(end_date)s " 
    if filters.room_type:
        sql = "{} and room_type_id=%(room_type)s ".format(sql)
    sql = sql + "group by date_format(date,'%%d-%%m-%%Y') "

    # add group by if parent row group is room type
    if filters.parent_row_group=="Room Type":
        sql = "{}, room_type_id".format(sql)

    return frappe.db.sql(sql,filters, as_dict=1)


def get_folio_transaction_data(filters, report_config ):
    sql = "select date_format(posting_date,'%%d-%%m-%%Y')  as row_group,"
    sql = "{} {} as parent_row_group,".format(sql,get_folio_transaction_group_by_field(filters))
        
    sql = "{} {}".format(sql,','.join([d.sql_expression for d in report_config.report_fields if d.reference_doctype =='Folio Transaction' and d.sql_expression]) )
    #filter
    sql = sql+ " from `tabFolio Transaction` a where transaction_type='Reservation Folio' "
    sql = sql + " and posting_date between %(start_date)s and %(end_date)s and property=%(property)s "
    if filters.room_type:
        sql = "{} and room_type_id=%(room_type)s".format(sql)


    if filters.business_source:
        sql = "{} and business_source=%(business_source)s".format(sql)

    if filters.guest_type:
        sql = "{} and guest_type=%(guest_type)s".format(sql)

 
    # group by
    sql = "{} group by date_format(posting_date,'%%d-%%m-%%Y')".format(sql)
    
    #add parent row group
    if filters.parent_row_group:
        sql = "{}, {}".format(sql, get_folio_transaction_group_by_field(filters)) 


    data = frappe.db.sql(sql,filters,as_dict = 1)
    return data


def get_report_chart(filters,report_data,report_config):
    precision = frappe.db.get_single_value("System Settings","currency_precision")

    columns =[]
    
    datasets = []
    if not filters.parent_row_group:
        columns = [d["row_group"] for d in  report_data if d["is_group"] == 0]
        for f in report_config.report_fields:
            if f.show_in_chart==1:
                if (f.fieldtype=="Currency"):
                    datasets.append({
                        "name": f.label,
                        "values": [round(d[f.fieldname], int(precision)) for d in  report_data if d["is_group"] == 0 and d["is_total_row"] ==0]
                    })
                else:
                    datasets.append({
                        "name": f.label,
                        "values": [d[f.fieldname] for d in  report_data if d["is_group"] == 0 and d["is_total_row"] ==0]
                    })

    else:
        columns = [d["row_group"] for d in  report_data if 'is_group' in d and  d["is_group"] == 1]
        for f in report_config.report_fields:
            if f.show_in_chart==1:
                if (f.fieldtype=="Currency"):
                    datasets.append({
                        "name": f.label,
                        "values": [round(d[f.fieldname],int(precision)) for d in  report_data if 'is_group_total' in d and  d["is_group_total"] ==1]
                    })
                else:
                    datasets.append({
                        "name": f.label,
                        "values": [d[f.fieldname] for d in  report_data if 'is_group_total' in d and  d["is_group_total"] ==1]
                    })
                
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
    return chart
