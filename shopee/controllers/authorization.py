import time
import frappe
from urllib.parse import urlencode, quote_plus
from .utils import generate_signature
from .token_management import get_tokens
from frappe import _
from shopee.config import SHOPEE_URL, get_partner_id, get_partner_key

# 常量配置
PARTNER_ID = get_partner_id()
PARTNER_KEY = get_partner_key()
HOST = frappe.utils.get_url()
#REDIRECT_URL = frappe.utils.get_url('/api/method/shopee_integration.shopee_auth_callback')  # 回调URL

@frappe.whitelist(allow_guest=True)
def generate_auth_link():
    """
    生成Shopee授权链接。
    """
    timestamp = int(time.time())
    path = "/api/v2/shop/auth_partner"
    signature = generate_signature(PARTNER_ID, path, timestamp, PARTNER_KEY)
    redirect_path = '/auth-callback'  # 前端回调路径
    redirect_url = f"{HOST}:3000{redirect_path}"

    query_params = {
        'partner_id': PARTNER_ID,
        'timestamp': timestamp,
        'sign': signature,
        'redirect': redirect_url
    }
    auth_url = f"{SHOPEE_URL}{path}?{urlencode(query_params, quote_via=quote_plus)}"
    return auth_url

def shopee_auth_callback(auth_code, main_account_id):
    """
    处理Shopee授权后的回调。
    """
    if auth_code and main_account_id:
        try:
            # 假设 get_tokens 函数已更新，以接收 main_account_id
            result = get_tokens(auth_code, main_account_id)
            if result:
                pass
            else:
                frappe.throw(_("Failed to process the authorization code."))
        except Exception as e:
            frappe.log_error(f"Error in processing authorization code: {str(e)}", 'Shopee Auth Callback Error')
            frappe.throw(_("Authorization failed. Please try again."))
    else:
        frappe.throw(_("Authorization failed. No auth code received."))

@frappe.whitelist(allow_guest=True)
def generate_deauth_link():
    """
    生成Shopee授权链接。
    """
    timestamp = int(time.time())
    path = "/api/v2/shop/cancel_auth_partner"
    signature = generate_signature(PARTNER_ID, path, timestamp, PARTNER_KEY)
    redirect_path = '/deauth-callback'  # 前端回调路径
    redirect_url = f"{HOST}:3000{redirect_path}"

    query_params = {
        'partner_id': PARTNER_ID,
        'timestamp': timestamp,
        'sign': signature,
        'redirect': redirect_url
    }
    deauth_url = f"{SHOPEE_URL}{path}?{urlencode(query_params, quote_via=quote_plus)}"
    return deauth_url