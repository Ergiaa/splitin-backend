# SplitIn Backend

This is the backend service for the SplitIn app, built with Flask.

## 📦 Requirements

- Python 3.11+
- Docker & Docker Compose
- pip / pipenv / virtualenv (your choice for managing Python dependencies)

---

## ⚙️ Setup Environment Variables

Duplicate the example config:

```bash
cp settings.py.example settings.py
```

Edit `settings.py` to configure your environment (e.g., database credentials, Firebase settings, etc.).

---

## 🐳 Setup Docker for Firestore Database

Start the database with:

```bash
docker-compose up -d
```

---

## 🔧 Run in Development

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   flask --app app --debug run
   ```

---

## 📂 Project Structure

```
splitin-backend/
├── /firebase           # Firebase Configuration
├── /middleware
├── /models             # App Models (Collections, Sub-Collections, & Documents)
├── /resource           # Routing File (Like Controllers)
├── /services           # Main App Logic
├── /utils
├── /validators         # Request data validators
├── settings.py         # Project settings
├── manage.py           # CLI entry for DB migration
├── requirements.txt
├── docker-compose.yml
└── README.md
```
