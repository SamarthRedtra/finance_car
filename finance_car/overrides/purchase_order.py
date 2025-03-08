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
            
        if len(self.items)>0 and self.items[0].custom_chassis_no != self.custom_chassis_no:
            print("hhhe",self.items[0].custom_chassis_no) 
            frappe.db.set_value('Purchase Order', self.name, 'custom_chassis_no', self.items[0].custom_chassis_no)
            frappe.db.commit()

    def before_insert(self):
        print("Exscuted",self.items[0].custom_chassis_no)
        if len(self.items)>0:
           chassi_no = self.items[0].custom_chassis_no 
        print(frappe.db.exists('Purchase Order', {'custom_chassis_no':chassi_no, 'docstatus':1}),"000")
        if frappe.db.exists('Purchase Order', {'custom_chassis_no':chassi_no, 'docstatus':1}):
            poname = frappe.db.get_value('Purchase Order', {'custom_chassis_no':chassi_no}, 'name')
            frappe.throw(f'Chassis No Already Exists For PO: {poname}')  
            
    
    def before_submit(self):
        if self.custom_total_debit >0 and self.custom_total_credit > 0 and  self.custom_total_debit != self.custom_total_credit:
            frappe.throw("Debit and Credit Should be Equal")
            
                    
               
    def post_accouting_entry(self):
        for row in self.custom_accouting_entry:
            frappe.get_doc({
                "doctype": "GL Entry",
                "account": row.account,
                "party_type":"Supplier",
                "party":self.supplier,
                "debit": row.debit,
                "credit": row.credit,
                "debit_in_account_currency":row.debit,
                "credit_in_account_currency":row.credit,
                "cost_center": row.get('cost_center') or frappe.get_cached_value("Company", self.company, "cost_center"),
                "voucher_type": 'Purchase Order',
                "voucher_no": self.name,
                "posting_date": self.transaction_date,
                "remarks": self.custom_user_remarks,
            }).insert(ignore_permissions=True).submit()   

    def on_cancel(self):
        # Reverse GL entries upon cancellation
        self.reverse_custom_gl_entries()
        # Call the original on_cancel method to retain standard behavior
        super().on_cancel()
        
    
    def reverse_custom_gl_entries(self):
        # Get the original GL entries for this Purchase Order
        gl_entries = frappe.get_all(
            "GL Entry",
            filters={
                "voucher_type": "Purchase Order",
                "voucher_no": self.name,
                "is_cancelled": 0  # Only fetch active GL entries
            },
            fields=["*"]
        )

        if gl_entries:
            for entry in gl_entries:
                # Create a new reversed GL entry by swapping debit and credit
                reversed_gl_entry = frappe.get_doc({
                    "doctype": "GL Entry",
                    "account": entry.account,
                    "party_type": entry.party_type,
                    "party": entry.party,
                    "debit": entry.credit,  # Swap debit and credit
                    "credit": entry.debit,
                    "debit_in_account_currency": entry.credit_in_account_currency,
                    "credit_in_account_currency": entry.debit_in_account_currency,
                    "cost_center": entry.cost_center,
                    "voucher_type": entry.voucher_type,
                    "voucher_no": entry.voucher_no,
                    "posting_date": frappe.utils.nowdate(),  # Use current date for the reversal
                    "company": entry.company,
                    "remarks": "Reversed entry for cancellation of Purchase Order " + self.name,
                    "is_cancelled": 1  # Mark the reversed entry as canceled
                })
                reversed_gl_entry.insert(ignore_permissions=True)
                reversed_gl_entry.submit()

            # Mark original entries as canceled
            frappe.db.sql("""
                UPDATE `tabGL Entry`
                SET is_cancelled = 1
                WHERE voucher_type = 'Purchase Order' AND voucher_no = %s
            """, self.name)
        
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

