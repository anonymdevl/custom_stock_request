# Copyright (c) 2025, Michael Appiah and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class StockRequest(Document):
	def validate(self):
		for item in self.requested_items:
			stock = frappe.db.get_value("Bin", {"item_code": item.item_code}, "actual_qty") or 0

			item.available_stock = stock

			if self.workflow_state == "Pending Approval" and item.qty > stock:
				frappe.throw(f"Insufficient stock for {item.item_name}. Requested Qty: {item.qty}. Available Qty: {stock}")

			#print(f"\n\n\n {stock} \n\n\n")
			
	def autoname(self):
		self.name = make_autoname("STR-.YYYY.-.MM.-.###")
