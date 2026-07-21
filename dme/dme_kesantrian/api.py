import frappe
from frappe import _
import json

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────

def _check_guardian_access(student_name):
    """Ensure current user (Guardian/Wali) can only access their own child."""
    user = frappe.session.user
    if user == "Administrator" or frappe.has_role("Super Admin") or frappe.has_role("Pengurus"):
        return True

    # Find guardian linked to this user
    guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
    if not guardian:
        frappe.throw(_("Akses ditolak: Akun Anda tidak terhubung ke data Wali Santri."), frappe.PermissionError)

    # Check if student is linked to this guardian
    linked = frappe.db.exists("Student Guardian", {
        "parent": student_name,
        "guardian": guardian
    })
    if not linked:
        frappe.throw(_("Akses ditolak: Anda tidak memiliki izin untuk mengakses data santri ini."), frappe.PermissionError)

    return True


# ─────────────────────────────────────────────
# STUDENT (SANTRI) ENDPOINTS
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_santri_list(page_length=20, start=0, search_term=None, status_santri=None):
    """
    GET list of Students (Santri).
    Guardians will only see their own children.
    Staff can see all.
    """
    filters = {}
    user = frappe.session.user

    # Row-level security for Guardian role
    if frappe.has_role("Wali Santri") and not (frappe.has_role("Super Admin") or frappe.has_role("Pengurus")):
        guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
        if not guardian:
            return {"status": "success", "data": [], "meta": {"total_count": 0}}
        # Get list of student names linked to this guardian
        linked_students = frappe.db.get_all("Student Guardian", filters={"guardian": guardian}, fields=["parent"])
        student_names = [s.parent for s in linked_students]
        if not student_names:
            return {"status": "success", "data": [], "meta": {"total_count": 0}}
        filters["name"] = ["in", student_names]

    if status_santri:
        filters["status_santri"] = status_santri

    or_filters = None
    if search_term:
        or_filters = [
            ["student_name", "like", f"%{search_term}%"],
            ["nis", "like", f"%{search_term}%"],
            ["nisn", "like", f"%{search_term}%"],
        ]

    fields = ["name", "student_name", "nis", "nisn", "gender", "status_santri", "joining_date", "image"]
    total = frappe.db.count("Student", filters=filters)

    data = frappe.get_all(
        "Student",
        fields=fields,
        filters=filters,
        or_filters=or_filters,
        limit_start=int(start),
        limit_page_length=int(page_length),
        order_by="student_name asc"
    )

    return {
        "status": "success",
        "data": data,
        "meta": {"total_count": total, "page_length": int(page_length), "start": int(start)}
    }


@frappe.whitelist()
def get_santri_detail(name):
    """GET full detail of one Student (Santri) with linked Guardian info."""
    _check_guardian_access(name)

    student = frappe.get_doc("Student", name)
    student_data = student.as_dict()

    # Get linked guardians
    guardians = frappe.db.get_all(
        "Student Guardian",
        filters={"parent": name},
        fields=["guardian", "guardian_name", "relation"]
    )
    guardian_details = []
    for g in guardians:
        if g.guardian:
            gd = frappe.get_doc("Guardian", g.guardian)
            guardian_details.append({
                "name": gd.name,
                "guardian_name": gd.guardian_name,
                "relation": g.relation,
                "hubungan_wali": gd.get("hubungan_wali"),
                "mobile_number": gd.mobile_number,
                "email_address": gd.email_address,
                "pekerjaan_wali": gd.get("pekerjaan_wali"),
                "nama_ayah_kandung": gd.get("nama_ayah_kandung"),
                "nama_ibu_kandung": gd.get("nama_ibu_kandung"),
            })

    return {
        "status": "success",
        "data": student_data,
        "guardians": guardian_details
    }


