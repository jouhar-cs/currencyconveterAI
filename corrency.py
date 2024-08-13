from flask import Flask, request, jsonify
import requests
import logging
import traceback

app = Flask(__name__)

API_KEY = 'e7d9f3af0d1431171ab4'

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['POST'])
def index():
    try:
        data = request.get_json()
        logging.debug(f"Received data: {data}")

        # Extracting parameters correctly from the JSON structure
        source_currency = data['queryResult']['parameters']['unit-currency'][0]['currency']
        amount = data['queryResult']['parameters']['unit-currency'][0]['amount']
        target_currency = data['queryResult']['parameters']['currency-name'][0]

        logging.debug(f"Source Currency: {source_currency}, Amount: {amount}, Target Currency: {target_currency}")

        cf = fetch_conversion_factor(source_currency, target_currency)
        final_amount = amount * cf

        response = {
            'fulfillmentText': "{} {} is {} {}".format(amount, source_currency, final_amount, target_currency)
        }
        logging.debug(f"Response: {response}")

        return jsonify(response)
    except KeyError as e:
        logging.error(f"Missing parameter: {e}")
        return jsonify({'fulfillmentText': f"Missing parameter: {str(e)}"}), 400
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(traceback.format_exc())
        return jsonify({'fulfillmentText': f"An error occurred: {str(e)}"}), 500

def fetch_conversion_factor(source, target):
    try:
        url = f"https://free.currconv.com/api/v7/convert?q={source}_{target}&compact=ultra&apiKey=e7d9f3af0d1431171ab4"
        logging.debug(f"Request URL: {url}")

        response = requests.get(url)
        response.raise_for_status()
        conversion_data = response.json()

        logging.debug(f"Conversion Data: {conversion_data}")

        return conversion_data[f'{source}_{target}']
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        raise Exception(f"API request failed: {str(e)}")
    except KeyError:
        logging.error("Invalid currency code in the response")
        raise Exception("Invalid currency code")

if __name__ == "__main__":
    app.run(debug=True)
