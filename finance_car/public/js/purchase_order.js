frappe.ui.form.on("Purchase Order", {
    refresh: function (frm) {
        if (frm.doc.workflow_state === 'Pending CIT') {
            frm.trigger('show_accounting_ledger_preview');
        }
       
        if(frm.doc.docstatus > 0) {
            cur_frm.add_custom_button(__('Accounting Ledger'), function() {
                frappe.route_options = {
                    voucher_no: frm.doc.name,
                    from_date: frm.doc.posting_date,
                    to_date: moment(frm.doc.modified).format('YYYY-MM-DD'),
                    company:frm.doc.company,
                    group_by: "Group by Voucher (Consolidated)",
                    show_cancelled_entries: frm.doc.docstatus === 2,
                    ignore_prepared_report: true
                };
                frappe.set_route("query-report", "General Ledger");
            }, __("View"));
        }
    },
    show_accounting_ledger_preview: function(frm) {
        let me = this;
        if (!frm.is_new() && frm.doc.docstatus == 0) {
            frm.add_custom_button(
                __("Accounting Ledger"),
                function () {
                    frappe.call({
                        type: "GET",
                        method: "finance_car.overrides.purchase_order.show_accounting_ledger_preview",
                        args: {
                            company: frm.doc.company,
                            doctype: frm.doc.doctype,
                            docname: frm.doc.name,
                        },
                        callback: function (response) {
                            console.log(response,  response.message.gl_columns, response.message.gl_data)
                            make_dialog(
                                "Accounting Ledger Preview",
                                "accounting_ledger_preview_html",
                                response.message.gl_columns,
                                response.message.gl_data
                            );
                        },
                    });
                },
                __("Preview")
            );
        }
    }
});

function make_dialog(label, fieldname, columns, data) {
    let me = this;
    let dialog = new frappe.ui.Dialog({
        size: "extra-large",
        title: __(label),
        fields: [
            {
                fieldtype: "HTML",
                fieldname: fieldname,
            },
        ],
    });

    setTimeout(function () {
        get_datatable(columns, data, dialog.get_field(fieldname).wrapper);
    }, 200);

    dialog.show();
}

function get_datatable(columns, data, wrapper) {
    const datatable_options = {
        columns: columns,
        data: data,
        dynamicRowHeight: true,
        checkboxColumn: false,
        inlineFilters: true,
    };

    new frappe.DataTable(wrapper, datatable_options);
}

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