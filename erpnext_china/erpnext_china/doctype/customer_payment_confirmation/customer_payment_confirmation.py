# Copyright (c) 2024, Digitwise Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class CustomerPaymentConfirmation(Document):
	def validate(self):
		if flt(self.paid_amount) <= 0:
			frappe.throw(_("Amount should be greater than zero."))
