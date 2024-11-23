import frappe
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder


class CustomSalesOrder(SalesOrder):

    @frappe.whitelist()
    def get_p13(self):
        company = self.company
        name = frappe.db.get_value('Sales Taxes and Charges Template', filters={'company': company, 'tax_category': 'P13专票含税'}, fieldname='name')
        if name:
            return {'name': name}