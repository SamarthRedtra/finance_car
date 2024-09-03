import frappe
from frappe.utils import cint, flt, get_datetime, getdate, nowdate


from erpnext.stock.doctype.purchase_receipt.purchase_receipt import  PurchaseReceipt
from erpnext.controllers.buying_controller import BuyingController
from finance_car.overrides.stock_controller import CustomStockController

class CustomPurchaseReceipt(PurchaseReceipt,CustomStockController):
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
        self.make_gl_entries(gl_entries=None, from_repost=False, via_landed_cost_voucher=False)
        super().repost_future_sle_and_gle()
        super().set_consumed_qty_in_subcontract_order()
        super().reserve_stock_for_sales_order()


    # def make_gl_entries(self, gl_entries=None, from_repost=False, via_landed_cost_voucher=False):
    #     from finance_car.overrides.stock_controller import CustomStockController
    #     CustomStockController.make_gl_entries(self, gl_entries, from_repost, via_landed_cost_voucher)
    #     print("accouting Entry from custom doc added")
        
