from pylatex import Document, Section, Command
from pylatex.utils import NoEscape
import os
from slides import Slide


class Presentation:
    def __init__(self, slides: Slide):
        self.slides = slides

    def create_presentation(self, title, output_dir):
        # create project folder
        sanitized_title = title.replace(" ", "-").lower()
        presentation_dir = os.path.join(output_dir, sanitized_title)
        presentation_path = os.path.join(presentation_dir, f"{sanitized_title}")
        os.makedirs(presentation_dir, exist_ok=True)

        # Create beamer presentation
        doc = Document(documentclass="beamer")
        doc.append(NoEscape(r"\setbeamertemplate{navigation symbols}{}"))

        # Add the title, author, and date
        doc.preamble.append(Command("title", title))
        doc.preamble.append(Command("date", Command("today")))
        doc.append(Command("maketitle"))

        # Add slides
        transcript = ""
        for i, slide in enumerate(self.slides):
            transcript += f"# SLIDE {i}\n"
            transcript += slide.transcript + "\n\n"
            doc.append(NoEscape(slide.latex))

        # Output to pdf
        doc.generate_pdf(presentation_path, clean_tex=False)
        transcript_path = presentation_path + ".txt"
        with open(transcript_path, "w") as f:
            f.write(transcript)
        print(f"[+] Presentation {sanitized_title} saved to {presentation_path}.")
        print(f"[+] Transcript saved to {transcript_path}.")
