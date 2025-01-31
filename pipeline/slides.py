import google.generativeai as genai
import json
import dataclasses
import typing_extensions as typing
import os
import nltk

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


class Slides:
    def __init__(self):
        self.prompts = {"retain-original": retain_original_prompt}
        # self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def get_slide_from_section(self, section_text, prompt_name="retain-original"):
        prompt = self.prompts[prompt_name]
        response = self.model.generate_content(prompt)
        return response.text

    def get_slide_latex(self, section_text):
        # sentences = nltk.sent_tokenize(section_text)
        slide_latex = r"\begin{frame}" + "\n"
        slide_latex += r"\frametitle{Carbon Budget and Limiting Global Warming}" + "\n"
        slide_latex += section_text
        # slide_latex += r"\begin{itemize}" + "\n"
        # for sentence in sentences:
        # slide_latex += r"\item " + sentence + "\n"
        # slide_latex += r"\end{itemize}" + "\n"
        slide_latex += r"\end{frame}" + "\n"
        return slide_latex


# \begin{frame}
# \frametitle{Key Findings}
# \begin{itemize}
#     \item \textcolor{green}{The study demonstrates a strong positive correlation between increased exercise frequency and improved cardiovascular health. }

#     \item \textcolor{orange}{Preliminary data suggests a potential link between exposure to blue light before sleep and reduced sleep quality,} however more investigation is needed.

#     \item \textcolor{green}{Our analysis confirms that implementing the proposed algorithm results in a 15\% reduction in processing time. }

#     \item \textcolor{orange}{Initial findings indicate that a novel drug candidate shows some promise in inhibiting tumor growth in vitro,} though further in-vivo testing is required.
# \end{itemize}
# \end{frame}
