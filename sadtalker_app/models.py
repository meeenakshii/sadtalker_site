from django.db import models
from django.contrib.auth.models import User

class GenerationRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    text = models.TextField()
    audio = models.FileField(upload_to='audios/', blank=True, null=True)
    selected_voice = models.CharField(max_length=100, blank=True)

    # ✅ New field to store cloned voice ID from ElevenLabs
    cloned_voice_id = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.user.username} at {self.created_at}"
