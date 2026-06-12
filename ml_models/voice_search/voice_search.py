from speech_to_text import (
    SpeechToText
)

from chatbot.retrieval import (
    ProductRetriever
)


class VoiceSearch:

    def __init__(self):
        from pathlib import Path
        PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
        dataset_path = PROJECT_ROOT / "ml_models" / "datasets" / "chatbot_dataset" / "Air Conditioners.csv"

        self.stt = SpeechToText()

        self.retriever = ProductRetriever(str(dataset_path))

    def search(self, audio_file=None):

        query = self.stt.listen(source_file=audio_file)


        if not query:

            return

        results = self.retriever.search(
            query
        )

        print("\nResults:\n")

        for product in results[:5]:

            print(
                product
            )


if __name__ == "__main__":

    VoiceSearch().search()