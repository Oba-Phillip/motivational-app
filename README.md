# Motivational Message App - PaaS Assignment

## 🚀 Live Demo
[Your Railway URL here]

## 📋 Project Overview
A Flask-based web application that generates motivational messages and stores user interactions in PostgreSQL database. Deployed on Railway with CI/CD.

## ✅ Requirements Completed

### 1. Application Deployment ✅
- Deployed on Railway with public URL
- Flask web application with motivational messages

### 2. Environment Configuration ✅
- All secrets stored in Railway environment variables
- `.env.example` template committed to GitHub
- `.gitignore` prevents secret exposure
- Security headers added to all responses

### 3. Database Integration ✅
- PostgreSQL database provisioned on Railway
- CRUD operations via REST API
- User messages and feedback stored
- Database schema with indexes

### 4. Scalability Awareness ✅
- Usage-based pricing documentation
- Scaling plan for low/medium/high traffic
- `/scalability-info` endpoint

### 5. CI/CD Workflow ✅
- GitHub integration with Railway
- Auto-deploy on push to main branch
- Zero-downtime deployments

### 6. Monitoring & Logging ✅
- Railway logs accessible via dashboard
- `/health` endpoint for monitoring
- Intentional error endpoint for debugging

### 7. Documentation ✅
- Complete deployment documentation
- API endpoint documentation
- Railway vs Heroku comparison

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages` | Get all messages |
| POST | `/api/messages` | Create new message |
| GET | `/api/messages/<username>` | Get user messages |
| PUT | `/api/messages/<id>/feedback` | Add feedback |
| DELETE | `/api/messages/<id>` | Delete message |
| GET | `/health` | Health check |
| GET | `/deploy-info` | CI/CD info |
| GET | `/scalability-info` | Scaling info |
| GET | `/stats` | App statistics |

## 🛠️ Local Development

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update values
6. Run: `python app.py`

## 🌍 Deployment on Railway

1. Push code to GitHub
2. Connect repository to Railway
3. Add PostgreSQL database
4. Set environment variables in Railway dashboard
5. Auto-deploy on every push

## 📊 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Flask secret key |
| `DATABASE_URL` | Yes | PostgreSQL connection URL |
| `DEBUG_MODE` | No | Enable debug mode |
| `WEATHER_API_KEY` | No | External API key |
| `PAYMENT_API_KEY` | No | External API key |

## 🔗 Links
- [Deployed App](your-url)
- [GitHub Repository](your-repo)

## 👨‍💻 Author
[Oba Phillip]
[03/04/2026]