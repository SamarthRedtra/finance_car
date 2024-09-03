import frappe
from frappe.utils import cint, flt, get_datetime, getdate, nowdate
from frappe import _


from erpnext.stock.doctype.purchase_receipt.purchase_receipt import  PurchaseReceipt,update_regional_gl_entries
from erpnext.controllers.buying_controller import BuyingController
from finance_car.overrides.stock_controller import CustomStockController
from erpnext.accounts.general_ledger import process_gl_map


class CustomPurchaseReceipt(PurchaseReceipt, CustomStockController):
    def on_submit(self):
        BuyingController.on_submit(self)
        print('called from custom class')

        # Check for Approving Authority
        frappe.get_doc("Authorization Control").validate_approving_authority(
            self.doctype, self.company, self.base_grand_total
        )

        super().update_prevdoc_status()
        if flt(self.per_billed) < 100:
            super().update_billing_status()
        else:
            super().db_set("status", "Completed")

        super().make_bundle_for_sales_purchase_return()
        super().make_bundle_using_old_serial_batch_fields()
        # Updating stock ledger should always be called after updating prevdoc status,
        # because updating ordered qty, reserved_qty_for_subcontract in bin
        # depends upon updated ordered qty in PO
        super().update_stock_ledger()
        self.make_gl_entries()
        super().repost_future_sle_and_gle()
        super().set_consumed_qty_in_subcontract_order()
        super().reserve_stock_for_sales_order()
        
    
    def get_gl_entries(self, warehouse_account=None, via_landed_cost_voucher=False):
        gl_entries = []
        self.make_item_gl_entries(gl_entries, warehouse_account=warehouse_account)
        self.make_tax_gl_entries(gl_entries, via_landed_cost_voucher)
        update_regional_gl_entries(gl_entries, self)
        if len(self.custom_accouting_entry) > 0:
            for custom_entry in self.custom_accouting_entry:
                gl_entries.append(
                    self.get_gl_dict(
                        {
                            "account": custom_entry.account,
                            "debit": custom_entry.debit,
                            "credit": custom_entry.credit,
                            "against": '',
                            "remarks": self.get("custom_user_remarks") or _("Accounting Entry for Stock"),
                            "project": self.get("project") or self.get("project"),
                            "party_type": "Supplier",
                            "party": self.supplier,
                            "cost_center": self.get('cost_center') or frappe.get_cached_value("Company", self.company, "cost_center"),
                            "voucher_type": 'Purchase Receipt',
                            "voucher_no": self.name,
                            "posting_date": self.posting_date,
                            "is_opening": self.get("is_opening") or "No",
                        },
                        item=custom_entry
                    )
                ) 
        
        merge_value = frappe.get_doc(
                    'Finance Car Settings'
                ).merge_accouting_entries   
                
        merge_value = False if merge_value == 0 else True        
        return process_gl_map(gl_entries, merge_entries=merge_value)    


    # def make_gl_entries(self, gl_entries=None, from_repost=False, via_landed_cost_voucher=False):
    #     from finance_car.overrides.stock_controller import CustomStockController
    #     CustomStockController.make_gl_entries(self, gl_entries, from_repost, via_landed_cost_voucher)
    #     print("accouting Entry from custom doc added")
    
    
    
  
