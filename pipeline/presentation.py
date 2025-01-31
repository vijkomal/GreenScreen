from pylatex import Document, Section, Command
from pylatex.utils import NoEscape
import os


class Presentation:
    def __init__(self, slides):
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
        for slide in self.slides:
            doc.append(NoEscape(slide))

        # Output to pdf
        doc.generate_pdf(presentation_path, clean_tex=False)
        print(f"[+] Presentation {sanitized_title} saved to {presentation_path}.")
