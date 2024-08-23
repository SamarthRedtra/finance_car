frappe.ui.form.on("FC Vehicle", {
    quick_entry: function(frm) {
        console.log('sjsbdbd')
        
    },
    chassis_no: function(frm) {
        // Attach the blur event to the chassis_no field
        $(frm.fields_dict['chassis_no'].input).on('blur', function() {
            // Fetch the chassis number length from "Finance Car Settings"
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Finance Car Settings",
                    fieldname: "chassis_no_length"
                },
                callback: function(response) {
                    if (response.message) {
                        const required_length = parseInt(response.message.chassis_no_length);
                        const chassis_number = frm.doc.chassis_no;

                        // Check if the chassis number has the required minimum length
                        if (chassis_number.length < required_length) {
                            frappe.msgprint(__('Chassis number must be at least {0} characters long.', [required_length]), 'Validation');
                            frm.set_value('chassis_no', '');
                            return;
                        }

                        // Check if the chassis number exists in the backend
                        frappe.call({
                            method: "frappe.client.get_value",
                            args: {
                                doctype: "FC Vehicle",  // Specify the Doctype to check
                                filters: {
                                    chassis_no: chassis_number
                                },
                                fieldname: "name"
                            },
                            callback: function(response) {
                                if (response.message.name) {
                                    // Show message below the field
                                    frappe.msgprint(__('Chassis number already exists in the system. Please enter a different one.'), 'Duplicate Entry');
                                    frm.set_value('chassis_no', '');
                                    return;
                                }
                            }
                        });
                    }
                }
            });
        });
    }
});