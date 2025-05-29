import frappe

@frappe.whitelist()
def get_created_lab_tests_for_bill(laboratory_bill):
    tests = frappe.get_all(
        "Lab Test",
        filters={"laboratory_bill_ref": laboratory_bill, "docstatus": 1},  # Only submitted
        fields=["source_item_code"]
    )
    return [t.source_item_code for t in tests if t.source_item_code]
