import frappe
from frappe.utils import money_in_words

@frappe.whitelist()
def money_in_words_api(amount):
    return money_in_words(amount)


# # In your app's API file (e.g., api.py)
# @frappe.whitelist()
# def get_last_encounter_doctor(patient):
#     last_encounter = frappe.db.get_value(
#         "Patient Encounter",
#         {"patient": patient},
#         ["name", "practitioner"],
#         order_by="creation desc"
#     )
#     if last_encounter:
#         return {
#             "encounter": last_encounter[0],
#             "doctor": last_encounter[1]
#         }
#     return {}




