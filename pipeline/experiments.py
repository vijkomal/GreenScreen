from report_reader import ReportReader, Report
from slides import SlidesGenerator, Slide
from presentation import Presentation
from evaluator import Evaluator
from utils import load_json, save_json
import time
from tqdm import tqdm


def generate_baseline_original_report(year="2018"):
    report_path = f"../data/IPCC_SPM_{year}.pdf"
    report_reader = ReportReader()
    report = report_reader.get_report(report_path, f"IPCC-{year}-Copy-Paste")

    # Get Slides
    slide_generator = SlidesGenerator()
    slides = [slide_generator.make_raw_slide(section) for section in report.sections]

    title = f"IPCC, {year}: Summary for Policymakers."
    presentation = Presentation(slides=slides)
    presentation.create_presentation(
        title=title,
        presentation_name=f"ipcc-{year}-copy-paste",
        output_dir="../output",
    )


def evaluate_report(report_path, title, year, readability=True):
    # Load report
    report_reader = ReportReader()
    report = report_reader.get_report(report_path, title)

    # Get Metrics
    evaluator = Evaluator()
    content_questions = load_json(f"../questions/QA_bank_{year}.json")
    evaluator.run(content_questions, report, readability)


def generate_presentation(prompt_name, presentation_name, year):
    report_path = f"../data/IPCC_SPM_{year}.pdf"
    report_reader = ReportReader()
    report = report_reader.get_report(report_path, f"IPCC {year}")

    slide_generator = SlidesGenerator()

    slides = []
    print(len(report.sections))
    start = 125
    step_size = 3
    print(f"Index {start}-{start+step_size}")
    for i in range(start, start + step_size):
        sample_slide = slide_generator.make_slide(
            prompt_name, [("TEXT", report.sections[i])]
        )
        slides.append(sample_slide)
        time.sleep(2)

    # Save latex
    latex_frame_code_path = f"../output/{presentation_name}.latex"
    latex_frame_code = "\n".join([s.latex_content for s in slides])
    with open(latex_frame_code_path, "a") as f:
        f.write(latex_frame_code)

    # title = "IPCC, 2018: Summary for Policymakers. Global Warming of 1.5°C. An IPCC Special Report"
    # presentation = Presentation(slides=slides)
    # presentation.create_presentation(
    #     title=title,
    #     presentation_name=presentation_name,
    #     output_dir="../output",
    # )


##### MAIN
# generate_presentation("slide-vanilla.prompt", "IPCC-2018-Vanilla")
# generate_presentation("slide-readable.prompt", "IPCC-2018-Readable")
# generate_presentation("slide-graphic.prompt", "IPCC-2018-Graphic")
# generate_baseline_original_report()

### CREATE AND EVALUATE

# ### BLANK
evaluate_report(
    "../presentations/blank.pdf", "IPCC-2019-blank", "2019", readability=False
)

### 2018
# generate_baseline_original_report(year="2018")
# evaluate_report("../data/IPCC_SPM_2018.pdf", "IPCC-2018-Original", "2018")
# evaluate_report(
#     "../output/ipcc-2018-original/ipcc-2018-copy-paste.pdf",
#     "IPCC-2018-copy-paste",
#     "2018",
# )
# evaluate_report(
#     "../output/IPCC-2018-Readable/ipcc-2018-readable.pdf",
#     "IPCC-2018-readable",
#     "2018",
# )


#### 2019
# generate_baseline_original_report(year="2019")
# evaluate_report("../data/IPCC_SPM_2019.pdf", "IPCC-2019-Original", "2019")
# evaluate_report(
#     "../output/ipcc-2019-copy-paste/ipcc-2019-copy-paste.pdf",
#     "IPCC-2019-copy-paste",
#     "2019",
# )


# generate_presentation("slide-readable.prompt", "IPCC-2019-Readable", "2019")
# evaluate_report(
#     "../presentations/ipcc-2019-readable.pdf",
#     "IPCC-2019-readable",
#     "2019",
# )
