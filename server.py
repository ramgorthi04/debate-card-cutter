from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route("/")
def index():
  return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
  text = request.form["text"]
  num_files = int(request.form["num_files"])

  # Call cutter.py with user input
  command = f"python cutter.py {text} {num_files}"
  subprocess.run(command.split())

  # Logic to retrieve information about generated documents (filenames, etc.)
  # Replace with your logic to get file details
  file_details = [{"name": f"Document_{i}.docx", "content": "..."} for i in range(1, num_files + 1)]

  return render_template("result.html", files=file_details)

if __name__ == "__main__":
  app.run(debug=True)
