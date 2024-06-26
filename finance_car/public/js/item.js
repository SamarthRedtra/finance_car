frappe.ui.form.on('Item', {
    refresh: function(frm) {
        if (frm.doc.custom_vehicle) {
        frm.trigger("custom_vehicle");
        }
    },
    custom_vehicle: function(frm) {
        console.log("hehhe",frm.custom_vehicle);
        if (frm.doc.custom_vehicle) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'FC Vehicle',
                    name: frm.doc.custom_vehicle
                },
                callback: function(r) {
                    if (r.message) {
                        let mandatory_fields = [];
                        frappe.model.with_doctype('FC Vehicle', function() {
                            $.each(frappe.meta.get_docfields('FC Vehicle'), function(idx, field) {
                                if (field.reqd) {
                                    mandatory_fields.push(field);
                                }
                            });
                            display_mandatory_fields(frm, mandatory_fields,r.message);
                        });
                    }
                }
            });
        }
    }
});
function display_mandatory_fields(frm, fields, doc) {
    let html = '<div class="card"><div class="card-body">';
    html += '<h5 class="card-title" style="padding-bottom: 10px; margin-bottom: 20px; font-size: 1.5em; font-weight: bold; color: #333;">Vehicle Details</h5>';
    html += '<div class="row">';
    fields.forEach(field => {
        html += `<div class="col-md-6" style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
                    <strong>${field.label}:</strong> ${doc[field.fieldname] || 'N/A'}
                 </div>`;
    });
    html += '</div></div></div>';
    frm.fields_dict.custom_vehicle_html.$wrapper.html(html);
}