from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
from frappe.utils import cint, flt
import frappe
from frappe import _

class CustomSalesInvoice(SalesInvoice):
    def get_gl_entries(self, warehouse_account=None):
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
        print('heee called here from brow')
        self.make_custom_accounting_gl_entry(gl_entries)
        

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

        
