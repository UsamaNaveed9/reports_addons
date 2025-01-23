from frappe import _
import frappe, erpnext
from frappe.utils import flt, getdate, formatdate, cstr

def _accounts_receivable():
	from frappe import _,qb, scrub
	from frappe.utils import cint, cstr, flt, getdate, nowdate
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
			(i for i, days in enumerate(self.ranges) if cint(row.age) >= cint(days)), len(self.ranges)
		)
		
		row["range" + str(index + 1)] = row.outstanding


	def _get_currency_fields(self):
		return [
			"invoiced",
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
			"range8",
			"range9",
			"range10",
			"range11",
			"range12",
			"range13",
			"future_amount",
			"remaining_balance",
		]

	def _get_columns(self):
		self.columns = []
		self.add_column(_("Posting Date"), fieldname="posting_date", fieldtype="Date")
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
		if self.account_type == "Receivable":
			label = _("Receivable Account")
		elif self.account_type == "Payable":
			label = _("Payable Account")
		else:
			label = _("Party Account")

		self.add_column(
			label=label,
			fieldname="party_account",
			fieldtype="Link",
			options="Account",
			width=180,
		)

		if self.party_naming_by == "Naming Series":
			if self.account_type == "Payable":
				label = _("Supplier Name")
				fieldname = "supplier_name"
			else:
				label = _("Customer Name")
				fieldname = "customer_name"
			self.add_column(
				label=label,
				fieldname=fieldname,
				fieldtype="Data",
			)

		if self.account_type == "Receivable":
			self.add_column(
				_("Customer Contact"),
				fieldname="customer_primary_contact",
				fieldtype="Link",
				options="Contact",
			)

		self.add_column(label=_("Cost Center"), fieldname="cost_center", fieldtype="Data")
		self.add_column(label=_("Voucher Type"), fieldname="voucher_type", fieldtype="Data")
		self.add_column(
			label=_("Voucher No"),
			fieldname="voucher_no",
			fieldtype="Dynamic Link",
			options="voucher_type",
			width=180,
		)

		self.add_column(label=_("Due Date"), fieldname="due_date", fieldtype="Date")

		if self.account_type == "Payable":
			self.add_column(label=_("Bill No"), fieldname="bill_no", fieldtype="Data")
			self.add_column(label=_("Bill Date"), fieldname="bill_date", fieldtype="Date")

		if self.filters.based_on_payment_terms:
			self.add_column(label=_("Payment Term"), fieldname="payment_term", fieldtype="Data")
			self.add_column(label=_("Invoice Grand Total"), fieldname="invoice_grand_total")

		self.add_column(_("Invoiced Amount"), fieldname="invoiced")
		self.add_column(_("Paid Amount"), fieldname="paid")
		if self.account_type == "Receivable":
			self.add_column(_("Credit Note"), fieldname="credit_note")
		else:
			# note: fieldname is still `credit_note`
			self.add_column(_("Debit Note"), fieldname="credit_note")
		self.add_column(_("Outstanding Amount"), fieldname="outstanding")

		self.add_column(label=_("Age (Days)"), fieldname="age", fieldtype="Int", width=80)
		self.setup_ageing_columns()

		self.add_column(
			label=_("Currency"), fieldname="currency", fieldtype="Link", options="Currency", width=80
		)

		if self.filters.show_future_payments:
			self.add_column(label=_("Future Payment Ref"), fieldname="future_ref", fieldtype="Data")
			self.add_column(label=_("Future Payment Amount"), fieldname="future_amount")
			self.add_column(label=_("Remaining Balance"), fieldname="remaining_balance")

		if self.filters.account_type == "Receivable":
			self.add_column(label=_("Customer LPO"), fieldname="po_no", fieldtype="Data")

			# comma separated list of linked delivery notes
			if self.filters.show_delivery_notes:
				self.add_column(label=_("Delivery Notes"), fieldname="delivery_notes", fieldtype="Data")
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

		if self.filters.account_type == "Payable":
			self.add_column(
				label=_("Supplier Group"),
				fieldname="supplier_group",
				fieldtype="Link",
				options="Supplier Group",
			)

		if self.filters.show_remarks:
			self.add_column(label=_("Remarks"), fieldname="remarks", fieldtype="Text", width=200)

	def _setup_ageing_columns(self):
		# for charts
		self.ageing_column_labels = []
		ranges = [*self.ranges, "Below"]
		
		prev_range_value = ranges[0]
		for idx, curr_range_value in enumerate(ranges):
			if idx == 0:  # Special case for the first range
				label = f"Above-{curr_range_value}"
			else:
				label = f"{prev_range_value}-{curr_range_value}"
			
			self.add_column(label=label, fieldname="range" + str(idx + 1))
			self.ageing_column_labels.append(label)

			if curr_range_value:
				prev_range_value = cint(curr_range_value) - 1

	def _get_chart_data(self):
		precision = cint(frappe.db.get_default("float_precision")) or 2
		# Initialize lists to store range-wise sums
		range_sums = [0] * len(self.range_numbers)
		
		for row in self.data:
			row = frappe._dict(row)
			if not cint(row.bold):
				for i, range_num in enumerate(self.range_numbers):
					range_value = flt(row.get(f"range{range_num}", 0), precision)
					range_sums[i] += range_value

		# Create the chart data
		labels = self.ageing_column_labels
		values = range_sums

		self.chart = {
			"data": {
				"labels": labels,
				"datasets": [{"name": _("Payments"), "values": values}],
			},
			"type": "bar",
			"fieldtype": "Currency",
			"options": "currency",
		}


	ReceivablePayableReport.__init__ = __init__
	ReceivablePayableReport.get_ageing_data = _get_ageing_data
	ReceivablePayableReport.set_ageing = _set_ageing
	ReceivablePayableReport.get_currency_fields = _get_currency_fields
	ReceivablePayableReport.setup_ageing_columns = _setup_ageing_columns
	ReceivablePayableReport.get_columns = _get_columns
	ReceivablePayableReport.get_chart_data = _get_chart_data


def main():
	_accounts_receivable()