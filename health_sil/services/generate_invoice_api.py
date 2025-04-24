import frappe
import json
from frappe import _
from frappe.utils import nowdate, flt


@frappe.whitelist()
def create_sales_invoice(patient, patient_name, doctor=None, items=None, mode_of_payment=None, price_list=None):
    """
    Creates a Sales Invoice and auto-generates Payment Entry
    """
    try:
        customer = get_validated_customer(patient_name)
        # Create and process Sales Invoice
        invoice = create_and_submit_invoice(customer, patient, patient_name, doctor, items, price_list)
        # Process payment if required
        process_payment(invoice, mode_of_payment) if mode_of_payment else None
        return invoice

    except Exception as e:
        handle_errors(e)


# ----------
# Helper Functions
# ----------
def get_validated_customer(patient_name):
    """Get and validate customer"""
    customer = frappe.get_cached_value("Patient", patient_name, "customer")
    
    if not customer:
        frappe.throw(_("No Customer linked to Patient {0}").format(patient_name))
    
    if frappe.get_cached_value("Customer", customer, "disabled"):
        frappe.throw(_("Customer {0} is disabled").format(customer))
    
    return customer

def create_and_submit_invoice(customer, patient, patient_name, doctor, items, price_list):
    """Create and submit Sales Invoice with optimized validations"""
    items = json.loads(items)
    invoice = frappe.new_doc("Sales Invoice")
    invoice.update({
        "customer": customer,
        "patient": patient,
        "patient_name": patient_name,
        "ref_practitioner": doctor,
        "selling_price_list": price_list,
        "due_date": nowdate(),
        "items": [validate_and_prepare_item(row) for row in items]
    })
    
    invoice.insert(ignore_permissions=True)
    invoice.submit()
    return invoice


def validate_and_prepare_item(item):
    """Validate individual item and prepare for insertion"""
    if (qty := flt(item.get("qty", 1))) <= 0:
        frappe.throw(_("Invalid quantity for item {0}").format(item.get("item_code")))
    
    if (rate := flt(item.get("rate", 0))) < 0:
        frappe.throw(_("Negative rate for item {0}").format(item.get("item_code")))
    
    return {
        "item_code": item.get("item_code"),
        "qty": qty,
        "rate": rate
    }

def process_payment(invoice, mode_of_payment):
    """Handle payment processing"""
    try:
        validate_mode_of_payment(mode_of_payment, invoice.company)
        return create_payment_entry(invoice, mode_of_payment)
    except Exception as e:
        log_and_notify_payment_error(invoice.name, e)
        return None
    
def validate_mode_of_payment(mode, company):
    """Validate mode of payment configuration"""
    if not frappe.db.exists("Mode of Payment", {"name": mode}):
        frappe.throw(_("Invalid Mode of Payment: {0}").format(mode))
    
    if not frappe.get_cached_value("Mode of Payment Account", 
        {"parent": mode, "company": company}, "default_account"):
        frappe.throw(_("Mode of Payment {0} not configured for company {1}").format(mode, company))

def log_and_notify_payment_error(invoice_name, error):
    """Centralized error handling for payments"""
    frappe.log_error(
        title=_("Payment Processing Failed"),
        message=f"Invoice: {invoice_name}\nError: {str(error)}"
    )

def create_payment_entry(invoice, mode_of_payment):
    """Create payment entry using existing invoice doc"""
    if invoice.outstanding_amount <= 0:
        return None

    pe = frappe.new_doc("Payment Entry")
    pe.update({
        "posting_date": nowdate(),
        "payment_type": "Receive",
        "mode_of_payment": mode_of_payment,
        "paid_from": invoice.debit_to,
        "paid_to": get_payment_account(mode_of_payment, invoice.company),
        "party_type": "Customer",
        "party": invoice.customer,
        "paid_amount": invoice.outstanding_amount,
        "received_amount": invoice.outstanding_amount,
        "references": [{
            "reference_doctype": "Sales Invoice",
            "reference_name": invoice.name,
            "allocated_amount": invoice.outstanding_amount
        }]
    })

    pe.insert(ignore_permissions=True)
    pe.submit()
    return pe

def get_payment_account(mode, company):
    """Cached lookup for payment account"""
    return frappe.get_cached_value("Mode of Payment Account", 
        {"parent": mode, "company": company}, "default_account")

def handle_errors(error):
    """Global error handler"""
    frappe.log_error(
        title=_("Sales Pipeline Error"),
        message=f"Error: {str(error)}"
    )
    frappe.throw(_("Process failed. Please check error logs for details."))
