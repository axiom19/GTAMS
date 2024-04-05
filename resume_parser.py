# Description: This file contains the ResumeParser class which is used to parse resumes

# import libraries
from docx import Document
import pdfplumber
import os


class ResumeParser(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_resume(self):
        # Determine the file type and call the appropriate parsing method
        file_extension = os.path.splitext(self.file_path)[1]
        if file_extension.lower() == '.docx':
            return self._parse_docx()
        elif file_extension.lower() == '.pdf':
            return self._parse_pdf()
        else:
            raise ValueError("Unsupported file format. Please use PDF or DOCX.")

    def _parse_docx(self):
        try:
            doc = Document(self.file_path)
            text = [p.text for p in doc.paragraphs]
            return '\n'.join(text)
        except Exception as e:
            # Handle exceptions related to DOCX parsing
            raise Exception(f"Error parsing DOCX file: {e}")

    def _parse_pdf(self):
        try:
            with pdfplumber.open(self.file_path) as pdf:
                text = [page.extract_text() for page in pdf.pages]
                # Filter out None values in case some pages don't have text
                text = filter(None, text)
                return '\n'.join(text)
        except Exception as e:
            # Handle exceptions related to PDF parsing
            raise Exception(f"Error parsing PDF file: {e}")


if __name__ == '__main__':
    # Test parsing a resume
    parser = ResumeParser('resume.pdf')
    print(parser.parse_resume())
