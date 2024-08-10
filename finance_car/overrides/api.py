import frappe
@frappe.whitelist()
def check_has_permission(doctype,name,ptype='write'):
    if frappe.has_permission(doctype, ptype):
        return True,frappe.get_doc(doctype,name).as_dict()
    
    else:
        return False

