from erpnext.stock.doctype.batch.batch import Batch
import frappe,datetime

class CustomBatch(Batch):
    
    def before_save(self):
        # 修改名称，保持名称唯一性
        self.name = self.name + '-' + self.item

        # 根据生产日期验证批号是否正确
        def check_manufactruing_date_in_batch_no(self):
            '''验证生产日期不超出批号30天'''
            manufacturing_date = frappe.utils.getdate(self.manufacturing_date)
            for days in list(range(-31,1)):
                result = False
                if frappe.utils.add_to_date(manufacturing_date, days=days).strftime('%y%m%d') in self.name:
                    result = True
                    break
            return result

        if self.custom_batchno_with_manufacturing_date == 1:
            # 选择从批号中创建生产日期
            year_pos = 999
            get_years = lambda: [str(datetime.datetime.now().year - i)[2:] for i in range(4)]
            for year in get_years():
                if self.name.find(year) != -1:
                    if self.name.find(year) < year_pos:
                        year_pos = self.name.find(year)
            self.manufacturing_date = datetime.datetime.strptime(self.name[year_pos:year_pos+6],'%y%m%d')
        else:
            if not check_manufactruing_date_in_batch_no(self):
                if not frappe.db.get_value('Has Role',{'parent':self.modified_by,'role':'仓库管理11'}):
                    frappe.msgprint(
                        msg='批号名称与生产日期不具备一致性，请核实后重新输入。（如果批号本身与生产日期不具备一致性，请联系管理人员录入）',
                        title='警告',
                        raise_exception=FileNotFoundError
                        )

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