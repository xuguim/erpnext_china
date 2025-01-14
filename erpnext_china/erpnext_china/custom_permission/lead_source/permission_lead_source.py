import frappe

def has_query_permission(user):
	if frappe.db.get_value('Has Role',{'parent':user,'role':'System Manager'}):
		conditions = ''
	else:
		if '网络推广' in frappe.get_roles(user):
			conditions = f''' `tabLead Source`.`name` != "业务自录入" '''
			return conditions

def has_permission(doc, user, permission_type=None):
	if frappe.db.get_value('Has Role',{'parent':user,'role':['in',['System Manager']]}):
		return True
	else:
		if doc.name == "业务自录入" and '网络推广' in frappe.get_roles(user):
			return False
		return True
