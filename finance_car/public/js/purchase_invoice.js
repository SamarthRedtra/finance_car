frappe.ui.form.on('Purchase Invoice', {
    onload: async function(frm) {
        const purchase_account =  await frappe.db.get_single_value('Finance Car Settings', 'purchase_account');
        console.log(purchase_account.toString(),"0000")
        let grid = frm.get_field("items").grid;

        // Loop through each row in the grid
        grid.grid_rows.forEach(function(row) {
            let data = row.doc;
            data.expense_account = purchase_account.toString();
            console.log(data,'ss')
        });
    }
});

// frappe.ui.form.on('Purchase Invoice Item', {    
//     onload: async function(frm, cdt, cdn) {
//         const data = await frappe.db.get_single_value('Finance Car Settings', 'purchase_account');
//         console.log(data, "4455");
//         let item = locals[cdt][cdn]; 
//         item.account = data;
//         frm.refresh_field('account');
//     }
// });