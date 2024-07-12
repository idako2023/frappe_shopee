import frappe

def after_install():
    create_shopee_token_management_doctype()

def create_shopee_token_management_doctype():
    # Check if the Doctype already exists
    if not frappe.db.exists('DocType', 'Shopee Token Management'):
        # Create new Doctype
        doctype = frappe.get_doc({
            'doctype': 'DocType',
            'name': 'Shopee Token Management',
            'module': 'shopee',  # Change to your app's module name
            'custom': 1,
            'is_submittable': 0,
            'fields': [
                {'label': 'Merchant ID', 'fieldname': 'merchant_id', 'fieldtype': 'Data'},
                {'label': 'Shop ID', 'fieldname': 'shop_id', 'fieldtype': 'Data'},
                {'label': 'Access Token', 'fieldname': 'access_token', 'fieldtype': 'Password'},
                {'label': 'Refresh Token', 'fieldname': 'refresh_token', 'fieldtype': 'Password'},
                {'label': 'Token Expiry', 'fieldname': 'token_expiry', 'fieldtype': 'Int'},
                {'label': 'Last Refreshed', 'fieldname': 'last_refreshed', 'fieldtype': 'Datetime'},
                {'label': 'Active', 'fieldname': 'active', 'fieldtype': 'Check'}
            ]
        })
        doctype.insert(ignore_permissions=True)
        print('Shopee Token Management Doctype Created')
