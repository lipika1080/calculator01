from flask  import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Connection (Replace with your Cosmos MongoDB URI)
MONGO_URI = "mongodb://calculator01:7pNHOgvChqgGqYgKnt7CBtVLKWJWPM5F4KdOiWHTLIfInwQkWKrqBfoBtKnE2JyebrV0ECX6IhjVACDbWEMaaQ==@calculator01.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@calculator01@"
client = MongoClient(MONGO_URI)
db = client["calculatorDB"]
calculations = db["calculations"]

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.json
        numbers = data["numbers"]
        operation = data["operation"]

        if not numbers or not operation:
            return jsonify({"error": "Invalid input"}), 400

        if operation == "add":
            result = sum(numbers)
        elif operation == "subtract":
            result = numbers[0] - sum(numbers[1:])
        elif operation == "multiply":
            result = 1
            for num in numbers:
                result *= num
        elif operation == "divide":
            result = numbers[0]
            for num in numbers[1:]:
                if num == 0:
                    return jsonify({"error": "Cannot divide by zero"}), 400
                result /= num
        else:
            return jsonify({"error": "Invalid operation"}), 400

        # Save to CosmosDB
        calc_record = {"numbers": numbers, "operation": operation, "result": result}
        calculations.insert_one(calc_record)

        return jsonify({"result": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def get_history():
    history = list(calculations.find({}, {"_id": 0}))  # Exclude ObjectId
    return jsonify(history), 200

if __name__ == "__main__":
    app.run(debug=True)
