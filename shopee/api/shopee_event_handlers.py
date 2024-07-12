import frappe

def handle_shop_authorization(data):
    # Logic for handling new shop authorization
    pass

def handle_shop_authorization_canceled(data):
    """
    Handle the cancellation of shop and merchant authorizations by updating the authorization
    status and expiry time in the Company DocType.
    """
    try:
        # Initialize lists to hold individual and multiple IDs
        shop_ids = data.get('shop_id_list', [])
        if 'shop_id' in data:
            shop_ids.append(data['shop_id'])  # Append individual shop ID if present

        merchant_ids = data.get('merchant_id_list', [])
        if 'merchant_id' in data:
            merchant_ids.append(data['merchant_id'])  # Append individual merchant ID if present

        # Current datetime for authorization expiry
        current_time = frappe.utils.now_datetime()

        # Process each shop ID
        for shop_id in shop_ids:
            update_company_authorization(shop_id, False, current_time)
            delete_associated_tokens(shop_id, 'shop_id') 

        # Process each merchant ID
        for merchant_id in merchant_ids:
            update_company_authorization(merchant_id, False, current_time)
            delete_associated_tokens(merchant_id, 'merchant_id')

        # Log successful processing
        frappe.log_error(f"Deauthorization processed for shops {shop_ids} and merchants {merchant_ids}.", "Shop Authorization Canceled")
        
    except Exception as e:
        frappe.log_error(f"Error processing shop authorization canceled webhook: {str(e)}", "Shop Authorization Canceled Error")

def update_company_authorization(identifier, is_authorized, expiry_time):
    """
    Update the authorization status and authorization expiry time of a company based on the identifier.
    """
    # Assuming identifier could be either shop_id or merchant_id
    filter_conditions = {"shop_id": identifier} if any(frappe.get_all("Company", filters={"shop_id": identifier})) \
        else {"merchant_id": identifier}
    
    # Get the name of the company using the identifier
    company_name = frappe.db.get_value("Company", filter_conditions, "name")
    
    if company_name:
        # Use db_set to update fields directly
        frappe.db.set_value("Company", company_name, "is_authorized", is_authorized)
        frappe.db.set_value("Company", company_name, "authorization_expiry_time", expiry_time)
        frappe.db.commit()

def delete_associated_tokens(identifier, identifier_type):
    """
    Delete all token records associated with the given identifier (shop_id or merchant_id).
    """
    # Delete tokens from the 'Token Management' DocType
    tokens = frappe.get_all("Token Management", filters={identifier_type: identifier}, fields=["name"])
    for token in tokens:
        frappe.delete_doc("Token Management", token['name'], force=1)  # force=1 to delete permanently
        frappe.db.commit()
        frappe.log_error(f"Deleted token for {identifier_type}: {identifier}", "Token Deletion Log")

def handle_order_status_update(data):
    # Logic for handling updates to order status
    pass

def handle_order_tracking_number_update(data):
    # Logic for handling updates to tracking numbers
    pass

def handle_shipping_document_status(data):
    # Logic for handling shipping document status updates
    pass

def handle_item_promotion(data):
    # Logic for handling item promotion updates
    pass

def handle_promotion_update(data):
    # Logic for handling promotion activity updates
    pass

def handle_reserved_stock_change(data):
    # Logic for handling reserved stock changes
    pass

def handle_video_upload(data):
    # Logic for handling video upload status
    pass

def handle_banned_item(data):
    # Logic for handling banned item notifications
    pass

def handle_brand_register_result(data):
    # Logic for handling brand registration results
    pass

def handle_webchat_update(data):
    # Logic for handling updates from chat
    pass

def handle_open_api_authorization_expiry(data):
    # Logic for handling API authorization expiry notifications
    pass

def handle_shopee_updates(data):
    # Logic for handling important Shopee updates
    pass

EVENT_HANDLER_MAP = {
    1: handle_shop_authorization,
    2: handle_shop_authorization_canceled,
    3: handle_order_status_update,
    4: handle_order_tracking_number_update,
    5: handle_shopee_updates,
    6: handle_banned_item,
    7: handle_item_promotion,
    8: handle_reserved_stock_change,
    9: handle_promotion_update,
    10: handle_webchat_update,
    11: handle_video_upload,
    12: handle_open_api_authorization_expiry,
    13: handle_brand_register_result,
    15: handle_shipping_document_status
}

def get_event_handler(event_code):
    """Retrieve the appropriate event handler function based on the event code."""
    return EVENT_HANDLER_MAP.get(event_code, default_handler)

def default_handler(data):
    """A default handler if no specific handler is found for an event code."""
    frappe.log_error(f"No specific handler found for data: {data}", "Shopee Webhook Error")