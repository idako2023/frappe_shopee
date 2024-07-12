import frappe
from shopee.controllers.authorization import generate_auth_link
from shopee.controllers.authorization import shopee_auth_callback

@frappe.whitelist(allow_guest=True)
def get_authorization_link():
    return generate_auth_link()


@frappe.whitelist(allow_guest=True)
def handle_auth_callback(auth_code, account_id):
    """
    API endpoint to handle the OAuth callback from Shopee.
    """
    # 调用控制器中的 shopee_auth_callback 函数处理授权回调
    return shopee_auth_callback(auth_code, account_id)

@frappe.whitelist(allow_guest=True)
def get_company_hierarchy():
    # Fetch companies that are authorized
    companies = frappe.get_all('Company', filters={'is_authorized': 1}, fields=['name', 'parent_company', 'entity_name'])
    
    if not companies:
        return {"message": _("No authorized companies found."), "data": []}

    # Build a dictionary for easy lookup
    company_map = {company['name']: company for company in companies}

    # Create a hierarchical structure from the flat company list
    hierarchy = []
    for company in companies:
        if company['parent_company'] and company['parent_company'] in company_map:
            parent = company_map[company['parent_company']]
            if 'children' not in parent:
                parent['children'] = []
            parent['children'].append(company)
        elif not company['parent_company']:  # This is a top-level company
            hierarchy.append(company)

    # Optionally convert to a more friendly format or add more data manipulation here
    return hierarchy