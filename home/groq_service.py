"""
Groq AI Service for WiseOwl
Handles AI conversations, quiz generation, and story narration
"""
import requests
import json
from django.conf import settings


class GroqAIService:
    """Service class for Groq AI integration"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.model = "llama-3.3-70b-versatile"  # Latest fast model
    
    def generate_scenes(self, topic, subject_type='history'):
        """Generate 3 educational scenes for a topic"""
        prompt = f"""You are WiseOwl, an educational AI guide. Create 3 DISTINCT progressive learning scenes for: {topic}

Subject: {subject_type}

IMPORTANT: Each scene must be COMPLETELY DIFFERENT with unique perspectives and details.

For each scene provide:
1. Scene title - Specific and descriptive (not generic)
2. Description - DETAILED 360° panoramic scene description (4-5 sentences) including:
   - Specific location/setting
   - What's in foreground, middle, and background
   - People/objects present
   - Lighting and atmosphere
   - Architectural or natural details
3. Educational narration - 4-5 paragraphs explaining:
   - What students are seeing
   - Historical/geographical significance
   - Interesting facts and details
   - Why this matters

Format as JSON:
{{
  "scenes": [
    {{
      "number": 1,
      "title": "Specific Scene Title",
      "description": "Detailed 360° panoramic description with foreground, middle ground, background, lighting, people, objects...",
      "narration": "Paragraph 1... Paragraph 2... Paragraph 3... Paragraph 4..."
    }},
    ...
  ]
}}

Make each scene VISUALLY DISTINCT and EDUCATIONALLY RICH. Think like a documentary filmmaker choosing 3 different camera positions."""

        try:
            # Retry logic for SSL issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json={
                            "model": self.model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 1500
                        },
                        timeout=45,
                        verify=True
                    )
                    break  # Success, exit retry loop
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise  # Last attempt, raise the error
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # Extract JSON from response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    return json.loads(content[start:end])
            
            return self._fallback_scenes(topic)
            
        except Exception as e:
            print(f"Groq API error: {str(e)}")
            return self._fallback_scenes(topic)
    
    def generate_quiz(self, topic, scene_description, scene_number=1):
        """Generate 2 unique quiz questions for a specific scene"""
        prompt = f"""Create 2 COMPLETELY UNIQUE multiple-choice questions ONLY about Scene {scene_number}:

Topic: {topic}
Scene {scene_number}: {scene_description}

CRITICAL RULES:
1. Questions MUST be about SPECIFIC details visible in THIS scene
2. Questions MUST be DIFFERENT from other scenes
3. Ask about what students SEE in this particular view
4. Reference specific objects, people, or features in the scene description
5. NO generic questions that could apply to any scene

Example good questions:
- "What architectural feature is visible in the foreground of this scene?"
- "Based on the lighting in this scene, what time of day is it?"
- "What activity are the people performing in this specific location?"

Format as JSON:
{{
  "questions": [
    {{
      "question": "Specific question about THIS scene only...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": 0,
      "explanation": "Explanation referencing specific scene details..."
    }},
    {{
      "question": "Another specific question about THIS scene only...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct": 1,
      "explanation": "Explanation referencing specific scene details..."
    }}
  ]
}}

