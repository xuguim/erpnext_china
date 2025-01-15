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
		if self.is_new():
			frappe.log('new')
			return 0
		so_info = frappe.get_all("Sales Order", filters={'name':self.parent}, fields=["grand_total","discount_amount"])[0]
		frappe.log(so_info)
		if flt(so_info.discount_amount) == 0 or flt(so_info.grand_total) == 0:
			return self.rate
		else:
			return self.rate * ( 1 - self.discount_amount / so_info.grand_total)
		
	@property
	def rate_after_discount_of_stock_uom(self):
		return self.rate_after_discount / self.conversion_factor