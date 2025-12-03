from django.contrib.auth.models import AbstractUser
from django.db import models
import json


class User(AbstractUser):
    # Optional WorkOS ID field
    workos_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.email or self.username


class Topic(models.Model):
    SUBJECT_CHOICES = [
        ('history', 'History'),
        ('geography', 'Geography'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    topic = models.CharField(max_length=255)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='history')
    
    # AI Generated Content
    scenes_data = models.JSONField(null=True, blank=True)  # Stores all 3 scenes info
    
    # Progress Tracking
    current_scene = models.IntegerField(default=1)  # Which scene user is on
    scenes_unlocked = models.JSONField(default=list)  # [1, 2, 3] as they unlock
    quiz_scores = models.JSONField(default=dict)  # {"scene_1": 2, "scene_2": 1, ...}
    total_score = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.topic


class Scene(models.Model):
    """Individual scene in a topic journey"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='scenes')
    scene_number = models.IntegerField()  # 1, 2, or 3
    title = models.CharField(max_length=255)
    description = models.TextField()  # For Bria prompt
    narration = models.TextField()  # What owl says
    
    # Generated Image
    json_scene = models.JSONField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    generation_status = models.CharField(max_length=50, default='pending')
    
    # Quiz for this scene
    quiz_data = models.JSONField(null=True, blank=True)  # 2 questions
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scene_number']
        unique_together = ['topic', 'scene_number']

    def __str__(self):
        return f"{self.topic.topic} - Scene {self.scene_number}"


class SceneVariation(models.Model):
    """Store multiple variations/regenerations of a topic"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='variations')
    json_scene = models.JSONField()
    image_url = models.URLField(max_length=500, null=True, blank=True)
    image_data = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
