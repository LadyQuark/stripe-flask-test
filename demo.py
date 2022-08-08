import stripe
import os

from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv(find_dotenv())

stripe.api_version = '2020-08-27'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

YOUR_DOMAIN = 'http://localhost:4242'

# plans = stripe.Plan.list(expand=['data.product'])
# for plan in plans.data:
#     print(f'{plan.product.name}: {plan.amount}/{plan.interval}')

# customer = stripe.Customer.create(
# 	name='Ashok Kumar',
# 	email='ashokkumar@example.com',
# 	payment_method='pm_card_visa',
# 	invoice_settings={
# 		'default_payment_method': 'pm_card_visa',
# 	},
# 	address={
# 		'line1': '1 Mall Road',
# 		'line2': '113 Everest Apartments',
# 		'city': 'Darjeeling',
# 	},
# 	preferred_locales=['en', 'es']
# )
# print(customer)

# result = stripe.Customer.delete('cus_MABLw00xOimeSQ')
# print(result)

# session = stripe.billing_portal.Session.create(
#         customer=stripe.Customer.retrieve('cus_MAYUx5oQltnZCy'),
#         return_url=YOUR_DOMAIN,
#     )
# print(session.url)

data = {'items': [{'id': 'price_1LSFLmSJW5sw0hdPE3YH9OUQ'}]}
price_ids = [item['id'] for item in data['items']]
print(price_ids)