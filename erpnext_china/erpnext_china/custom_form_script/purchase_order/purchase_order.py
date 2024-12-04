import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction

def make_internal_sales_order(doc, method):
	if frappe.db.get_single_value("Selling Settings", "allow_generate_inter_company_transactions"):
		current_user = frappe.session.user
		frappe.set_user("Administrator")
		sales_order = make_inter_company_transaction('Purchase Order',doc.name,target_doc=None)
		sales_order.save().submit()
		msg = f"""
			<div>
			<h5>已自动生成内部销售订单</h5>
			<a href="/app/sales-order/{sales_order.name}" target="_blank">{sales_order.name}</a>
			</div>
		"""

		frappe.msgprint(msg,alert=1)
		frappe.set_user(current_user)