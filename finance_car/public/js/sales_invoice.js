
frappe.ui.form.on('Sales Invoice Item', {
    refresh: function(frm, cdt, cdn) {
        console.log("hhshsh")
        let row = locals[cdt][cdn];
        if (row.vehicle) {
            frm.trigger('vehicle', cdt, cdn);
        }
        
    },
    onload: (frm, cdt, cdn) => {
        console.log(frm)
        
    },
    vehicle: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.vehicle) {
            // Fetch the entire Vehicle document
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'FC Vehicle',
                    name: row.vehicle
                },
                callback: function(r) {
                    if (r.message) {
                        let vehicle_doc = r.message;
                        console.log(vehicle_doc)

                        
                        // if (vehicle_doc.field1) {
                        //     frappe.model.set_value(cdt, cdn, 'target_field1', vehicle_doc.field1);
                        // }
                        // if (vehicle_doc.field2) {
                        //     frappe.model.set_value(cdt, cdn, 'target_field2', vehicle_doc.field2);
                        // }
                        // if (vehicle_doc.field3) {
                        //     frappe.model.set_value(cdt, cdn, 'target_field3', vehicle_doc.field3);
                        // }
                        // Add more fields as necessary
                    }
                }
            });
        }
    }
});
