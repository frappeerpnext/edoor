frappe.pages['frontdesk'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Frontdesk',
		single_column: true
	});
}