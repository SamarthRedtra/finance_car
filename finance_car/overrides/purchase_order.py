from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
import frappe
class CustomPurchaseOrder(PurchaseOrder):
    def on_update(self):
        print('hssh',self.as_dict())
        if self.docstatus == 0 and self.workflow_state == 'Pending CIT':
            frappe.db.sql("UPDATE `tabPurchase Order` SET status = 'Pending CIT' WHERE name = %(name)s", {'name':self.name})
            frappe.db.set_value('Purchase Order', self.name, 'status', 'Pending CIT')
            print('Exscuteds')

            
    def on_submit(self):
        super().on_submit()
        # frappe.db.sql("UPDATE `tabPurchase Order` SET status = 'Pending CIT' WHERE name = %(name)s", {'name':self.name})
        # frappe.db.commit()

    @frappe.whitelist()
    def complete_cit(self, docname):
        self.docstatus = 0
        super().on_submit()
        print('done',self.as_dict())
        


       
       

