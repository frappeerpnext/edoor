// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Deposit Ledger", {
    refresh(frm) {
      set_indicator(frm); 
      if (!frm.doc.__islocal) {
        getItemListFromGuestFolio(frm);
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
  
  function set_indicator(frm) {
    if (frm.doc.__islocal) return;
  
    if (frm.doc.total_debit > 0)
      frm.dashboard.add_indicator(
        __("Total Debit: {0}", [format_currency(frm.doc.total_debit)]),
        "gray"
      );
    if (frm.doc.total_credit > 0)
      frm.dashboard.add_indicator(
        __("Total Credit: {0}", [format_currency(frm.doc.total_credit)]),
        "pink"
      );
    if (frm.doc.balance)
      frm.dashboard.add_indicator(
        __("Balance: {0}", [format_currency(frm.doc.balance)]),
        "blue"
      );
  }
  
  function getItemListFromGuestFolio(frm) {
    $(frm.fields_dict["item_list"].wrapper).html(
      "Loading folio transaction list..."
    );
    frm.refresh_field("item_list");
    frappe.db
      .get_list("Folio Transaction", {
        fields: [
          "name",
          "transaction_number",
          "posting_date",
          "reservation",
          "room_number",
          "parent_reference",
          "type",
          "account_code",
          "account_name",
          "quantity",
          "input_amount",
          "price",
          "amount",
          "discount_amount",
          "total_tax",
          "total_amount",
          "bank_fee_amount",
          "note",
          "creation",
          "owner",
          "modified",
          "modified_by",
          "show_print_preview",
          "print_format",
          "is_auto_post",
          "allow_enter_quantity",
          "target_transaction_number",
          "city_ledger_name",
          "source_transaction_number",
          "report_description",
        ],
        filters: [
          ["transaction_number", "=", frm.doc.name],
          ["transaction_type", "=", "Deposit Ledger"],
        ],
        order_by: "modified asc",
        limit: 1000,
      })
      .then((result) => {
        const folio_transaction = result;
        folio_transaction.forEach((r) => {
          r.quantity = r.allow_enter_quantity == 1 ? r.quantity : 0;
          r.total_amount =
            r.type == "Credit"
              ? (r.total_amount - r.bank_fee_amount) * -1
              : r.total_amount;
          r.amount = r.type == "Credit" ? r.amount * -1 : r.amount;
          r.price =
            r.type == "Credit" ? (r.price + r.bank_fee_amount) * -1 : r.price;
        });
  
        let html = frappe.render_template("deposit_ledger_transaction_list", {
          data: folio_transaction?.filter(
            (r) => (r.parent_reference || "") == ""
          ),
        });
        $(frm.fields_dict["item_list"].wrapper).html(html);
        frm.refresh_field("item_list");
      });
  
    //   folio transaction summary
    frappe
      .call("edoor.api.reservation.get_folio_summary_by_transaction_type", {
        transaction_type: "Deposit Ledger",
        transaction_number: frm.doc.name,
      })
      .then((result) => {
        html = frappe.render_template("deposit_ledger_summary_list", {
          data: result.message,
        });
        $(frm.fields_dict["item_summary"].wrapper).html(html);
        frm.refresh_field("item_summary");
      })
      .catch((error) => {
        throw new Error(error.exception || error.message);
      });
  }
