from report_reader import ReportReader, Report
from slides import SlidesGenerator, Slide
from presentation import Presentation
from evaluator import Evaluator
from utils import load_json, save_json
import time


def generate_baseline_original_report():
    report_path = "../data/IPCC_SPM_2018.pdf"
    report_reader = ReportReader()
    report = report_reader.get_report(report_path, "IPCC-2018-Original")

    # Get Slides
    slide_generator = SlidesGenerator()
    slides = [slide_generator.make_raw_slide(section) for section in report.sections]

    title = "IPCC, 2018: Summary for Policymakers. Global Warming of 1.5°C. An IPCC Special Report"
    presentation = Presentation(slides=slides)
    presentation.create_presentation(
        title=title,
        presentation_name="ipcc-2018-original",
        output_dir="../output",
    )


def evaluate_baseline_original_report(year=2018):
    # Load report
    report_path = f"../data/IPCC_SPM_{year}.pdf"
    report_reader = ReportReader()
    report = report_reader.get_report(report_path, f"IPCC-{year}-Original")

    # Get Metrics
    evaluator = Evaluator()
    content_questions = load_json(f"../questions/QA_bank_{year}.json")
    evaluator.run(content_questions, report)


def generate_presentation(prompt_name):
    report_path = "../data/IPCC_SPM_2018.pdf"
    report_reader = ReportReader()
    report = report_reader.get_report(report_path, "IPCC 2018")

    slide_generator = SlidesGenerator()

    slides = []
    for i in range(5, 10):
        sample_slide = slide_generator.make_slide(
            prompt_name, [("TEXT", report.sections[i])]
        )
        slides.append(sample_slide)
        time.sleep(1)

    title = "IPCC, 2018: Summary for Policymakers. Global Warming of 1.5°C. An IPCC Special Report"
    presentation = Presentation(slides=slides)
    presentation.create_presentation(
        title=title,
        presentation_name="IPCC-2018-Vanilla",
        output_dir="../output",
    )


##### MAIN
# generate_presentation(prompt_name="slide-vanilla.prompt")
# generate_baseline_original_report()
