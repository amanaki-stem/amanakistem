// Copyright (c) 2023, Senituli Taumoepeau and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Student Monthly Attendance Report"] = {
	"filters": [{
		"fieldname": "month",
		"label": __("Month"),
		"fieldtype": "Select",
		"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
		"default": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
			"Dec"
		][frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth()],
	},
	{
		"fieldname": "year",
		"label": __("Year"),
		"fieldtype": "Select",
		"reqd": 1
	},
	{
		"fieldname": "student_group",
		"label": __("Student Group"),
		"fieldtype": "Select",
		"options": "Junior\nIntermidiate\nSenior",
		"reqd": 1
	}
	],

	"onload": function() {
		return frappe.call({
			method: "asa.education.report.student_monthly_attendance_report.student_monthly_attendance_report.get_attendance_years",
			callback: function(r) {
				var year_filter = frappe.query_report.get_filter('year');
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			}
		});
	}
}