@frappe.whitelist(methods=["POST"])
def create_santri(data):
    """
    POST: Create new Student (Santri) with optional Guardian creation.
    data: JSON string or dict.
    """
    if frappe.has_role("Wali Santri") and not frappe.has_role("Pengurus"):
        frappe.throw(_("Anda tidak memiliki izin untuk menambah data santri."), frappe.PermissionError)

    if isinstance(data, str):
        data = json.loads(data)

    guardian_data = data.pop("wali_data", None)
    guardian_name_link = data.pop("guardian_name_link", None)  # existing Guardian name

    # Create Guardian if wali_data provided
    guardian_doc = None
    if guardian_data and not guardian_name_link:
        required_wali = ["guardian_name", "hubungan_wali", "mobile_number"]
        for f in required_wali:
            if not guardian_data.get(f):
                frappe.throw(_(f"Field wali '{f}' wajib diisi."))

        guardian_doc = frappe.get_doc({
            "doctype": "Guardian",
            **guardian_data
        })
        guardian_doc.insert(ignore_permissions=True)
        guardian_name_link = guardian_doc.name

    # Map field names
    first_name = data.get("nama_lengkap", "").split(" ", 1)
    student_doc_data = {
        "doctype": "Student",
        "first_name": first_name[0],
        "last_name": first_name[1] if len(first_name) > 1 else "",
        "gender": "Male" if data.get("jenis_kelamin") == "Laki-laki" else "Female",
        "date_of_birth": data.get("tanggal_lahir"),
        "joining_date": data.get("tanggal_masuk"),
        "student_email_id": data.get("email"),
        "nis": data.get("nis"),
        "nisn": data.get("nisn"),
        "nik": data.get("nik"),
        "no_kk": data.get("no_kk"),
        "status_santri": data.get("status_santri", "Aktif"),
        "no_hp_santri": data.get("no_hp_santri"),
        "alamat_lengkap": data.get("alamat_lengkap"),
    }

    # Link guardian via child table
    if guardian_name_link:
        student_doc_data["guardians"] = [{
            "guardian": guardian_name_link,
            "relation": guardian_data.get("hubungan_wali", "Lainnya") if guardian_data else "Lainnya"
        }]

    student = frappe.get_doc(student_doc_data)
    student.insert(ignore_permissions=True)

    frappe.db.commit()
    return {
        "status": "success",
        "message": "Santri berhasil dibuat.",
        "data": {"student_id": student.name, "guardian_id": guardian_name_link}
    }


@frappe.whitelist(methods=["POST"])
def update_santri(name, data):
    """PUT: Update Student (Santri) data."""
    _check_guardian_access(name)

    if isinstance(data, str):
        data = json.loads(data)

    student = frappe.get_doc("Student", name)
    guardian_data = data.pop("wali_data", None)

    # Update student fields
    field_map = {
        "nama_lengkap": None,  # handled specially below
        "jenis_kelamin": "gender",
        "tanggal_lahir": "date_of_birth",
        "tanggal_masuk": "joining_date",
        "email": "student_email_id",
        "nis": "nis",
        "nisn": "nisn",
        "nik": "nik",
        "no_kk": "no_kk",
        "status_santri": "status_santri",
        "no_hp_santri": "no_hp_santri",
        "alamat_lengkap": "alamat_lengkap",
    }

    if "nama_lengkap" in data:
        parts = data["nama_lengkap"].split(" ", 1)
        student.first_name = parts[0]
        student.last_name = parts[1] if len(parts) > 1 else ""

    for src, dst in field_map.items():
        if dst and src in data:
            if src == "jenis_kelamin":
                setattr(student, dst, "Male" if data[src] == "Laki-laki" else "Female")
            else:
                setattr(student, dst, data[src])

    student.save(ignore_permissions=True)

    # Update Guardian if wali_data provided
    if guardian_data:
        # Find first linked guardian
        linked = frappe.db.get_all("Student Guardian", filters={"parent": name}, fields=["guardian"])
        if linked:
            guardian = frappe.get_doc("Guardian", linked[0].guardian)
            for k, v in guardian_data.items():
                if hasattr(guardian, k):
                    setattr(guardian, k, v)
                else:
                    guardian.set(k, v)
            guardian.save(ignore_permissions=True)

    frappe.db.commit()
    return {"status": "success", "message": "Data santri berhasil diperbarui."}


@frappe.whitelist(methods=["POST"])
def delete_santri(name):
    """DELETE: Remove Student record."""
    if not (frappe.has_role("Super Admin") or frappe.has_role("Pengurus")):
        frappe.throw(_("Anda tidak memiliki izin untuk menghapus data santri."), frappe.PermissionError)

    frappe.delete_doc("Student", name, ignore_permissions=True)
    frappe.db.commit()
    return {"status": "success", "message": f"Santri {name} berhasil dihapus."}


# ─────────────────────────────────────────────
# GUARDIAN (WALI SANTRI) ENDPOINTS
# ─────────────────────────────────────────────

@frappe.whitelist()
def get_wali_list(page_length=20, start=0, search_term=None):
    """GET list of Guardians. Staff only."""
    filters = {}
    if search_term:
        filters["guardian_name"] = ["like", f"%{search_term}%"]

    total = frappe.db.count("Guardian", filters=filters)
    data = frappe.get_all(
        "Guardian",
        fields=["name", "guardian_name", "mobile_number", "email_address", "hubungan_wali", "pekerjaan_wali"],
        filters=filters,
        limit_start=int(start),
        limit_page_length=int(page_length),
        order_by="guardian_name asc"
    )
    return {
        "status": "success",
        "data": data,
        "meta": {"total_count": total, "page_length": int(page_length), "start": int(start)}
    }


