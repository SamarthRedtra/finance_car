// Debounce function
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

frappe.provide("frappe.ui.form");

frappe.ui.form.FCVehicleQuickEntryForm = class FCVehicleQuickEntryForm extends frappe.ui.form.QuickEntryForm {
    constructor(doctype, after_insert, init_callback, doc, force) {
        super(doctype, after_insert, init_callback, doc, force);
    }

    render_dialog() {
        // Customize the dialog rendering if needed
        super.render_dialog();
        console.log('Quick Entry form rendered');

        // Attach custom logic for the chassis_no field when the Quick Entry form is opened
        this.dialog.fields_dict.chassis_no.df.onchange = debounce(() => {
            this.validate_chassis_no();
        }, 2000); // 300 ms debounce delay
    }

    validate_chassis_no() {
        console.log('Validating chassis number');
        const chassis_number = this.dialog.get_value('chassis_no');

        // Fetch the chassis number length from "Finance Car Settings"
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Finance Car Settings",
                fieldname: "chassis_no_length"
            },
            callback: (response) => {
                if (response.message) {
                    const required_length = parseInt(response.message.chassis_no_length);

                    // Check if the chassis number has the required minimum length
                    if (chassis_number.length < required_length) {
                        frappe.msgprint(__('Chassis number must be at least {0} characters long.', [required_length]), 'Validation');
                        // this.dialog.set_value('chassis_no', '');
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
                        callback: (response) => {
                            if (response.message.name) {
                                // Show message below the field
                                frappe.msgprint(__('Chassis number already exists in the system. Please enter a different one.'), 'Duplicate Entry');
                                // this.dialog.set_value('chassis_no', '');
                            }
                        }
                    });
                }
            }
        });
    }

    insert() {
        // Custom insert logic if needed
        return super.insert();
    }
};

// Override the existing Quick Entry form for FC Vehicle Doctype
frappe.quick_entry_map['FC Vehicle'] = frappe.ui.form.FCVehicleQuickEntryForm;