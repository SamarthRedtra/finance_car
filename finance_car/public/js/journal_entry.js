frappe.ui.form.on('Journal Entry', {
    onload: function(frm) {
        console.log("hhshsh",frm.doc.voucher_type)
        if(frm.doc.__islocal){
            frm.set_value('voucher_type', frm.doc.voucher_type);
            frm.refresh_field('voucher_type');
            frm.script_manager.trigger('voucher_type', frm.doc.doctype, frm.doc.name);
            console.log("hhshshmdd",frm.doc.voucher_type)
        }
        
    }
});
