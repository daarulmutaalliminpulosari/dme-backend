import frappe
import json
from frappe import _

def check_permission(doctype):
    if not frappe.has_permission(doctype):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

@frappe.whitelist(allow_guest=False)
def get_santri_list(page_length=20, start=0, search_term=""):
    check_permission("Santri")
    
    filters = {}
    if search_term:
        filters = [
            ["Santri", "nama_lengkap", "like", f"%{search_term}%"]
        ]
        
    santri_list = frappe.get_all(
        "Santri",
        filters=filters,
        fields=["name", "nis", "nisn", "nama_lengkap", "jenis_kelamin", "status_santri", "kelas_tingkatan"],
        limit_page_length=page_length,
        limit_start=start,
        order_by="creation desc"
    )
    
    total_count = frappe.db.count("Santri", filters=filters)
    
    return {
        "status": "success",
        "data": santri_list,
        "meta": {
            "total_count": total_count,
            "page_length": page_length,
            "start": start
        }
    }

@frappe.whitelist(allow_guest=False)
def get_santri_detail(name):
    check_permission("Santri")
    
    if not frappe.db.exists("Santri", name):
        return {"status": "error", "message": "Santri not found"}
        
    doc = frappe.get_doc("Santri", name)
    
    # If the santri has a linked wali, we might want to return that too
    wali_data = None
    if doc.wali_santri:
        wali_doc = frappe.get_doc("Wali Santri", doc.wali_santri)
        wali_data = wali_doc.as_dict()
        
    return {
        "status": "success",
        "data": doc.as_dict(),
        "wali_data": wali_data
    }

@frappe.whitelist(allow_guest=False)
def create_santri(data):
    check_permission("Santri")
    
    if isinstance(data, str):
        data = json.loads(data)
        
    try:
        # Check if we need to create Wali Santri first
        wali_data = data.get("wali_data")
        wali_name = data.get("wali_santri")
        
        if wali_data and not wali_name:
            # Create Wali Santri
            check_permission("Wali Santri")
            wali_doc = frappe.get_doc({
                "doctype": "Wali Santri",
                **wali_data
            })
            wali_doc.insert()
            wali_name = wali_doc.name
            
        # Create Santri
        santri_doc = frappe.get_doc({
            "doctype": "Santri",
            "wali_santri": wali_name,
            **{k: v for k, v in data.items() if k != "wali_data"}
        })
        santri_doc.insert()
        
        return {
            "status": "success",
            "message": "Santri created successfully",
            "data": santri_doc.as_dict()
        }
    except Exception as e:
        frappe.log_error(title="API Create Santri Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist(allow_guest=False)
def update_santri(name, data):
    check_permission("Santri")
    
    if not frappe.db.exists("Santri", name):
        return {"status": "error", "message": "Santri not found"}
        
    if isinstance(data, str):
        data = json.loads(data)
        
    try:
        doc = frappe.get_doc("Santri", name)
        
        # Update Wali Santri if data provided
        wali_data = data.get("wali_data")
        if wali_data and doc.wali_santri:
            check_permission("Wali Santri")
            wali_doc = frappe.get_doc("Wali Santri", doc.wali_santri)
            wali_doc.update(wali_data)
            wali_doc.save()
            
        # Remove wali_data from data to update santri
        if "wali_data" in data:
            del data["wali_data"]
            
        doc.update(data)
        doc.save()
        
        return {
            "status": "success",
            "message": "Santri updated successfully",
            "data": doc.as_dict()
        }
    except Exception as e:
        frappe.log_error(title="API Update Santri Error")
        return {
            "status": "error",
            "message": str(e)
        }

@frappe.whitelist(allow_guest=False)
def delete_santri(name):
    check_permission("Santri")
    
    if not frappe.db.exists("Santri", name):
        return {"status": "error", "message": "Santri not found"}
        
    try:
        frappe.delete_doc("Santri", name)
        return {
            "status": "success",
            "message": "Santri deleted successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ==========================================
# Wali Santri Endpoints (Standalone if needed)
# ==========================================

@frappe.whitelist(allow_guest=False)
def get_wali_list(page_length=20, start=0, search_term=""):
    check_permission("Wali Santri")
    
    filters = {}
    if search_term:
        filters = [
            ["Wali Santri", "nama_ayah_kandung", "like", f"%{search_term}%"]
        ]
        
    wali_list = frappe.get_all(
        "Wali Santri",
        filters=filters,
        fields=["name", "nama_ayah_kandung", "no_hp_wali", "yang_membiayai"],
        limit_page_length=page_length,
        limit_start=start,
        order_by="creation desc"
    )
    
    return {
        "status": "success",
        "data": wali_list
    }
