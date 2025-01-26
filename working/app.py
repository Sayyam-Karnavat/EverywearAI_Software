from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Initialize LLM and parser
llm = OllamaLLM(model="llama3.2:3b")
output_parser = StrOutputParser()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes (or specific routes if desired)
CORS(app, resources={r"/*": {"origins": "*"}})  # Use "*" for all origins or specify like "http://127.0.0.1:5500"

@app.route("/")
def index_page():
    return "Server is running!"

@app.route("/get_response", methods=["GET", "OPTIONS", "POST"])
def get_response():
    if request.method == "OPTIONS":
        # Handle the preflight request
        return "", 200

    try:
        if request.method == "POST":
            # Get the user query from the JSON body of the POST request
            data = request.get_json()
            user_query = data.get("query")
        else:
            # Fallback for GET requests (if applicable)
            user_query = request.args.get("user_query")

        print("user query:", user_query)

        if not user_query:
            return jsonify({"error": "No user query provided"}), 400

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
