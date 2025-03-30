import subprocess

import speech_recognition as sr

r = sr.Recognizer()


def get_phrase():
    with sr.Microphone() as source:
        print("Listening")
        audio_text = r.listen(source)
        print("Time over, thanks")
        # recoginze_() method will throw a request
        # error if the API is unreachable,
        # hence using exception handling

        try:
            # using google speech recognition
            return r.recognize_google(audio_text)
        except:
            return "Sorry, I did not get that"


