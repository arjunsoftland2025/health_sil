import frappe
from datetime import datetime, timedelta

@frappe.whitelist()
def get_expiring_medicines():
    today = datetime.today()
    threshold = today + timedelta(days=90)

    items = frappe.get_all('Item',
        filters={
            'item_group': 'Medications',
            'has_expiry_date': 1,
            'disabled': 0
        },
        fields=['name', 'item_name', 'expiry_date']
    )

    expiring = []
    for item in items:
        if item.expiry_date and today.date() <= item.expiry_date <= threshold.date():
            expiring.append(f"{item.item_name} (expires on {item.expiry_date})")

    return expiring

@frappe.whitelist()
def check_item_expiry(item_code):
    item = frappe.get_doc("Item", item_code)
    today = datetime.today().date()
    threshold = today + timedelta(days=90)

    if item.has_expiry_date and item.expiry_date and today <= item.expiry_date <= threshold:
        return {
            "status": "expiring",
            "message": f"{item.item_name} is expiring on {item.expiry_date}"
        }

    return {"status": "ok"}
