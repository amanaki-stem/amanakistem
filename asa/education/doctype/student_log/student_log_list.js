frappe.listview_settings['Student Log'] = {
	hide_name_column: true,

	add_fields: ["type"],
	has_indicator_for_draft: 1,
	 
	get_indicator: function(doc) {
		if (doc.type=="Academic") {
		 var indicator = [_(doc.type), frappe.utils.guess_colour(doc.type), "type,=," + doc.type];
            indicator[1] = {
                "Academic": "blue",
                "General": "grey",
				"Medical": "orange",
				"Achievement":"green"
            }[doc.type];
            return indicator;
		}
	}
};
