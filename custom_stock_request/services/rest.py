import frappe
import requests


def generate_qr_code(doc, method):
    base_url = frappe.utils.get_url()

    verify_url = f"{base_url}/verify?dn={doc.name}"

    qr_api = "https://api.qrserver.com/v1/create-qr-code/"

    response = requests.get(qr_api, params={"size": "150X150", "data": verify_url})

    doc.db_set("custom_qr_code_url", response.url)