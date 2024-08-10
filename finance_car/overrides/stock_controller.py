import frappe
from frappe.utils import cint, flt
from frappe import _
import erpnext
from erpnext.accounts.general_ledger import (
    make_gl_entries,
    make_reverse_gl_entries,
    process_gl_map,
)
from erpnext.stock import get_warehouse_account_map
from erpnext.controllers.stock_controller import StockController

class CustomStockController(StockController):
    def make_gl_entries(self, gl_entries=None, from_repost=False, via_landed_cost_voucher=False):
        if self.docstatus == 2:
            make_reverse_gl_entries(voucher_type=self.doctype, voucher_no=self.name)

        provisional_accounting_for_non_stock_items = cint(
            frappe.get_cached_value(
                "Company", self.company, "enable_provisional_accounting_for_non_stock_items"
            )
        )

        is_asset_pr = any(d.get("is_fixed_asset") for d in self.get("items"))

        if (
            cint(erpnext.is_perpetual_inventory_enabled(self.company))
            or provisional_accounting_for_non_stock_items
            or is_asset_pr
        ):
            warehouse_account = get_warehouse_account_map(self.company)
            if self.docstatus == 1:
                if not gl_entries:
                    gl_entries = self.get_gl_entriess(warehouse_account, via_landed_cost_voucher)
                    print(gl_entries,"0000")	
                make_gl_entries(gl_entries, from_repost=from_repost)

    def get_gl_entriess(self, warehouse_account=None, default_expense_account=None, default_cost_center=None):
        if not warehouse_account:
            warehouse_account = get_warehouse_account_map(self.company)

        sle_map = self.get_stock_ledger_details()
        voucher_details = self.get_voucher_details(default_expense_account, default_cost_center, sle_map)

        gl_list = []
        warehouse_with_no_account = []
        precision = self.get_debit_field_precision()

        for item_row in voucher_details:
            sle_list = sle_map.get(item_row.name)
            sle_rounding_diff = 0.0

            if sle_list:
                for sle in sle_list:
                    if warehouse_account.get(sle.warehouse):
                        # From warehouse account
                        sle_rounding_diff += flt(sle.stock_value_difference)

                        self.check_expense_account(item_row)

                        # Expense account/ target_warehouse / source_warehouse
                        if item_row.get("target_warehouse"):
                            warehouse = item_row.get("target_warehouse")
                            expense_account = warehouse_account[warehouse]["account"]
                        else:
                            expense_account = item_row.expense_account

                        gl_list.append(
                            self.get_gl_dict(
                                {
                                    "account": warehouse_account[sle.warehouse]["account"],
                                    "against": expense_account,
                                    "cost_center": item_row.cost_center,
                                    "project": item_row.project or self.get("project"),
                                    "remarks": self.get("remarks") or _("Accounting Entry for Stock"),
                                    "debit": flt(sle.stock_value_difference, precision),
                                    "is_opening": item_row.get("is_opening")
                                    or self.get("is_opening")
                                    or "No",
                                },
                                warehouse_account[sle.warehouse]["account_currency"],
                                item=item_row,
                            )
                        )

                        gl_list.append(
                            self.get_gl_dict(
                                {
                                    "account": expense_account,
                                    "against": warehouse_account[sle.warehouse]["account"],
                                    "cost_center": item_row.cost_center,
                                    "remarks": self.get("remarks") or _("Accounting Entry for Stock"),
                                    "debit": -1 * flt(sle.stock_value_difference, precision),
                                    "project": item_row.get("project") or self.get("project"),
                                    "is_opening": item_row.get("is_opening")
                                    or self.get("is_opening")
                                    or "No",
                                },
                                item=item_row,
                            )
                        )
                    elif sle.warehouse not in warehouse_with_no_account:
                        warehouse_with_no_account.append(sle.warehouse)

            if abs(sle_rounding_diff) > (1.0 / (10**precision)) and self.is_internal_transfer():
                warehouse_asset_account = ""
                if self.get("is_internal_customer"):
                    warehouse_asset_account = warehouse_account[item_row.get("target_warehouse")]["account"]
                elif self.get("is_internal_supplier"):
                    warehouse_asset_account = warehouse_account[item_row.get("warehouse")]["account"]

                expense_account = frappe.get_cached_value("Company", self.company, "default_expense_account")
                if not expense_account:
                    frappe.throw(
                        _(
                            "Please set default cost of goods sold account in company {0} for booking rounding gain and loss during stock transfer"
                        ).format(frappe.bold(self.company))
                    )

                gl_list.append(
                    self.get_gl_dict(
                        {
                            "account": expense_account,
                            "against": warehouse_asset_account,
                            "cost_center": item_row.cost_center,
                            "project": item_row.project or self.get("project"),
                            "remarks": _("Rounding gain/loss Entry for Stock Transfer"),
                            "debit": sle_rounding_diff,
                            "is_opening": item_row.get("is_opening") or self.get("is_opening") or "No",
                        },
                        warehouse_account[sle.warehouse]["account_currency"],
                        item=item_row,
                    )
                )

                gl_list.append(
                    self.get_gl_dict(
                        {
                            "account": warehouse_asset_account,
                            "against": expense_account,
                            "cost_center": item_row.cost_center,
                            "remarks": _("Rounding gain/loss Entry for Stock Transfer"),
                            "credit": sle_rounding_diff,
                            "project": item_row.get("project") or self.get("project"),
                            "is_opening": item_row.get("is_opening") or self.get("is_opening") or "No",
                        },
                        item=item_row,
                    )
                )


        if len(self.custom_accouting_entry) > 0:
            for custom_entry in self.custom_accouting_entry:
                gl_list.append(
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
            print('gl_list',gl_list)    

        if warehouse_with_no_account:
            for wh in warehouse_with_no_account:
                if frappe.get_cached_value("Warehouse", wh, "company"):
                    frappe.throw(
                        _(
                            "Warehouse {0} is not linked to any account, please mention the account in the warehouse record or set default inventory account in company {1}."
                        ).format(wh, self.company)
                    )

        return process_gl_map(gl_list, precision=precision)