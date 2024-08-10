
frappe.ui.form.on('Account', {
    refresh:(frm)=>{
        //frm.toggle_enable(["account_number"], frm.is_new());
        frm.set_df_property("account_number", "hidden", 0);
        frm.refresh_field('account_number');
    }


})