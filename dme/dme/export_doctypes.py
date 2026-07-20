import frappe

def execute():
    santri = frappe.get_doc("DocType", "Santri")
    santri.export_doc()
    
    wali = frappe.get_doc("DocType", "Wali Santri")
    wali.export_doc()
    
    print("Exported DocType JSONs")
