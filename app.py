from flask import Flask, request, jsonify
from pywidevine.cdm import Cdm
from pywidevine.device import Device
from pywidevine.pssh import PSSH
import requests
import os
import traceback

app = Flask(__name__)

# ✅ Your device path
DEVICE_PATH = "/storage/emulated/0/Documents/Pydroid3/generic_8159_l3.wvd"


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Server running"})


@app.route("/get_keys", methods=["POST"])
def get_keys():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        pssh_data = data.get("pssh")
        lic_url = data.get("license_url")

        if not pssh_data or not lic_url:
            return jsonify({"error": "Missing pssh or license_url"}), 400

        # ✅ check file
        if not os.path.exists(DEVICE_PATH):
            return jsonify({"error": "WVD file not found"}), 500

        # Load device
        device = Device.load(DEVICE_PATH)

        # Create CDM
        cdm = Cdm.from_device(device)

        # Open session
        session_id = cdm.open()

        # Create PSSH
        pssh_obj = PSSH(pssh_data)

        # Generate challenge
        challenge = cdm.get_license_challenge(session_id, pssh_obj)

        # Send license request
        response = requests.post(lic_url, data=challenge)
        response.raise_for_status()

        # Parse license
        cdm.parse_license(session_id, response.content)

        # ✅ FIXED KEY EXTRACTION
        keys = []
        for key in cdm.get_keys(session_id):
            try:
                kid = key.kid.hex()
            except:
                kid = str(key.kid)

            try:
                k = key.key.hex()
            except:
                k = str(key.key)

            keys.append({
                "type": str(key.type),
                "kid": kid,
                "key": k
            })

        # Close session
        cdm.close(session_id)

        return jsonify({"keys": keys})

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)