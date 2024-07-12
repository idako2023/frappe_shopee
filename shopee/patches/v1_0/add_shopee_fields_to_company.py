import frappe

def execute():
    custom_fields = [
        # Fields for merchant (company level)
        {'fieldname': 'entity_name', 'label': 'Entity Name', 'fieldtype': 'Data', 'insert_after': 'country'},
        {'fieldname': 'entity_id', 'label': 'Entity ID', 'fieldtype': 'Data', 'insert_after': 'entity_name'},
        {'fieldname': 'status', 'label': 'Status', 'fieldtype': 'MultiSelect', 'options': 'Cross-Border\nCNSC\nKRSC\nUNUPGRADED\nSIP\nPure-FBS\nPure-3PF\nPFF-FBS\nPFF-3PF\nOthers\nUnknown', 'insert_after': 'entity_id'},
        {'fieldname': 'authorization_time', 'label': 'Authorization Time', 'fieldtype': 'Datetime', 'insert_after': 'status'},
        {'fieldname': 'authorization_expiry_time', 'label': 'Authorization Expiry Time', 'fieldtype': 'Datetime', 'insert_after': 'authorization_time'},
        {'fieldname': 'is_authorized', 'label': 'Is Authorized', 'fieldtype': 'Check', 'insert_after': 'authorization_expiry_time'},
    ]
    create_custom_fields(custom_fields)

def create_custom_fields(fields):
    for field in fields:
        if not frappe.db.exists('Custom Field', {'fieldname': field['fieldname'], 'dt': 'Company'}):
            new_field = frappe.get_doc({
                'doctype': 'Custom Field',
                'dt': 'Company',
                'fieldname': field['fieldname'],
                'fieldtype': field['fieldtype'],
                'label': field['label'],
                'insert_after': field['insert_after'],
                'options': field.get('options', ''),
                'in_list_view': 1,
                'no_copy': 1
            })
            new_field.insert()
            print(f"Added {field['label']} to Company")
        else:
            print(f"Field {field['label']} already exists in Company")