import frappe

def get_token_by_shop_or_merchant_id(shop_id=None, merchant_id=None):
    """
    Retrieve the access token for a given shop_id or merchant_id.
    """
    if shop_id:
        token_doc = frappe.get_all('Shopee Token Management', fields=['access_token'], filters={'shop_id': shop_id, 'active': 1})
    elif merchant_id:
        token_doc = frappe.get_all('Shopee Token Management', fields=['access_token'], filters={'merchant_id': merchant_id, 'active': 1})
    else:
        return None  # or raise an exception if required

    return token_doc[0]['access_token'] if token_doc else None
