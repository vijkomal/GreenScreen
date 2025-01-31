from report_reader import ReportReader
from slides import Slides
from presentation import Presentation


def main():
    report_path = "../data/pages/IPCC_SPM_2018-page-7.pdf"
    reader = ReportReader(report_path)
    report_sections = reader.get_labeled_sections()
    with open("../playground/section.txt", "w") as f:
        f.write(report_sections[-1])

    slide_generator = Slides()
    slides = [slide_generator.get_slide_latex(section) for section in report_sections]

    presentation = Presentation(slides=slides)
    presentation.create_presentation(
        title="end-to-end",
        output_dir="../output",
    )


if __name__ == "__main__":
    main()
