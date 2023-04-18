# Copyright (c) 2015, Frappe Technologies and contributors

import frappe
from frappe import _


class OverlapError(frappe.ValidationError):
	pass


def validate_overlap_for(doc, doctype, fieldname, value=None):
	"""Checks overlap for specified field.

	:param fieldname: Checks Overlap for this field
	"""

	existing = get_overlap_for(doc, doctype, fieldname, value)
	if existing:
		frappe.throw(
			_("This {0} conflicts with {1} for {2} {3}").format(
				doc.doctype,
				existing.name,
				doc.meta.get_label(fieldname) if not value else fieldname,
				value or doc.get(fieldname),
			),
			OverlapError,
		)


def get_overlap_for(doc, doctype, fieldname, value=None):
	"""Returns overlaping document for specified field.

	:param fieldname: Checks Overlap for this field
	"""

	existing = frappe.db.sql(
		"""select name, from_time, to_time from `tab{0}`
		where `{1}`=%(val)s and schedule_date = %(schedule_date)s and
		(
			(from_time > %(from_time)s and from_time < %(to_time)s) or
			(to_time > %(from_time)s and to_time < %(to_time)s) or
			(%(from_time)s > from_time and %(from_time)s < to_time) or
			(%(from_time)s = from_time and %(to_time)s = to_time))
		and name!=%(name)s and docstatus!=2""".format(
			doctype, fieldname
		),
		{
			"schedule_date": doc.schedule_date,
			"val": value or doc.get(fieldname),
			"from_time": doc.from_time,
			"to_time": doc.to_time,
			"name": doc.name or "No Name",
		},
		as_dict=True,
	)

	return existing[0] if existing else None


def validate_duplicate_student(students):
	unique_students = []
	for stud in students:
		if stud.student in unique_students:
			frappe.throw(
				_("Student {0} - {1} appears Multiple times in row {2} & {3}").format(
					stud.student, stud.student_name, unique_students.index(stud.student) + 1, stud.idx
				)
			)
		else:
			unique_students.append(stud.student)

	return None


# LMS Utils
def get_current_student():
	"""Returns current student from frappe.session.user

	Returns:
	        object: Student Document
	"""
	email = frappe.session.user
	if email in ("Administrator", "Guest"):
		return None
	try:
		student_id = frappe.get_all("Student", {"student_email_id": email}, ["name"])[0].name
		return frappe.get_doc("Student", student_id)
	except (IndexError, frappe.DoesNotExistError):
		return None


def get_time_in_timedelta(time):
	"""
	Converts datetime.time(10, 36, 55, 961454) to datetime.timedelta(seconds=38215)
	"""
	return timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)


def set_first_response_time(communication, method):
	if communication.get("reference_doctype") == "Issue":
		issue = get_parent_doc(communication)
		if is_first_response(issue) and issue.service_level_agreement:
			first_response_time = calculate_first_response_time(
				issue, get_datetime(issue.first_responded_on)
			)
			issue.db_set("first_response_time", first_response_time)


def is_first_response(issue):
	responses = frappe.get_all(
		"Communication", filters={"reference_name": issue.name, "sent_or_received": "Sent"}
	)
	if len(responses) == 1:
		return True
	return False


def calculate_first_response_time(issue, first_responded_on):
	issue_creation_date = issue.service_level_agreement_creation or issue.creation
	issue_creation_time = get_time_in_seconds(issue_creation_date)
	first_responded_on_in_seconds = get_time_in_seconds(first_responded_on)
	support_hours = frappe.get_cached_doc(
		"Service Level Agreement", issue.service_level_agreement
	).support_and_resolution

	if issue_creation_date.day == first_responded_on.day:
		if is_work_day(issue_creation_date, support_hours):
			start_time, end_time = get_working_hours(issue_creation_date, support_hours)

			# issue creation and response on the same day during working hours
			if is_during_working_hours(issue_creation_date, support_hours) and is_during_working_hours(
				first_responded_on, support_hours
			):
				return get_elapsed_time(issue_creation_date, first_responded_on)

			# issue creation is during working hours, but first response was after working hours
			elif is_during_working_hours(issue_creation_date, support_hours):
				return get_elapsed_time(issue_creation_time, end_time)

			# issue creation was before working hours but first response is during working hours
			elif is_during_working_hours(first_responded_on, support_hours):
				return get_elapsed_time(start_time, first_responded_on_in_seconds)

			# both issue creation and first response were after working hours
			else:
				return 1.0  # this should ideally be zero, but it gets reset when the next response is sent if the value is zero

		else:
			return 1.0

	else:
		# response on the next day
		if date_diff(first_responded_on, issue_creation_date) == 1:
			first_response_time = 0
		else:
			first_response_time = calculate_initial_frt(
				issue_creation_date, date_diff(first_responded_on, issue_creation_date) - 1, support_hours
			)

		# time taken on day of issue creation
		if is_work_day(issue_creation_date, support_hours):
			start_time, end_time = get_working_hours(issue_creation_date, support_hours)

			if is_during_working_hours(issue_creation_date, support_hours):
				first_response_time += get_elapsed_time(issue_creation_time, end_time)
			elif is_before_working_hours(issue_creation_date, support_hours):
				first_response_time += get_elapsed_time(start_time, end_time)

		# time taken on day of first response
		if is_work_day(first_responded_on, support_hours):
			start_time, end_time = get_working_hours(first_responded_on, support_hours)

			if is_during_working_hours(first_responded_on, support_hours):
				first_response_time += get_elapsed_time(start_time, first_responded_on_in_seconds)
			elif not is_before_working_hours(first_responded_on, support_hours):
				first_response_time += get_elapsed_time(start_time, end_time)

		if first_response_time:
			return first_response_time
		else:
			return 1.0


def get_time_in_seconds(date):
	return timedelta(hours=date.hour, minutes=date.minute, seconds=date.second)


def get_working_hours(date, support_hours):
	if is_work_day(date, support_hours):
		weekday = frappe.utils.get_weekday(date)
		for day in support_hours:
			if day.workday == weekday:
				return day.start_time, day.end_time


def is_work_day(date, support_hours):
	weekday = frappe.utils.get_weekday(date)
	for day in support_hours:
		if day.workday == weekday:
			return True
	return False


def is_during_working_hours(date, support_hours):
	start_time, end_time = get_working_hours(date, support_hours)
	time = get_time_in_seconds(date)
	if time >= start_time and time <= end_time:
		return True
	return False


def get_elapsed_time(start_time, end_time):
	return round(time_diff_in_seconds(end_time, start_time), 2)


def calculate_initial_frt(issue_creation_date, days_in_between, support_hours):
	initial_frt = 0
	for i in range(days_in_between):
		date = issue_creation_date + timedelta(days=(i + 1))
		if is_work_day(date, support_hours):
			start_time, end_time = get_working_hours(date, support_hours)
			initial_frt += get_elapsed_time(start_time, end_time)

	return initial_frt


def is_before_working_hours(date, support_hours):
	start_time, end_time = get_working_hours(date, support_hours)
	time = get_time_in_seconds(date)
	if time < start_time:
		return True
	return False


def get_holidays(holiday_list_name):
	holiday_list = frappe.get_cached_doc("Holiday List", holiday_list_name)
	holidays = [holiday.holiday_date for holiday in holiday_list.holidays]
	return holidays