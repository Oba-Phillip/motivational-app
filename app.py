from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import random
import os
import sys
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ============================================
# REQUIREMENT 2: ENVIRONMENT CONFIGURATION
# NO HARDCODED VALUES - ALL FROM ENVIRONMENT
# ============================================

# ALL configuration from environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Check for required SECRET_KEY in production
if not SECRET_KEY:
    if os.environ.get('DEBUG_MODE', 'False').lower() == 'true':
        SECRET_KEY = 'dev-key-for-local-only'
        print("⚠️ WARNING: Using development SECRET_KEY")
    else:
        raise ValueError("SECRET_KEY environment variable not set in production!")

# Fix Railway's postgres:// vs postgresql:// (only if DATABASE_URL exists)
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Configure database (only if DATABASE_URL is provided)
if DATABASE_URL:
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    DATABASE_ENABLED = True
    print("✅ Database configured")
else:
    DATABASE_ENABLED = False
    db = None
    print("⚠️ Running without database (add PostgreSQL on Railway)")

app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'

# API Keys from environment (optional)
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
PAYMENT_API_KEY = os.environ.get('PAYMENT_API_KEY')

# Motivational messages (these are not secrets, safe to hardcode)
MESSAGES = [
    "you can make it 💪",
    "great things are coming your way 🌟",
    "keep pushing forward 🚀",
    "you are stronger than you think 🔥",
    "success is within your reach 🎯",
    "believe in yourself ✨",
    "today is your day 🌈",
    "you are amazing just as you are 💫",
    "every step counts 🦶",
    "you've got this! 💯"
]

# ============================================
# REQUIREMENT 3: DATABASE INTEGRATION
# ============================================

if DATABASE_ENABLED:
    class UserMessage(db.Model):
        __tablename__ = 'user_messages'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), nullable=False)
        message = db.Column(db.String(500), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'message': self.message,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    class UserFeedback(db.Model):
        __tablename__ = 'user_feedback'
        
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(100), nullable=False)
        feedback = db.Column(db.String(500), nullable=False)
        rating = db.Column(db.Integer, default=5)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'username': self.username,
                'feedback': self.feedback,
                'rating': self.rating,
                'created_at': self.created_at.isoformat() if self.created_at else None
            }
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
else:
    class UserMessage:
        pass
    class UserFeedback:
        pass

# ============================================
# ROUTES
# ============================================

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    username = ""
    saved_messages_count = 0
    
    if request.method == "POST":
        username = request.form.get("username", "")
        message = random.choice(MESSAGES)
        result = f"✨ Hello {username}, {message} ✨"
        
        if DATABASE_ENABLED and username:
            try:
                user_msg = UserMessage(username=username, message=message)
                db.session.add(user_msg)
                db.session.commit()
                print(f"✅ Saved message for {username}")
            except Exception as e:
                print(f"Error saving to database: {e}")
                db.session.rollback()
    
    if DATABASE_ENABLED:
        saved_messages_count = UserMessage.query.count()
    
    return render_template("index.html", 
                         result=result, 
                         username=username,
                         saved_count=saved_messages_count,
                         db_enabled=DATABASE_ENABLED,
                         debug_mode=app.config['DEBUG'])

# ============================================
# TEST ENDPOINTS
# ============================================

@app.route("/simple")
def simple():
    return "App is running on Railway!"

@app.route("/ping")
def ping():
    return jsonify({"status": "alive", "timestamp": datetime.utcnow().isoformat()})

# ============================================
# CRUD API ENDPOINTS
# ============================================

@app.route("/api/messages", methods=["POST"])
def create_message():
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not configured'}), 503
    
    data = request.json
    if not data or not data.get('username') or not data.get('message'):
        return jsonify({'error': 'Username and message required'}), 400
    
    user_msg = UserMessage(
        username=data['username'],
        message=data['message']
    )
    db.session.add(user_msg)
    db.session.commit()
    return jsonify(user_msg.to_dict()), 201

@app.route("/api/messages", methods=["GET"])
def get_messages():
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not configured'}), 503
    
    messages = UserMessage.query.order_by(UserMessage.created_at.desc()).limit(50).all()
    return jsonify([m.to_dict() for m in messages])

@app.route("/api/messages/<username>", methods=["GET"])
def get_user_messages(username):
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not configured'}), 503
    
    messages = UserMessage.query.filter_by(username=username).order_by(UserMessage.created_at.desc()).all()
    return jsonify([m.to_dict() for m in messages])

@app.route("/api/messages/<int:message_id>/feedback", methods=["PUT"])
def add_feedback(message_id):
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not configured'}), 503
    
    message = UserMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    data = request.json
    feedback = UserFeedback(
        username=message.username,
        feedback=data.get('feedback', ''),
        rating=data.get('rating', 5)
    )
    db.session.add(feedback)
    db.session.commit()
    return jsonify(feedback.to_dict())

