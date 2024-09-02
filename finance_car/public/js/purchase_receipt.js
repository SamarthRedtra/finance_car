// frappe.ui.form.on('Accounting Entries', {
//     refresh: function(frm, cdt, cdn) {
//         console.log("hhshsh")
//         if(frm.doc.__islocal){
//             console.log('heeess')
//             let row = locals[cdt][cdn];
//             console.log('row',row)
        
//             // Check if the Purchase Order is new and the current row has a debit amount
//             if ( row.debit > 0) {
//                 // Shift the debit amount to credit
//                 row.credit = row.debit;
//                 row.debit = 0;
    
//             }
//             else if(row.credit>0) {
//                 row.remove()
//                 //frm.get_field("custom_accouting_entry").grid.grid_rows_by_docname[cdn].remove();
//             }
//             frm.refresh_field('custom_accouting_entry');
            
//         }
       
//     }
// });

frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        if (frm.is_new()) {
            // console.log('bjbbs')
            // let grid = frm.get_field("custom_accouting_entry").grid;

            // // Loop through each row in the grid
            // grid.grid_rows.forEach(function(row) {
            //     let data = row.doc;

            //     if (data.debit > 0) {
            //         // Shift debit amount to credit
            //         data.credit = data.debit;
            //         data.debit = 0;

            //         // Mark the row for deletion
                    
            //     }else if(data.credit>0) {
            //         row.remove();
            //         //frm.get_field("custom_accouting_entry").grid.grid_rows_by_docname[row.docname].remove();
            //     }
            // });

            // // Refresh the grid to reflect changes
            // frm.refresh_field('custom_accouting_entry');
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

