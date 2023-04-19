# Copyright (c) 2023, Senituli Taumoepeau and contributors
# For license information, please see license.txt

import datetime
import json

import frappe
from frappe import msgprint, _
from frappe.model.document import Document
from frappe.utils import getdate

class StudentAttendanceTool(Document):
	pass


@frappe.whitelist()
def get_students(date: str | datetime.date, student_group: str = None) -> dict[str, list]:
	
	filters = {"status": "Active", "student_group": "student_group", "joining_date": ["<=", date]}

	for field, value in {"student_group": student_group}.items():
		if value:
			filters[field] = value

	student_list = frappe.get_list(
		"Student", fields=["name", "student_name"], filters=filters, order_by="student_name"
	)

	attendance_list = frappe.get_list(
		"Student Attendance",
		fields=["name", "student", "student_name", "status"],
		filters={
			"date": date,
			"docstatus": 1,
		},
		order_by="student_name",
	)
#	frappe.throw(_("UNMARKED {0}.").format(attendance_list))

	unmarked_attendance = _get_unmarked_attendance(student_list, attendance_list)

	return {"marked": attendance_list, "unmarked": unmarked_attendance}


def _get_unmarked_attendance(student_list: list[dict], attendance_list: list[dict]) -> list[dict]:
	marked_students = [entry.name for entry in attendance_list]
	unmarked_attendance = []
#	frappe.throw(_("UNMARKED {0}.").format(student_list))
	for entry in student_list:
		if entry.student not in marked_students:
			unmarked_attendance.append(entry)

	return unmarked_attendance


@frappe.whitelist()
def mark_student_attendance(
	student_list: list | str,
	status: str,
	date: str | datetime.date,
	leave_type: str = None,
	student_group: str = None,
	late_entry: str = None,
	early_exit: str = None,
) -> None:
	if isinstance(student_list, str):
		student_list = json.loads(student_list)

	for student in student_list:
		leave_type = None

		if status == "On Leave" and leave_type:
			leave_type = leave_type

		attendance = frappe.get_doc(
			dict(
				doctype="Student Attendance",
				student=student,
				date=getdate(date),
				status=status,
				leave_type=leave_type,
				late_entry=late_entry,
				early_exit=early_exit,
			)
		)
		attendance.insert()
		attendance.submit()
