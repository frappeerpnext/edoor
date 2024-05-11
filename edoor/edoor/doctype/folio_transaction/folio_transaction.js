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
        "This transaction has been transferred from the Reservation Folio " + "<a href=" + '/app/reservation-folio/' + frm.doc.source_transaction_number + "><strong>"  + frm.doc.source_transaction_number + "</strong></a>.", "blue"
      );
    }

    if (frm.doc.target_transaction_number && frm.doc.transaction_type == "Reservation Folio") {
      frm.set_intro(
        "This folio transaction transferred to " + frm.doc.target_transaction_type + " " + "<a href=" + '/app/reservation-folio/' + frm.doc.target_transaction_number + "><strong>" + frm.doc.target_transaction_number + "</strong></a>", "blue"
      );
    }

    if (frm.doc.target_transaction_number && frm.doc.transaction_type == "City Ledger") {
      frm.set_intro(
        "This folio transaction transferred to " + frm.doc.target_transaction_type + " " + "<a href=" + '/app/reservation-folio/' + frm.doc.target_transaction_number + "><strong>" + frm.doc.target_transaction_number + "</strong></a>", "blue"
      );
    }

    if (frm.doc.sale) {
      frm.set_intro(
        "This folio transaction is transferred from " + frm.doc.account_category + ". " + "View Sale transaction " + "<a href=" + '/app/sale/' + frm.doc.sale + "><strong>" + frm.doc.sale + "</strong></a>", "blue"
      );
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

    if (frm.doc.transaction_type == "Reservation Folio") {
      frm.add_custom_button(
        __("View Reservation Folio"),
        function () {
          window.open("/app/reservation-folio/" + frm.doc.transaction_number);
        },
        __("View")
      );
    }

    if (frm.doc.transaction_type == "Desk Folio") {
      frm.add_custom_button(
        __("View Desk Folio"),
        function () {
          window.open("/app/desk-folio/" + frm.doc.transaction_number);
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