frappe.ui.form.on("Purchase Order", {
    refresh: function (frm) {
        // if (frm.doc.workflow_state === 'Pending CIT') {
        //     let statusIndicator = $('.indicator-pill.red'); // Adjust the selector as needed
            
        //     if (frm.doc.workflow_state === 'Pending CIT' && statusIndicator.length) {
        //         // Remove the existing "Draft" text
        //         statusIndicator.text('');

        //         // Check if the "Pending CIT" label already exists; if not, add it
        //         if (!statusIndicator.find('.pending-cit-label').length) {
        //             // Create the label element
        //             let pendingCITLabel = $('<span class="indicator-pill no-indicator-dot whitespace-nowrap red pending-cit-label" style="margin-left: 10px;">Pending CIT</span>');
                    
        //             // Append the label to the status indicator
        //             statusIndicator.append(pendingCITLabel);
        //         }
        //     } 
        // }

    },
});
