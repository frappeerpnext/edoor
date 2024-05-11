// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Folio Transaction", {
	onload(frm) {
        
        
	},
  refresh(frm) {
    updateTransactionList(frm) 

    if(frm.doc.parent_reference){
      frm.set_intro(
        "This transaction is a sub transaction of " + "<a href=" + '/app/folio-transaction/' + frm.doc.parent_reference + "><strong>" + frm.doc.parent_reference + "</strong></a>" + " folio transaction",  
        "blue"
      );
    }

    if (frm.doc.source_transaction_number) {
      frm.set_intro(
        "This transaction has been transferred from the Reservation Folio " + "<a href=" + '/app/reservation-folio/' + frm.doc.source_transaction_number + "><strong>"  + frm.doc.source_transaction_number + "</strong></a>."
        + "Transaction Number " + "<a href=" + '/app/folio-transaction/' + frm.doc.reference_folio_transaction + "><strong>"  + frm.doc.reference_folio_transaction + "</strong></a>", "blue"
      );
    }

    if (frm.doc.target_transaction_number) {
      
    }

    // if(frm.doc.vendor){
    //   frm.set_intro(
    //     "This folio transaction is from " + "<strong>Payable Ledger</strong> transaction. View transaction " + "<a href=" + '/app/payable-ledger/' + frm.doc.transaction_number + "><strong>" + frm.doc.parent_reference + "</strong></a>",  
    //     "blue"
    //   );
    // }

    if (frm.doc.reservation_stay) {
      frm.add_custom_button(
        __("View Reservation Stay"),
        function () {
          window.open("/frontdesk/stay-detail/" + frm.doc.reservation_stay);
        },
        __("View")
      );
    }

    if (frm.doc.reservation) {
      frm.add_custom_button(
        __("View Reservation"),
        function () {
          window.open("/frontdesk/reservation-detail/" + frm.doc.reservation);
        },
        __("View")
      );
    }
  },
  setup(frm) {
      for (const key in frm.fields_dict) {
        if (
          [
            "Currency",
            "Data",
            "Int",
            "Link",
            "Date",
            "Datetime",
            "Float",
            "Select",
          ].includes(frm.fields_dict[key].df.fieldtype)
        ) {
          frm.fields_dict[key].$wrapper.addClass("custom_control");
        }
      }
    },
});




function updateTransactionList(frm) {

	const html = frappe.render_template("folio_transaction_list", frm)
	$(frm.fields_dict['item_list'].wrapper).html(html);
	frm.refresh_field('item_list');


  const html_summary = frappe.render_template("folio_transaction_summary_list", frm)
	$(frm.fields_dict['summary_list'].wrapper).html(html_summary);
	frm.refresh_field('summary_list');
} 