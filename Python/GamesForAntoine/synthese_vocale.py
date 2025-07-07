import pyttsx3

engine = pyttsx3.init()
engine.say("Bonjour")
engine.runAndWait()
engine.stop()

engine.say("1")
engine.runAndWait()
engine.say("123")
engine.runAndWait()
engine.say("Bonjour")
engine.runAndWait()
