# Speech Clarity Enhancement System - Production Version

A complete, production-ready AI-powered speech clarity enhancement system with authentication, usage limits, subscriptions, and database integration.

## 🚀 Features

### Core AI Functionality (Preserved)
- **Speech Enhancement Model**: Custom Conv1dAutoEncoder trained on stuttered/clear speech pairs
- **ASR Pipeline**: OpenAI Whisper for speech-to-text conversion
- **Text Cleaning**: Rule-based algorithm to remove fillers and repetitions
- **TTS Engine**: Text-to-speech synthesis for enhanced audio output
- **Fluency Metrics**: Before/after analysis with improvement scoring

### New Production Features
- **User Authentication**: JWT-based login/registration system
- **Usage Limits**: 10 free uses for normal users, unlimited for premium
- **Subscription Management**: Free, Monthly Premium, Yearly Premium plans
- **User Dashboard**: Statistics, recent activity, usage tracking
- **Processing History**: Complete audit trail with search and filtering
- **Admin Panel**: User management, system statistics, usage controls
- **Database Integration**: MySQL with comprehensive data models
- **Role-Based Access**: Normal, Premium, and Admin user roles

## 🏗️ Architecture

### Backend (FastAPI + MySQL)
```
backend/
├── app/
│   ├── main.py              # Main FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # Authentication system
│   ├── usage_limits.py      # Usage tracking and limits
│   ├── schemas.py           # Pydantic schemas
│   ├── pipeline.py          # AI processing pipeline (preserved)
│   ├── routers/             # API route modules
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── dashboard.py     # Dashboard data
│   │   ├── history.py       # Processing history
│   │   └── admin.py         # Admin panel
│   └── ...
├── models/                  # Trained AI models
├── media/                   # Audio file storage
├── requirements.txt         # Python dependencies
└── init_database.py         # Database setup script
```

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── App.tsx              # Main application with routing
│   ├── contexts/
│   │   └── AuthContext.tsx  # Authentication context
│   ├── components/
│   │   ├── Layout.tsx       # Main layout with navigation
│   │   ├── ProtectedRoute.tsx # Route protection
│   │   └── Waveform.tsx     # Audio visualization (preserved)
│   ├── pages/
│   │   ├── LoginPage.tsx    # User login
│   │   ├── RegisterPage.tsx # User registration
│   │   ├── DashboardPage.tsx # User dashboard
│   │   ├── ProcessAudioPage.tsx # Audio processing (enhanced)
│   │   ├── HistoryPage.tsx  # Processing history
│   │   ├── SubscriptionPage.tsx # Subscription management
│   │   ├── ProfilePage.tsx  # User profile
│   │   └── AdminPage.tsx    # Admin panel
│   ├── utils/
│   │   └── api.ts           # API client with authentication
│   └── ...
├── package.json
└── ...
```

### Database Schema
```sql
-- Core tables
users                 # User accounts and authentication
usage_logs           # Usage tracking and limits
subscriptions        # Premium plan management
audio_history        # Processing results and files
fluency_scores       # Before/after metrics
user_sessions        # JWT token management
system_settings      # Admin configuration
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Git

### 1. Clone Repository
```bash
git clone <repository-url>
cd speech-clarity-enhancement
```

### 2. Database Setup
```bash
# Start MySQL server
# Create database (or use init script)
mysql -u root -p
CREATE DATABASE AI_Speech;
exit
```

### 3. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_database.py

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 6. Default Admin Credentials
- **Email**: admin@speechclarity.com
- **Password**: admin123

## 📊 Database Schema Details

### Users Table
```sql
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('normal', 'premium', 'admin') DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE
);
```

