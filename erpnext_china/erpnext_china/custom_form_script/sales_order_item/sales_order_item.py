import frappe
from erpnext.selling.doctype.sales_order_item.sales_order_item import SalesOrderItem
from erpnext.stock.dashboard.item_dashboard import get_data

class CustomSalesOrderItem(SalesOrderItem):
	@property
	def realtime_stock_qty(self):
		return get_data(self.item_code, self.warehouse)[0].actual_qty