import frappe
from datetime import datetime, timedelta
from .controllers.token_management import refresh_token  # 确保导入路径正确

PARTNER_ID = frappe.local.conf.get('shopee_partner_id', '')
PARTNER_KEY = frappe.local.conf.get('shopee_partner_key', '')

def refresh_all_tokens():
    """
    每周检查并刷新即将过期的所有 refresh_tokens。
    """
    tokens = frappe.get_all('Shopee Token Management',
                            fields=['name', 'shop_id', 'merchant_id', 'refresh_token', 'last_refreshed', 'active'],
                            filters={'active': 1})
    
    one_week_from_now = datetime.now() + timedelta(days=7)  # 计算从现在起一周后的时间
    for token in tokens:
        # 计算 refresh_token 的实际过期时间
        refresh_token_expiry = token['last_refreshed'] + timedelta(days=30)
        
        if refresh_token_expiry < one_week_from_now:
            print("Need to refresh")
            id_type = 'shop_id' if token['shop_id'] else 'merchant_id'
            id_value = token['shop_id'] if token['shop_id'] else token['merchant_id']
            refresh_token(id_type, id_value, token['refresh_token'])
