// Copyright (c) 2023, Senituli Taumoepeau and contributors
// For license information, please see license.txt

frappe.ui.form.on('Student Attendance Tool', {
	refresh(frm) {
		frm.trigger("reset_attendance_fields")
		frm.trigger("load_students");
		frm.trigger("set_primary_action");
	},

	onload(frm) {
		frm.set_value("date", frappe.datetime.get_today());
	
	},

	date(frm) {
		frm.trigger("load_students");
	},

	academic_year(frm) {
		frm.trigger("load_students");
	},

	academic_term(frm) {
		frm.trigger("load_students");
	},

	student_group(frm) {
		frm.trigger("load_students");
	},

	status(frm) {
		frm.trigger("set_primary_action");
	},

	reset_attendance_fields(frm) {
		frm.set_value("status", "");
//		frm.set_value("shift", "");
		frm.set_value("late_entry", 0);
		frm.set_value("early_exit", 0);
	},

	load_students(frm) {
		if (!frm.doc.date)
			return;
		
		frappe.call({
			method: "asa.education.doctype.student_attendance_tool.student_attendance_tool.get_students",
			args: {
				date: frm.doc.date,
				student_group: frm.doc.student_group
			}
		}).then((r) => {
			
			frm.students = r.message["unmarked"];

			if (r.message["unmarked"].length > 0) {
				unhide_field("unmarked_attendance_section");
				unhide_field("attendance_details_section");
				frm.events.show_unmarked_students(frm, r.message["unmarked"]);
			} else {
				hide_field("unmarked_attendance_section");
				hide_field("attendance_details_section");
			}

			if (r.message["marked"].length > 0) {
				console.log(r.message)
				unhide_field("marked_attendance_html");
				frm.events.show_marked_students(frm, r.message["marked"]);
			} else {
				hide_field("marked_attendance_html");
			}
		});
	},

	show_unmarked_students(frm, unmarked_students) {
		const $wrapper = frm.get_field("students_html").$wrapper;
		$wrapper.empty();
		const student_wrapper = $(`<div class="student_wrapper">`).appendTo($wrapper);

		frm.students_multicheck = frappe.ui.form.make_control({
			parent: student_wrapper,
			df: {
				fieldname: "students_multicheck",
				fieldtype: "MultiCheck",
				select_all: true,
				columns: 4,
				get_data: () => {
					return unmarked_students.map((student) => {
						return {
							label: `${student.name} : ${student.student_name}`,
							value: student.name,
							checked: 0,
						};
					});
				},
			},
			render_input: true,
		});

		frm.students_multicheck.refresh_input();
	},

	show_marked_students(frm, marked_students) {
		const $wrapper = frm.get_field("marked_attendance_html").$wrapper;
		const summary_wrapper = $(`<div class="summary_wrapper">`).appendTo($wrapper);
		console.log(marked_students)
		const data = marked_students.map((entry) => {
			return [`${entry.student} : ${entry.student_name}`, entry.status];
		});
		
		frm.events.render_datatable(frm, data, summary_wrapper);
	},

	render_datatable(frm, data, summary_wrapper) {
		const columns = frm.events.get_columns_for_marked_attendance_table(frm);

		if (!frm.marked_stu_datatable) {
			const datatable_options = {
				columns: columns,
				data: data,
				dynamicRowHeight: true,
				inlineFilters: true,
				layout: "fixed",
				cellHeight: 35,
				noDataMessage: __("No Data"),
				disableReorderColumn: true,
			};
			frm.marked_stu_datatable = new frappe.DataTable(
				summary_wrapper.get(0),
				datatable_options,
			);
		} else {
			frm.marked_stu_datatable.refresh(data, columns);
		}
	},

	get_columns_for_marked_attendance_table(frm) {
		return [
			{
				name: "student_name",
				id: "student_name",
				content: `${__("Student")}`,
				editable: false,
				sortable: false,
				focusable: false,
				dropdown: false,
				align: "left",
				width: 350,
			},
			{
				name: "status",
				id: "status",
				content: `${__("Status")}`,
				editable: false,
				sortable: false,
				focusable: false,
				dropdown: false,
				align: "left",
				width: 150,
				format: (value) => {
					if (value == "Present")
						return `<span style="color:green">${__(value)}</span>`;
					else if (value == "Absent")
						return `<span style="color:red">${__(value)}</span>`;
					else if (value == "Half Day")
						return `<span style="color:orange">${__(value)}</span>`;
					else if (value == "Leave")
						return `<span style="color:#318AD8">${__(value)}</span>`;
				}
			},
		]
	},

	set_primary_action(frm) {
		frm.disable_save();
		frm.page.set_primary_action(__("Mark Attendance"), () => {
			if (frm.students.length === 0) {
				frappe.msgprint({
					message: __("Attendance for all the students under this criteria has been marked already."),
					title: __("Attendance Marked"),
					indicator: "green"
				});
				return;
			}

			if (frm.students_multicheck.get_checked_options().length === 0) {
				frappe.throw({
					message: __("Please select the students you want to mark attendance for."),
					title: __("Mandatory")
				});
			}

			if (!frm.doc.status) {
				frappe.throw({
					message: __("Please select the attendance status."),
					title: __("Mandatory")
				});
			}

			frm.trigger("mark_attendance");
		});
	},

	mark_attendance(frm) {
		const marked_students = frm.students_multicheck.get_checked_options();

		frappe.call({
			method: "asa.education.doctype.student_attendance_tool.student_attendance_tool.mark_student_attendance",
			args: {
				student_list: marked_students,
				status: frm.doc.status,
				date: frm.doc.date,
				late_entry: frm.doc.late_entry,
				early_exit: frm.doc.early_exit,

			},
			freeze: true,
			freeze_message: __("Marking Attendance")
		}).then((r) => {
			if (!r.exc) {
				frappe.show_alert({ message: __("Attendance marked successfully"), indicator: "green" });
				frm.refresh();
			}
		});
	},
});
