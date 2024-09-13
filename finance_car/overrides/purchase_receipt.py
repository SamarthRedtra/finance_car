import frappe
from frappe.utils import cint, flt, get_datetime, getdate, nowdate
from frappe import _
import erpnext


from erpnext.stock.doctype.purchase_receipt.purchase_receipt import  PurchaseReceipt,update_regional_gl_entries,get_stock_value_difference
from erpnext.controllers.buying_controller import BuyingController
from finance_car.overrides.stock_controller import CustomStockController
from erpnext.accounts.utils import get_account_currency
from erpnext.assets.doctype.asset.asset import get_asset_account, is_cwip_accounting_enabled
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account
from erpnext.buying.utils import check_on_hold_or_closed_status
from erpnext.controllers.accounts_controller import merge_taxes
from erpnext.controllers.buying_controller import BuyingController
from erpnext.stock.doctype.delivery_note.delivery_note import make_inter_company_transaction

from erpnext.accounts.general_ledger import process_gl_map

def get_item_account_wise_additional_cost(purchase_document):
    landed_cost_vouchers = frappe.get_all(
        "Landed Cost Purchase Receipt",
        fields=["parent"],
        filters={"receipt_document": purchase_document, "docstatus": 1},
    )

    if not landed_cost_vouchers:
        return None,[]

    item_account_wise_cost = {}
    debit_account_list = []

    for lcv in landed_cost_vouchers:
        landed_cost_voucher_doc = frappe.get_doc("Landed Cost Voucher", lcv.parent)
        debit_account_new = landed_cost_voucher_doc.custom_debit_account

        based_on_field = None
        # Use amount field for total item cost for manually cost distributed LCVs
        if landed_cost_voucher_doc.distribute_charges_based_on != "Distribute Manually":
            based_on_field = frappe.scrub(landed_cost_voucher_doc.distribute_charges_based_on)

        total_item_cost = 0
        total_cost_debit_account = 0
        if landed_cost_voucher_doc.taxes:
            total_cost_debit_account = sum([ i.get("amount") for i in landed_cost_voucher_doc.taxes ])
        
        debit_account_list.append({'account':debit_account_new,'amount':total_cost_debit_account})    
            

        if based_on_field:
            for item in landed_cost_voucher_doc.items:
                total_item_cost += item.get(based_on_field)

        for item in landed_cost_voucher_doc.items:
            if item.receipt_document == purchase_document:
                for account in landed_cost_voucher_doc.taxes:
                    item_account_wise_cost.setdefault((item.item_code, item.purchase_receipt_item), {})
                    item_account_wise_cost[(item.item_code, item.purchase_receipt_item)].setdefault(
                        account.expense_account, {"amount": 0.0, "base_amount": 0.0}
                    )

                    if total_item_cost > 0:
                        item_account_wise_cost[(item.item_code, item.purchase_receipt_item)][
                            account.expense_account
                        ]["amount"] += account.amount * item.get(based_on_field) / total_item_cost

                        item_account_wise_cost[(item.item_code, item.purchase_receipt_item)][
                            account.expense_account
                        ]["base_amount"] += account.base_amount * item.get(based_on_field) / total_item_cost
                    else:
                        item_account_wise_cost[(item.item_code, item.purchase_receipt_item)][
                            account.expense_account
                        ]["amount"] += item.applicable_charges
                        item_account_wise_cost[(item.item_code, item.purchase_receipt_item)][
                            account.expense_account
                        ]["base_amount"] += item.applicable_charges
                        
    print(" debit_account_list",debit_account_list)
    return item_account_wise_cost,debit_account_list

