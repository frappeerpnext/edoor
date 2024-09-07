class MyPrintPreview extends frappe.ui.form.PrintView{
    
	show(frm) {
        
		this.frm = frm;
		this.set_title();
		this.set_breadcrumbs();
		this.setup_customize_dialog();

		// print format builder beta
		this.page.add_inner_message(`
			<a style="line-height: 2.4" href="/app/print-format-builder-beta?doctype=${this.frm.doctype}">
				${__("Try the new Print Format Builder")}
			</a>
		`);

		let tasks = [
			this.set_default_print_format,
			this.set_default_print_language,
			this.set_default_letterhead,
			this.preview,
		].map((fn) => fn.bind(this));

		this.setup_additional_settings();
		return frappe.run_serially(tasks);
	}

}

frappe.ui.form.PrintView = MyPrintPreview