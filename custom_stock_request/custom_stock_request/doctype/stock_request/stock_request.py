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

	#Workflow State "Approved" should trigger new stock entry"	
	def on_update(self):
		if self.workflow_state == "Approved" and not self.material_request_created: #if workflow state is approved, then we call our create material request function below
			self.create_material_request()

	def material_request_created(self):
		return frappe.db.exists("Material Request Already exists!")

	def create_material_request(self):
		mr = frappe.new_doc("Material Request")
		mr.material_request_type = "Material Issue"
		mr.transaction_date = self.request_date or frappe.utils.nowdate()
		mr.stock_request = self.name

		for item in self.requested_items:
			mr.append("items", {
			 "item_code": item.item_code,
			 "qty": item.qty,
			 "schedule_date": self.request_date or frappe.utils.nowdate()
			 }
			)

		mr.insert(ignore_permissions=True)
		mr.submit()	
		
	#Workflow State "Delivered" should trigger new stock entry"	
	def on_update(self):
		if self.workflow_state == "Delivered": #if workflow state is Delivered, then we call our create stock entry function below
			self.create_stock_entry()


	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Issue"
		se.posting_date = self.request_date or frappe.utils.nowdate()
		se.from_warehouse = self.source_warehouse
		se.stock_request = self.name

		for item in self.requested_items:
			se.append("items", {
			 "item_code": item.item_code,
			 "qty": item.qty,
			 "source_warehouse": self.source_warehouse
			#  "schedule_date": self.request_date or frappe.utils.nowdate()
			 }
			)

		se.insert(ignore_permissions=True)
		se.submit()
		
		#Assignment for this is to create a stock entry when the document state is "Mark as delivered"


