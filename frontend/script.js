const socket = io("http://localhost:5000"); // Update with your backend URL
let mediaRecorder, audioChunks = [], streamURL = "";

document.getElementById("toggle").onclick = async () => {
    if (!mediaRecorder || mediaRecorder.state === "inactive") {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();

        // Request unique stream ID
        socket.emit('start_recording');

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
            socket.emit('audio_chunk', { user_id: streamURL, audio: event.data });
        };

        mediaRecorder.onstop = () => audioChunks = [];
        document.getElementById("toggle").innerText = "Stop Mic";
    } else {
        mediaRecorder.stop();
        document.getElementById("toggle").innerText = "Start Mic";
    }
};

// Receive unique stream URL
socket.on('stream_id', data => {
    streamURL = data.stream_url;
    document.getElementById("stream_link").innerHTML = `🔗 <a href="${streamURL}" target="_blank" class="text-blue-400">${streamURL}</a>`;
});

// Receive amplified audio and play
socket.on('amplified_audio', data => {
    const audioBlob = new Blob([data], { type: 'audio/wav' });
    document.getElementById("audio").src = URL.createObjectURL(audioBlob);
});
