from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import cint, flt
import frappe
from frappe import _
import json

class CustomSalesInvoice(SalesInvoice):
    def get_gl_entries(self, warehouse_account=None):
        from erpnext.accounts.general_ledger import merge_similar_entries

        gl_entries = []
        print('heee called here from brow')
        self.make_custom_accounting_gl_entry(gl_entries)
        
        
        accounts = [i.get('account') for i in gl_entries]
        values = frappe.get_all(
            "Account",
            filters={
                "name": ["in", accounts]
            },
            fields=["name", "root_type", "account_type"],
        )
                
        for i in gl_entries:
            for j in values:
                if i.get('account') == j.get('name') and j.get('account_type') not in ['Receivable', 'Payable']:
                    i.update({
                        'party_type': None,
                        'party': None,
                    })
                    
        return gl_entries
    
    def make_custom_accounting_gl_entry(self, gl_entries):
        if len(self.custom_accouting_entry) > 0:
            for custom_entry in self.custom_accouting_entry:
                    gl_entries.append(
                        self.get_gl_dict(
                            {
                                "account": custom_entry.account,
                                "debit": custom_entry.debit,
                                "credit": custom_entry.credit,
                                "against": '',
                                "remarks": self.get("custom_user_remarks") or _("Accounting Entry for Sales Invoice {0}").format(self.name),
                                "project": self.get("project") or self.get("project"),
                                "party_type": "Customer",
                                "party": self.customer,
                                "cost_center": self.get('cost_center') or frappe.get_cached_value("Company", self.company, "cost_center"),
                                "voucher_type": 'Sales Invoice',
                                "voucher_no": self.name,
                                "posting_date": self.posting_date,
                                "is_opening": self.get("is_opening") or "No",
                            },
                            item=custom_entry
                        )
                    )
    @frappe.whitelist()
    def before_insert(self,is_web = False):
        from erpnext.accounts.general_ledger import merge_similar_entries

        gl_entries = []
        self.make_customer_gl_entry(gl_entries)

        self.make_tax_gl_entries(gl_entries)
        self.make_internal_transfer_gl_entries(gl_entries)

        self.make_item_gl_entries(gl_entries)
        self.make_precision_loss_gl_entry(gl_entries)
        self.make_discount_gl_entries(gl_entries)

        # merge gl entries before adding pos entries
        gl_entries = merge_similar_entries(gl_entries)

        self.make_loyalty_point_redemption_gle(gl_entries)
        self.make_pos_gl_entries(gl_entries)

        self.make_write_off_gl_entry(gl_entries)
        self.make_gle_for_rounding_adjustment(gl_entries)
        print("gl entries",gl_entries)
        total_debit = 0
        total_credit = 0
        self.custom_accouting_entry = []
        if len(gl_entries)>0:
            for i in gl_entries:
                total_debit += i.debit
                total_credit += i.credit
                self.append("custom_accouting_entry", {
                    'account': i.account,
                    'debit': i.debit,
                    'credit': i.credit,
                })
                
        if self.custom_purchase_receipt:
            purchase_receipt = frappe.get_doc(
                "Purchase Receipt", self.custom_purchase_receipt
            )
            if len(purchase_receipt.custom_accouting_entry):
                for i in purchase_receipt.custom_accouting_entry:
                    if i.debit > 0:
                        total_credit += i.debit
                        self.append("custom_accouting_entry", {
                            'account': i.account,
                            'debit': 0,
                            'credit': i.debit,
                        })
                
            if purchase_receipt.custom_landed_cost_details:
                debits_accounts = eval(purchase_receipt.custom_landed_cost_details)
                for i in debits_accounts:
                    if i.get('account') and i.get('amount')>0:
                        total_credit += i.get('amount')
                        self.append("custom_accouting_entry", {
                            'account': i.get('account'),
                            'debit': 0,
                            'credit': i.get('amount')
                        })        
                        
                
        self.custom_total_debit = flt(total_debit) 
        self.custom_total_credit = flt(total_credit)    
        if is_web == 1 or is_web == "1":
            self.save(ignore_permissions=True)
            frappe.db.commit()   
                
                
        
