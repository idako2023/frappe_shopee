# config.py
import frappe

SHOPEE_URL = "https://openplatform.shopee.cn"

def get_partner_id():
    partner_id = frappe.local.conf.get('shopee_partner_id', None)
    if not partner_id:
        frappe.throw("Shopee partner id is not configured.", exc=frappe.ConfigurationError)
    return partner_id

def get_partner_key():
    partner_key = frappe.local.conf.get('shopee_partner_key', None)
    if not partner_key:
        frappe.throw("Shopee partner key is not configured.", exc=frappe.ConfigurationError)
    return partner_key
