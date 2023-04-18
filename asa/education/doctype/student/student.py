# Copyright (c) 2023, Senituli Taumoepeau and contributors
# For license information, please see license.txt


import frappe
from frappe import _
from frappe.desk.form.linked_with import get_linked_doctypes
from frappe.model.document import Document
from frappe.utils import getdate, today

#from education.education.utils import (check_content_completion,
#                                       check_quiz_completion)

class Student(Document):
	def validate(self):
		self.set_title()
		self.set_student_name()
#		self.validate_dates()
#		self.validate_user()

#		if self.student_applicant:
#			self.check_unique()
#			self.update_applicant_status()

	def set_title(self):
		self.title = " ".join(
			filter(None, [self.first_name, self.middle_name, self.last_name])
		)
	def set_student_name(self):
		self.student_name = " ".join(
			filter(None, [self.first_name, self.middle_name, self.last_name])
		)

	def validate_dates(self):
#		for sibling in self.siblings:
#			if sibling.date_of_birth and getdate(sibling.date_of_birth) > getdate():
#				frappe.throw(
#					_("Row {0}:Sibling Date of Birth cannot be greater than today.").format(
#						sibling.idx
#					)
#				)

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate():
			frappe.throw(_("Date of Birth cannot be greater than today."))

		if self.date_of_birth and getdate(self.date_of_birth) >= getdate(self.joining_date):
			frappe.throw(_("Date of Birth cannot be greater than Joining Date."))

		if (
			self.joining_date
			and self.date_of_leaving
			and getdate(self.joining_date) > getdate(self.date_of_leaving)
		):
			frappe.throw(_("Joining Date can not be greater than Leaving Date"))

	def validate_user(self):
		"""Create a website user for student creation if not already exists"""
		if not frappe.db.get_single_value(
			"Education Settings", "user_creation_skip"
		) and not frappe.db.exists("User", self.student_email_id):
			student_user = frappe.get_doc(
				{
					"doctype": "User",
					"first_name": self.first_name,
					"last_name": self.last_name,
					"email": self.student_email_id,
					"gender": self.gender,
					"send_welcome_email": 1,
					"user_type": "Website User",
				}
			)
			student_user.add_roles("Student")
			student_user.save(ignore_permissions=True)

			self.user = student_user.name


def get_timeline_data(doctype, name):
	"""Return timeline for attendance"""
	return dict(
		frappe.db.sql(
			"""select unix_timestamp(`date`), count(*)
		from `tabStudent Attendance` where
			student=%s
			and `date` > date_sub(curdate(), interval 1 year)
			and docstatus = 1 and status = 'Present'
			group by date""",
			name,
		)
	)