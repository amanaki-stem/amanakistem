// Copyright (c) 2023, Senituli Taumoepeau and contributors
// For license information, please see license.txt



frappe.ui.form.on('Student', {
	refresh: function(frm) {
		frm.set_query("user", function (doc) {
			return {
				filters: {
					ignore_user_type: 1,
				},
			};
		});
		
		frm.add_custom_button(__('Attendance'), function (){
			frappe.route_options = {
                    "student": "frm.doc.name",
                }
			 frappe.set_route("Form", "Student Attendance", "new-student-attendence-1");
		});
				

	//	frappe.db.get_single_value('Education Settings', 'user_creation_skip', (r) => {
	//		if (cint(r.user_creation_skip) !== 1) {
	//			frm.set_df_property('student_email_id', 'reqd', 1);
	//		}
	//	});
	}
});

frappe.ui.form.on('Student Guardian', {
	guardians_add: function(frm){
		frm.fields_dict['guardians'].grid.get_field('guardian').get_query = function(doc){
			let guardian_list = [];
			if(!doc.__islocal) guardian_list.push(doc.guardian);
			$.each(doc.guardians, function(idx, val){
				if (val.guardian) guardian_list.push(val.guardian);
			});
			return { filters: [['Guardian', 'name', 'not in', guardian_list]] };
		};
	}
});

