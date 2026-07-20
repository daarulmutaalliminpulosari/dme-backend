import frappe

def execute():
    # 3. Setup Struktur Modul Dasar
    modules = [
        "DMe Kesantrian",
        "DMe Akademik",
        "DMe Keuangan"
    ]
    
    for mod in modules:
        if not frappe.db.exists("Module Def", mod):
            frappe.get_doc({
                "doctype": "Module Def",
                "module_name": mod,
                "app_name": "dme",
                "custom": 0
            }).insert(ignore_permissions=True)
            print(f"Created Module: {mod}")

    # 4. Setup Role Akses Dasar
    roles = [
        "Super Admin",
        "Pengasuh",
        "Pengurus",
        "Wali Santri",
        "Santri",
        "Ustadz"
    ]
    
    for r in roles:
        if not frappe.db.exists("Role", r):
            frappe.get_doc({
                "doctype": "Role",
                "role_name": r,
                "desk_access": 1
            }).insert(ignore_permissions=True)
            print(f"Created Role: {r}")

    frappe.db.commit()
    print("Setup completed successfully.")