@frappe.whitelist()
def get_anak_saya():
    """
    GET list of Student(s) linked to the current logged-in Guardian (Wali Santri).
    """
    user = frappe.session.user
    guardian = frappe.db.get_value("Guardian", {"user": user}, "name")
    if not guardian:
        return {"status": "success", "data": [], "message": "Akun ini tidak terhubung ke data Wali Santri."}

    linked = frappe.db.get_all("Student Guardian", filters={"guardian": guardian}, fields=["parent", "guardian_name", "relation"])
    result = []
    for l in linked:
        s = frappe.db.get_value("Student", l.parent,
            ["name", "student_name", "nis", "gender", "status_santri", "image"],
            as_dict=True)
        if s:
            s["relation"] = l.relation
            result.append(s)

    return {"status": "success", "data": result}


# ─────────────────────────────────────────────
# AUTH & PROFILE ENDPOINTS
# ─────────────────────────────────────────────

@frappe.whitelist(allow_guest=True, methods=["POST"])
def register_pendaftar(email, full_name, password, no_hp=None):
    """
    Register new account for PPDB applicant (Calon Wali Santri).
    Guest accessible.
    """
    if frappe.db.exists("User", email):
        frappe.throw(_("Email sudah terdaftar. Silakan login atau gunakan email lain."))

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": full_name,
        "mobile_no": no_hp or "",
        "send_welcome_email": 0,
        "roles": [{"role": "Calon Wali Santri"}]
    })
    user.new_password = password
    user.insert(ignore_permissions=True)
    frappe.db.commit()

    return {
        "status": "success",
        "message": "Akun berhasil dibuat. Silakan login untuk melanjutkan pendaftaran.",
        "data": {"email": email}
    }


@frappe.whitelist()
def get_profil_santri(student_name):
    """GET full profile of a Santri for mobile app."""
    _check_guardian_access(student_name)
    return get_santri_detail(student_name)


# ─────────────────────────────────────────────
# PPDB ENDPOINTS
# ─────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def get_ppdb_info():
    """GET current active PPDB period info."""
    active_admission = frappe.db.get_all("Student Admission", filters={"publish": 1}, fields=["name", "admission_title", "academic_year", "route", "introduction"], limit=1)
    if not active_admission:
        return {"status": "error", "message": "Tidak ada periode pendaftaran yang aktif saat ini."}
        
    return {"status": "success", "data": active_admission[0]}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_pendaftaran(data):
    """
    POST: Submit a new Student Applicant.
    Required fields: first_name, student_email_id, program
    Custom fields required: no_hp_wali, nama_wali_pendaftar
    """
    if isinstance(data, str):
        data = json.loads(data)
        
    if not frappe.db.exists("Student Admission", "PPDB 2025-2026"):
        frappe.throw("Periode PPDB belum dikonfigurasi. Hubungi Admin.")

    required = ["first_name", "student_email_id", "program", "no_hp_wali", "nama_wali_pendaftar"]
    for f in required:
        if not data.get(f):
            frappe.throw(f"Field '{f}' wajib diisi.")

    # Create Applicant
    applicant = frappe.get_doc({
        "doctype": "Student Applicant",
        "first_name": data.get("first_name"),
        "last_name": data.get("last_name"),
        "student_email_id": data.get("student_email_id"),
        "program": data.get("program"),
        "student_admission": "PPDB 2025-2026",
        "application_status": "Applied",
        "gender": "Male" if data.get("jenis_kelamin") == "Laki-laki" else "Female",
        "date_of_birth": data.get("tanggal_lahir"),
        # Custom Fields for PPDB
        "no_hp_wali": data.get("no_hp_wali"),
        "nama_wali_pendaftar": data.get("nama_wali_pendaftar"),
    })
    
    applicant.insert(ignore_permissions=True)
    frappe.db.commit()
    
    return {
        "status": "success", 
        "message": "Pendaftaran berhasil disubmit. Silakan pantau status pendaftaran Anda.",
        "data": {"applicant_id": applicant.name}
    }


@frappe.whitelist(allow_guest=True)
def cek_status_ppdb(applicant_id):
    """GET status of Student Applicant by ID."""
    if not frappe.db.exists("Student Applicant", applicant_id):
        return {"status": "error", "message": "ID Pendaftaran tidak ditemukan."}
        
    applicant = frappe.db.get_value("Student Applicant", applicant_id, 
        ["name", "first_name", "last_name", "application_status", "program"], as_dict=True)
        
    return {"status": "success", "data": applicant}

# ─────────────────────────────────────────────
# PING (Health Check)
# ─────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def ping():
    return {"status": "ok", "message": "DMe API is running.", "version": "2.0.0"}
