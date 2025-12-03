from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from home.models import Topic, Scene
from home.bria_service import BriaFIBOService
from home.groq_service import GroqAIService
import json


def landing(request):
    """Landing page - redirect to home if authenticated"""
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/landing.html')


@login_required
def home(request):
    """WiseOwl home page with owl guide"""
    recent_topics = request.user.topics.all()[:5]
    
    # Calculate stats
    all_topics = request.user.topics.all()
    total_scenes = sum(len(topic.scenes_unlocked) for topic in all_topics)
    total_score = sum(topic.total_score for topic in all_topics)
    completed = all_topics.filter(completed=True).count()
    
    stats = {
        'total_topics': all_topics.count(),
        'total_scenes': total_scenes,
        'total_score': total_score,
        'completed': completed
    }
    
    return render(request, 'home/home.html', {
        'user': request.user,
        'recent_topics': recent_topics,
        'stats': stats
    })


@login_required
def generate_journey(request):
    """Generate 3-scene educational journey"""
    if request.method == 'POST':
        topic_text = request.POST.get('topic', '').strip()
        subject_type = request.POST.get('subject_type', 'history')
        
        if not topic_text:
            messages.error(request, 'Please enter a topic')
            return redirect('home:home')
        
        try:
            # Initialize services
            groq = GroqAIService()
            bria = BriaFIBOService()
            
            # Generate 3 scenes with Groq
            print(f"Generating scenes for: {topic_text}")
            scenes_data = groq.generate_scenes(topic_text, subject_type)
            
            # Create topic
            topic = Topic.objects.create(
                user=request.user,
                topic=topic_text,
                subject_type=subject_type,
                scenes_data=scenes_data,
                scenes_unlocked=[1],  # Scene 1 always unlocked
                current_scene=1
            )
            
            # Generate Scene 1 image immediately
            scene_info = scenes_data['scenes'][0]
            scene_result = bria.translate_to_scene(scene_info['description'], 'single')
            json_scene = scene_result.get('scene', {})
            
            image_result = bria.generate_image(json_scene, scene_info['description'])
            image_url = image_result.get('image_url') if image_result.get('status') == 'success' else None
            
            # Generate quiz for Scene 1
            quiz_data = groq.generate_quiz(topic_text, scene_info['description'], scene_number=1)
            
            # Create Scene 1
            Scene.objects.create(
                topic=topic,
                scene_number=1,
                title=scene_info['title'],
                description=scene_info['description'],
                narration=scene_info['narration'],
                json_scene=json_scene,
                image_url=image_url,
                quiz_data=quiz_data,
                generation_status='completed' if image_url else 'pending'
            )
            
            messages.success(request, f'Journey created! Scene 1 is ready.')
            return redirect('home:journey', topic_id=topic.id)
            
        except Exception as e:
            print(f"Error generating journey: {str(e)}")
            messages.error(request, f'Error: {str(e)}')
            return redirect('home:home')
    
    return redirect('home:home')


@login_required
def journey_view(request, topic_id):
    """View the 3-scene journey"""
    topic = get_object_or_404(Topic, id=topic_id, user=request.user)
    scenes = topic.scenes.all()
    current_scene = scenes.filter(scene_number=topic.current_scene).first()
    
    return render(request, 'home/journey.html', {
        'topic': topic,
        'scenes': scenes,
        'current_scene': current_scene,
        'json_scene': json.dumps(current_scene.json_scene, indent=2) if current_scene and current_scene.json_scene else '{}'
    })


@login_required
def quiz_view(request, topic_id, scene_number):
    """Quiz for a specific scene"""
    topic = get_object_or_404(Topic, id=topic_id, user=request.user)
    scene = get_object_or_404(Scene, topic=topic, scene_number=scene_number)
    
    return render(request, 'home/quiz.html', {
        'topic': topic,
        'scene': scene,
        'quiz_data': scene.quiz_data
    })


