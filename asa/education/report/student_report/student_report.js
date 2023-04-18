// Copyright (c) 2023, Senituli Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Report"] = {
	"filters": [
		{
			"fieldname":"academic_term",
			"label":__("Academic Term"),
			"fieldtype":"Link",
			"options": "Academic Term",
			"width": "90px",
			"reqd": 1
		},,
		{
			"fieldname":"academic_year",
			"label":__("Academic Year"),
			"fieldtype":"Link",
			"options": "Academic Year",
			"width": "90px",
			"reqd": 1
		},
		{
			"fieldname": "student",
			"label": __("Student ID"),
			"fieldtype": "Link",
			"options": "Student",
			"reqd": 1,
			on_change: () => {
				var student = frappe.query_report.get_filter_value('student');			
				var academic_term = frappe.query_report.get_filter_value('academic_term');
				var academic_year = frappe.query_report.get_filter_value('academic_year');

				if (student) {
					frappe.db.get_value('Student', student, ["title"], function(value) {
					frappe.query_report.set_filter_value('title', value["title"].toUpperCase());
					});
				}
			}
		},
		{
			"fieldname": "title",
			"label": __("Student Name"),
			"fieldtype": "Data",
			"hidden": 1
		},

	]
};
