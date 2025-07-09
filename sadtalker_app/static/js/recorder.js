let mediaRecorder;
let audioChunks = [];

document.addEventListener('DOMContentLoaded', function () {
    const recordBtn = document.getElementById('recordBtn');
    const audioInput = document.getElementById('recordedAudioInput');

    recordBtn.addEventListener('click', async function () {
        if (recordBtn.dataset.recording === 'true') {
            // Stop recording
            mediaRecorder.stop();
            recordBtn.textContent = 'Start Recording';
            recordBtn.dataset.recording = 'false';
        } else {
            // Start recording
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                    console.log("[DEBUG] audio data received");
                };

                mediaRecorder.onstop = async () => {
                    console.log("[DEBUG] mediaRecorder stopped");

                    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                    const file = new File([audioBlob], 'recorded_audio.wav', { type: 'audio/wav' });

                    // Add to hidden file input so Django gets it
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    audioInput.files = dataTransfer.files;

                    console.log("[DEBUG] Recorded audio attached:", file);

                    // OPTIONAL: Add audio player to listen before submit
                    const audioURL = URL.createObjectURL(audioBlob);
                    const audioEl = document.createElement("audio");
                    audioEl.src = audioURL;
                    audioEl.controls = true;
                    document.body.appendChild(audioEl);
                };

                mediaRecorder.start();
                recordBtn.textContent = 'Stop Recording';
                recordBtn.dataset.recording = 'true';
                console.log("[DEBUG] Recording started...");
            } catch (err) {
                console.error("Microphone permission denied or error:", err);
                alert("Please allow microphone access to record audio.");
            }
        }
    });
});
