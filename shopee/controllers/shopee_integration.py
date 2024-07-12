import frappe
import requests
from datetime import datetime
from .utils import generate_signature  # 确保这个函数可以生成正确的签名
from shopee.shopee.doctype.shopee_token_management.api_helper import get_token_by_shop_or_merchant_id
from shopee.config import SHOPEE_URL, get_partner_id, get_partner_key

# 常量配置
PARTNER_ID = get_partner_id()
PARTNER_KEY = get_partner_key()

def fetch_merchant_info(merchant_id):
    # 获取必要的 token 和时间戳
    access_token = get_token_by_shop_or_merchant_id(merchant_id=merchant_id)
    timestamp = int(datetime.now().timestamp())
    sign = generate_signature(PARTNER_ID, '/api/v2/merchant/get_merchant_info', timestamp, access_token=access_token, merchant_id=merchant_id)

    # 构建请求 URL 和参数
    url = f"{SHOPEE_URL}/api/v2/merchant/get_merchant_info"
    params = {
        'partner_id': PARTNER_ID,
        'timestamp': timestamp,
        'sign': sign,
        'access_token': access_token,
        'merchant_id': merchant_id
    }

    # 发送请求
    response = requests.get(url, params=params)
    data = response.json()

    # 检查是否有错误返回
    if data.get('error'):
        frappe.log_error(data['message'], 'Shopee API Error: ' + data['error'])
        return

    # 处理返回的商户数据
    process_merchant_data(data, merchant_id)

def process_merchant_data(data, merchant_id):
    merchant_name = data.get('merchant_name', '')
    region = data.get('merchant_region', '')
    company_name = f"SP_{region[:2]}_{merchant_name[:2]}"

    # Initialize status list based on conditions
    status = []
    if data.get('is_cnsc', False):
        status.append('Cross-Border')
        status.append('CNSC')
    elif region == 'KR' and data.get('is_upgraded_cbsc', False):
        status.append('Cross-Border')
        status.append('KRSC')
    else:
        status.append('UNUPGRADED')

    # Status for MultiSelect fields in ERPNext needs to be line-separated
    status_string = '\n'.join(status)

    auth_time = datetime.fromtimestamp(data.get('auth_time'))
    expire_time = datetime.fromtimestamp(data.get('expire_time'))

    # Check if the company record exists
    company_exists = frappe.db.exists('Company', {'entity_id': data.get('request_id')})

    if company_exists:
        # Update existing company record
        company_doc = frappe.get_doc('Company', company_exists)
    else:
        # Create a new company record if it doesn't exist
        company_doc = frappe.new_doc('Company')
        company_doc.name = company_name

    # Updating the doc with new or existing values
    company_doc.update({
        'entity_name': merchant_name,
        'entity_id': merchant_id,
        'status': status_string,
        'authorization_time': auth_time,
        'authorization_expiry_time': expire_time,
        'is_authorized': True,
        'is_group': 1,
        'country': region,
        'default_currency': data.get('merchant_currency', '')
    })

    company_doc.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.log_error(f"Processed merchant info for {data.get('request_id')}", 'Shopee Merchant Process')


def fetch_shop_info(shop_id):
    access_token = get_token_by_shop_or_merchant_id(shop_id=shop_id)
    timestamp = int(datetime.now().timestamp())
    sign = generate_signature(PARTNER_ID, '/api/v2/shop/get_shop_info', timestamp, access_token, shop_id=shop_id)

    url = f"{SHOPEE_URL}/api/v2/shop/get_shop_info"
    params = {
        'partner_id': PARTNER_ID,
        'timestamp': timestamp,
        'sign': sign,
        'access_token': access_token,
        'shop_id': shop_id
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('error') is not None:
            frappe.log_error(data['message'], 'Shopee API Error')
        else:
            process_shop_data(data, shop_id)
    else:
        frappe.log_error(response.text, 'Failed to fetch shop info from Shopee')

def process_shop_data(data, shop_id):
    shop_name = data.get('shop_name', '')
    region = data.get('region', '')
    company_name = f"SP_{region[:2]}_{shop_name[:2]}"

    # Status construction based on detailed conditions
    status = []
    # Add CBSC status
    shop_cbsc = data.get('shop_cbsc')
    status.append(shop_cbsc)

    # Check for SIP status
    if data.get('is_sip', False):
        status.append('SIP')

    # Fulfillment flag mapping to status
    fulfillment_map = {
        'Pure - FBS Shop': 'Pure-FBS',
        'Pure - 3PF Shop': 'Pure-3PF',
        'PFF - FBS Shop': 'PFF-FBS',
        'PFF - 3PF Shop': 'PFF-3PF'
    }
    fulfillment_flag = data.get('shop_fulfillment_flag', 'Unknown')
    status.append(fulfillment_map.get(fulfillment_flag, 'Others'))

    status_string = '\n'.join(status)

    # Handling authorization times
    auth_time = datetime.fromtimestamp(data.get('auth_time')) if data.get('auth_time') else datetime.now()
    expire_time = datetime.fromtimestamp(data.get('expire_time')) if data.get('expire_time') else datetime.now()

    # Determine the parent company based on merchant_id
    merchant_id = data.get('merchant_id')
    parent_company = frappe.get_value('Company', {'merchant_id': merchant_id}, 'name') if merchant_id else None

    # Check if the shop record exists by using shop_id
    shop_exists = frappe.db.exists('Company', {'entity_id': shop_id})

    if shop_exists:
        # Update existing shop record
        shop_doc = frappe.get_doc('Company', shop_exists)
    else:
        # Create a new shop record if it doesn't exist
        shop_doc = frappe.new_doc('Company')
        shop_doc.is_group = 0  # Ensure it is not marked as a group

    # Updating the doc with new or existing values
    shop_doc.update({
        'company_name': company_name,
        'entity_name': shop_name,
        'entity_id': shop_id,  # Save shop_id as entity_id
        'status': status_string,
        'authorization_time': auth_time,
        'authorization_expiry_time': expire_time,
        'is_authorized': True,
        'country': region,
        'default_currency': 'Currency based on region',
        'is_group': 1,
        'parent_company': parent_company
    })

    shop_doc.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.log_error(f"Processed shop info for {shop_id}", 'Shopee Shop Process')

