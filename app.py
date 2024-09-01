from flask import Flask, request, render_template, jsonify
import requests
import os 

app = Flask(__name__)

# Replace with your actual API key
API_KEY = os.getenv('AT_API_KEY')
API_URL = 'https://insights.sandbox.africastalking.com/v1/sim-swap'
USERNAME = 'sandbox'  # Using the sandbox username

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_sim_swap', methods=['POST'])
def check_sim_swap():
    phone_number = request.form['phone_number']

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'apiKey': API_KEY
    }

    data = {
        'username': USERNAME,
        'phoneNumbers': [phone_number]
    }

    try:
        # Make a POST request to the Africa's Talking SIM swap API
        response = requests.post(API_URL, headers=headers, json=data)
        response_data = response.json()

        # Process the response based on your API's structure
        if response.status_code == 200:
            sim_swap_status = response_data.get('data', {}).get('status', 'Unknown')
            message = f"SIM Swap Status for {phone_number}: {sim_swap_status}"
        else:
            message = f"Failed to retrieve SIM swap status. Reason: {response_data.get('errorMessage', 'Unknown error')}"

    except Exception as e:
        message = f"An error occurred: {str(e)}"

    return jsonify({'message': message})

# Callback endpoint to receive notifications from Africa's Talking API
@app.route('/sim_swap_callback', methods=['POST'])
def sim_swap_callback():
    try:
        callback_data = request.json  # Get the JSON data sent by the callback
        print("Received callback data:", callback_data)

        # Extract important details from the callback
        transaction_id = callback_data.get('transactionId', 'Unknown')
        status = callback_data.get('status', 'Unknown')
        total_cost = callback_data.get('totalCost', {'amount': 'Unknown', 'currencyCode': 'Unknown'})
        responses = callback_data.get('responses', [])

        # Iterate through responses to extract detailed information
        response_details = []
        for entry in responses:
            phone_number = entry.get('phoneNumber', {})
            cost = entry.get('cost', {})
            request_id = entry.get('requestId', 'Unknown')
            response_status = entry.get('status', 'Unknown')

            response_details.append({
                'carrierName': phone_number.get('carrierName', 'Unknown'),
                'countryCode': phone_number.get('countryCode', 'Unknown'),
                'networkCode': phone_number.get('networkCode', 'Unknown'),
                'number': phone_number.get('number', 'Unknown'),
                'numberType': phone_number.get('numberType', 'Unknown'),
                'cost_amount': cost.get('amount', 'Unknown'),
                'cost_currencyCode': cost.get('currencyCode', 'Unknown'),
                'requestId': request_id,
                'status': response_status
            })

        # Log or process the extracted data
        print(f"Transaction ID: {transaction_id}")
        print(f"Overall Status: {status}")
        print(f"Total Cost: {total_cost['amount']} {total_cost['currencyCode']}")
        print("Response Details:")
        for detail in response_details:
            print(detail)

        # Return a response to acknowledge the receipt of the callback
        return jsonify({'status': 'success', 'message': 'Callback received successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(port=5005, debug=True)  # Running on port 5001 to avoid conflicts

