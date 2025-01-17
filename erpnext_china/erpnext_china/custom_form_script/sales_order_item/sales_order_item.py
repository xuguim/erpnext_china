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
		try:
			parent_doc = frappe.db.get_value(self.parenttype,self.parent, ["discount_amount", "grand_total"], as_dict=True)
			if parent_doc:
				return self.rate * ( 1 - parent_doc.discount_amount / parent_doc.grand_total)
			else:
				return 0
		except:
			return 0

	@property
	def rate_after_discount_of_stock_uom(self):
		try:
			parent_doc = frappe.db.get_value(self.parenttype,self.parent, ["discount_amount", "grand_total"], as_dict=True)
			if parent_doc:
				return self.stock_uom_rate * ( 1 - parent_doc.discount_amount / parent_doc.grand_total)
			else:
				return 0
		except:
			return 0