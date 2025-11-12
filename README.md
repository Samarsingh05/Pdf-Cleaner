PDF White Page Remover

A lightweight web tool that automatically removes blank/white pages from uploaded PDF files.
Fast, accurate, private — everything happens in-memory, so no files are stored on the server.

✨ Features

✅ Upload or drag-and-drop PDF

✅ Detects true blank pages (not just empty — handles faint borders & watermarks)

✅ Returns a cleaned PDF with blank pages removed

✅ Works fully offline / locally

✅ Clean and modern UI

How to Run Locally
1️⃣ Clone this repository
git clone https://github.com/<your-user>/pdf-white-page-remover.git
cd pdf-white-page-remover

2️⃣ Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

3️⃣ Start the server
python app.py

4️⃣ Open in browser
http://localhost:5050
