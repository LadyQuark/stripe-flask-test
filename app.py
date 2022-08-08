""" 
Testing Stripe with Flask to:
    • accept payment for a single subscription
        - using Checkout (Stripe-hosted payment page)
        - using Elements (self-hosted payment page)
    • receive signed webhook notifications for events
"""

import stripe
import os
import json

from flask import Flask, redirect, render_template, jsonify, request
from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_version = '2020-08-27'
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

app = Flask(__name__)

YOUR_DOMAIN = 'http://localhost:4242'


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/public-keys')
def public_keys():
    """ Route for front-end to get Stripe publishable key """
    
    return jsonify({
        'key': os.getenv('STRIPE_PUBLISHABLE_KEY')
    })


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    Called to redirect to Stripe-hosted checkout page.
    Example for single subscription: `mode='subscription'`
        stripe customer id can be passed, otherwise creates new customer 
        price_id is temporarily hard-coded in HTML
    """
    
    price = request.form.get('priceID')

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[{
                'price': price,
                'quantity': 1
            }],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=YOUR_DOMAIN + '/cancel?session_id={CHECKOUT_SESSION_ID}',     
        )
    except stripe.error.StripeError as e:
        return jsonify({'error': {'message': str(e)}}), 400
    except Exception as e:
        return jsonify({'error': {'message': str(e)}}), 500

    return redirect(checkout_session.url, code=303)


@app.route('/success', methods=['GET'])
def success():
    """ Route when checkout is successful, optional parameter of checkout session id """
    
    customer_name = ""
    session_id = request.args.get('session_id')
    if session_id:
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand = ['customer']
            )
        customer_name = session.customer.name

    return render_template("success.html", customer_name=customer_name)


@app.route('/cancel', methods=['GET'])
def cancel():
    """ Route when checkout is cancelled, optional parameter of checkout session id """
    
    session_id = request.args.get('session_id')
    status = ""
    if session_id:
        session = stripe.checkout.Session.retrieve(
            session_id,
            )
        if session.status == 'expired':
            status = 'Checkout session has expired.'
    return render_template("cancelled.html", status=status)



@app.route('/webhook', methods=['POST'])
def webhook():
    """ Handles webhooks after verifying signature """

    payload = request.data
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=webhook_secret
        )
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': str(e)})            
    except Exception as e:
        return jsonify({'error': str(e)})

    # Match type of event
    match event.type:
        case 'checkout.session.completed':
            checkout_session = event.data.object
            print('Checkout Session completed ' + checkout_session.id)
        case _:
            print(event.type)

    return jsonify({'status': 'success'})


@app.route('/create-payment-intent', methods=['POST'])
def create_payment():
    """ 
    Example of custom payment flow using Stripe Elements 
    front-end: checkout.html, checkout.js
    """

    try:
        data = json.loads(request.data)
        price_ids = [item['id'] for item in data['items']]
        # print(price_ids)
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=2000,
            currency="inr",
            automatic_payment_methods={
                'enabled': True,
            },
            customer='cus_MAYUx5oQltnZCy'
        )
    except Exception as e:
        return jsonify(error=str(e)), 403
    else:
        return jsonify({
            'clientSecret': intent.client_secret
        })


@app.route('/checkout', methods=['GET'])
def checkout():
    return render_template("checkout.html")


if __name__== '__main__':
	app.run(port=4242)