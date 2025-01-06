import math
import json
from datetime import datetime

import frappe

from .wechat import api

def add_employee_checkin_log(check_in_data, code, employee):
	"""
	写入考勤记录
	"""
	checkin_time = datetime.fromtimestamp(check_in_data.get('checkin_time'))
	exception_type = check_in_data.get('exception_type')
	doc_data = {
		"doctype": "Employee Checkin Log",
		"employee": employee,
		"checkin_time": checkin_time,
		"code": code,
		"exception_type": exception_type
	}

	checkin_type = check_in_data.get('checkin_type')
	address = ','.join([check_in_data.get('location_title', ''), check_in_data.get('location_detail', '')])
	if checkin_type in ['上班打卡', '下班打卡']:
		doc_data.update({
			"location_or_device_id": address,
			"log_type": '内勤-考勤机',
		})
	else:
		doc_data.update({
			"address": address,
			"longitude": check_in_data.get('lng'),
			"latitude": check_in_data.get('lat'),
			"log_type": '外勤-手机定位',
		})
	doc = frappe.get_doc(doc_data).insert(ignore_permissions=True)
	frappe.db.commit()


def get_today_timestamp():
	"""
	返回每天00:00:00 到当前的两个时间点
	"""
	now = datetime.now()
	year = now.year
	month = now.month
	day = now.day
	start_time = int(datetime(year, month, day, 0, 0, 0).timestamp())
	end_time = int(now.timestamp())
	return start_time, end_time


def get_temp_users():
	"""
	没有梳理好Employee和User中的数据时，暂时用
	"""
	users_id = [
		"bianxuezhen@zhushigroup.cn",
		"wangzhenhua@zhushigroup.cn",
		"lichengxi@zhushigroup.cn",
		"limingyuan@zhushigroup.cn",
		"lixiulu@zhushigroup.cn",
		"houjun@zhushigroup.cn",
		"dongjuanjuan@zhushigroup.cn",
		"liziyuan@zhushigroup.cn",
		"yangzhen@zhushigroup.cn",
		"liuchao@zhushigroup.cn"
	]
	users = []
	for uid in users_id:
		user = {"user": uid, "employee": "", "wecom": uid}
		custom_wecom_uid = frappe.db.get_value("User", uid, fieldname='custom_wecom_uid')
		if custom_wecom_uid:
			user.update({"wecom": custom_wecom_uid})
		employee_name = frappe.db.get_value("Employee", {"user_id": uid}, fieldname="name")
		if employee_name:
			user.update({"employee": employee_name})
		users.append(user)
	return users


def get_all_active_users():
	employees = frappe.get_all("Employee", filters={"status": 'Active'}, fields=["name", "user_id"])
	users = []
	for employee in employees:
		user = {"user": employee.user_id, "employee": employee.name, "wecom": employee.user_id}
		if employee.user_id:
			custom_wecom_uid = frappe.db.get_value("User", employee.user_id, fieldname='custom_wecom_uid')
			if custom_wecom_uid:
				user.update({"wecom": custom_wecom_uid})
			users.append(user)
	return users


def get_user_slices(users):
	# user 每次最多100
	slices = math.ceil(len(users) / 100)
	return [users[i*100:(i+1)*100] for i in range(slices)]


def trans_user_dict(users):
	result = {}
	for user in users:
		result.update({user.get('wecom'): user})
	return result


def has_exists(code):
	return frappe.db.exists("Employee Checkin Log", {"code": code})


def timestamp_to_str(dt:int, fmt: str=r"%Y-%m-%d %H:%M:%S"):
	return datetime.fromtimestamp(dt).strftime(fmt)


def get_exists_count(users, start_time, end_time):
	count = frappe.db.count("Employee Checkin Log", filters=[
		["checkin_time", "between", [
			timestamp_to_str(start_time), 
			timestamp_to_str(end_time)
		]],
		["employee", 'in', [user.get('employee') for user in users]]
	])
	return count or 0


@frappe.whitelist(allow_guest=True)
def task_get_check_in_data():
	# [{user, employee, wecom}]
	all_users = get_all_active_users()
	# all_users = get_temp_users()
	setting = frappe.get_doc("WeCom Setting")
	access_token = setting.access_token
	
	if not access_token:
		return
	
	start_time, end_time = get_today_timestamp()
	
	# [[0-100],[100-200],[200-267]]
	user_slices = get_user_slices(all_users)
	for users in user_slices:
		results = api.get_check_in_data(access_token, [user.get("wecom") for user in users], start_time, end_time)
		local_exists_count = get_exists_count(users, start_time, end_time)
		
		# 当日已存在的记录个数和新拉取的数据个数一致说明无变化
		# 避免没有新数据增量出现也会执行has_exists去重操作
		# 过了四个打卡高峰期后，一般不会有新增量出现
		if local_exists_count >= len(results):
			continue
		
		trans_users = trans_user_dict(users)
		for result in results:
			# 这里的userid其实是我们User的custom_wecom_uid
			userid = result.get('userid')
			code = '.'.join([userid, str(result.get('checkin_time'))])

			# 每条数据根据 code 判重，code为索引字段
			if has_exists(code):
				continue

			employee = trans_users.get(userid).get('employee')
			add_employee_checkin_log(result, code, employee)


def disable_user(name):
	# 使用管理员账号进行修改
	doc = frappe.get_doc("User", name)
	try:
		if doc.enabled:
			doc.enabled = False
			doc.save(ignore_permissions=True)
	except:  # 有的可能因为信息不全在保存时报错
		pass


@frappe.whitelist(allow_guest=True)
def task_check_user_in_wecom():
	# 这里需要通过通讯录secret获取到单独的access_token
	access_token = api.get_access_token_by_secret()
	
	# 预定义白名单
	whitelist = [
		"Administrator",
		"api@api.com",
		"api001@api.com",
		"Guest",
		"admin2@zhushigroup.cn"
	]
	users = api.get_all_user_list_id(access_token)
	# 企微中所有的用户的id
	wecom_user_id_set = set([user.get("userid") for user in users])
	
	# 获取数据库中所有的user
	local_user_list = frappe.get_all("User", fields=["name", "custom_wecom_uid"])
	local_user_dict = {user.custom_wecom_uid: user.name for user in local_user_list}
	local_user_id_list = set(local_user_dict.keys())
	
	# 如果本地存在，企微不存在，则将用户关闭
	wecom_not_exist_users = local_user_id_list - wecom_user_id_set
	frappe.set_user('Administrator')
	for user in wecom_not_exist_users:
		if user:
			name = local_user_dict.get(user)
			if name not in whitelist:
				disable_user(name)
	frappe.db.commit()

			
