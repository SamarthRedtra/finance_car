app_name = "finance_car"
app_title = "Finance Car"
app_publisher = "Redtra Technologies FZE LLC"
app_description = "Finance Car Custom Module"
app_email = "info@redtra.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/finance_car/css/finance_car.css"
# app_include_js = "/assets/finance_car/js/finance_car.js"

# include js, css files in header of web template
# web_include_css = "/assets/finance_car/css/finance_car.css"
# web_include_js = "/assets/finance_car/js/finance_car.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "finance_car/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = { "Item" : "public/js/item.js", 
                "Sales Invoice":"public/js/sales_invoice.js",
                "Purchase Order":"public/js/purchase_order.js",
                "Journal Entry":"public/js/journal_entry.js",
                }
doctype_list_js = {"Purchase Order" : "public/js/purchase_order_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "finance_car/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "finance_car.utils.jinja_methods",
# 	"filters": "finance_car.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "finance_car.install.before_install"
# after_install = "finance_car.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "finance_car.uninstall.before_uninstall"
# after_uninstall = "finance_car.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "finance_car.utils.before_app_install"
# after_app_install = "finance_car.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "finance_car.utils.before_app_uninstall"
# after_app_uninstall = "finance_car.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "finance_car.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Purchase Order": "finance_car.overrides.purchase_order.CustomPurchaseOrder",
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"finance_car.tasks.all"
# 	],
# 	"daily": [
# 		"finance_car.tasks.daily"
# 	],
# 	"hourly": [
# 		"finance_car.tasks.hourly"
# 	],
# 	"weekly": [
# 		"finance_car.tasks.weekly"
# 	],
# 	"monthly": [
# 		"finance_car.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "finance_car.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "finance_car.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "finance_car.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["finance_car.utils.before_request"]
# after_request = ["finance_car.utils.after_request"]

# Job Events
# ----------
# before_job = ["finance_car.utils.before_job"]
# after_job = ["finance_car.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"finance_car.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures=[
    {"dt": "Custom HTML Block"}
]
