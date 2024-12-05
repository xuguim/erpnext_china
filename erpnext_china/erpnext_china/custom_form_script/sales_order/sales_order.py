import frappe
from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from erpnext.selling.doctype.sales_order.sales_order import make_purchase_order_for_default_supplier


class CustomSalesOrder(SalesOrder):

    @frappe.whitelist()
    def get_p13(self):
        company = self.company
        name = frappe.db.get_value('Sales Taxes and Charges Template', filters={'company': company, 'tax_category': 'P13专票含税'}, fieldname='name')
        if name:
            return {'name': name}

    def before_validate(self, method=None):
        items = [d.item_code for d in self.items]
        # 只从数据库读取一次
        default_warehouse_list = frappe.get_all('Item Default', 
                filters={"parent":['in',items], 'default_warehouse':['!=','']},
                fields=['parent as item_code','company','default_warehouse']
            )
        for item in self.items:
            company_warehouse = [d.default_warehouse for d in default_warehouse_list if d.company == self.company and d.item_code==item.item_code]
            if len(company_warehouse) == 0:
                shipping_company = [d.company for d in default_warehouse_list if d.company != self.company and d.item_code==item.item_code]
                if len(shipping_company) > 0:
                    if len(shipping_company) == 1:
                        shipping_company.append('')

                    query = f"""
                        select
                            sup.name
                        from
                            `tabSupplier` sup, `tabAllowed To Transact With` al
                        where
                            sup.name = al.parent
                            and sup.is_internal_supplier = 1
                            and al.parenttype = 'Supplier'
                            and al.company = '{self.company}'
                            and sup.name in {tuple(shipping_company)}
                    """
                    internal_supplier = frappe.db.sql(query,as_dict=1)
                    if not internal_supplier:
                        frappe.throw("行 #{0} 的物料{1}已有默认仓库归属的公司{2}，但是并没有对应的内部供应商，请先创建内部供应商信息".format(item.idx, item.item_code, shipping_company[0]))
                    item.delivered_by_supplier = 1
                    item.supplier = internal_supplier[0].name
                else:
                    frappe.throw("行 #{0} 的物料没有公司{1}的默认值配置，请添加配置或检查是否用错了下单公司".format(item.idx, self.company))
        
        # 此时is_internal_customer字段可能还没被赋值
        internal_customer = frappe.db.exists("Customer", {"name":self.customer,"is_internal_customer": 1, "disabled": 0})
        if internal_customer:
            self.clear_drop_ship()
            self.get_final_customer()

    def clear_drop_ship(self):
        for d in self.get("items"):
            d.delivered_by_supplier = 0
            d.supplier = None

    def get_final_customer(self):
        reference_po = list(set([d.purchase_order for d in self.items]))
        if len(reference_po) > 0 and reference_po[0]:
            po_name = reference_po[0]
            query = f"""
                select
                    so.customer
                from
                    (select
                        distinct poi.sales_order
                    from
                        `tabPurchase Order` po, `tabPurchase Order Item` poi
                    where
                        po.name = poi.parent
                        and po.name = '{po_name}') po_so
                left join
                    `tabSales Order` so on so.name = po_so.sales_order
            """

            res = frappe.db.sql(query,as_dict=1)
            if len(res) > 0:
                self.final_customer = res[0].customer

            


def make_internal_purchase_order(doc,method=None):
    if frappe.db.get_single_value("Selling Settings", "allow_generate_inter_company_transactions"):
        internal_suppliers = frappe.get_all('Supplier', filters={'is_internal_supplier':1,'disabled':0},pluck='name')
        items = [d for d in doc.items if d.delivered_by_supplier and d.supplier in internal_suppliers]
        if not items:
            return
        current_user = frappe.session.user
        frappe.set_user("Administrator")
        purchase_orders = make_purchase_order_for_default_supplier(doc.name, items)
        msg = f"""
            <h5>已自动生成{len(purchase_orders)}张采购订单</h5>
        """
        for po in purchase_orders:
            po.save().submit()
            msg += f"""
                <a href="/app/purchase-order/{po.name}" target="_blank">{po.name}</a>
            """
        frappe.msgprint(f"""<div>{msg}<div>""",alert=1)
        frappe.set_user(current_user)

