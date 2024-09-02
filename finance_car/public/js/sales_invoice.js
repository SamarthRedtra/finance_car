
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

frappe.ui.form.on('Accounting Entries', {
    debit: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    credit: function(frm, cdt, cdn) {
        calculate_totals(frm);
    },
    custom_accouting_entry_remove: function(frm, cdt, cdn) {
        calculate_totals(frm);
    }
});


function calculate_totals(frm) {
    let total_debit = 0;
    let total_credit = 0;

    // Iterate through each row in the custom_accouting_entry child table
    frm.doc.custom_accouting_entry.forEach(function(row) {
        total_debit += flt(row.debit);
        total_credit += flt(row.credit);
    });

    // Set the calculated totals to the respective fields in the Purchase Order doctype
    frm.set_value('custom_total_debit', total_debit);
    frm.set_value('custom_total_credit', total_credit);
    frm.refresh_field('custom_total_debit');
    frm.refresh_field('custom_total_credit');
    console.log(total_debit, total_credit,"00")
}
