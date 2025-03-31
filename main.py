import queue
import threading
import time
import cv2 as cv
import keyboard
import mediapipe.python.solutions.hands as mp_hands
import atexit
import signal
import sys

import gestures
import speech_util
from commands.spotify_commands import CloseSpotifyCommand, OpenSpotifyCommand, PlaySpotifyCommand
from invoker.voice_invoker import VoiceCommandInvoker
from receiver.voice_receiver import VoiceReceiver



class GestureVoiceApplication:
    """Main application class that manages the entire application lifecycle."""

    def __init__(self):
        """Initialize the application components."""
        # Initialize state flags
        self.is_running = False
        self.stop_event = threading.Event()

        # Initialize data structures
        self.result_queue = queue.Queue()
        self.shared_data = {'right_hand_vol': 0, 'text_pos': (0, 0)}

        # Initialize command system
        self.setup_command_system()

        # Thread containers
        self.threads = []

        # Register shutdown handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def setup_command_system(self):
        """Set up the command recognition system."""
        self.receiver = VoiceReceiver()
        self.invoker = VoiceCommandInvoker()

        # Register commands
        open_spotify_cmd = OpenSpotifyCommand(self.receiver)
        close_spotify_cmd = CloseSpotifyCommand(self.receiver)
        play_song_cmd = PlaySpotifyCommand(self.receiver)

        self.invoker.set_command('open spotify', open_spotify_cmd)
        self.invoker.set_command('close spotify', close_spotify_cmd)
        self.invoker.set_command('play song', play_song_cmd)

    def start(self):
        """Start the application and all its components."""
        if self.is_running:
            print("Application is already running")
            return

        print("Starting Gesture Voice Application...")
        self.is_running = True

        # Start camera thread
        camera_thread = threading.Thread(
            target=self.camera_operations,
            name="CameraThread",
            daemon=True
        )
        camera_thread.start()
        self.threads.append(camera_thread)

        # Start keyboard listener thread
        keyboard_thread = threading.Thread(
            target=self.listen_for_quit,
            name="KeyboardThread",
            daemon=True
        )
        keyboard_thread.start()
        self.threads.append(keyboard_thread)

        # Start main command processing loop
        self.process_commands()

    def camera_operations(self):
        """Camera handling and gesture recognition thread."""
        # Initialize MediaPipe hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2
        )

        # Initialize camera
        cam = None
        try:
            cam = cv.VideoCapture(0)
            if not cam.isOpened():
                print("Error: Could not open camera")
                return

            print("Camera initialized successfully")

            while not self.stop_event.is_set() and cam.isOpened():
                # Capture frame
                success, frame = cam.read()
                if not success:
                    print("Warning: Failed to capture frame")
                    time.sleep(0.1)  # Short delay before retry
                    continue

                # Process frame
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                frame = cv.flip(frame, 1)
                hands_detected = hands.process(frame)

                # Convert back for display
                frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

                # Process hand landmarks if detected
                if hands_detected.multi_hand_landmarks:
                    try:
                        hand_label = hands_detected.multi_handedness
                        landmarks = hands_detected.multi_hand_landmarks
                        gestures.volume_gesture(landmarks, hand_label, frame, cv, self.shared_data)
                    except Exception as e:
                        print(f"Error in gesture processing: {e}")

                # Display frame
                cv.imshow("Gesture Control", frame)

                # Check for exit key
                if cv.waitKey(20) & 0xff == ord('q'):
                    print("Exit key pressed in camera window")
                    self.stop_event.set()
                    break

        except Exception as e:
            print(f"Camera thread error: {e}")
        finally:
            # Cleanup camera resources
            if cam is not None and cam.isOpened():
                cam.release()
            cv.destroyAllWindows()
            print("Camera resources released")

    def listen_for_quit(self):
        """Listen for quit key press."""
        try:
            while not self.stop_event.is_set():
                if keyboard.is_pressed("q"):
                    print("Quit key pressed")
                    self.stop_event.set()
                    break
                time.sleep(0.1)  # Reduce CPU usage
        except Exception as e:
            print(f"Keyboard listener error: {e}")

    def process_commands(self):
        """Main command processing loop."""
        try:
            print("Command processing started")

            while not self.stop_event.is_set():
                # Create speech recognition thread for this cycle
                speech_thread = threading.Thread(
                    target=speech_util.get_phrase,
                    args=(self.result_queue,),
                    name="SpeechThread"
                )
                speech_thread.start()
                speech_thread.join()  # Wait for speech recognition to complete

                # Process any detected commands
                if not self.result_queue.empty():
                    result = self.result_queue.get()
                    if result:
                        print(f"Executing command: '{result}'")
                        self.invoker.execute_command(result.lower())

                # Short delay to prevent high CPU usage
                time.sleep(0.1)

        except Exception as e:
            print(f"Command processing error: {e}")
        finally:
            print("Command processing stopped")
            self.stop()

    def stop(self):
        """Stop the application."""
        if not self.is_running:
            return

        print("Stopping application...")
        self.stop_event.set()
        self.is_running = False

        # Give threads a moment to terminate
        time.sleep(0.5)

        # Perform cleanup
        self.cleanup()

    def cleanup(self):
        """Clean up all resources."""
        if hasattr(self, 'cleaned_up') and self.cleaned_up:
            return

        print("Cleaning up resources...")

        # Set stop event to signal threads to stop
        self.stop_event.set()

        # Clean up gesture module resources
        try:
            gestures.close_threads()
        except Exception as e:
            print(f"Error closing gesture threads: {e}")

        # Mark as cleaned up to prevent duplicate cleanup
        self.cleaned_up = True
        print("Cleanup complete")

    def signal_handler(self, sig, frame):
        """Handle system signals for clean shutdown."""
        print(f"Received signal {sig}, shutting down...")
        self.stop()
        sys.exit(0)


def main():
    """Application entry point."""
    app = GestureVoiceApplication()
    app.start()


if __name__ == "__main__":
    main()