import frappe
from frappe.utils import cstr
from frappe import conf
import os, shutil
import asyncio
import shlex, subprocess
@frappe.whitelist()
def run_backup_command():   
    site_name = cstr(frappe.local.site)
    frappe.db.sql("delete from `tabError Log`")
    frappe.db.commit()
    
    asyncio.run(run_bench_command("bench --site " + site_name + " backup"))

async def run_bench_command(command, kwargs=None):
    site = {"site": frappe.local.site}
    cmd_input = None
    if kwargs:
        cmd_input = kwargs.get("cmd_input", None)
        if cmd_input:
            if not isinstance(cmd_input, bytes):
                raise Exception(f"The input should be of type bytes, not {type(cmd_input).__name__}")
            del kwargs["cmd_input"]
        kwargs.update(site)
    else:
        kwargs = site
    command = " ".join(command.split()).format(**kwargs)
    command = shlex.split(command)
    subprocess.run(command, input=cmd_input, capture_output=True)