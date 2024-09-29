from flask import Flask, render_template, jsonify, request
from waitress import serve
import logging
app = Flask(__name__)

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

logger = logging.getLogger(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/hydrogel', methods=["POST"])
def make_hydrogel():
    data = request.get_json()
    logger.info(f"Form submitted with data: {data}")
    return jsonify({"message":"Data received", "data":data}), 200 


if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8000)
