from flask import Flask , request , jsonify



app = Flask(__name__)


@app.route("/validate_token", methods = ['POST'])
def validate_token():
    token = request.json['token']

    if token == "sanyam":
        print("Success")
        return jsonify({"valid" : "success"}) , 200
    else:
        return jsonify({"Invalid" : "Fail"}), 400

if __name__ == "__main__":

    app.run(host="0.0.0.0" , port=1111 , debug=False)