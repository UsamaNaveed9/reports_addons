from frappe import _
import frappe, erpnext
from frappe.utils import flt, getdate, formatdate, cstr, today, now_datetime, nowdate
from dateutil.relativedelta import relativedelta

def _accounts_receivable_summary():
	# import erpnext.accounts.report.item_wise_purchase_register.item_wise_purchase_register as original
	from erpnext.accounts.report.accounts_receivable_summary.accounts_receivable_summary import AccountsReceivableSummary
	from frappe import _,qb, scrub
	from frappe.utils import flt, cint
	from erpnext.accounts.party import get_partywise_advanced_payment_amount
	from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport
	from six import iteritems

	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.qb_selection_filter = []
		self.ple = qb.DocType("Payment Ledger Entry")
		self.filters.report_date = getdate(self.filters.report_date or nowdate())
		self.age_as_on = (
			getdate(nowdate()) if self.filters.report_date > getdate(nowdate()) else self.filters.report_date
		)

		if not self.filters.range:
			self.filters.range = "30, 60, 90, 120"
		self.ranges = [num.strip() for num in self.filters.range.split(",") if num.strip()]
		self.range_numbers = [num for num in range(1, len(self.ranges) + 2)]

	def _get_columns(self):
		self.columns = []
		self.add_column(
			label=_("Party Type"),
			fieldname="party_type",
			fieldtype="Data",
			width=100,
		)
		self.add_column(
			label=_("Party"),
			fieldname="party",
			fieldtype="Dynamic Link",
			options="party_type",
			width=180,
		)

		if self.party_naming_by == "Naming Series":
			self.add_column(
				label=_("Supplier Name") if self.account_type == "Payable" else _("Customer Name"),
				fieldname="party_name",
				fieldtype="Data",
			)

		credit_debit_label = "Credit Note" if self.account_type == "Receivable" else "Debit Note"

		self.add_column(_("Advance Amount"), fieldname="advance")
		self.add_column(_("Invoiced Amount"), fieldname="invoiced")
		self.add_column(_("Paid Amount"), fieldname="paid")
		self.add_column(_(credit_debit_label), fieldname="credit_note")
		self.add_column(_("Outstanding Amount"), fieldname="outstanding")

		if self.filters.show_gl_balance:
			self.add_column(_("GL Balance"), fieldname="gl_balance")
			self.add_column(_("Difference"), fieldname="diff")

		self.setup_ageing_columns()
		self.add_column(label="Total Amount Due", fieldname="total_due")

		if self.filters.show_future_payments:
			self.add_column(label=_("Future Payment Amount"), fieldname="future_amount")
			self.add_column(label=_("Remaining Balance"), fieldname="remaining_balance")

		if self.account_type == "Receivable":
			self.add_column(
				label=_("Territory"), fieldname="territory", fieldtype="Link", options="Territory"
			)
			self.add_column(
				label=_("Customer Group"),
				fieldname="customer_group",
				fieldtype="Link",
				options="Customer Group",
			)
			if self.filters.show_sales_person:
				self.add_column(label=_("Sales Person"), fieldname="sales_person", fieldtype="Data")

			if self.filters.sales_partner:
				self.add_column(label=_("Sales Partner"), fieldname="default_sales_partner", fieldtype="Data")

		else:
			self.add_column(
				label=_("Supplier Group"),
				fieldname="supplier_group",
				fieldtype="Link",
				options="Supplier Group",
			)

		self.add_column(
			label=_("Currency"), fieldname="currency", fieldtype="Link", options="Currency", width=80
		)

	
	def _setup_ageing_columns(self):
		# for charts
		self.ageing_column_labels = []
		ranges = [*self.ranges, "Above"]
		
		prev_range_value = ranges[0]
		for idx, curr_range_value in enumerate(ranges):
			if idx == 0:  # Special case for the first range
				label = f"Below-{curr_range_value}"
			else:
				label = f"{prev_range_value}-{curr_range_value}"
			
			self.add_column(label=label, fieldname="range" + str(idx + 1))
			self.ageing_column_labels.append(label)

			if curr_range_value:
				prev_range_value = cint(curr_range_value) + 1

	def _set_ageing(self, row):
		if self.filters.ageing_based_on == "Due Date":
			# use posting date as a fallback for advances posted via journal and payment entry
			# when ageing viewed by due date
			entry_date = row.due_date or row.posting_date
		elif self.filters.ageing_based_on == "Supplier Invoice Date":
			entry_date = row.bill_date
		else:
			entry_date = row.posting_date

		self.get_ageing_data(entry_date, row)
		
		# ageing buckets should not have amounts if due date is not reached
		# if getdate(entry_date) > getdate(self.filters.report_date):
		# 	[setattr(row, f"range{i}", 0.0) for i in self.range_numbers]

		row.total_due = sum(row[f"range{i}"] for i in self.range_numbers)


	def _get_ageing_data(self, entry_date, row):
		# [-365--365,-364--270,-269--180,-179--120,-119--90,-89--60,-59--30,-29-0,1-30, 30-60, 60-90, 90-120, 120-above]
		[setattr(row, f"range{i}", 0.0) for i in self.range_numbers]

		if not (self.age_as_on and entry_date):
			return

		row.age = (getdate(self.age_as_on) - getdate(entry_date)).days or 0
		
		index = next(
			(i for i, days in enumerate(self.ranges) if cint(row.age) <= cint(days)), len(self.ranges)
		)
		
		row["range" + str(index + 1)] = row.outstanding


	def _get_currency_fields(self):
		return [
			"invoiced",
			"advance",
			"paid",
			"credit_note",
			"outstanding",
			"range1",
			"range2",
			"range3",
			"range4",
			"range5",
			"range6",
			"range7",
			"range9",
			"range10",
			"range11",
			"range12",
			"range13",
			"future_amount",
			"remaining_balance",
			"management_fee"
		]

	AccountsReceivableSummary.get_columns = _get_columns
	AccountsReceivableSummary.setup_ageing_columns = _setup_ageing_columns
	ReceivablePayableReport.set_ageing = _set_ageing
	ReceivablePayableReport.get_ageing_data = _get_ageing_data
	ReceivablePayableReport.get_currency_fields = _get_currency_fields
	#ReceivablePayableReport.__init__ = __init__


def main():
	_accounts_receivable_summary()