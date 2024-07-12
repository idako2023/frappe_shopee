import frappe
import requests
import time
from frappe import _
from .utils import generate_signature
from urllib.parse import urlencode
from datetime import datetime
from .shopee_integration import fetch_merchant_info, fetch_shop_info 
from shopee.config import SHOPEE_URL, get_partner_id, get_partner_key

# 常量配置
PARTNER_ID = get_partner_id()
PARTNER_KEY = get_partner_key()

def get_tokens(auth_code, main_account_id, is_merchant=False):
    """
    使用授权码获取access_token和refresh_token。
    """
    timestamp = int(time.time())
    path = "/api/v2/auth/token/get"
    
    # 使用外部模块生成签名
    signature = generate_signature(PARTNER_ID, path, timestamp, PARTNER_KEY)

    # 构建带有签名的完整URL
    url = f"{SHOPEE_URL}{path}?partner_id={PARTNER_ID}&timestamp={timestamp}&sign={signature}"
    
    # 构建JSON请求体
    body = {
        "code": auth_code,
        "main_account_id": main_account_id,  # 加入 main_account_id 参数
        "partner_id": PARTNER_ID
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=body, headers=headers)

    if response.ok:
        result = response.json()
        print(result)
        # 检查是否有错误信息
        if result.get('error'):
            error_msg = result.get('message', 'No additional error message provided.')
            if error_msg:
                frappe.log_error(f"Shopee API error: {error_msg}", 'Shopee Token Retrieval Error')
                frappe.throw(_("Failed to obtain tokens: ") + error_msg)

        # 检查是否包含必要的令牌信息
        if 'access_token' in result and 'refresh_token' in result:
            # 处理可能的ID列表
            merchant_ids = result.get('merchant_id_list', [])
            shop_ids = result.get('shop_id_list', [])
            # 如果需要，这里可以添加供应商ID的处理逻辑

            # 保存令牌信息
            for merchant_id in merchant_ids:
                save_tokens(result['access_token'], result['refresh_token'], result['expire_in'], merchant_id, is_merchant=True)
                fetch_merchant_info(merchant_id)  # 自动保存商户信息
            for shop_id in shop_ids:
                save_tokens(result['access_token'], result['refresh_token'], result['expire_in'], shop_id, is_merchant=False)
                fetch_shop_info(shop_id)  # 自动保存商店信息

            return result
        else:
            frappe.throw(_("Failed to obtain tokens: Detailed API response: ") + response.text)
    else:
        frappe.throw(_("Failed to communicate with Shopee API. Detailed response: ") + response.text)

def save_tokens(access_token, refresh_token, expire_in, identifier, is_merchant):
    """
    Save or update the token information in Shopee Token Management doctype.
    """
    existing_doc = frappe.get_all('Shopee Token Management', filters={('merchant_id' if is_merchant else 'shop_id'): identifier}, fields=['name'])
    if existing_doc:
        doc = frappe.get_doc('Shopee Token Management', existing_doc[0]['name'])
    else:
        doc = frappe.new_doc('Shopee Token Management')
        if is_merchant:
            doc.merchant_id = identifier
        else:
            doc.shop_id = identifier

    doc.access_token = access_token
    doc.refresh_token = refresh_token
    doc.token_expiry = int(time.time()) + int(expire_in)
    doc.last_refreshed = datetime.now()
    doc.active = 1
    doc.save(ignore_permissions=True)
    frappe.db.commit()

def ensure_valid_access_token(shop_id=None, merchant_id=None):
    """
    确保获取有效的access_token。
    如果access_token即将过期或已过期，使用refresh_token刷新它。
    """
    identifier_field = 'shop_id' if shop_id else 'merchant_id'
    identifier_value = shop_id if shop_id else merchant_id
    
    token_doc = frappe.get_all('Shopee Token Management', filters={identifier_field: identifier_value},
                               fields=['name', 'access_token', 'refresh_token', 'token_expiry'], limit=1)
    if not token_doc:
        frappe.throw(_('No token found for the given identifier.'))

    token_doc = frappe.get_doc('Shopee Token Management', token_doc[0].name)
    now = int(time.time())
    
    # Check if the token is about to expire or has already expired
    if token_doc.token_expiry - now <= 300:  # Consider refreshing if less than 5 minutes left
        new_access_token, new_refresh_token = refresh_token(identifier_field, identifier_value, token_doc.refresh_token)
        print("refreshing")
        if new_access_token and new_refresh_token:
            token_doc.access_token = new_access_token
            token_doc.refresh_token = new_refresh_token
            token_doc.token_expiry = now + 14400  # Assuming the new access token lasts for 4 hours
            token_doc.last_refreshed = datetime.now()
            token_doc.save(ignore_permissions=True)
            frappe.db.commit()
    
    return token_doc.access_token

def refresh_token(id_type, id_value, current_refresh_token):
    """
    Refresh the access token for a given shop or merchant ID and update the database record.

    Args:
    id_type (str): 'shop_id' or 'merchant_id'
    id_value (int): ID of the shop or merchant
    current_refresh_token (str): Current refresh token

    Returns:
    tuple: (new_access_token, new_refresh_token) if successful, otherwise None
    """
    timest = int(time.time())
    host = "https://openplatform.shopee.cn"
    path = "/api/v2/auth/access_token/get"
    body = {id_type: id_value, "refresh_token": current_refresh_token, "partner_id": PARTNER_ID}
    
    signature = generate_signature(PARTNER_ID, path, timest, PARTNER_KEY)
    url = f"{host}{path}?partner_id={PARTNER_ID}&timestamp={timest}&sign={signature}"

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=body, headers=headers)
    
    if response.status_code == 200:
        ret = response.json()
        new_access_token = ret.get("access_token")
        new_refresh_token = ret.get("refresh_token")

        # Call save_tokens to update the tokens in the database
        if new_access_token and new_refresh_token:
            save_tokens(new_access_token, new_refresh_token, ret.get('expire_in'), id_value, id_type == 'merchant_id')
            return new_access_token, new_refresh_token
        else:
            frappe.log_error(_("Failed to obtain new tokens."), 'Token Refresh Error')
            return None, None
    else:
        error = response.json()
        frappe.log_error(str(error), 'Refresh Token Error')
        return None, None