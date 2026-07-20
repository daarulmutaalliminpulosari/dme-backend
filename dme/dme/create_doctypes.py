import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def create_wali_santri():
    if frappe.db.exists("DocType", "Wali Santri"):
        print("DocType Wali Santri already exists.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Wali Santri",
        "module": "DMe Kesantrian",
        "custom": 0,
        "is_submittable": 0,
        "autoname": "field:nama_wali",
        "fields": [
            {"fieldname": "data_wali_utama_sec", "fieldtype": "Section Break", "label": "Data Wali Utama"},
            {"fieldname": "nama_wali", "fieldtype": "Data", "label": "Nama Wali", "reqd": 1, "unique": 1},
            {"fieldname": "hubungan_wali", "fieldtype": "Select", "label": "Hubungan Wali", "reqd": 1, "options": "Ayah Kandung\nIbu Kandung\nKakek/Nenek\nPaman/Bibi\nSaudara Kandung\nLainnya"},
            {"fieldname": "no_hp_wali", "fieldtype": "Data", "label": "No HP Wali", "reqd": 1},
            {"fieldname": "alamat_email", "fieldtype": "Data", "label": "Alamat Email"},
            {"fieldname": "pekerjaan_wali", "fieldtype": "Data", "label": "Pekerjaan Wali"},
            
            {"fieldname": "data_orang_tua_kandung_sec", "fieldtype": "Section Break", "label": "Data Orang Tua Kandung"},
            {"fieldname": "nama_ayah_kandung", "fieldtype": "Data", "label": "Nama Ayah Kandung"},
            {"fieldname": "nama_ibu_kandung", "fieldtype": "Data", "label": "Nama Ibu Kandung"},
            
            {"fieldname": "sistem_akun_sec", "fieldtype": "Section Break", "label": "Sistem Akun"},
            {"fieldname": "user_akun", "fieldtype": "Link", "label": "User Akun", "options": "User"}
        ],
        "permissions": [
            {"role": "Super Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "Pengurus", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "Wali Santri", "read": 1, "write": 1}
        ]
    })
    doc.insert(ignore_permissions=True)
    print("Created DocType Wali Santri")

def create_santri():
    if frappe.db.exists("DocType", "Santri"):
        print("DocType Santri already exists.")
        return

    doc = frappe.get_doc({
        "doctype": "DocType",
        "name": "Santri",
        "module": "DMe Kesantrian",
        "custom": 0,
        "is_submittable": 0,
        "autoname": "naming_series:",
        "image_field": "foto",
        "fields": [
            {"fieldname": "naming_series", "fieldtype": "Select", "label": "Naming Series", "options": "SNT-.YYYY.-.####"},
            {"fieldname": "data_diri_sec", "fieldtype": "Section Break", "label": "Data Diri"},
            {"fieldname": "nama_lengkap", "fieldtype": "Data", "label": "Nama Lengkap", "reqd": 1, "in_list_view": 1},
            {"fieldname": "nis", "fieldtype": "Data", "label": "NIS", "unique": 1, "in_list_view": 1},
            {"fieldname": "nisn", "fieldtype": "Data", "label": "NISN"},
            {"fieldname": "nik", "fieldtype": "Data", "label": "NIK"},
            {"fieldname": "no_kk", "fieldtype": "Data", "label": "No KK"},
            
            {"fieldname": "cb1", "fieldtype": "Column Break"},
            {"fieldname": "foto", "fieldtype": "Attach Image", "label": "Foto"},
            {"fieldname": "tempat_lahir", "fieldtype": "Data", "label": "Tempat Lahir"},
            {"fieldname": "tanggal_lahir", "fieldtype": "Date", "label": "Tanggal Lahir"},
            {"fieldname": "jenis_kelamin", "fieldtype": "Select", "label": "Jenis Kelamin", "options": "Laki-laki\nPerempuan"},
            {"fieldname": "no_handphone_santri", "fieldtype": "Data", "label": "No Handphone Santri"},
            {"fieldname": "alamat_lengkap", "fieldtype": "Small Text", "label": "Alamat Lengkap"},
            
            {"fieldname": "status_akademik_sec", "fieldtype": "Section Break", "label": "Status Akademik & Asrama"},
            {"fieldname": "status_santri", "fieldtype": "Select", "label": "Status Santri", "options": "Aktif\nCuti\nKeluar\nLulus", "reqd": 1, "in_list_view": 1},
            {"fieldname": "tanggal_masuk", "fieldtype": "Date", "label": "Tanggal Masuk"},
            {"fieldname": "pendidikan_yang_diikuti", "fieldtype": "Link", "label": "Pendidikan Yang Diikuti", "options": "Program"},
            {"fieldname": "kelas", "fieldtype": "Link", "label": "Kelas", "options": "Student Group"},
            
            {"fieldname": "keluarga_sec", "fieldtype": "Section Break", "label": "Keluarga / Wali"},
            {"fieldname": "wali_santri", "fieldtype": "Link", "label": "Wali Santri", "options": "Wali Santri", "reqd": 1},
            
            {"fieldname": "lainnya_sec", "fieldtype": "Section Break", "label": "Lain-lain"},
            {"fieldname": "keterangan_tambahan", "fieldtype": "Text", "label": "Keterangan Tambahan"}
        ],
        "permissions": [
            {"role": "Super Admin", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "Pengurus", "read": 1, "write": 1, "create": 1, "delete": 1},
            {"role": "Wali Santri", "read": 1}
        ]
    })
    doc.insert(ignore_permissions=True)
    print("Created DocType Santri")

def execute():
    create_wali_santri()
    create_santri()
    frappe.db.commit()
    print("Doctype setup complete.")
