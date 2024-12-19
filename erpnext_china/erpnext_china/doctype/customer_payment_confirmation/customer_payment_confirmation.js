// Copyright (c) 2024, Digitwise Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Customer Payment Confirmation", {
	refresh(frm) {
		if (frm.doc.__islocal) {
			frm.set_value("transaction_date", frappe.datetime.now_date());
		}
		frm.set_query("bank_account",function() {
				return {
					filters: {
						"party_type": "Customer",
						"party": frm.doc.customer,
						"disabled": 0
					}
				}
			}
		)
	},
	validate(frm) {
		if(!frm.doc.paid_amount) {
			frappe.throw(__("Amount should be greater than zero."));
		}
	}
});
