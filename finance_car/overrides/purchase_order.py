from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from erpnext.accounts.general_ledger import (
	make_gl_entries,
	make_reverse_gl_entries,
	process_gl_map,
)
import frappe
class CustomPurchaseOrder(PurchaseOrder):
    def on_update(self):
        old_doc = self.get_doc_before_save()
        if self.docstatus == 0 and self.workflow_state == 'Pending CIT':
            # if len(self.custom_accouting_entry) == 0:
            #     frappe.throw('Please Put Accouting Entry For CIT Accounting')
            # self.post_accouting_entry()    
            frappe.db.sql("UPDATE `tabPurchase Order` SET status = 'Pending CIT' WHERE name = %(name)s", {'name':self.name})
            self.reload()
            print('Exscuteds')

    def post_accouting_entry(self):
        for row in self.custom_accouting_entry:
            frappe.get_doc({
                "doctype": "GL Entry",
                "account": row.account,
                "party_type":"Supplier",
                "party":self.supplier,
                "debit": row.debit,
                "credit": row.credit,
                "cost_center": row.get('cost_center') or frappe.get_cached_value("Company", self.company, "cost_center"),
                "voucher_type": 'Purchase Order',
                "voucher_no": self.name,
                "posting_date": self.transaction_date,
                "remarks": self.custom_user_remarks,
            }).insert(ignore_permissions=True).submit()   

    def on_submit(self):
        if len(self.custom_accouting_entry) == 0:
            frappe.throw('Please Put Accouting Entry For CIT Accounting')
        self.post_accouting_entry()  
        super().on_submit()
        # frappe.db.sql("UPDATE `tabPurchase Order` SET status = 'Pending CIT' WHERE name = %(name)s", {'name':self.name})
        # frappe.db.commit()

    @frappe.whitelist()
    def complete_cit(self, docname):
        self.docstatus = 0
        super().on_submit()
        print('done',self.as_dict())
   


def get_accounting_ledger_preview(doc, filters):
    from erpnext.accounts.report.general_ledger.general_ledger import get_columns as get_gl_columns

    gl_columns, gl_data = [], []
    fields = [
        "posting_date",
        "account",
        "debit",
        "credit",
        "against",
        "party_type",
        "party",
        "cost_center",
        "against_voucher_type",
        "against_voucher",
    ]

    doc.post_accouting_entry()
    columns = get_gl_columns(filters)
    gl_entries = get_gl_entries_for_preview(doc.doctype, doc.name, fields)

    gl_columns = get_columns(columns, fields)
    gl_data = get_data(fields, gl_entries)

    return gl_columns, gl_data     
        

def get_data(raw_columns, raw_data):
	datatable_data = []
	for row in raw_data:
		data_row = []
		for column in raw_columns:
			data_row.append(row.get(column) or "")

		datatable_data.append(data_row)

	return datatable_data


def get_gl_entries_for_preview(doctype, docname, fields):
	return frappe.get_all("GL Entry", filters={"voucher_type": doctype, "voucher_no": docname}, fields=fields)


def get_columns(raw_columns, fields):
	return [
		{"name": d.get("label"), "editable": False, "width": 110}
		for d in raw_columns
		if not d.get("hidden") and d.get("fieldname") in fields
	]      

@frappe.whitelist()
def show_accounting_ledger_preview(company, doctype, docname):
	filters = frappe._dict(company=company, include_dimensions=1)
	doc = frappe.get_doc(doctype, docname)
	doc.run_method("before_gl_preview")

	gl_columns, gl_data = get_accounting_ledger_preview(doc, filters)
	print(gl_columns, gl_data,"--")
	print(frappe.db.count('GL Entry', filters=[]))

	frappe.db.rollback()

	return {"gl_columns": gl_columns, "gl_data": gl_data}       

