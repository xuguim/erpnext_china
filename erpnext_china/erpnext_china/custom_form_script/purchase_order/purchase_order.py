import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_inter_company_transaction
from frappe.share import add_docshare
from frappe.permissions import get_role_permissions

def make_internal_sales_order(doc, method):
	if frappe.db.get_single_value("Selling Settings", "allow_generate_inter_company_transactions"):
		current_user = frappe.session.user
		frappe.set_user("Administrator")
		sales_order = make_inter_company_transaction('Purchase Order',doc.name,target_doc=None)
		validate_delivery_date(sales_order,doc)
		sales_order.save().submit()
		sales_order.db_set('owner',doc.owner)

		role_permissions = get_role_permissions(frappe.get_meta(sales_order.doctype), current_user)
		add_docshare(
			sales_order.doctype, 
			sales_order.name, 
			doc.owner, 
			read=role_permissions.get('read'), 
			write=role_permissions.get('write'), 
			submit=role_permissions.get('submit'), 
			share=1, 
			flags={"ignore_share_permission": True}
		)
		
		msg = f"""
			<div>
			<h5>已自动生成内部销售订单</h5>
			<a href="/app/sales-order/{sales_order.name}" target="_blank">{sales_order.name}</a>
			</div>
		"""

		frappe.msgprint(msg,alert=1)
		frappe.set_user(current_user)

def validate_delivery_date(sales_order,purchase_order):
	for soi in sales_order.items:
		if not soi.delivery_date:
			poi_name = soi.purchase_order_item
			poi_schedule_date = [poi.schedule_date for poi in purchase_order.items if poi.name == poi_name]
			if len(poi_schedule_date) > 0:
				soi.delivery_date = poi_schedule_date[0]
			else:
				soi.delivery_date = purchase_order.schedule_date