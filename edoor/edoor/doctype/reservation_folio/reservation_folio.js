// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reservation Folio", {
  refresh(frm) {

    set_indicator(frm);
    if (frm.doc.tax_invoice_number) {
      frm.set_intro(
        "This Folio has Generate Tax Invoice - " + frm.doc.tax_invoice_number,
        "blue"
      );
    }
    if(frm.doc.is_master){
      frm.set_intro(
        "This Folio is a <b>Master Folio</b> of Reservation Stay" + " <b>" + frm.doc.reservation_stay + "</b>",  
        "blue"
      );
    }
    frm.add_custom_button(
      __("View Reservation Stay"),
      function () {
        window.open("/app/reservation-stay/" + frm.doc.reservation_stay);
      },
      __("View")
    );

    frm.add_custom_button(
      __("View Reservation"),
      function () {
        window.open("/app/reservation/" + frm.doc.reservation);
      },
      __("View")
    );

    if (frm.doc.tax_invoice_number) {
      frm.add_custom_button(
        __("View Tax Invoice"),
        function () {
          frappe.set_route("Form", "Tax Invoice", frm.doc.tax_invoice_number);
        },
        __("View")
      );
    }

         setupActionMenu(frm);

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

function setupActionMenu(frm) {
  frm.add_custom_button(
    __("Post Charge"),
    async function () {
      let dlg = new frappe.ui.Dialog({
        title: "Post Charge",
        fields: [
           
          {
            fieldname: "reservation_stay",
            fieldtype: "Link",
            label: "Reservation Stay",
            options: "Reservation Stay",
            filters:{"reservation":frm.doc.reservation}
          } ,
          {"fieldtype":"Column Break","fieldname": "column_break_01",},
          {
            fieldname: "room_id",
            fieldtype: "Link",
            label: "Room Number",
            options: "Room",
            filters:{"property":frm.doc.property}
          } ,
          {"fieldtype":"Column Break","fieldname": "column_break_02",},
          {
            fieldname: "guest",
            fieldtype: "Link",
            label: "Guest",
            options: "Customer"
          } ,
          {
            "fieldname": "charge_section",
            "fieldtype": "Section Break",
            "label": "Charge Amount"
           },
           {
            fieldname: "account_code",
            fieldtype: "Link",
            label: "Account Code",
            options: "Account Code"
          } ,
          {"fieldtype":"Column Break"},
          {
            fieldname: "input_amount",
            fieldtype: "Currency",
            label: "Amount",
          } ,
        ],
        primary_action_label: "Save",
        primary_action(d) {
          alert("save me")
          
        },
      });

      dlg.show();
    },
    __("Action")
  );

  if(frm.doc.tax_invoice_number){
    return
  }

  frm.add_custom_button(
    __("Generate Tax Invoice"),
    async function () {

    exchange_rate = await frappe.call("edoor.api.utils.get_exchange_rate",{property:frm.doc.property})
    
 
      let dlg = new frappe.ui.Dialog({
        title: "Generate Tax Invoice",
        fields: [
          {
            fieldname: "info",
            label: "Info",
            fieldtype: "HTML",
            options:
              "<p class='alert alert-warning'>Please make sure that once generated, the Tax Invoice cannot be deleted or regenerated.</p>",
          },
          {
            fieldname: "tax_invoice_date",
            fieldtype: "Date",
            label: "Tax Invoice Date",
          },
          {
            fieldname: "tax_invoice_type",
            fieldtype: "Select",
            label: "Tax Invoice Type",
            options: "\nTax Invoice\nCommercial Invoice",
          },
          {
            fieldname: "exchange_rate",
            fieldtype: "Currency",
            label: "Exchange Rate",
            default: exchange_rate?.message || 0,
          },
          {
            fieldname: "confirm",
            fieldtype: "Check",
            label: "I am verify that all information is correct",
          },
        ],
        primary_action_label: "Generate",
        primary_action(d) {
          if(!d.tax_invoice_date){
            frappe.throw(__("Please select tax invoice date"));
          }
          if(!d.tax_invoice_type){
            frappe.throw(__("Please select tax invoice type"));
          }
          
          if(!d.confirm){
            frappe.throw(__("Please check on check box confirm to verify all your date is correct."));
          }

          frappe.confirm(
            'Are you sure you want to proceed?',
            function() {
              dlg.freeze = true;
              frappe
                .call("edoor.api.utils.generate_tax_invoice", {
                  property: frm.doc.property,
                  document_type:'Reservation Folio',
                  folio_number: frm.doc.name,
                  tax_invoice_date: d.tax_invoice_date,
                  tax_invoice_type: d.tax_invoice_type,
                  exchange_rate: d.exchange_rate,
                })
                .then((result) => {
                  frm.reload_doc();
                  dlg.hide();
                });
          })
          
        },
      });

      dlg.show();
    },
    __("Action")
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
        ["transaction_type", "=", "Reservation Folio"],
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

      let html = frappe.render_template("folio_transaction_list", {
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
      transaction_type: "Reservation Folio",
      transaction_number: frm.doc.name,
    })
    .then((result) => {
      html = frappe.render_template("folio_summary_list", {
        data: result.message,
      });
      $(frm.fields_dict["folio_summary"].wrapper).html(html);
      frm.refresh_field("folio_summary");
    })
    .catch((error) => {
      throw new Error(error.exception || error.message);
    });
}
