# 🦉 WiseOwl - Immersive 360° Learning Platform

> Transform education into immersive time-travel experiences


## 💡 The Problem

- Students forget **90% of textbook content** within a week
- Traditional learning is passive, boring, and ineffective
- Visual learners struggle with text-heavy education
- No engagement = No retention

## 🚀 Our Solution

**WiseOwl transforms education into immersive 360° time-travel experiences.**

Students don't just READ about history - they **STEP INSIDE** it.

## ✨ Features

### 🌍 360° Immersive Scenes
- Full panoramic views students can explore
- Interactive controls (zoom, rotate, pan)
- Feel like you're actually THERE

### 🤖 AI-Generated Content
- **Groq AI** (Llama 3.3 70B) creates unique educational narratives
- **Bria FIBO API** generates photorealistic 360° images
- Works for ANY topic - unlimited possibilities

### 🎮 Progressive Learning System
- 3 scenes per topic (beginner → intermediate → advanced)
- Take quizzes to unlock next scenes
- Gamified learning keeps students engaged

### 🎨 Student Customization
- Add your own ideas to scenes
- Choose camera angles, lighting, colors
- Make learning personal and creative

### 💬 AI Owl Guide
- Chat with WiseOwl for help
- Context-aware responses
- Friendly, encouraging learning companion

### 🏆 Achievement System
- Track progress with stats dashboard
- Earn points for correct answers
- Get completion certificates

## 🛠️ Technology Stack

- **AI Content:** Groq (Llama 3.3 70B)
- **360° Images:** Bria FIBO API
- **Backend:** Django 5.2 (Python 3.11)
- **Frontend:** HTML5, CSS3, JavaScript
- **3D Viewer:** Pannellum.js
- **Database:** SQLite (dev) / PostgreSQL (prod)

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd fibo
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GROQ_API_KEY=your_groq_key
# - BRIA_API_KEY=your_bria_key
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Start the server**
```bash
python manage.py runserver
```

7. **Open in browser**
```
http://localhost:8000
```

## 🎯 Quick Start

### Try Demo Journeys (Instant)
1. Visit home page
2. Click **"Ancient Rome"** or **"Amazon Rainforest"**
3. Explore pre-written educational content
4. Click **"Generate 360° Scene"** to create immersive view

### Create Custom Journey
1. Choose **History** or **Geography**
2. Enter your topic (e.g., "World War II", "Grand Canyon")
3. Wait 30-60 seconds for AI generation
4. Explore your custom 3-scene journey!

## 📚 Usage

### For Students
- Explore immersive 360° scenes
- Take quizzes to unlock new content
- Customize scenes with your ideas
- Chat with WiseOwl for help
- Earn certificates

### For Teachers
- Track student progress
- View completion statistics
- Assign topics for exploration
- Monitor quiz scores

## 🎓 Educational Impact

**Students retain 65% more information with visual learning**

- **Engagement:** Students WANT to learn
- **Retention:** They REMEMBER what they see
- **Accessibility:** Works for all learning styles
- **Scalability:** Any subject, any topic, any level

## 🏗️ Project Structure

```
fibo/
├── home/                   # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── groq_service.py    # Groq AI integration
│   ├── bria_service.py    # Bria FIBO integration
│   └── urls.py            # URL routing
├── templates/             # HTML templates
│   └── home/
│       ├── home.html      # Home page
│       ├── journey.html   # 360° viewer
│       ├── quiz.html      # Quiz interface
│       └── certificate.html # Completion certificate
├── static/                # Static files
│   └── css/
│       └── fibo.css       # Styles
├── fibo/                  # Django project settings
├── manage.py              # Django management
└── requirements.txt       # Python dependencies
```

## 🔑 API Keys

### Groq API
Get your key at: https://console.groq.com/keys

### Bria FIBO API
Get your key at: https://bria.ai/

Add to `.env`:
```
GROQ_API_KEY=your_groq_api_key_here
BRIA_API_KEY=your_bria_api_key_here
```

## 🚀 Future Enhancements

- VR headset support
- Multi-language content
- Teacher dashboards
- Classroom collaboration
- Voice narration
- Mobile app
- Offline mode


---

**Made with ❤️ for the future of education** 🦉✨
