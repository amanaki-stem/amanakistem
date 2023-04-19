frappe.listview_settings['Student'] = {
	add_fields: ["image", "status", "team", "student_group"],
	has_indicator_for_draft: 1,
	get_indicator: function(doc) {
        if (doc.status) {
            var indicator = [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
            indicator[1] = {
                "Active": "green",
                "Exit": "black",
                "Suspended": "orange",
            }[doc.status];
            return indicator;

        }
	
		if (doc.team) {
			var indicator = [__(doc.team), frappe.utils.guess_colour(doc.team), "team,=," + doc.team];
			indicator[2] = {
				"RED": "red",
                "YELLOW": "yellow",
                "BLUE": "lightblue",
                "GREEN": "green",
			}[doc.team];
			return indicator;
		}
}
}
