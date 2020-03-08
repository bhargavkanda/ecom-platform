#EMAIL NOTIFICATIONS
WELCOME_LOGIN_HTML = {
                      'html': 'welcome_login.html',
                      'subject': 'Welcome To Zapyle'
}
UPLOAD_ALBUM_INTERNAL_HTML = { 'to_email': "zapyle@googlegroups.com",
                      'html': 'album_upload.html',
                      'subject': 'Verification needed for a listed product',
                      'vars':['USER', 'TYPE', 'ALBUMNAME']
}
UPLOAD_ALBUM_HTML = {
                      'html': 'album_user_upload.html',
                      'subject': 'Thanks For Your Listing!',
                      'vars':['user']
}
ACCOUNT_NUMBER_CHANGE_HTML = {
    "subject": "Your Account Number Has Successfully Been Changed",
    "html": "account_change.html",
    "vars": ['user'],
}
ORDER_COFIRMED_HTML_1 = {
    "subject": "Yay! Your Zapyle Order Has Been Confirmed.",
    "html": "order_confirmation_buyer.html",
    "vars": ['buyer_name','productImage','product_title','product_qty','unit_price','final_price','shipping_charge']
}
# ORDER_COFIRMED_SELLER_HTML = {
#     "subject": "Yay! Your Deal's Gone Through on Zapyle!.",
#     "html": "order_confirmation_seller.html",
#     "vars": ['user','product_title','product_pickup_address']
# }
ORDER_COFIRMED_HTML_2 = {
    "to_email": "zapyle@googlegroups.com",
    "subject": "Yay! Zapyle got an order.",
    "html": "internal_order.html",
    "vars": ['buyer','seller','album_name']
}
PRODUCT_APPROVED_HTML = {
    "subject": "Congrats! Your Listing Has Been Approved.",
    "html": "listing_approved.html"
}
# PAYOUT_SELLER_HTML = {
#     "subject": "You Just Received Your Earnings For Your Item!",
#     "html": "payout_seller.html",
#     "vars": ['amt','user'],
# }
RETURN_REQUEST_BUYER_HTML = {
    "subject": "We Received Your Request For Return.",
    "html": "return_request_buyer.html",
    "vars": ['user'],
}
RETURN_REQUEST_SELLER_HTML = {
    "subject": "We've Got Some Bad News.",
    "html": "return_request_seller.html",
    "vars": ['user'],
}
ZAPCASH_RETURN_HTML = {
    "subject": "Your Zap Account Has Been Credited!",
    "html": "zapcash_return.html",
    "vars": ['user'],
}

SELLER_ADDRESS_CONF_AFTER_ORDER = {
    "subject": "Yay! Your Deal's Gone Through on Zapyle!.",
    "html": "seller_after_order.html",
    "vars": ['seller_name','from_name','from_add','from_city','from_state','from_pincode','from_country','productLink','img','productName','productSize','productColor','productPrice','accountDecider'],
}
SELLER_GENERIC = {
    "subject": "Zapyle - You've Received An Order. Get Packing!",
    "html": "seller_generic.html",
    "vars": ['userTypeDecider','seller_name','product_titles','buyer_name','products'],
}
SELLER_NOTIF = {
    "subject": "Zapyle - Follow up on the order received. Get Packing!",
    "html": "seller_notif.html",
    "vars": ['userTypeDecider','seller_name','product_titles','buyer_name','products'],
}
RETURN_AFTER_SCHEDULE = {
    "subject": "Follow Up on Returns - Zapyle",
    "html": "other_return.html",
    "vars": ['buyer_name'],
}
DELHIVERY_RETURN_DOC = {
    "subject": "Returns Document - Zapyle",
    "html": "DL_return.html",
    "vars": ['buyer_name'],
}
BUYER_AFTER_RETURN = {
    "subject": "Zapyle - Your Item Has Been Safely Returned!",
    "html": "buyer_after_returns.html",
    "vars": ['buyer_name','product_desc'],
}
BUYER_FEEDBACK = {
    "subject": "Zapyle - Delivery Confirmation of your item!",
    "html": "buyer_feedback.html",
    "vars": ['buyer_name','products'],
}
SELLER_AFTER_RETURN = {
    "subject": "Zapyle - Your Item Is Getting Listed Again!",
    "html": "seller_after_returns.html",
    "vars": ['seller_name','profile_link','zap_username'],
}
SELLER_PAYOUT = {
    "subject": "You Just Received Your Earnings For Your Item!",
    "html": "seller_payout.html",
    "vars": ['seller','amt'],
}
SELLER_BANK_INFO = {
    "subject": "Zapyle - Your Account Details Is Required!",
    "html": "seller_bank_info.html",
    "vars": ['seller_name'],
}

LEAD_TEMPLATE = {
    "html": "lead_layout.html",
}

NEW_MESSAGE_TEMPLATE = {
    "html": "new_message.html"
}