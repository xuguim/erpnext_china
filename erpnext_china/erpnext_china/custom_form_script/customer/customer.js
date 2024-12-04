frappe.ui.form.on('Customer', {
	refresh(frm) {
		// 内部客户字段仅财务和管理员可见
		if (has_common(frappe.user_roles, ["Administrator", "System Manager", "Accounts User", "Accounts Manager"])) {
			frm.set_df_property('internal_customer_section', 'hidden', 0);
		}
	}
});