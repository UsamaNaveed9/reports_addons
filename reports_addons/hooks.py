app_name = "reports_addons"
app_title = "Accounting Reports Enhancement"
app_publisher = "Nextlogic"
app_description = "Accounting Reports Enhancement"
app_email = "usamanaveed9263@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/reports_addons/css/reports_addons.css"
# app_include_js = "/assets/reports_addons/js/reports_addons.js"

app_reports_js = {
	"Accounts Payable Summary": "public/js/accounts_payable_summary.js",
	"Accounts Payable": "public/js/accounts_payable.js"
}
# include js, css files in header of web template
# web_include_css = "/assets/reports_addons/css/reports_addons.css"
# web_include_js = "/assets/reports_addons/js/reports_addons.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "reports_addons/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "reports_addons/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "reports_addons.utils.jinja_methods",
#	"filters": "reports_addons.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "reports_addons.install.before_install"
# after_install = "reports_addons.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "reports_addons.uninstall.before_uninstall"
# after_uninstall = "reports_addons.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "reports_addons.utils.before_app_install"
# after_app_install = "reports_addons.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "reports_addons.utils.before_app_uninstall"
# after_app_uninstall = "reports_addons.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "reports_addons.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"reports_addons.tasks.all"
#	],
#	"daily": [
#		"reports_addons.tasks.daily"
#	],
#	"hourly": [
#		"reports_addons.tasks.hourly"
#	],
#	"weekly": [
#		"reports_addons.tasks.weekly"
#	],
#	"monthly": [
#		"reports_addons.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "reports_addons.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"frappe.desk.query_report.get_script": "reports_addons.whitelisted.get_script",
    "frappe.desk.query_report.run": "reports_addons.whitelisted.run",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "reports_addons.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["reports_addons.utils.before_request"]
# after_request = ["reports_addons.utils.after_request"]

# Job Events
# ----------
# before_job = ["reports_addons.utils.before_job"]
# after_job = ["reports_addons.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"reports_addons.auth.validate"
# ]
