import google.generativeai as genai
import json
import dataclasses
import typing_extensions as typing
import os
import nltk
from dataclasses import dataclass
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np
from utils import get_prompt
import time

nltk.download("punkt")

# config genAI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


### PROMPTS
retain_original_prompt = """
You are an expert Latex Beamer slide creator. Your task is to convert the following
paragraph into a single Latex Beamer slide.

Rules:
- You must preserve the original text
- Color code each claim with a confidence label, using green for high confidence and
orange for lower confidence.
- Make the information more readable by dividing the text into 
- Respond using valid Latex beamer code. Only include the code for the begin/end frame, i.e.
do not include the documentclass etc.
""".strip()


###
@dataclasses.dataclass
class Slide:
    latex_content: str
    transcript: str


###
class SlidesGenerator:
    def __init__(self):
        self.prompts = {"retain-original": retain_original_prompt}
        self.vectorizer = CountVectorizer(stop_words="english")
        self.transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def get_slide_from_section(self, section_text, prompt_name="retain-original"):
        prompt = self.prompts[prompt_name]
        response = self.model.generate_content(prompt)
        return response.text

    def get_keywords(self, text, n=5):
        word_count = self.vectorizer.fit_transform([text])
        tfidf = self.transformer.fit_transform(word_count)
        scores = tfidf.toarray()[0]
        feature_names = self.vectorizer.get_feature_names_out()
        top_indices = np.argsort(scores)[::-1][:n]
        top_keywords = [feature_names[i] for i in top_indices]
        return ", ".join(top_keywords)

    def get_raw_slide_latex(self, section_text, title):
        # sentences = nltk.sent_tokenize(section_text)
        slide_latex = r"\begin{frame}" + "\n"
        slide_latex += r"\frametitle{" + title + r"}" + "\n"
        # slide_latex += r"\fontsize{8}{15}\selectfont" + "\n"
        slide_latex += section_text + "\n"
        slide_latex += r"\end{frame}" + "\n"
        # slide_latex = slide_latex.encode("utf-8", "ignore").decode("utf-8")
        return slide_latex

    def make_raw_slide(self, section_text):
        # title = self.get_keywords(section_text)
        title = ""
        slide = Slide(
            latex_content=self.get_raw_slide_latex(section_text, title),
            transcript=section_text,
        )
        return slide

    def parse_latex_response(self, latex_response):
        latex_response = latex_response.replace("```latex", "")
        latex_response = latex_response.replace("```", "")
        return latex_response.strip()

    def make_slide(self, prompt_name, placeholders):
        print("[*] Making slide...")
        prompt = get_prompt(prompt_name, placeholders)
        response = self.model.generate_content(prompt)
        latex_response = self.parse_latex_response(response.text)

        slide = Slide(
            latex_content=latex_response,
            transcript="",
        )
        return slide


# \begin{frame}
# \frametitle{Key Findings}
# \begin{itemize}
#     \item \textcolor{green}{The study demonstrates a strong positive correlation between increased exercise frequency and improved cardiovascular health. }

#     \item \textcolor{orange}{Preliminary data suggests a potential link between exposure to blue light before sleep and reduced sleep quality,} however more investigation is needed.

#     \item \textcolor{green}{Our analysis confirms that implementing the proposed algorithm results in a 15\% reduction in processing time. }

#     \item \textcolor{orange}{Initial findings indicate that a novel drug candidate shows some promise in inhibiting tumor growth in vitro,} though further in-vivo testing is required.
# \end{itemize}
# \end{frame}
