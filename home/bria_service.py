"""
Bria FIBO Integration Service
Handles all API calls to Bria Translator and Generator
"""
import requests
import json
from django.conf import settings


class BriaFIBOService:
    """Service class for Bria FIBO API integration"""
    
    def __init__(self):
        self.translator_url = "https://engine.prod.bria-api.com/v2/structured_prompt/generate"
        self.generator_url = "https://engine.prod.bria-api.com/v2/image/generate"
        self.api_key = settings.BRIA_API_KEY
        self.headers = {
            'api_token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def translate_to_scene(self, text, mode='single'):
        """
        Convert natural language text to structured JSON scene using Bria API
        
        Args:
            text: User's topic/description
            mode: Generation mode (single, timeline, map, quiz, storyboard)
        
        Returns:
            dict: JSON scene with FIBO parameters
        """
        try:
            # Build educational prompt based on mode
            educational_prompt = self._build_educational_prompt(text, mode)
            
            payload = {
                'prompt': educational_prompt,
                'sync': True  # Wait for response
            }
            
            # Retry logic for SSL issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.translator_url,
                        headers=self.headers,
                        json=payload,
                        timeout=60
                    )
                    break
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                    print(f"Translator attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    import time
                    time.sleep(2)
            
            print(f"Translator API Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                structured_prompt = result.get('result', {}).get('structured_prompt', '{}')
                return {
                    'status': 'success',
                    'scene': json.loads(structured_prompt) if isinstance(structured_prompt, str) else structured_prompt
                }
            else:
                print(f"API Error: {response.text}")
                return self._create_mock_scene(text, mode)
                
        except Exception as e:
            print(f"Translator API error: {str(e)}")
            return self._create_mock_scene(text, mode)
    
    def generate_image(self, json_scene, prompt):
        """
        Generate image from JSON scene using Bria API
        
        Args:
            json_scene: Structured JSON scene from translator
            prompt: Original text prompt
        
        Returns:
            dict: Response with image_url
        """
        try:
            # Convert JSON scene to string if needed
            structured_prompt_str = json.dumps(json_scene) if isinstance(json_scene, dict) else json_scene
            
            payload = {
                'prompt': prompt,
                'structured_prompt': structured_prompt_str,
                'aspect_ratio': '16:9',
                'steps_num': 50,
                'guidance_scale': 5,
                'sync': True  # Wait for response
            }
            
            # Retry logic for SSL issues
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        self.generator_url,
                        headers=self.headers,
                        json=payload,
                        timeout=120
                    )
                    break
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError) as e:
                    print(f"Generator attempt {attempt + 1} failed: {str(e)}")
                    if attempt == max_retries - 1:
                        raise
                    import time
                    time.sleep(2)
            
            print(f"Generator API Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                image_url = result.get('result', {}).get('image_url')
                if image_url:
                    return {
                        'status': 'success',
                        'image_url': image_url
                    }
            
            print(f"API Error: {response.text}")
            return {
                'status': 'error',
                'message': f'Generator API returned {response.status_code}'
            }
                
        except Exception as e:
            print(f"Generator API error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _build_educational_prompt(self, text, mode):
        """Build an educational prompt for the topic with enhanced 360° depth"""
        # Enhanced immersive prompt for true 360° panoramic experience
        immersive_base = "Create a full 360-degree equirectangular panoramic scene, ultra-wide spherical view, complete immersive environment with rich depth"
        
        # Add depth and detail instructions
        depth_instructions = "Include detailed foreground elements (2-5 meters away), middle ground features (10-30 meters), and distant background (50+ meters). Add atmospheric perspective with depth haze. Multiple layers of visual interest at different distances."
        
        if mode == 'timeline':
            return f"{immersive_base}. {depth_instructions} Historical scene showing {text}. Photorealistic environment where a student feels transported to that era. Include period-accurate architecture in foreground, people in authentic clothing at various distances, atmospheric lighting with natural shadows. Rich historical details at multiple depth levels. Educational and meticulously accurate."
        elif mode == 'map':
            return f"{immersive_base}. {depth_instructions} Bird's eye view geographical visualization of {text}. Show terrain with elevation changes, mountains in distance, rivers winding through landscape, cities with visible buildings, climate zones with vegetation. Multiple layers of geographical features from close to far. Educational with clear landmarks at various scales."
        elif mode == 'quiz':
            return f"Create an educational illustration for {text}. Clean, labeled diagram style with depth. Show key components at different distances with visual hints. Multiple layers of information. Perfect for students to learn and identify parts in 3D space."
        elif mode == 'storyboard':
            return f"{immersive_base}. {depth_instructions} Scene depicting {text} as if you are standing there. Ultra-wide angle with objects at varying distances, detailed environment with foreground, middle, and background elements, atmospheric depth, engaging composition. Educational visualization with spatial depth for students."
        else:  # single
            return f"{immersive_base}. {depth_instructions} Immersive educational scene of {text}. Full 360-degree spherical panorama as if student is standing in the center of the scene. Rich detail at multiple distances - close objects, medium distance features, far background. Atmospheric perspective, natural lighting, photorealistic. Make the student feel completely immersed with explorable depth in all directions."
    
    def _create_mock_scene(self, text, mode='single'):
        """
        Create a mock JSON scene for development/fallback
        """
        base_scene = {
            'topic': text,
            'mode': mode,
            'camera': {
                'angle': 45,
                'fov': 60,
                'tilt': 0,
                'pan': 0
            },
            'lighting': {
                'type': 'natural',
                'intensity': 0.8,
                'direction': 'top-left',
                'ambient': 0.3
            },
            'color_palette': {
                'primary': '#1A2A52',
                'secondary': '#E4C77F',
                'accent': '#F8F9FC',
                'mood': 'educational'
            },
            'composition': {
                'layout': 'centered',
                'depth': 'medium',
                'perspective': 'isometric'
            },
            'objects': [
                {
                    'type': 'main_subject',
                    'description': text,
                    'position': 'center',
                    'scale': 1.0
                }
            ],
            'style': {
                'type': 'educational',
                'detail_level': 'high',
                'realism': 0.7
            }
        }
        
        # Mode-specific adjustments
        if mode == 'timeline':
            base_scene['timeline'] = {
                'stages': 5,
                'progression': 'left-to-right'
            }
        elif mode == 'map':
            base_scene['map'] = {
                'projection': '3d',
                'terrain': True,
                'labels': True
            }
        elif mode == 'quiz':
            base_scene['quiz'] = {
                'hint_level': 'medium',
                'reveal_percentage': 0.6
            }
        elif mode == 'storyboard':
            base_scene['storyboard'] = {
                'panels': 4,
                'layout': 'grid'
            }
        
        return {
            'status': 'success',
            'scene': base_scene
        }