def delete_existing_gl_entry(voucher_no, account, debit, credit):
    """
    Delete existing GL entries using an SQL query and log the names of deleted entries.
    """
    try:
        # Fetch existing GL entries
        existing_gl_entries = frappe.get_all('GL Entry', filters={
            'voucher_no': voucher_no,
            'account': account,
            'debit': debit,
            'credit': credit
        }, fields=['name'])

        # Check if there are entries to delete
        if existing_gl_entries:
            # Log the GL entry names before deletion
            entry_names = [entry['name'] for entry in existing_gl_entries]
            frappe.logger().info(f"Deleting GL Entries: {', '.join(entry_names)}")

            # Log the GL entry names as a Frappe message (optional, for user feedback)
            frappe.log_error(message=f"Deleted GL Entries: {', '.join(entry_names)}",title="Deleted GL Entries")

            # Delete the entries using an SQL query
            frappe.db.sql("""
                DELETE FROM `tabGL Entry`
                WHERE voucher_no = %s AND account = %s AND debit = %s AND credit = %s
            """, (voucher_no, account, debit, credit))

            # Commit the deletion
            frappe.db.commit()

    except Exception as e:
        frappe.throw(f"Error deleting GL entry: {str(e)}")


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
        def validate_account(account_type):
            frappe.throw(_("{0} account not found while submitting purchase receipt").format(account_type))  
        def get_debit_account(lvc):
            return frappe.db.get_value('Landed Cost Voucher', lvc, 'custom_debit_account')      
        def make_landed_cost_gl_entries(item, debit_accounts):
             # Amount added through landed-cost-voucher
            if item.landed_cost_voucher_amount and landed_cost_entries:
                if (item.item_code, item.name) in landed_cost_entries:
                    for account, amount in landed_cost_entries[(item.item_code, item.name)].items():
                        account_currency = get_account_currency(account)
                        credit_amount = (
                            flt(amount["base_amount"])
                            if (amount["base_amount"] or account_currency != self.company_currency)
                            else flt(amount["amount"])
                        )

                        if not account:
                            validate_account("Landed Cost Account")

                        # Check if GL entry already exists
                        #delete_existing_gl_entry(self.name, account, 0.0, credit_amount)
                       
                        # self.add_gl_entry(
                        #     gl_entries=gl_entries,
                        #     account=account,
                        #     cost_center=item.cost_center,
                        #     debit=0.0,
                        #     credit=credit_amount,
                        #     remarks=remarks,
                        #     against_account=stock_asset_account_name,
                        #     credit_in_account_currency=flt(amount["amount"]),
                        #     account_currency=account_currency,
                        #     project=item.project,
                        #     item=item,
                        # )
                        gl_entries.append(
                                self.get_gl_dict(
                                    {
                                        "account": account,
                                        "credit": credit_amount,
                                        "against": '',
                                        'project': item.project,
                                        "remarks": remarks,
                                        "cost_center": item.cost_center,
                                        "voucher_type": 'Purchase Receipt',
                                        "voucher_no": self.name,
                                        "posting_date": self.posting_date,
                                        "is_opening": self.get("is_opening") or "No",
                                        "credit_in_account_currency":flt(amount["amount"]),
                                        "account_currency":account_currency
                                    },
                                    item=item
                                )
                            ) 
                        
                            
                ### Make debit entry
                if len(debit_accounts) > 0:
                    debit_new_amount = flt(item.landed_cost_voucher_amount / len(debit_accounts))
                    frappe.db.set_value('Purchase Receipt', self.name, 'custom_landed_cost_details', str(debit_accounts))
                    
                    for dbcnt in debit_accounts:
                        # Check if GL entry already exists
                        # delete_existing_gl_entry(self.name, dbcnt.get('account'), dbcnt.get('amount'), 0.0)
                        # self.add_gl_entry(
                        #     gl_entries=gl_entries,
                        #     account=dbcnt.get('account'),
                        #     cost_center=item.cost_center,
                        #     debit=dbcnt.get('amount'),
                        #     against_account=stock_asset_account_name,
                        #     credit=0.0,
                        #     remarks=remarks,
                        #     project=item.project,
                        #     item=item,
                        # )
                        gl_entries.append(
                                self.get_gl_dict(
                                    {
                                        "account": dbcnt.get('account'),
                                        "debit":dbcnt.get('amount'),
                                        "against": '',
                                        'project': item.project,
                                        "remarks": remarks,
                                        "cost_center": item.cost_center,
                                        "voucher_type": 'Purchase Receipt',
                                        "voucher_no": self.name,
                                        "posting_date": self.posting_date,
                                        "is_opening": self.get("is_opening") or "No",
                                        "credit_in_account_currency":flt(amount["amount"]),
                                        "account_currency":account_currency
                                    },
                                    item=item
                                )
                            ) 
              
        
        for d in self.get("items"):
            """ For Landed Cost Voucher """
            if flt(d.qty) and (flt(d.valuation_rate) or self.is_return):
                remarks = self.get("remarks") or _("Accounting Entry for {0}").format(
                    "Asset" if d.is_fixed_asset else "Stock"
                )
                landed_cost_entries,debit_accounts = get_item_account_wise_additional_cost(self.name)
                if d.is_fixed_asset:
                    stock_asset_account_name = d.expense_account
                elif warehouse_account.get(d.warehouse):
                    stock_asset_account_name = warehouse_account[d.warehouse]["account"]
                if (flt(d.valuation_rate) or self.is_return or d.is_fixed_asset) and flt(d.qty) :
                    make_landed_cost_gl_entries(d,debit_accounts)
        
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
        print(  gl_entries ,"00")       
        return process_gl_map(gl_entries, merge_entries=merge_value)    


    # def make_gl_entries(self, gl_entries=None, from_repost=False, via_landed_cost_voucher=False):
    #     from finance_car.overrides.stock_controller import CustomStockController
    #     CustomStockController.make_gl_entries(self, gl_entries, from_repost, via_landed_cost_voucher)
    #     print("accouting Entry from custom doc added")
    
    
    
  
