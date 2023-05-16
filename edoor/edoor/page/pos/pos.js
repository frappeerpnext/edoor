frappe.pages['pos'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
	$(".page-head").remove();
}

MyPage = Class.extend({
	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			single_column: true
		});
		this.make();
	},
	make: function() {
		$(frappe.render_template("pos", this)).appendTo(this.page.main);
	}
})