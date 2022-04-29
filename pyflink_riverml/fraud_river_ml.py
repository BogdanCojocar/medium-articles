
from flask import Flask, jsonify, request
from river import linear_model
from river import metrics
from river import evaluate
from river import preprocessing
from river import compose
import json

app = Flask(__name__)

class RiverML:
    # fraud detection model
    model = compose.Pipeline(
        preprocessing.StandardScaler(),
        linear_model.LogisticRegression()
    )

    # ROCAUC metric to score the model as it trains
    metric = metrics.ROCAUC()
fraud_model = RiverML()

@app.route('/predict', methods=['POST'])
def predict():
    # convert into dict
    request_data = request.get_json()
    x_data = json.loads(request_data['x'])
    y_data = json.loads(request_data['y'])

    # do the prediction and score it
    y_pred = fraud_model.model.predict_one(x_data)
    metric = fraud_model.metric.update(y_data, y_pred)

    # update the model
    model = fraud_model.model.learn_one(x_data, y_data)

    return jsonify({'result': y_pred, 'performance': {'ROCAUC': fraud_model.metric.get()}})

if __name__ == '__main__':
    app.run(port=9000)
