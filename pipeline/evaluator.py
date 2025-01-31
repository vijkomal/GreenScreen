import json
import os
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
import PyPDF2

import google.generativeai as genai
import json
from utils import load_json
import re

# config genAI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

CACHE_FILE = "evaluator.cache"


def get_cached_report_name():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            return file.read().strip()
    return None


def cache_report_name(report_name):
    with open(CACHE_FILE, "w") as file:
        file.write(report_name)


class Evaluator:
    def __init__(self, pdf_path, questions):
        self.pdf_path = pdf_path
        self.questions = questions
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            generation_config={
                "response_mime_type": "application/json"
            },  # json response
        )

        # upload pdf
        cached_report_name = get_cached_report_name()
        try:
            self.report_file = genai.get_file(name=cached_report_name)
        except Exception:
            self.report = genai.upload_file(path=pdf_path, display_name="IPCC Report")
            self.report_file = genai.get_file(name=self.report.name)
            cache_report_name(self.report.name)

    def get_prompt(self):
        initial_prompt = """
        Your task is to answer the following multiple choice questions about the report. 
        For each question, provide a sentence about your reasoning. Then answer using
        the number of the option with the correct answer. If you cannot answer the question
        based on the provided context, use `-1` as your answer. Format your response
        using this JSON schema:

        Answer = {'question': int, 'reasoning': str, 'answer': int}
        Return: list[Answer]
        """.strip()
        question_prompt = """
        Question [QUESTION_NUM]: [QUESTION]
        Options:
        [OPTIONS]
        """.strip()

        prompt = initial_prompt
        prompt += "\n\nMultiple-Choice Exam:\n"
        prompt += "###################################"
        for i, data in enumerate(self.questions):
            q_prompt = question_prompt
            q_prompt = q_prompt.replace("[QUESTION_NUM]", str(i + 1))
            q_prompt = q_prompt.replace("[QUESTION]", data["question"])
            option_list = f"""
            1) {data['option_1']}
            2) {data['option_2']}
            3) {data['option_3']}
            """.strip()
            q_prompt = q_prompt.replace("[OPTIONS]", option_list)
            prompt += "\n" + q_prompt + "\n"

        prompt += "###################################"
        prompt = re.sub(
            r"[ \t]+", " ", prompt
        )  # remove excessive spaces but keep newlines
        return prompt

    def evaluate(self, with_report=True):
        print("[*] Getting answers...")
        prompt = self.get_prompt()
        if with_report:
            raw_response = self.model.generate_content([prompt, self.report_file])
        else:
            raw_response = self.model.generate_content(prompt)
        answers = json.loads(raw_response.text)
        return answers

    def calculate_metrics(self, results):
        print("[*] Calculating metrics...")
        # get predictions
        y_true = [q["answer"] for q in self.questions]
        y_pred = [a["answer"] for a in results]

        accuracy = accuracy_score(y_true, y_pred)

        # Compute Precision (macro-average)
        precision = precision_score(y_true, y_pred, average="macro")

        # Compute Recall (macro-average)
        recall = recall_score(y_true, y_pred, average="macro")

        # Compute F1 Score (macro-average)
        f1 = f1_score(y_true, y_pred, average="macro")

        metrics = {
            "accuracy": round(accuracy, 2),
            "precision": round(precision, 2),
            "recall": round(recall, 2),
            "f1": round(f1, 2),
        }

        return metrics

    def save_results(self, results, metrics):
        output_path = os.path.join(
            os.path.dirname(self.pdf_path), "evaluation_results.json"
        )
        with open(output_path, "w") as file:
            json.dump({"answers": results, "metrics": metrics}, file, indent=4)
        print("Saved results")

    def run(self):
        results = self.evaluate()
        metrics = self.calculate_metrics(results)
        self.save_results(results, metrics)


# Example usage:
# pdf_path = '/path/to/presentation.pdf'
# questions = [{'question': 'What is the main topic?', 'answer': 'AI'}, ...]
# evaluator = Evaluator(pdf_path, questions)
# evaluator.run()


questions = load_json("../questions/sample-questions.json")
evaluator = Evaluator(
    "/Users/alice/Documents/02-OUTPUT/Row4Labs/GreenScreen/data/pages/IPCC_SPM_2018-page-7.pdf",  # check gt
    questions,
)
evaluator.run()
