import frappe

def execute():
    # Fetch only required fields and filter out FC Vehicles without investor names
    fc_vehicles = frappe.get_all(
        'FC Vehicle', 
        fields=["name", "investor_name"], 
        filters={'investor_name': ['!=', '']}
    )

    # Iterate through each FC Vehicle entry
    for vehicle in fc_vehicles:
        investor_name = vehicle.investor_name
        
        # Check if investor does not exist and create if necessary
        if not frappe.db.exists('Investor', investor_name):
            create_investor(investor_name)
        
        # Update the investor field in FC Vehicle
        frappe.db.set_value('FC Vehicle', vehicle.name, 'investor', investor_name)
    
    # Commit once after all operations
    frappe.db.commit()


def create_investor(investor_name):
    # Create a new Investor document and insert it
    doc = frappe.get_doc({
        'doctype': 'Investor',
        'investor_name': investor_name
    })
    doc.insert(ignore_permissions=True)