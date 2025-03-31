import os

import speech_recognition as sr
import queue

class SpeechRecognizer:
    def __init__(self, pause_threshold=2, energy_threshold=200):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.energy_threshold = energy_threshold


    def get_phrase(self, q: queue.Queue):
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_text = self.recognizer.listen(source, phrase_time_limit=10)

            print("Time over, thanks.")

            try:
                # Using Google Speech Recognition
                results = self.recognizer.recognize_wit(audio_text,os.environ['wit_key'])
                q.put(results)
            except Exception as e:
                print(f"Error: {e}")
                q.put("Sorry, I did not get that")