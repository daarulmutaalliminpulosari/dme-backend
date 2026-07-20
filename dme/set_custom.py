import frappe
def execute():
    frappe.db.set_value("DocType", "Wali Santri", "custom", 1)
    frappe.db.set_value("DocType", "Santri", "custom", 1)
    frappe.db.commit()
    print("Doctypes updated to custom=1")