### Usage Tracking
```sql
CREATE TABLE usage_logs (
    usage_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    total_uses INT DEFAULT 0,
    remaining_uses INT DEFAULT 10,
    last_used_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Subscription Management
```sql
CREATE TABLE subscriptions (
    subscription_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    plan_type ENUM('free', 'monthly_premium', 'yearly_premium'),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    amount DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 🔐 Authentication System

### JWT Token Flow
1. User logs in with email/password
2. Server validates credentials and creates JWT token
3. Token stored in localStorage and sent with API requests
4. Server validates token and extracts user information
5. Protected routes require valid authentication

### Role-Based Access Control
- **Normal Users**: 10 free speech enhancements
- **Premium Users**: Unlimited usage, priority processing
- **Admin Users**: Full system access, user management

## 💳 Subscription System

### Plans Available
- **Free Plan**: 10 total enhancements, basic features
- **Monthly Premium**: $9.99/month, unlimited usage
- **Yearly Premium**: $99.99/year, unlimited usage + savings

### Simulated Payment
⚠️ **Important**: This is a simulated payment system for academic purposes only. No real payments are processed.

## 🎯 Usage Limits

### Free Users
- Limited to 10 total speech enhancements
- Usage counter decrements with each processing
- Upgrade prompt when limit approached

### Premium Users
- Unlimited speech enhancements
- Priority processing queue
- Advanced analytics and history

## 📈 Admin Features

### User Management
- View all users with filtering and search
- Upgrade users to premium
- Reset usage limits
- Deactivate accounts

### System Statistics
- Total users and conversion rates
- Usage analytics and trends
- Revenue tracking (simulated)
- System performance metrics

### Settings Management
- Configure system parameters
- Update pricing and limits
- Maintenance mode control

## 🔧 API Endpoints

### Authentication
```
POST /auth/register     # User registration
POST /auth/login        # User login
POST /auth/logout       # User logout
GET  /auth/me          # Get current user
POST /auth/change-password # Change password
```

### Audio Processing
```
POST /enhance-speech    # Process audio (protected)
GET  /download/{filename} # Download enhanced audio
```

### User Management
```
GET  /users/profile     # Get user profile
PUT  /users/profile     # Update profile
GET  /users/usage       # Get usage information
GET  /users/subscription # Get subscription info
POST /users/subscription # Create subscription
```

### Dashboard & History
```
GET  /dashboard/overview # Dashboard data
GET  /history           # Processing history
GET  /history/{id}      # Specific audio details
DELETE /history/{id}    # Delete audio record
```

### Admin (Admin Only)
```
GET  /admin/users       # All users
GET  /admin/statistics  # System stats
PUT  /admin/users/{id}  # Update user
POST /admin/users/{id}/upgrade # Upgrade user
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
# Run with test database
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Manual Testing Scenarios
1. **User Registration/Login Flow**
2. **Audio Processing with Usage Limits**
3. **Subscription Upgrade Process**
4. **Admin User Management**
5. **Processing History and Downloads**

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Use proper secrets management
2. **Database**: Configure production MySQL with backups
3. **File Storage**: Use cloud storage (AWS S3, etc.)
4. **Authentication**: Implement email verification
5. **Payment**: Integrate real payment processor (Stripe, etc.)
6. **Monitoring**: Add logging and error tracking
7. **SSL/HTTPS**: Enable secure connections
8. **Rate Limiting**: Implement API rate limits

### Docker Deployment (Optional)
```dockerfile
# Example Dockerfile for backend
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📝 Academic Notes

### For MCA Project Evaluation
- **Complete System**: Full-stack application with database
- **AI Integration**: Preserved original ML models and pipeline
- **Production Features**: Authentication, subscriptions, admin panel
- **Clean Architecture**: Modular, maintainable code structure
- **Documentation**: Comprehensive setup and usage guides
- **Scalability**: Designed for production deployment

### Key Learning Outcomes
1. **Full-Stack Development**: React + FastAPI integration
2. **Database Design**: Relational schema with proper relationships
3. **Authentication Systems**: JWT-based security implementation
4. **Business Logic**: Usage limits and subscription management
5. **API Design**: RESTful endpoints with proper error handling
6. **User Experience**: Professional UI with role-based access

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is for academic purposes. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Check database logs and connection
4. Verify all dependencies are installed

---

**Note**: This is an academic project demonstrating a production-ready speech enhancement system with complete user management, authentication, and subscription features.