from flask import Flask, jsonify, request
import requests
from cachetools import deque
import time

app = Flask(__name__)

# Window size
WINDOW_SIZE = 10
# Initialize deque for storing numbers with a fixed size
window = deque(maxlen=WINDOW_SIZE)

def fetch_numbers_from_server(numberid):
    url = f"https://thirdparty.server/api/numbers/{numberid}"
    try:
        response = requests.get(url, timeout=0.5)
        response.raise_for_status()
        numbers = response.json().get("numbers", [])
        return list(set(numbers))  # Remove duplicates
    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        return []

@app.route('/numbers/<numberid>', methods=['GET'])
def get_numbers(numberid):
    if numberid not in ['p', 'f', 'e', 'r']:
        return jsonify({"error": "Invalid number ID"}), 400

    window_prev_state = list(window)
    fetched_numbers = fetch_numbers_from_server(numberid)
    
    # Append unique numbers to the window
    for number in fetched_numbers:
        if len(window) < WINDOW_SIZE or number not in window:
            window.append(number)
    
    window_curr_state = list(window)
    
    # Calculate average if window is full
    avg = sum(window_curr_state) / len(window_curr_state) if len(window_curr_state) == WINDOW_SIZE else None
    
    response = {
        "windowPrevState": window_prev_state,
        "windowCurrState": window_curr_state,
        "numbers": fetched_numbers,
        "avg": round(avg, 2) if avg is not None else None
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