@login_required
@require_POST
def submit_quiz(request, topic_id, scene_number):
    """Submit quiz answers and unlock next scene"""
    topic = get_object_or_404(Topic, id=topic_id, user=request.user)
    scene = get_object_or_404(Scene, topic=topic, scene_number=scene_number)
    
    try:
        data = json.loads(request.body)
        answers = data.get('answers', [])
        
        # Calculate score
        correct = 0
        quiz_questions = scene.quiz_data.get('questions', [])
        for i, answer in enumerate(answers):
            if i < len(quiz_questions) and answer == quiz_questions[i]['correct']:
                correct += 1
        
        # Update topic score
        topic.quiz_scores[f'scene_{scene_number}'] = correct
        topic.total_score += correct * 10
        
        # Unlock next scene if score is good enough
        if correct >= 1 and scene_number < 3:
            next_scene_num = scene_number + 1
            if next_scene_num not in topic.scenes_unlocked:
                topic.scenes_unlocked.append(next_scene_num)
                topic.current_scene = next_scene_num
                
                # Generate next scene if not exists
                if not topic.scenes.filter(scene_number=next_scene_num).exists():
                    generate_next_scene(topic, next_scene_num)
        
        # Mark as completed if all scenes done
        if scene_number == 3 and correct >= 1:
            topic.completed = True
        
        topic.save()
        
        # Check if journey is complete
        journey_complete = topic.completed and len(topic.scenes_unlocked) == 3
        
        return JsonResponse({
            'status': 'success',
            'correct': correct,
            'total': len(quiz_questions),
            'score': topic.total_score,
            'unlocked': topic.scenes_unlocked,
            'next_scene': topic.current_scene,
            'journey_complete': journey_complete
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def generate_next_scene(topic, scene_number):
    """Generate the next scene in background"""
    try:
        scene_info = topic.scenes_data['scenes'][scene_number - 1]
        bria = BriaFIBOService()
        groq = GroqAIService()
        
        # Generate image
        scene_result = bria.translate_to_scene(scene_info['description'], 'single')
        json_scene = scene_result.get('scene', {})
        image_result = bria.generate_image(json_scene, scene_info['description'])
        image_url = image_result.get('image_url') if image_result.get('status') == 'success' else None
        
        # Generate quiz
        quiz_data = groq.generate_quiz(topic.topic, scene_info['description'], scene_number=scene_number)
        
        # Create scene
        Scene.objects.create(
            topic=topic,
            scene_number=scene_number,
            title=scene_info['title'],
            description=scene_info['description'],
            narration=scene_info['narration'],
            json_scene=json_scene,
            image_url=image_url,
            quiz_data=quiz_data,
            generation_status='completed' if image_url else 'pending'
        )
    except Exception as e:
        print(f"Error generating scene {scene_number}: {str(e)}")


@login_required
@require_POST
def regenerate_scene(request, topic_id, scene_number):
    """Regenerate scene with edited JSON or simple customization"""
    topic = get_object_or_404(Topic, id=topic_id, user=request.user)
    scene = get_object_or_404(Scene, topic=topic, scene_number=scene_number)
    
    try:
        data = json.loads(request.body)
        bria = BriaFIBOService()
        
        # Check if it's simple customization or JSON edit
        if 'enhanced_prompt' in data:
            # Simple customization from student or demo generation
            enhanced_prompt = data.get('enhanced_prompt')
            is_demo = data.get('generate_demo', False)
            
            # Generate new scene with enhanced prompt
            scene_result = bria.translate_to_scene(enhanced_prompt, 'single')
            json_scene = scene_result.get('scene', scene.json_scene)
            result = bria.generate_image(json_scene, enhanced_prompt)
            
            # Update generation status if it was a demo
            if is_demo and result.get('status') == 'success':
                scene.generation_status = 'completed'
        else:
            # Advanced JSON editing
            json_scene = data.get('json_scene', scene.json_scene)
            result = bria.generate_image(json_scene, scene.description)
        
        if result.get('status') == 'success':
            scene.json_scene = json_scene if 'json_scene' in locals() else scene.json_scene
            scene.image_url = result.get('image_url')
            scene.save()
            
            return JsonResponse({
                'status': 'success',
                'image_url': result.get('image_url')
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': result.get('message', 'Failed to generate')
            }, status=400)
            
    except Exception as e:
        print(f"Regenerate error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def owl_chat(request):
    """Owl responds to user questions"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        context = data.get('context', '')
        
        print(f"Owl Chat - Message: {message}, Context: {context}")
        
        groq = GroqAIService()
        response = groq.owl_chat(message, context)
        
        print(f"Owl Chat - Response: {response}")
        
        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        print(f"Owl Chat Error: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def certificate(request, topic_id):
    """Generate completion certificate"""
    topic = get_object_or_404(Topic, id=topic_id, user=request.user, completed=True)
    
    return render(request, 'home/certificate.html', {
        'topic': topic,
        'user': request.user
    })


@login_required
def demo_journey(request, demo_slug):
    """Load pre-generated demo journey"""
    # Demo data (pre-generated for instant access)
    demos = {
        'ancient-rome': {
            'topic': 'Ancient Rome - The Roman Forum',
            'subject_type': 'history',
            'scenes_data': {
                'scenes': [
                    {
                        'number': 1,
                        'title': 'The Heart of Rome',
                        'description': 'A wide panoramic view of the Roman Forum at its peak, showing the Temple of Saturn, Arch of Septimius Severus, and bustling marketplace with citizens in togas',
                        'narration': 'Welcome to the Roman Forum, the beating heart of Ancient Rome! This was the center of political, commercial, and judicial life. Around you stand magnificent temples dedicated to the gods, government buildings where senators debated, and the Rostra where great orators like Cicero addressed the crowds. The Forum was more than just a marketplace - it was where democracy was born, where laws were made, and where the fate of an empire was decided. Notice the grand columns, the marble pavements worn smooth by countless footsteps, and imagine the voices of thousands of Romans echoing through these spaces.'
                    },
                    {
                        'number': 2,
                        'title': 'Daily Life in the Forum',
                        'description': 'Ground-level view showing Roman citizens trading goods, senators in discussion, and children playing near the fountains, with the Colosseum visible in the background',
                        'narration': 'Now let\'s experience the Forum at ground level, as a Roman citizen would have seen it. The Forum was alive with activity from dawn to dusk. Merchants sold everything from exotic spices to fine pottery. Lawyers argued cases in the basilicas. Politicians campaigned for votes. Notice how the rich wore purple-trimmed togas while common citizens wore simple white. The Forum had public fountains providing fresh water from the aqueducts, and public latrines showing Roman engineering prowess. This wasn\'t just a place of power - it was where ordinary Romans lived their daily lives, gossiped, made deals, and felt connected to their great civilization.'
                    },
                    {
                        'number': 3,
                        'title': 'Legacy of the Forum',
                        'description': 'Sunset view of the Forum ruins as they appear today, with modern Rome visible in the background, showing the passage of time',
                        'narration': 'As the sun sets over the Forum, we see how this ancient center of power has endured through the ages. Though now in ruins, these stones tell the story of one of history\'s greatest civilizations. The Roman Forum influenced architecture, law, and government systems that we still use today. The concept of a republic, the idea of citizenship, the structure of our legal systems - all have roots here. When you visit modern government buildings with their columns and domes, you\'re seeing Roman influence. The Forum reminds us that great civilizations leave lasting legacies, and that the past continues to shape our present.'
                    }
                ]
            }
        },
        'amazon-rainforest': {
            'topic': 'Amazon Rainforest - The Lungs of Earth',
            'subject_type': 'geography',
            'scenes_data': {
                'scenes': [
                    {
                        'number': 1,
                        'title': 'The Canopy Layer',
                        'description': 'Aerial bird\'s eye view of the dense Amazon rainforest canopy, showing the vast green expanse with emergent trees, colorful macaws flying, and morning mist',
                        'narration': 'Welcome to the Amazon Rainforest, often called the "Lungs of Earth"! From this aerial view, you can see why - the canopy stretches endlessly in every direction, a sea of green that produces 20% of the world\'s oxygen. The Amazon covers 5.5 million square kilometers across nine countries. What you\'re seeing is the canopy layer, about 30-45 meters high, where most of the rainforest\'s life exists. Notice the emergent trees that tower even higher, reaching for sunlight. The Amazon is home to 10% of all species on Earth - that\'s over 40,000 plant species, 1,300 bird species, and 2.5 million insect species! This incredible biodiversity makes it one of the most important ecosystems on our planet.'
                    },
                    {
                        'number': 2,
                        'title': 'The Forest Floor',
                        'description': 'Ground-level view showing massive tree trunks, hanging vines, colorful poison dart frogs, leafcutter ants, and filtered sunlight creating a mystical atmosphere',
                        'narration': 'Now let\'s descend to the forest floor, a completely different world. Only about 2% of sunlight reaches here, creating a dim, humid environment. Despite the darkness, life thrives everywhere you look. See those leafcutter ants? They\'re farming! They cut leaves and use them to grow fungus for food. The colorful poison dart frogs warn predators with their bright colors. Notice the massive tree trunks - some are over 1,000 years old. The forest floor is covered in decomposing leaves that quickly break down in the heat and humidity, recycling nutrients back into the soil. Indigenous peoples have lived in harmony with this forest for over 11,000 years, developing deep knowledge of medicinal plants and sustainable living practices.'
                    },
                    {
                        'number': 3,
                        'title': 'The Amazon River',
                        'description': 'Wide view of the mighty Amazon River winding through the rainforest, with pink river dolphins, local communities in boats, and the meeting of waters where different colored rivers merge',
                        'narration': 'The Amazon River is the lifeblood of the rainforest, the largest river by volume in the world. It discharges more water than the next seven largest rivers combined! The river and its 1,100 tributaries create a vast network that supports countless communities and species. See those pink river dolphins? They\'re unique to the Amazon. The river floods seasonally, rising up to 15 meters, which spreads nutrients across the forest floor. However, the Amazon faces serious threats - deforestation, climate change, and human activity are endangering this vital ecosystem. Scientists estimate we\'re losing an area the size of a football field every single minute. Protecting the Amazon isn\'t just about saving trees - it\'s about preserving Earth\'s climate, biodiversity, and the future of our planet.'
                    }
                ]
            }
        }
    }
    
    if demo_slug not in demos:
        messages.error(request, 'Demo not found')
        return redirect('home:home')
    
    demo_data = demos[demo_slug]
    
    # Check if user already has this demo
    existing = Topic.objects.filter(
        user=request.user,
        topic=demo_data['topic']
    ).first()
    
    if existing:
        return redirect('home:journey', topic_id=existing.id)
    
    # Create demo topic (no images, just text for instant access)
    topic = Topic.objects.create(
        user=request.user,
        topic=demo_data['topic'],
        subject_type=demo_data['subject_type'],
        scenes_data=demo_data['scenes_data'],
        scenes_unlocked=[1, 2, 3],  # All unlocked for demo
        current_scene=1
    )
    
    # Create all 3 scenes (without images for speed)
    groq = GroqAIService()
    for i, scene_info in enumerate(demo_data['scenes_data']['scenes'], 1):
        quiz_data = groq.generate_quiz(demo_data['topic'], scene_info['description'], scene_number=i)
        
        Scene.objects.create(
            topic=topic,
            scene_number=i,
            title=scene_info['title'],
            description=scene_info['description'],
            narration=scene_info['narration'],
            json_scene={},  # Empty for demo
            image_url=None,  # Will show placeholder
            quiz_data=quiz_data,
            generation_status='demo'
        )
    
    messages.success(request, f'🎉 Demo loaded! All scenes unlocked for exploration.')
    return redirect('home:journey', topic_id=topic.id)


def logout_view(request):
    """Logout"""
    logout(request)
    return redirect('home:landing')
