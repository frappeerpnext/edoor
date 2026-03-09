# Copyright (c) 2024, Tes Pheakdey and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document


class RoomFloorPlanView(Document):
	pass


@frappe.whitelist()
def get_room_for_floor_plan_view(apiParams):
	
	params = json.loads(apiParams)
	rooms = frappe.db.get_list(params['doctype'],fields=params["fields"] or ['name'],filters=params["filters"])
	floor_plan_view = frappe.db.get_list('Room Floor Plan View',fields=["name","x","y","width","height","room"],filters={'room':['in',','.join([r['name'] for r in rooms])]})
	for r in rooms:
		r['floor_view']=[d for d in floor_plan_view if d['room'] == r.name][0]
	return rooms