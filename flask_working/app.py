from flask import Flask, jsonify, request , render_template
from flask_cors import CORS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize LLM and parser
llm = OllamaLLM(model="llama3.2:3b")
output_parser = StrOutputParser()

# Initialize Flask app
app = Flask(__name__ , template_folder="templates" , static_folder="static")

# Enable CORS for all routes (or specific routes if desired)
CORS(app, resources={r"/*": {"origins": "*"}})  # Use "*" for all origins or specify like "http://127.0.0.1:5500"

@app.route("/")
def index_page():
    return render_template("index.html")


@app.route('/overlay')
def overlay():
    return render_template('overlay.html')




@app.route("/get_response", methods=["GET", "OPTIONS", "POST"])
def get_response():
    if request.method == "OPTIONS":
        # Handle the preflight request
        return "", 200

    try:
        if request.method == "POST":
            data = request.get_json()
            user_query = data.get("query")
            api_key = data.get("api_key")  # Get the API key
        else:
            # Fallback for GET requests (if applicable)
            user_query = request.args.get("user_query")
            api_key = request.args.get("api_key")

        print("User query:", user_query)
        print("API key:", api_key)

        if not user_query or not api_key:
            return jsonify({"error": "No user query or API key provided"}), 400

        # Here you can add logic to verify the API key or use it as needed.
        # Example: if api_key != "expected-api-key":
        #             return jsonify({"error": "Invalid API key"}), 403

        # Generate the response using your LLM
        prompt = ChatPromptTemplate.from_template(
            """
            You are a very helpful and expert assistant. Answer the query asked by the user to your fullest knowledge.

            User query: {user_query}
            """
        )

        chain = prompt | llm | output_parser
        response = chain.invoke(input={"user_query": user_query})

        # Return the response as JSON
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7777)
