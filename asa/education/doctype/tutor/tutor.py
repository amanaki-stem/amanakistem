# Copyright (c) 2023, Senituli Taumoepeau and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class Tutor(Document):
	def validate(self):
		self.set_title()

	def set_title(self):
		self.title = " ".join(
			filter(None, [self.first_name, self.middle_name, self.last_name])
		) 
