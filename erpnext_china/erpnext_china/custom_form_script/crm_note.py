import frappe
from frappe.model.document import Document


class CrmNote(Document):
    pass
    def before_save(self):
        self.has_value_changed("a")
        self.is_new()
        doc = self.get_doc_before_save()  # None 

        # 修改一个表的一条数据
        doc = frappe.get_doc("Auto Allocation Log", "xxxx") # 根据name获取document
        doc.sdf = 'xxxx'
        doc.aaa = 'xxxx'
        doc.save()
		