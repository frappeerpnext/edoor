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
        "This transaction has been transferred from the " + frm.doc.source_transaction_type + " " + "<a href=" + onchangeURL(frm.doc) + frm.doc.source_transaction_number + "><strong>"  + frm.doc.source_transaction_number + "</strong></a>.", "blue"
      );
    }

    if (frm.doc.target_transaction_number) {
      frm.set_intro(
        "This transaction has been transferred to " + frm.doc.target_transaction_type + " " + (frm.doc.city_ledger_name ? '(' + frm.doc.city_ledger_name + ')' : '') + " " + "<a href=" + onchangeURL(frm.doc) + frm.doc.target_transaction_number + "><strong>" + frm.doc.target_transaction_number + "</strong></a>", "blue"
      );
    }

    if (frm.doc.sale) {
      frm.set_intro(
        "This folio transaction is transferred from " + frm.doc.account_category + ". " + "View Sale transaction " + "<a href=" + '/app/sale/' + frm.doc.sale + "><strong>" + frm.doc.sale + "</strong></a>", "blue"
      );
    } 

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
          window.location.href = "/app/desk-folio/" + frm.doc.transaction_number;
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
  if (!frm.doc.is_package) {
    const html = frappe.render_template("folio_transaction_list", frm);
    $(frm.fields_dict["item_list"].wrapper).html(html);
    frm.refresh_field("item_list");

    const html_summary = frappe.render_template(
      "folio_transaction_summary_list",
      frm
    );
    $(frm.fields_dict["summary_list"].wrapper).html(html_summary);
    frm.refresh_field("summary_list");
  } else { 
    frm.call("get_package_data").then((r) => {
    //get package list
    const html = frappe.render_template("folio_transaction_list", {data:r.message.transaction_list, doc:null});
    $(frm.fields_dict["item_list"].wrapper).html(html);
    frm.refresh_field("item_list");


    //get package data summary
    const html_summary = frappe.render_template(
      "folio_transaction_summary_list",
      {summary:r.message.summary, doc:null, total_amount:frm.doc}
    );
    $(frm.fields_dict["summary_list"].wrapper).html(html_summary);
    frm.refresh_field("summary_list");



    });
  }
} 

function onchangeURL(frm) {
  if (frm.source_transaction_type == "Desk Folio" || frm.target_transaction_type == "Desk Folio" ) {
    return "/app/desk-folio/"
  }else if (frm.source_transaction_type == "Reservation Folio" || frm.target_transaction_type == "Reservation Folio") {
    return "/app/reservation-folio/" 
  }else if (frm.source_transaction_type == "Deposit Ledger" || frm.target_transaction_type == "Deposit Ledger") {
    return "/app/deposit-ledger/"
  }else if (frm.source_transaction_type == "City Ledger" || frm.target_transaction_type == "City Ledger") {
    return "/app/city-ledger/"
  } 
}