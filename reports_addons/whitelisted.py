import frappe
from frappe import _, msgprint
import datetime
import calendar
from frappe.utils import cint, date_diff, flt, getdate, add_days, nowdate, cstr
import json
from six import string_types, iteritems
from erpnext.accounts.doctype.pricing_rule.pricing_rule import get_pricing_rule_for_item
from erpnext.accounts.utils import get_account_currency
from erpnext.controllers.accounts_controller import AccountsController, get_supplier_block_status
from erpnext.accounts.doctype.payment_entry.payment_entry import get_negative_outstanding_invoices, \
	get_orders_to_be_billed
from erpnext.setup.utils import get_exchange_rate
import erpnext
from erpnext.accounts.utils import get_held_invoices
import os

@frappe.whitelist()
@frappe.read_only()
def run(report_name, filters=None, user=None, ignore_prepared_report=False, custom_columns=None):
	from frappe.desk.query_report import get_report_doc, get_prepared_report_result, generate_report_result
	report = get_report_doc(report_name)
	if not user:
		user = frappe.session.user
	if not frappe.has_permission(report.ref_doctype, "report"):
		frappe.msgprint(_("Must have report permission to access this report."),
						raise_exception=True)

	result = None

	# custom code for overriding native reports
	try:
		from reports_addons.override_reports import reports
		reports.main(report_name)
	except:
		pass

	if report.prepared_report and not report.disable_prepared_report and not ignore_prepared_report and not custom_columns:
		if filters:
			if isinstance(filters, string_types):
				filters = json.loads(filters)

			dn = filters.get("prepared_report_name")
			filters.pop("prepared_report_name", None)
		else:
			dn = ""
		result = get_prepared_report_result(report, filters, dn, user)
	else:
		result = generate_report_result(report, filters, user, custom_columns)

	result["add_total_row"] = report.add_total_row and not result.get('skip_total_row', False)

	return result


@frappe.whitelist()
def get_script(report_name):
	from frappe.desk.query_report import get_report_doc
	from frappe.modules import scrub, get_module_path
	from frappe.utils import get_html_format
	from frappe.model.utils import render_include
	from frappe.translate import send_translations

	report = get_report_doc(report_name)
	module = report.module or frappe.db.get_value("DocType", report.ref_doctype, "module")
	module_path = get_module_path(module)
	report_folder = os.path.join(module_path, "report", scrub(report.name))
	script_path = os.path.join(report_folder, scrub(report.name) + ".js")
	print_path = os.path.join(report_folder, scrub(report.name) + ".html")

	script = None
	# Customized code to override js of reports
	reports_script = frappe.get_hooks().get('app_reports_js', {})
	if reports_script and reports_script.get(report_name):
		script_path = frappe.get_app_path("reports_addons", reports_script.get(report_name)[0])

	# Customized code to override default print format of reports
	# reports_print = frappe.get_hooks().get('app_reports_html', {})
	# if reports_print and reports_print.get(report_name):
	#     print_path = frappe.get_app_path("jawaerp", reports_print.get(report_name)[0])

	if os.path.exists(script_path):
		with open(script_path, "r") as f:
			script = f.read()

	html_format = get_html_format(print_path)

	if not script and report.javascript:
		script = report.javascript

	if not script:
		script = "frappe.query_reports['%s']={}" % report_name

	# load translations
	if frappe.lang != "en":
		send_translations(frappe.get_lang_dict("report", report_name))

	return {
		"script": render_include(script),
		"html_format": html_format,
		"execution_time": frappe.cache().hget('report_execution_time', report_name) or 0
	}