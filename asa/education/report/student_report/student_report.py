# Copyright (c) 2023, Senituli Taumoepeau and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from itertools import groupby
import json
import time
import math
import ast
import os.path
import sys
import datetime
import pandas as pd
import numpy as np
import functools

from openpyxl import load_workbook
from frappe import _, msgprint, utils
from datetime import datetime, timedelta
from frappe.utils import flt, getdate, datetime, comma_and
from collections import defaultdict
from werkzeug.wrappers import Response
import frappe


def execute(filters=None):
	if not filters: filters = {}
	columns, data = [], []

	termSQL = filters.get("academic_term")
	yearSQL = filters.get("academic_year")
	studentSQL = filters.get("student")
	studentsql = "tabAR.student = '{student}'".format(student=filters.student) if filters.student else "1 = 1"

	attendanceSQL = frappe.db.sql("""SELECT student, student_name, date, academic_term, status 
					FROM `tabStudent Attendance`
					WHERE student = %s
					AND YEAR(date) = %s
					AND academic_term = %s""", (studentSQL, yearSQL, termSQL), as_dict = 1)
	

	dataframe = pd.DataFrame.from_records(attendanceSQL)


	return columns, data
