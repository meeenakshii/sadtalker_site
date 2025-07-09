import os
import uuid
import requests
from django.core.files.base import ContentFile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .forms import GenerationForm
from .models import GenerationRequest

# ✅ Built-in ElevenLabs Voice IDs
BUILTIN_VOICES = {
    "female.mp3": "pNInz6obpgDQGcFmaJgB",  # Female
    "hero.mp3": "TxGEqnHWrfWFTfGW9XjX",    # Heroic Male
    "male.mp3": "EXAVITQu4vr4xnSDxMaL"     # Neutral Male
}

# ✅ Generate speech using ElevenLabs
def generate_speech_from_text(text, voice_id):
    print(f"[DEBUG] Generating TTS with voice_id={voice_id}...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("[DEBUG] TTS generation successful ✅")
        return response.content
    else:
        print("[ERROR] TTS generation failed:", response.text)
        return None

@login_required
def home(request):
    if request.method == 'POST':
        form = GenerationForm(request.POST, request.FILES)
        if form.is_valid():
            gen_req = form.save(commit=False)
            gen_req.user = request.user

            use_cloning = request.POST.get("clone_voice") == "on"
            uploaded_audio = request.FILES.get("audio")
            selected_voice = request.POST.get("selected_voice", "")
            cloned_voice_id = None

            # ✅ Save uploaded audio (if any)
            if uploaded_audio:
                print("[DEBUG] Saving uploaded audio...")
                gen_req.audio = uploaded_audio
                gen_req.save()

            # ✅ Clone uploaded audio
            if use_cloning and gen_req.audio:
                try:
                    print("[DEBUG] Cloning uploaded voice...")
                    with open(gen_req.audio.path, 'rb') as f:
                        files = {'files': (gen_req.audio.name, f, 'audio/wav')}
                        data = {
                            'name': f"{request.user.username}_voice",
                            'description': "Voice cloned from user audio"
                        }
                        headers = {'xi-api-key': settings.ELEVENLABS_API_KEY}
                        response = requests.post('https://api.elevenlabs.io/v1/voices/add', headers=headers, data=data, files=files)
                        if response.status_code == 200:
                            cloned_voice_id = response.json().get("voice_id")
                            gen_req.cloned_voice_id = cloned_voice_id
                            print(f"[DEBUG] Cloning success ✅ Voice ID: {cloned_voice_id}")
                        else:
                            print("[ERROR] Voice cloning failed:", response.text)
                except Exception as e:
                    print("[EXCEPTION] Cloning failed:", e)

            # ✅ Fallback to built-in voice if not cloning
            if not cloned_voice_id and selected_voice in BUILTIN_VOICES:
                cloned_voice_id = BUILTIN_VOICES[selected_voice]
                print(f"[DEBUG] Using built-in voice: {selected_voice} → {cloned_voice_id}")

            # ✅ Generate speech from text and voice ID
            if cloned_voice_id:
                speech_data = generate_speech_from_text(gen_req.text, cloned_voice_id)
                if speech_data:
                    audio_filename = f"{uuid.uuid4()}.mp3"
                    print(f"[DEBUG] Saving generated speech to: {audio_filename}")
                    gen_req.audio.save(audio_filename, ContentFile(speech_data), save=False)

            gen_req.save()

            # ✅ Email confirmation
            send_mail(
                subject="SadTalker Video Processing",
                message=f"Hi {request.user.username},\n\nYour SadTalker video is now being processed. You'll receive another email once it's ready.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=False,
            )
            print("[DEBUG] Email sent to user.")

            return render(request, 'success.html', {
                'message': 'Generation request submitted!',
                'final_audio_url': gen_req.audio.url if gen_req.audio else None
            })

    else:
        form = GenerationForm()

    # ✅ Show only the built-in voice options
    sample_voices = list(BUILTIN_VOICES.keys())

    return render(request, 'index.html', {
        'form': form,
        'sample_voices': sample_voices
    })
