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

    def evaluate_content(self, results_id, questions: list, report: Report):
        print("[*] Getting answers...")

        results_path = f"../results/{results_id}.json"

        # Upload report
        report_file = genai.upload_file(
            path=report.filepath, display_name=report.display_name
        )
        print(f"Uploaded {report.display_name}")

        results = []
        step_size = 10
        for i in range(0, len(questions), step_size):
            curr = questions[i : i + step_size]
            prompt = self.get_prompt("exam-question-initial.prompt", [])
            prompt += "\n\n"
            for j, qa in enumerate(curr):
                # Create multiple-choice question prompt
                option_list = f"1) {qa['option_1']}\n"
                option_list += f"2) {qa['option_2']}\n"
                option_list += f"3) {qa['option_3']}\n"
                placeholders = [
                    ("[QUESTION_NUM]", str(j + 1)),
                    ("[QUESTION]", qa["question"]),
                    ("[OPTIONS]", option_list),
                ]
                q_prompt = self.get_prompt("exam-question.prompt", placeholders)
                prompt += q_prompt + "\n"

            # Get model response
            raw_response = self.model.generate_content([prompt, report_file])
            json_response = json.loads(raw_response.text)
            results.extend(json_response)

            # Slight delay
            time.sleep(0.1)

            # Save every stepsize
            save_json(results, results_path)

        # Delete file
        genai.delete_file(report_file.name)
        print(f"Deleted {report.display_name}.")

        print(f"Saved results to {results_path}.")
        save_json(results, results_path)

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
        fk = r.flesch_kincaid()
        f = r.flesch()
        dc = r.dale_chall()
        ari = r.ari()
        gf = r.gunning_fog()

        readability_scores = {
            "flesch_kincaid_score": fk.score,
            "flesch_kincaid_grade_level": fk.grade_level,
            "flesch_score": f.score,
            "flesch_ease": f.ease,
            "flesch_grade_levels": f.grade_levels,
            "dale_chall_score": dc.score,
            "dale_chall_grade_levels": dc.grade_levels,
            "ari_score": ari.score,
            "ari_grade_levels": ari.grade_levels,
            "ari_ages": ari.ages,
            "gunning_fog_score": gf.score,
            "gunning_fog_grade_level": gf.grade_level,
        }

        return readability_scores

    def save_results(self, results_id, labels, data):
        results_path = f"../results/{results_id}-metrics.json"
        results_data = {l: d for l, d in zip(labels, data)}
        with open(results_path, "w") as file:
            json.dump(results_data, file, indent=4)
        print(f"Saved results and metrics to {results_path}")

    def run(self, questions: list, report: Report):
        results_id = report.display_name.lower().replace(" ", "-")

        # Get content question answers
        content_results = self.evaluate_content(results_id, questions, report)

        # Compute metrics
        content_metrics = self.calculate_metrics(questions, content_results)
        readability_metrics = self.evaluate_readability(report.text)

        # Save results
        self.save_results(
            results_id,
            ["content_metrics", "readability_metrics"],
            [content_metrics, readability_metrics],
        )


report_reader = ReportReader()
evaluator = Evaluator()

content_questions = load_json("../questions/sample-questions.json")
sample_report = report_reader.get_report(
    "../data/pages/IPCC_SPM_2018-page-7.pdf", "IPPC 2018"
)
evaluator.run(content_questions, sample_report)