@app.route("/api/messages/<int:message_id>", methods=["DELETE"])
def delete_message(message_id):
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not configured'}), 503
    
    message = UserMessage.query.get(message_id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Message deleted successfully'})

# ============================================
# SECURITY HEADERS
# ============================================

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# ============================================
# MONITORING & HEALTH CHECKS
# ============================================

@app.route('/health')
def health_check():
    db_status = 'not_configured'
    if DATABASE_ENABLED:
        try:
            db.session.execute('SELECT 1')
            db_status = 'connected'
        except Exception as e:
            db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'environment': {
            'database_url': '✅ set' if DATABASE_URL else '❌ missing',
            'secret_key': '✅ set' if app.config['SECRET_KEY'] else '❌ missing',
            'weather_api': '✅ set' if WEATHER_API_KEY else '⚠️ optional',
            'payment_api': '✅ set' if PAYMENT_API_KEY else '⚠️ optional',
            'debug_mode': app.config['DEBUG'],
            'database_enabled': DATABASE_ENABLED
        },
        'app_stats': {
            'total_messages': UserMessage.query.count() if DATABASE_ENABLED else 0,
            'total_feedback': UserFeedback.query.count() if DATABASE_ENABLED else 0
        }
    })

# ============================================
# INTENTIONAL ERROR FOR DEBUGGING
# ============================================

@app.route('/demo-error')
def demo_error():
    try:
        result = 10 / 0
        return jsonify({'result': result})
    except ZeroDivisionError as e:
        app.logger.error(f"Demo error triggered: {str(e)}")
        return jsonify({'error': 'Demo error occurred', 'message': 'Check Railway logs for debugging'}), 500

# ============================================
# CI/CD STATUS ENDPOINT
# ============================================

@app.route('/deploy-info')
def deploy_info():
    return jsonify({
        'app_name': 'Motivational Message App',
        'version': '2.0.0',
        'deployment_platform': 'Railway',
        'auto_deploy_enabled': True,
        'ci_cd': 'GitHub → Railway auto-deploy on push',
        'last_deploy': datetime.utcnow().isoformat()
    })

# ============================================
# SCALABILITY INFO ENDPOINT
# ============================================

@app.route('/scalability-info')
def scalability_info():
    return jsonify({
        'current_config': {
            'database_enabled': DATABASE_ENABLED,
            'debug_mode': app.config['DEBUG']
        },
        'scaling_recommendations': {
            'low_traffic': 'Single instance, basic PostgreSQL',
            'medium_traffic': '2-3 instances, add Redis cache, read replicas',
            'high_traffic': '5+ instances, CDN, queue workers, connection pooling'
        },
        'estimated_costs': {
            '100_requests_per_day': '$5-10/month',
            '10k_requests_per_day': '$50-100/month',
            '100k_requests_per_day': '$300-500/month'
        },
        'railway_pricing': 'Usage-based: CPU time + RAM + bandwidth'
    })

# ============================================
# UTILITY ENDPOINTS
# ============================================

@app.route('/motivational-messages')
def get_messages_list():
    return jsonify({
        'messages': MESSAGES,
        'count': len(MESSAGES)
    })

@app.route('/stats')
def get_stats():
    if not DATABASE_ENABLED:
        return jsonify({'error': 'Database not enabled'}), 503
    
    stats = {
        'total_messages': UserMessage.query.count(),
        'unique_users': db.session.query(UserMessage.username).distinct().count(),
        'total_feedback': UserFeedback.query.count(),
        'average_rating': db.session.query(db.func.avg(UserFeedback.rating)).scalar() or 0
    }
    return jsonify(stats)

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# MAIN - NO HARDCODED VALUES!
# ============================================

if __name__ == "__main__":
    # NO HARDCODED PORT - reads from environment
    port = int(os.environ.get("PORT", 5000))
    
    print("=" * 50)
    print("🚀 Motivational Message App Starting...")
    print("=" * 50)
    print(f"📡 Port: {port} (from environment variable)")
    print(f"🗄️  Database: {'Connected' if DATABASE_ENABLED else 'Not configured'}")
    print(f"🔐 Secret Key: {'Set' if app.config['SECRET_KEY'] else 'Missing'}")
    print(f"🐛 Debug Mode: {app.config['DEBUG']}")
    
    if DATABASE_ENABLED:
        try:
            with app.app_context():
                message_count = UserMessage.query.count()
                print(f"📊 Total Messages: {message_count}")
        except Exception as e:
            print(f"📊 Total Messages: Unable to count")
    else:
        print(f"📊 Total Messages: 0 (database not configured)")
    
    print("=" * 50)
    print("✅ App is ready!")
    print(f"📍 Local URL: http://localhost:{port}")
    print("=" * 50)
    
    # NO HARDCODED PORT HERE EITHER
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
