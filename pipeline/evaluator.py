import json
import os
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score
import PyPDF2

import google.generativeai as genai
import json
from utils import load_json, save_json
import re
from slides import Slide
from readability import Readability
import pandas as pd
from report_reader import Report
from report_reader import ReportReader
from tqdm import tqdm
import time

# Config genAI
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

UPLOADED_FILES_CACHE = "../cache/uploaded-files.json"


class Evaluator:
    def __init__(self):
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash-exp",
            generation_config={
                "response_mime_type": "application/json"
            },  # json response
        )
        self.cache = load_json(UPLOADED_FILES_CACHE)

    def get_prompt(self, prompt_name, placeholders):
        with open(f"../prompts/{prompt_name}") as f:
            prompt = f.read()

        for ph in placeholders:
            prompt = prompt.replace(ph[0], ph[1])

        return prompt

    def add_report_to_cache(self, report):
        report = genai.upload_file(
            path=report.filepath, display_name=report.display_name
        )
        self.cache[report.display_name] = report.name
        save_json(self.cache, UPLOADED_FILES_CACHE)
        return report

    def remove_report_from_cache(self, report):
        if report.display_name in self.cache:
            del self.cache[report.display_name]
            save_json(self.cache, UPLOADED_FILES_CACHE)

    def evaluate_content(self, questions: list, report: Report):
        print("[*] Getting answers...")

        # results_path = report.display_name.lower().replace(" ", "-")

        # Upload report
        report = genai.upload_file(
            path=report.filepath, display_name=report.display_name
        )
        print(f"Uploaded {report.display_name}")

        results = []
        for i, data in tqdm(enumerate(questions)):
            # Create multiple-choice question prompt
            option_list = f"1) {data['option_1']}\n"
            option_list += f"2) {data['option_2']}\n"
            option_list += f"3) {data['option_3']}\n"
            placeholders = [
                ("[QUESTION_NUM]", str(i + 1)),
                ("[QUESTION]", data["question"]),
                ("[OPTIONS]", option_list),
            ]
            prompt = self.get_prompt("exam-question.prompt", placeholders)

            # Get model response
            raw_response = self.model.generate_content([prompt, report])
            results.append(json.loads(raw_response.text))

            # Slight delay
            time.sleep(0.1)

            # Save every 10
            if i % 10 == 0:
                save_json()

        # Delete file
        genai.delete_file(report.name)
        print(f"Deleted {report.display_name}.")

        return results

    def calculate_metrics(self, answers, results):
        print("[*] Calculating metrics...")
        # get predictions
        y_true = [q["answer"] for q in answers]
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

    def evaluate_readability(self, transcript):
        r = Readability(transcript)

        readability_scores = {
            "flesch_kincaid": r.flesch_kincaid(),
            "flesch": r.flesch(),
            "gunning_fog": r.gunning_fog(),
            "coleman_liau": r.coleman_liau(),
            "dale_chall": r.dale_chall(),
            "ari": r.ari(),
            "linsear_write": r.linsear_write(),
            "smog": r.smog(),
            "spache": r.spache(),
        }

        return readability_scores

    def save_results(self, results, metrics):
        output_path = os.path.join(
            os.path.dirname(self.pdf_path), "evaluation_results.json"
        )
        with open(output_path, "w") as file:
            json.dump({"answers": results, "metrics": metrics}, file, indent=4)
        print("Saved results")

    def run(self, report: Report):
        # Evaluate content
        questions = []
        content_results = self.evaluate_content()
        content_metrics = self.calculate_metrics(content_results)
        # Evaluate readability
        readability_metrics = self.evaluate_readability()
        # Save results
        self.save_results(
            ["content_results", "content_metrics", "readability_metrics"],
            [content_results, content_metrics, readability_metrics],
        )


# Example usage:
# pdf_path = '/path/to/presentation.pdf'
# questions = [{'question': 'What is the main topic?', 'answer': 'AI'}, ...]
# evaluator = Evaluator(pdf_path, questions)
# evaluator.run()

# questions = load_json("../questions/sample-questions.json")
# evaluator = Evaluator(
#     "/Users/alice/Documents/02-OUTPUT/Row4Labs/GreenScreen/data/pages/IPCC_SPM_2018-page-7.pdf",  # check gt
#     questions,
# )
# evaluator.run()


report_reader = ReportReader()
evaluator = Evaluator()

content_questions = load_json("../questions/sample-questions.json")

sample_report = report_reader.get_report(
    "../data/pages/IPCC_SPM_2018-page-7.pdf", "IPPC 2018"
)
results = evaluator.evaluate_content(content_questions, sample_report)
print(results)
