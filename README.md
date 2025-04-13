🔁 1. Head Tracking for Cursor Movement
Uses MediaPipe FaceMesh to track the nose tip (landmark index 1).

Moves the mouse cursor based on the nose's deviation from the screen center.

Sensitivity can be adjusted (currently 3.5) to fine-tune cursor movement.

Controlled with the "Tracking" button on screen (toggles on/off).

👁️‍🗨️ 2. Eye Blink Detection for Mouse Clicks
Calculates Eye Aspect Ratio (EAR) using six eye landmarks for both eyes.

If EAR falls below a threshold (0.21) for a few frames, a blink is detected.

Supports:

Single click (2 blinks in 3 seconds)

Double click (3 blinks in 4 seconds)

Right click (4 blinks in 5 seconds)

Controlled with the "Blink Ctrl" button on screen.

🎤 3. Voice Command Support
Uses speech_recognition library with Google Speech API.

Commands include:

"click" – single click

"double click" – double click

"right click" or "option menu" – right click

"hold click" – click and hold (mouse down)

"release click" – release held click (mouse up)

⌨️ 4. On-Screen Keyboard Toggle
Clicking the "Keyboard" button opens or closes the Windows on-screen keyboard (osk.exe).

Allows users to type using other interaction methods (e.g., voice, gaze, or external switches).

🧠 5. UI Overlay with Toggle Buttons
A GUI overlay is rendered with 3 buttons to toggle:

Head Tracking

Blink Control

On-Screen Keyboard

Buttons change color (green = enabled, red = disabled) and respond to mouse clicks.

🧵 6. Multi-threaded Execution
Uses Python threading to simultaneously:

Run head and blink tracking (head_tracking())

Process voice commands (voice_commands())

🛑 7. Graceful Exit
Pressing Esc or using Ctrl+C (KeyboardInterrupt) sets exit_app = True to stop all loops and safely close resources like the webcam and GUI.

Features
🖊️ Drawing Question Solving
This feature allows users to solve problems involving drawings or visual elements. Users can draw diagrams, equations, or sketches related to various subjects, and the AI assistant will analyze the drawing and provide solutions or explanations. This feature is especially beneficial for visually impaired users or when solving problems that require visual representation.

🎤 Voice Typing & AI Assistance
This feature enables users to type text or perform tasks via voice commands. Users can dictate text, control applications, and get AI-assisted support for tasks like setting reminders, sending messages, and retrieving information. It enhances accessibility for users with limited mobility and provides an easy way to interact with the system without needing to type.