Remember: Scene {scene_number} questions must be UNIQUE and SPECIFIC to this scene's description!"""

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.6,
                    "max_tokens": 800
                },
                timeout=20
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end > start:
                    return json.loads(content[start:end])
            
            return self._fallback_quiz(topic)
            
        except Exception as e:
            print(f"Groq quiz error: {str(e)}")
            return self._fallback_quiz(topic, scene_number)
    
    def owl_chat(self, user_message, context=""):
        """Owl responds to user questions"""
        
        # Build a clear, direct prompt
        if context:
            system_prompt = f"You are WiseOwl, a friendly and knowledgeable educational guide. The student is learning about: {context}. Answer their questions clearly and helpfully in 2-3 sentences."
        else:
            system_prompt = "You are WiseOwl, a friendly and knowledgeable educational guide. Answer student questions clearly and helpfully in 2-3 sentences."
        
        try:
            print(f"Owl Chat Request - Message: {user_message}, Context: {context}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 250
                },
                timeout=20
            )
            
            print(f"Groq API Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                answer = result['choices'][0]['message']['content'].strip()
                print(f"Owl Chat Response: {answer}")
                
                # Make sure we got a real answer
                if len(answer) > 10:
                    return answer
                else:
                    print("Response too short, using fallback")
                    return "I'm here to help you learn! What would you like to know?"
            else:
                print(f"API Error: {response.text}")
                return "I'm having trouble connecting right now. Please try again!"
            
        except requests.exceptions.Timeout:
            print("Owl chat timeout")
            return "I'm thinking too hard! Please try asking again."
        except Exception as e:
            print(f"Owl chat error: {str(e)}")
            import traceback
            traceback.print_exc()
            return "I'm having trouble right now. Please try again!"
    
    def _fallback_scenes(self, topic):
        """Fallback scenes if API fails - Rich detailed content"""
        return {
            "scenes": [
                {
                    "number": 1,
                    "title": f"Discovering {topic}",
                    "description": f"A detailed 360-degree panoramic view introducing {topic}. The scene shows the foundational elements in the foreground, with key features visible in the middle distance, and contextual environment in the background. Natural lighting illuminates the scene, creating depth and atmosphere.",
                    "narration": f"""Welcome to your immersive journey into {topic}!

**What You're Seeing:**
• In the foreground, you'll notice the primary elements that define {topic}
• The middle ground reveals the context and setting where this takes place
• The background shows the broader environment and atmosphere

**Why This Matters:**
This scene introduces you to the fundamental aspects of {topic}. Understanding these basics is crucial because they form the foundation for everything that follows. Take your time to observe the details - each element tells part of the story.

**Key Points to Notice:**
• The spatial arrangement and how elements relate to each other
• The scale and proportions that give you a sense of the real environment
• The atmospheric conditions that set the mood and context

This is just the beginning of your exploration. As you progress through the scenes, you'll gain deeper insights into the significance and impact of {topic}."""
                },
                {
                    "number": 2,
                    "title": f"Inside {topic}",
                    "description": f"An immersive ground-level 360-degree view placing you directly within {topic}. Close-up details are visible in the immediate foreground, with active elements and interactions in the middle ground, and the surrounding environment providing context in the background. Dynamic lighting creates visual interest.",
                    "narration": f"""Now you're standing right in the heart of {topic}!

**Your Perspective:**
• You're positioned at ground level, experiencing this from a human viewpoint
• Close-up details surround you, allowing you to see intricate features
• The environment extends in all directions, creating full immersion

**What Makes This Special:**
This scene reveals the inner workings and active elements of {topic}. You're no longer just observing from outside - you're experiencing it from within. This perspective helps you understand how different components interact and function together.

**Important Details:**
• Notice the textures, materials, and construction methods used
• Observe how people or elements move and interact in this space
• Pay attention to the functional aspects and practical applications

**Educational Insight:**
Understanding {topic} from this intimate perspective gives you appreciation for the complexity and ingenuity involved. The details you see here demonstrate the skill, knowledge, and effort that went into creating or maintaining this."""
                },
                {
                    "number": 3,
                    "title": f"Impact of {topic}",
                    "description": f"A wide-angle 360-degree panoramic view showing the lasting influence and legacy of {topic}. The foreground displays modern connections, the middle ground shows historical progression, and the background reveals the broader impact on society and culture. Dramatic lighting emphasizes the significance.",
                    "narration": f"""This final scene reveals how {topic} shaped our world!

**The Bigger Picture:**
• See how {topic} influenced development and progress over time
• Understand the connections between past innovations and present reality
• Recognize the lasting impact on society, culture, and technology

**Legacy and Influence:**
What you're witnessing here is the remarkable legacy of {topic}. The innovations, methods, and ideas developed here didn't just stay in one place or time - they spread, evolved, and influenced countless other developments. This is why studying {topic} matters today.

**Modern Connections:**
• Many modern systems and technologies trace their roots back to these concepts
• The principles demonstrated here are still relevant and applied today
• Understanding this history helps us appreciate current achievements

**Why This Matters to You:**
By completing this journey through {topic}, you've gained more than just historical knowledge. You've developed an understanding of how human ingenuity, problem-solving, and innovation work. These lessons apply to challenges we face today and will face in the future.

**Reflection:**
Take a moment to consider: How does understanding {topic} change your perspective? What connections can you make to your own life and the world around you? This kind of deep, immersive learning helps create lasting understanding that goes beyond memorizing facts."""
                }
            ]
        }
    
    def _fallback_quiz(self, topic, scene_number=1):
        """Fallback quiz if API fails - Unique questions per scene"""
        
        # Scene 1 questions - Introduction/Discovery
        if scene_number == 1:
            return {
                "questions": [
                    {
                        "question": f"Based on the introductory scene, what is the primary purpose of {topic}?",
                        "options": [
                            "A) To demonstrate foundational concepts and basic elements",
                            "B) To show only modern applications",
                            "C) To display unrelated historical artifacts",
                            "D) To focus solely on aesthetic design"
                        ],
                        "correct": 0,
                        "explanation": f"The first scene introduces the foundational elements of {topic}, helping you understand the basic concepts before diving deeper."
                    },
                    {
                        "question": "What perspective does this opening scene provide?",
                        "options": [
                            "A) An overview showing the context and setting",
                            "B) A microscopic close-up view",
                            "C) A view from inside looking out",
                            "D) A purely abstract representation"
                        ],
                        "correct": 0,
                        "explanation": "The introductory scene provides an overview perspective, allowing you to see the broader context before exploring details."
                    }
                ]
            }
        
        # Scene 2 questions - Inside/Details
        elif scene_number == 2:
            return {
                "questions": [
                    {
                        "question": f"In this immersive scene, what can you observe about the inner workings of {topic}?",
                        "options": [
                            "A) Detailed components and how they interact with each other",
                            "B) Only the external appearance",
                            "C) Nothing specific or detailed",
                            "D) Just the surrounding landscape"
                        ],
                        "correct": 0,
                        "explanation": f"This scene places you inside {topic}, revealing the intricate details and interactions between components."
                    },
                    {
                        "question": "What makes this ground-level perspective valuable for learning?",
                        "options": [
                            "A) It shows textures, materials, and functional details up close",
                            "B) It only provides a distant view",
                            "C) It hides important information",
                            "D) It shows nothing new compared to the first scene"
                        ],
                        "correct": 0,
                        "explanation": "The ground-level perspective lets you see textures, materials, and functional details that aren't visible from a distance."
                    }
                ]
            }
        
        # Scene 3 questions - Impact/Legacy
        else:
            return {
                "questions": [
                    {
                        "question": f"How does this final scene demonstrate the lasting impact of {topic}?",
                        "options": [
                            "A) By showing connections between historical innovations and modern applications",
                            "B) By only displaying ancient artifacts",
                            "C) By ignoring any modern relevance",
                            "D) By focusing solely on aesthetic beauty"
                        ],
                        "correct": 0,
                        "explanation": f"The final scene reveals how {topic} influenced modern developments, showing the lasting legacy and continued relevance."
                    },
                    {
                        "question": "What is the main lesson from completing this three-scene journey?",
                        "options": [
                            "A) Understanding how innovation and problem-solving create lasting impact",
                            "B) Memorizing dates and names",
                            "C) Learning that history has no connection to today",
                            "D) Recognizing that old methods are obsolete"
                        ],
                        "correct": 0,
                        "explanation": "The journey teaches you how human ingenuity and innovation create solutions that influence future generations."
                    }
                ]
            }

