import frappe

@frappe.whitelist(allow_guest=True)
def ping():
    return {"status": "ok", "message": "DMe API is working"}
