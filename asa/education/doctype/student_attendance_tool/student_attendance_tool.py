# Copyright (c) 2023, Senituli Taumoepeau and contributors
# For license information, please see license.txt

import datetime
import json

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class StudentAttendanceTool(Document):
	pass


@frappe.whitelist()
def get_students(
	date: str | datetime.date, academic_year: str | datetime.date, academic_term: str | datetime.date, academy: str = None
) -> dict[str, list]:
	filters = {"status": "Active", "date_of_joining": ["<=", date]}

	for field, value in {"academic_year": academic_year, "academic_term": academic_term, "academy": academy}.items():
		if value:
			filters[field] = value

	student_list = frappe.get_list(
		"Student", fields=["student", "student_name"], filters=filters, order_by="student_name"
	)
	attendance_list = frappe.get_list(
		"Student Attendance",
		fields=["student", "student_name", "status"],
		filters={
			"date": date,
			"docstatus": 1,
		},
		order_by="student_name",
	)

	unmarked_attendance = _get_unmarked_attendance(student_list, attendance_list)

	return {"marked": attendance_list, "unmarked": unmarked_attendance}


def _get_unmarked_attendance(student_list: list[dict], attendance_list: list[dict]) -> list[dict]:
	marked_students = [entry.student for entry in attendance_list]
	unmarked_attendance = []

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
	academy: str = None,
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
				shift=shift,
			)
		)
		attendance.insert()
		attendance.submit()
