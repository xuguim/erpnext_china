from erpnext.stock.doctype.batch.batch import Batch
import frappe,datetime

class CustomBatch(Batch):
    
    def before_save(self):
        # 修改名称，保持名称唯一性
        self.name = self.name + '-' + self.item

        # 根据物料有效期，补全到期日期
        item = frappe.get_doc('Item', self.item)
        if int(item.shelf_life_in_days) > 0:
            self.expiry_date = frappe.utils.add_to_date(self.manufacturing_date, days=item.shelf_life_in_days, as_string=True)
        else:
            frappe.msgprint(
                msg='物料未填写保质期，请完善物料保质期',
                title='警告',
                raise_exception=FileNotFoundError
            )
        # 根据生产日期验证批号是否正确
        if frappe.utils.getdate(self.manufacturing_date).strftime('%y%m%d') not in self.name:
            if not frappe.db.get_value('Has Role',{'parent':self.modified_by,'role':'仓库管理'}):
                frappe.msgprint(
                    msg='批号名称与生产日期不具备一致性，请核实后重新输入。（如果批号本身与生产日期不具备一致性，请联系管理人员录入）',
                    title='警告',
                    raise_exception=FileNotFoundError
                    )