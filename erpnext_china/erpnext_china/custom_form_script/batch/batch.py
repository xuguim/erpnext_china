
from erpnext.stock.doctype.batch.batch import Batch


class CustomBatch(Batch):
    
    def before_save(self):
        self.name = self.name + '-' + self.item