# FIBO — Visual Learning App

## 🎯 What's Built

A complete AI-powered visual learning platform for History + Geography topics.

### ✅ Completed Features

1. **Landing Page** - Simple username login (no password needed)
2. **Home Page** - Clean interface to enter topics
3. **Generate Flow** - AI mock generator for topics
4. **Result Page** - Beautiful display of generated content
5. **Database** - Topic storage with user relationships

## 🎨 Design System

- **Primary Color**: Navy Blue (#1A2A52)
- **Background**: Soft White (#F8F9FC)
- **Accent**: Gold (#E4C77F)
- **Text**: Dark (#0D1B2A)

## 📁 File Structure

```
fibo/
├── home/
│   ├── models.py          # User + Topic models
│   ├── views.py           # All views (landing, home, generate, result)
│   ├── urls.py            # URL routing
│   └── auth_views.py      # Simple login
├── templates/
│   └── home/
│       ├── landing.html   # Login page
│       ├── home.html      # Main FIBO interface
│       └── result.html    # Topic result display
├── static/
│   ├── logo.svg           # FIBO logo (replace with your PNG)
│   └── css/
│       ├── style.css      # Landing page styles
│       └── fibo.css       # FIBO app styles
```

## 🚀 How to Use

1. **Login**: Enter any username (3+ characters)
2. **Home**: Enter a topic (e.g., "World War II", "Mount Everest")
3. **Generate**: Click "Generate Visualization"
4. **View**: See the AI-generated summary, story, diagram, and facts

## 🔧 URLs

- `/` - Landing page (login)
- `/home/` - Main FIBO interface
- `/generate/` - Process topic generation
- `/topic/<id>/` - View generated topic
- `/auth/logout/` - Logout

## 📊 Data Structure

Each topic includes:
- **topic**: The subject entered
- **summary**: Overview text
- **visual_story**: Creative narrative explanation
- **diagram**: Concept diagram description
- **difficulty**: easy | medium | hard
- **topic_type**: educational | historical | geographical
- **created_at**: Timestamp

## 🎨 Customization

### Replace Logo
1. Add your `logo.png` to `static/` folder
2. Update templates to use `logo.png` instead of `logo.svg`

### Replace Favicon
1. Add your `favicon.ico` to `static/` folder

### Connect Real AI
Replace the mock generator in `views.py` > `generate_visualization()` with:
- OpenAI API
- Anthropic Claude
- Google Gemini
- Or any other AI service

## 🏆 Hackathon Ready

- ✅ Clean, professional design
- ✅ Fast and responsive
- ✅ No complex auth setup
- ✅ Easy to demo
- ✅ Scalable architecture

## 🔮 Future Enhancements

- Real AI integration
- Image generation for diagrams
- Export to PDF
- Share topics with others
- Topic history and favorites
- Advanced filtering

---

**Built for hackathon success! 🚀**
