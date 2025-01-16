import frappe
from frappe.utils import flt
from erpnext.selling.doctype.sales_order_item.sales_order_item import SalesOrderItem
from erpnext.stock.dashboard.item_dashboard import get_data

class CustomSalesOrderItem(SalesOrderItem):
	@property
	def realtime_stock_qty(self):
		items = get_data(self.item_code, self.warehouse)
		if len(items) > 0:
			return items[0].actual_qty
		return 0
	
	@property
	def rate_after_discount(self):
		parent_doc = frappe.get_doc(self.parenttype,self.parent)
		return self.rate * ( 1 - parent_doc.discount_amount / parent_doc.grand_total)
	@property
	def rate_after_discount_of_stock_uom(self):
		parent_doc = frappe.get_doc(self.parenttype,self.parent)
		return self.stock_uom_rate * ( 1 - parent_doc.discount_amount / parent_doc.grand_total)