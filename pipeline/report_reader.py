# report_reader: read and chunk reports

from PyPDF2 import PdfReader
import re


class ReportReader:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        self.text = self._extract_text()

    def _extract_text(self):
        text = ""
        for page in self.reader.pages:
            text += page.extract_text()
        return text

    def clean_section(self, text):
        text = text.strip()
        text = text.replace("\n", " ")
        text = re.sub(r"ﬁ", "fi", text)  # Fix fi ligature
        text = re.sub(r"ﬂ", "fl", text)  # Fix fl ligature
        text = re.sub(r"–", "-", text)  # Replace en dash with hyphen
        text = re.sub(r"—", "-", text)  # Replace em dash with hyphen
        text = re.sub(r"“|”", '"', text)  # Replace curly quotes with straight quotes
        text = re.sub(
            r"‘|’", "'", text
        )  # Replace curly apostrophes with straight apostrophes
        text = re.sub(r'\s([?.!,:;"])', r"\1", text)  # Remove space before punctuation
        text = text.replace("confidenc e", "confidence")
        text = re.sub(
            r"(\w)-\n(\w)", r"\1\2", text
        )  # Fix line breaks between words (e.g. En-viron)
        text = re.sub(r"\s+", " ", text)
        text = text.replace("%", "\\%")
        text = text.replace("{", "\\{")
        text = text.replace("}", "\\}")
        return text

    def get_labeled_sections(self):
        # Regular expression pattern to match section headers (e.g., B.1, B.1.1, etc.)
        pattern = r"(B\.\d+(\.\d+)*\s.*?)(?=B\.\d|\Z)"
        sections = re.findall(pattern, self.text, flags=re.DOTALL)

        # Clean up the sections (remove unwanted extra spaces)
        cleaned_sections = [self.clean_section(section[0]) for section in sections[:3]]
        return cleaned_sections

    def process_section(self, section: str):
        """Returns json object about the section"""
        return
