import frappe
import hmac
import hashlib
import json
from shopee.config import get_partner_key
from .shopee_event_handlers import get_event_handler

@frappe.whitelist(allow_guest=True)
def shopee_webhook():
    # 获取请求数据和头部中的签名
    request_data = frappe.request.data.decode('utf-8')  # 确保解码
    header_signature = frappe.request.headers.get('Authorization')

    # 验证签名
    if not verify_shopee_signature(request_data, header_signature):
        frappe.log_error("Invalid signature in Shopee webhook request", "Shopee Webhook Error")
        frappe.throw("Invalid signature", exc=frappe.PermissionError)  # 使用frappe.throw抛出权限错误

    # 签名验证通过后，处理数据
    data = json.loads(request_data)
    event_type = data.get('code')
    event_handler = get_event_handler(event_type)
    if event_handler:
        event_handler(data)
    else:
        frappe.log_error(f"No handler for event type {event_type}", "Shopee Webhook Error")

    return "Webhook processed successfully", 200

@frappe.whitelist(allow_guest=True)
def get_current_url():
    return frappe.request.url

@frappe.whitelist(allow_guest=True)
def verify_shopee_signature(request_body, authorization_header):
    # 获取当前请求的完整 URL
    current_url = get_current_url()
    
    # 构建用于签名的基本字符串
    base_string = f"{current_url}|{request_body}"  # 直接使用request_body，确保已经是字符串

    # 尝试从配置中获取 partner_key，如果未配置，则抛出错误
    try:
        partner_key = get_partner_key().encode('utf-8')
    except frappe.ConfigurationError as e:
        frappe.log_error(str(e), "Shopee Webhook Error")
        return False  # 适当地处理错误，不继续执行
    
    # 计算 HMAC SHA-256 签名
    calculated_signature = hmac.new(partner_key, base_string.encode('utf-8'), hashlib.sha256).hexdigest()

    # 比较计算出的签名和推送请求中的签名
    return hmac.compare_digest(calculated_signature, authorization_header)
