import speech_recognition as sr


class SpeechToText:

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen(self, source_file=None):
        if source_file is not None:
            try:
                with sr.AudioFile(source_file) as source:
                    audio = self.recognizer.record(source)
            except Exception as e:
                print(f"Audio file read error: {e}")
                return ""
        else:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=1
                    )
                    audio = self.recognizer.listen(
                        source
                    )
            except Exception as e:
                print(f"Microphone access error (no mic or running in headless/Docker environment): {e}")
                return ""

        try:

            text = self.recognizer.recognize_google(
                audio
            )

            print(
                f"Recognized: {text}"
            )

            return text

        except Exception as e:

            print(
                f"Error recognizing speech: {e}"
            )

            return ""



if __name__ == "__main__":

    stt = SpeechToText()

    text = stt.listen()

    print(text)