# Copyright (c) 2015, Frappe Technologies and contributors
# For license information, please see license.txt


import json

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cstr, flt, getdate



@frappe.whitelist()
def check_attendance_records_exist(course_schedule=None, student_group=None, date=None):
	"""Check if Attendance Records are made against the specified Course Schedule or Student Group for given date.

	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
#	if course_schedule:
#		return frappe.get_list(
#			"Student Attendance", filters={"course_schedule": course_schedule}
#		)
#	else:
	return frappe.get_list(
		"Student Attendance", filters={"student_group": student_group, "date": date}
	)


@frappe.whitelist()
def mark_attendance(
	students_present, students_absent, student_group, academic_year, date=None
):
	"""Creates Multiple Attendance Records.

	:param students_present: Students Present JSON.
	:param students_absent: Students Absent JSON.
	:param course_schedule: Course Schedule.
	:param student_group: Student Group.
	:param date: Date.
	"""
	if student_group:
#		academic_year = frappe.db.get_value("Student", student_group, "academic_year")
#		if academic_year:
		year_start_date, year_end_date = frappe.db.get_value(
			"Academic Year", academic_year, ["year_start_date", "year_end_date"]
			)
		if getdate(date) < getdate(year_start_date) or getdate(date) > getdate(
			year_end_date
		):
			frappe.throw(
				_("Attendance cannot be marked outside of Academic Year {0}").format(academic_year)
			)

	present = json.loads(students_present)
	absent = json.loads(students_absent)

	for d in present:
		make_attendance_records(
			d["student"], d["student_name"], "Present", student_group, date
		)

	for d in absent:
		make_attendance_records(
			d["student"], d["student_name"], "Absent", student_group, date
		)

	frappe.db.commit()
	frappe.msgprint(_("Attendance has been marked successfully."))


def make_attendance_records(
	student, student_name, status, student_group=None, date=None
):
	"""Creates/Update Attendance Record.

	:param student: Student.
	:param student_name: Student Name.
	:param course_schedule: Course Schedule.
	:param status: Status (Present/Absent)
	"""
	student_attendance = frappe.get_doc(
		{
			"doctype": "Student Attendance",
			"student": student,
#			"course_schedule": course_schedule,
			"student_group": student_group,
			"date": date,
		}
	)
	#if not student_attendance:
	student_attendance = frappe.new_doc("Student Attendance")
	student_attendance.student = student
	student_attendance.student_name = student_name
#	student_attendance.course_schedule = course_schedule
	student_attendance.student_group = student_group
	student_attendance.date = date
	student_attendance.status = status
	student_attendance.save()
	student_attendance.submit()


@frappe.whitelist()
def get_student_guardians(student):
	"""Returns List of Guardians of a Student.

	:param student: Student.
	"""
	guardians = frappe.get_all(
		"Student Guardian", fields=["guardian"], filters={"parent": student}
	)
	return guardians


@frappe.whitelist()
def get_student_group_students(student_group, include_inactive=0):
	"""Returns List of student, student_name in Student Group.

	:param student_group: Student Group.
	"""
	if include_inactive:
		students = frappe.get_all(
			"Student",
			fields=["name", "student_name"],
			filters={"student_group": student_group},
			order_by="name",
		)
	else:
		students = frappe.get_all(
			"Student",
			fields=["name", "student_name"],
			filters={"student_group": student_group, "status": "active"},
			order_by="name",
		)
	return students

