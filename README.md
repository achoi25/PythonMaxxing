# PythonMaxxing

Full-stack application with Python Flask backend and React Vite frontend.

## Project Structure

```
pythonmaxxing/
├── frontend/                 # React + Vite frontend application
│   ├── src/                 # React components and pages
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── eslint.config.js     # ESLint configuration
│   └── index.html           # Entry HTML file
├── backend/                 # Python Flask backend
│   └── app.py              # Flask application
└── package.json            # Root scripts for managing both frontend and backend
```

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run ESLint
```

### Backend

```bash
cd backend
# Set up Python virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-cors

# Run the server
python app.py
```

## Root Level Commands

From the root directory:

```bash
npm run frontend:dev    # Start frontend development server
npm run frontend:build  # Build frontend
npm run backend:dev     # Run backend server
```
