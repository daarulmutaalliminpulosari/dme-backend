import frappe

def execute():
    # Update Module Defs in DB to title case "Dme ..." instead of "DMe ..."
    modules = ["DMe Kesantrian", "DMe Akademik", "DMe Keuangan"]
    for mod in modules:
        if frappe.db.exists("Module Def", mod):
            new_name = mod.replace("DMe", "Dme")
            if not frappe.db.exists("Module Def", new_name):
                frappe.rename_doc("Module Def", mod, new_name, force=True)
            print(f"Renamed {mod} to {new_name}")
            
    # Also update doctypes module field
    doctypes = ["Wali Santri", "Santri"]
    for dt in doctypes:
        if frappe.db.exists("DocType", dt):
            frappe.db.set_value("DocType", dt, "module", "Dme Kesantrian")
            print(f"Updated module of {dt} to Dme Kesantrian")
            
    frappe.db.commit()
