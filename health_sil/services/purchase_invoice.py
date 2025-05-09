import frappe

@frappe.whitelist()
def create_stock_entry_from_purchase_invoice(purchase_invoice):
    # Fetch the Purchase Invoice document
    pi = frappe.get_doc("Purchase Invoice", purchase_invoice)
    
    # Loop through all items in the purchase invoice
    for item in pi.items:
        # Check if custom_is_free_qty is True and custom_free_qty is greater than 0
        if item.custom_is_free_qty and item.custom_free_qty > 0:
            # Create a new Stock Entry
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.custom_purchase_invoice_no = purchase_invoice
            stock_entry.purpose = "Material Receipt"  # Material receipt purpose for Stock Entry
            stock_entry.stock_entry_type = "Purchase Receipt"  # Stock Entry type
            stock_entry.company = pi.company  # Use the same company as the Purchase Invoice
            
            # Add the item to Stock Entry
            stock_entry.append("items", {
                "item_code": item.item_code,
                "qty": item.custom_free_qty,  # Use the free quantity
                "rate": 0,  # Rate is 0 for free items
                "t_warehouse": item.warehouse,  # Same warehouse as the purchase item
                "item_name": item.item_name,
                "uom": item.uom,
                "batch_no": item.batch_no,
                "stock_uom": item.uom,
                "basic_rate": 0,  # Basic rate is 0
            })
            
            # Submit the Stock Entry
            stock_entry.insert()
            stock_entry.submit()
            
            # Optionally, you can log that the stock entry was created
            # frappe.msgprint(f"Stock Entry for {item.item_code} created with qty {item.custom_free_qty}")
