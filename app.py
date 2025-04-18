import gradio as gr
import os
import tempfile

from pipeline import utils
from pipeline.report_reader import ReportReader, Report
from pipeline.slides import SlidesGenerator, Slide
from pipeline.presentation import Presentation


# report_reader = ReportReader()
# report = report_reader.get_report(report_path, title)


def process_input(pdf_file, text_input, use_readability, grade_level, format_type):
    report_reader = ReportReader()
    output_path = None
    if pdf_file is not None:
        report = report_reader.get_report_from_object(pdf_file, "Uploaded Report")
        content = report.text

        slide_generator = SlidesGenerator()
        slides = [
            slide_generator.make_raw_slide(section) for section in report.sections
        ]

        title = "Generated Report"
        presentation = Presentation(slides=slides)
        presentation.create_presentation(
            title=title,
            presentation_name=f"generated",
            output_dir="temp",
        )
        output_path = "temp/generated/generated.pdf"

    elif text_input.strip():
        content = text_input

    return output_path, content


def show_pdf(pdf_path):
    if pdf_path is None:
        return "<p>Please upload a PDF file</p>"

    # Get the file path for embedding
    file_path = pdf_path.name if hasattr(pdf_path, "name") else pdf_path

    # Create HTML with embedded PDF viewer
    html_content = f"""
    <div style="display: flex; justify-content: center;">
        <embed src="file={file_path}" type="application/pdf" width="800px" height="600px" />
    </div>
    """
    return html_content


# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# GreenScreen")

    with gr.Row():
        # Left column - Input options
        with gr.Column():
            gr.Markdown("### Input")
            pdf_file = gr.File(label="Upload PDF", file_types=[".pdf"])
            text_input = gr.Textbox(
                label="Or enter text directly",
                lines=5,
                placeholder="Type your text here...",
            )

        # Right column - Processing options
        with gr.Column():
            gr.Markdown("### Options")

            with gr.Row():
                use_readability = gr.Checkbox(label="Adjust Readability", value=False)
                grade_level = gr.Slider(
                    minimum=1, maximum=20, step=1, value=8, label="Grade Level (1-20)"
                )

            format_type = gr.Radio(
                choices=["mainly visual", "mainly auditory", "mainly structured"],
                label="Format",
                value="mainly structured",
            )

            generate_btn = gr.Button("Generate", variant="primary")

    # Output row
    with gr.Row():
        # output_pdf = gr.File(label="Generated PDF")

        output_pdf = gr.File(label="Generated PDF")
        html_output = gr.HTML()
        output_pdf.change(fn=show_pdf, inputs=output_pdf, outputs=html_output)

        # output_pdf = gr.PDF()
        output_message = gr.Textbox(label="Status")

    # Set up the event handler
    # generate_btn.click(
    #     fn=process_input,
    #     inputs=[pdf_file, text_input, use_readability, grade_level, format_type],
    #     outputs=[output_pdf, output_message],
    # )
    generate_btn.click(
        fn=process_input,
        inputs=[pdf_file, text_input, use_readability, grade_level, format_type],
        outputs=[output_pdf, output_message],
    )

# Launch the app
demo.launch()
