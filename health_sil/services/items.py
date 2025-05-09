import frappe

def update_item_valuation_rate_on_submit(doc, method):
    # Loop through the items in the purchase invoice
    for item in doc.items:
        # Check if the custom valuation rate is set
        if item.custom_valuation_rate is not None:
            try:
                # Fetch the item record
                item_doc = frappe.get_doc("Item", item.item_code)
                # Update the valuation_rate field with the value from the custom field
                item_doc.valuation_rate = item.custom_valuation_rate
                item_doc.save(ignore_permissions=True)  # Save the changes
                frappe.db.commit()  # Commit the transaction
            except Exception as e:
                # Log any errors that occur
                frappe.log_error(frappe.get_traceback(), "Valuation Rate Update Error")

