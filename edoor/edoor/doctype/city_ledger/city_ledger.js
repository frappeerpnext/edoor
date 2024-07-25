// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on("City Ledger", {
	refresh(frm) { 
        if (!frm.doc.__islocal) {
            frm.dashboard.add_indicator(__("Total Debit: {0}", [format_currency(frm.doc.total_debit)]), "blue");
            frm.dashboard.add_indicator(__("Total Credit: {0}", [format_currency(frm.doc.total_credit)]), "blue");
            frm.dashboard.add_indicator(__("Balance: {0}", [format_currency(frm.doc.balance)]), "blue");

            showCityLedgerTransaction(frm)
        }
	},
});


function showCityLedgerTransaction (frm) {  
    let parser = new DOMParser()
    $(frm.fields_dict["transaction_detail"].wrapper).html("Loading city ledger transaction...");
    frm.refresh_field("transaction_detail");

    frappe.db
    .get_list("Folio Transaction", {
      fields: [
        "name",
        "posting_date",
        "room_number",
        "account_code",
        "guest",
        "total_amount",
        "amount",
        "payment_by",
        "payment_by_phone_number",
        "owner",
        "modified_by",
        "modified",
        "reservation_status",
        "note",
        "type",
        "is_auto_post",
        "reservation_status_color",
        "account_name",
        "guest_name",
        "is_verify",
        "reference_folio_transaction"
      ],
      filters: [
        ["property", "=", frm.doc.property],
        ["transaction_type", "=", "City Ledger"],
        ["transaction_number", "=", frm.doc.name],
      ],
      order_by: "modified desc",
      limit: 20,
    })
    .then((result) => { 
        result.forEach(el => {
            let date = new Date(el.modified);
            el.modified = prettyDate(date) 
        });

        let html = frappe.render_template("city_ledger_transaction", {data:result,dataLength:result.length});
        $(frm.fields_dict["transaction_detail"].wrapper).html(html);

        
        let property = encodeURIComponent(frm.doc.property);
        let city_ledger = encodeURIComponent(frm.doc.name);
        let ledger_type = encodeURIComponent('City Ledger');
        let show_summary = "1";
        let show_package_breakdown = "1";
        let auto_refresh = "1";
    

        let baseUrl = window.location.origin + "/app/" + "query-report/General Journal Transaction";
        let params = `?property=${property}&city_ledger=${city_ledger}&ledger_type=%5B"${ledger_type}"%5D&show_summary=${show_summary}&show_package_breakdown=${show_package_breakdown}&auto_refresh=${auto_refresh}`;
    
        let url = baseUrl + params;

 
        
        $(frm.fields_dict["transaction_detail"].wrapper).on('click', '#view_general_journal_report', function () {
            window.location.href = url; // Navigate to the constructed URL
        });
    });
}

function prettyDate(date) {
    var diff = Math.floor((new Date() - date) / 1000);
    var dayDiff = Math.floor(diff / 86400);

    if (isNaN(dayDiff) || dayDiff < 0) {
        return '';
    }

    if (dayDiff === 0) {
        if (diff < 60) return 'Just now';
        if (diff < 120) return '1 minute ago';
        if (diff < 3600) return Math.floor(diff / 60) + ' minutes ago';
        if (diff < 7200) return '1 hour ago';
        if (diff < 86400) return Math.floor(diff / 3600) + ' hours ago';
    }

    if (dayDiff === 1) return 'Yesterday';
    if (dayDiff < 7) return dayDiff + ' days ago';
    if (dayDiff < 31) return Math.ceil(dayDiff / 7) + ' weeks ago';
    if (dayDiff < 365) return Math.ceil(dayDiff / 30) + ' months ago';
    return Math.ceil(dayDiff / 365) + ' years ago';
}