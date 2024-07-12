import hmac
import hashlib
import frappe

def generate_signature(partner_id, path, timestamp, partner_key, access_token=None, shop_id=None, merchant_id=None):
    """
    根据不同API类型生成Shopee API所需的签名。
    - 对于public API: 只需要 partner_id, path, timestamp, partner_key
    - 对于global API: 需要 partner_id, path, timestamp, access_token, merchant_id, partner_key
    - 对于shop API: 需要 partner_id, path, timestamp, access_token, shop_id, partner_key
    """
    # 构建基础消息
    message = f"{partner_id}{path}{timestamp}"
    
    # 根据API类型添加额外的参数
    if access_token:
        message += access_token
    if shop_id:
        message += str(shop_id)
    if merchant_id:
        message += str(merchant_id)
    
    # 使用HMAC-SHA256算法生成签名
    signature = hmac.new(partner_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

def print_shopee_token_management():
    documents = frappe.get_all('Shopee Token Management', fields=['*'])
    for doc in documents:
        print(doc)

def delete_all_shopee_token_management_records():
    """
    删除 Shopee Token Management 中的所有记录
    """
    # 获取所有记录的名称
    records = frappe.get_all('Shopee Token Management', fields=['name'])

    # 循环删除每条记录
    for record in records:
        doc = frappe.get_doc('Shopee Token Management', record['name'])
        doc.delete()

    frappe.db.commit()  # 确保提交数据库操作

    print(f"Deleted {len(records)} records from Shopee Token Management.")
