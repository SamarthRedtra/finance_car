
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
    },
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

frappe.ui.form.on('Sales Invoice', {
    // Trigger this function when the custom_purchase_receipt field is updated
    custom_purchase_receipt: function(frm) {
        console.log('hshhess changes')
        if (frm.doc.custom_purchase_receipt) {
            // Fetch the Purchase Receipt document
            frappe.db.get_doc('Purchase Receipt', frm.doc.custom_purchase_receipt)
                .then(doc => {
                    console.log(doc,"doc ")
                    // Ensure that the Purchase Receipt has accounting entries
                    if (doc.custom_accouting_entry && doc.custom_accouting_entry.length > 0) {
                        // Loop through accounting entries in the Purchase Receipt
                        doc.custom_accouting_entry.forEach(entry => {
                            if (entry.debit > 0) { // Only consider entries with debit values
                                // Append to the Sales Invoice's child table
                                let new_row = frm.add_child('custom_accouting_entry');
                                new_row.account = entry.account;  // Set account value
                                new_row.credit = entry.debit;      // Set debit value
                                new_row.debit = 0;                 
                            }
                        });
                        frm.doc.custom_accouting_entry.forEach(function(row) {
                            frm.script_manager.trigger('debit', row.doctype, row.name);
                            frm.script_manager.trigger('credit', row.doctype, row.name);
                        });
                        // Refresh the child table in the Sales Invoice form
                        frm.refresh_field('custom_accouting_entry');
                    } else {
                        frappe.msgprint(__('No accounting entries found in the selected Purchase Receipt.'));
                    }
                    if (doc.custom_landed_cost_details) {
                        // Loop through accounting entries in the Purchase Receipt
                        let debit_acounts = safeParseLandedCostDetails(doc.custom_landed_cost_details);
                        console.log(debit_acounts)
                        debit_acounts.forEach(entry => {
                            if (entry.amount > 0 && entry.account) { // Only consider entries with debit values
                                // Append to the Sales Invoice's child table
                                let new_row = frm.add_child('custom_accouting_entry');
                                new_row.account = entry.account;  // Set account value
                                new_row.credit = entry.amount;      // Set debit value
                                new_row.debit = 0;                 
                            }
                        });
                        frm.doc.custom_accouting_entry.forEach(function(row) {
                            frm.script_manager.trigger('debit', row.doctype, row.name);
                            frm.script_manager.trigger('credit', row.doctype, row.name);
                        });
                        // Refresh the child table in the Sales Invoice form
                        frm.refresh_field('custom_accouting_entry');
                    } else {
                        frappe.msgprint(__('No landed cost entries found in the selected Purchase Receipt.'));
                    }


                });
        }
    },
    custom_get_accouting_entries: function(frm) {
            frappe.dom.freeze('Getting accounting entries...');
            frappe.call({
                method: "before_insert",
                doc: frm.doc,  
                args:{
                 is_web: 1
                } ,  // Document name (ID)
                callback: function(r) {
                    frappe.dom.unfreeze();
                    if (r.message) {
                        frappe.msgprint(__('Custom method executed: ' + r.message.message));
                        frm.refresh();
                        frm.reload_doc() // Refresh the form if required
                    }
                }
            });
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

// Helper function to safely parse custom_landed_cost_details
function safeParseLandedCostDetails(jsonString) {
    try {
        // Try to parse the JSON string normally
        return JSON.parse(jsonString);
    } catch (error) {
        console.warn('Initial JSON parse failed:', error);
        
        // Attempt to fix common issues with improperly formatted JSON strings
        let sanitizedString = jsonString
            .replace(/'/g, '"')   // Replace single quotes with double quotes
            .replace(/None/g, 'null') // Replace Python's None with null
            .replace(/True/g, 'true') // Replace True with true
            .replace(/False/g, 'false'); // Replace False with false
        
        try {
            // Try to parse the sanitized string
            return JSON.parse(sanitizedString);
        } catch (sanitizationError) {
            console.error('Sanitized string parse also failed:', sanitizationError);
            frappe.msgprint(__('Unable to parse landed cost details.'));
            return null; // Return null or an empty array as a fallback
        }
    }
}
