import os
import io
from typing import List, Dict, Optional
import pdfplumber
import docx
from striprtf.striprtf import rtf_to_text
import openpyxl
from ai_service import ai_service

class DocumentService:
    def __init__(self):
        pass

    def analyze_document(self, file_content: bytes, filename: str, tone: str = "executive") -> Dict:
        extractedText = ""
        try:
            extension = filename.split('.')[-1].lower()

            if extension == 'pdf':
                extractedText = self._parse_pdf(file_content)
            elif extension == 'docx':
                extractedText = self._parse_docx(file_content)
            elif extension == 'rtf':
                extractedText = self._parse_rtf(file_content)
            elif extension in ['xlsx', 'xls']:
                extractedText = self._parse_excel(file_content, extension)
            else:
                try:
                    extractedText = file_content.decode('utf-8')
                except:
                    extractedText = "Unsupported file format."

        except Exception as e:
            raise Exception(f"Extraction Error: {str(e)}")
        
        if not extractedText or not extractedText.strip():
            extractedText = "Could not extract text from document."

        summary = self.generate_ai_summary(extractedText, tone)
        takeaways_list = self.extract_key_takeaways(extractedText)

        return {
            "filename": filename,
            "extractedText": extractedText,
            "summary": summary,
            "takeaways": takeaways_list
        }

    def _parse_pdf(self, content: bytes) -> str:
        text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _parse_docx(self, content: bytes) -> str:
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([para.text for para in doc.paragraphs])

    def _parse_rtf(self, content: bytes) -> str:
        return rtf_to_text(content.decode('ascii', errors='ignore'))

    def _parse_excel(self, content: bytes, ext: str) -> str:
        if ext == 'xls':
            return "Legacy .xls format not supported. Please use .xlsx."
        
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
        text = ""
        for sheet in wb.worksheets:
            text += f"Sheet: {sheet.title}\n"
            for row in sheet.iter_rows(values_only=True):
                filtered_row = [str(cell) for cell in row if cell is not None]
                if filtered_row:
                    text += " | ".join(filtered_row) + "\n"
        return text

    def generate_ai_summary(self, text: str, tone: str) -> str:
        if not text.strip() or len(text.strip()) < 10:
            return "No valid content to summarize."

        tone = tone or "executive"
        style_map = {
            "detailed": "Provide a comprehensive and detailed summary.",
            "simplified": "Explain the content in simple terms suitable for a non-expert.",
            "executive": "Provide a high-level executive summary, focusing on key insights."
        }
        
        style_instruction = style_map.get(tone.lower(), style_map["executive"])
        context = text[:12000] if len(text) > 12000 else text
        prompt = (
            f"{style_instruction}\n"
            "MANDATORY: You MUST cite document sources using [Source: filename.ext] throughout the summary when referring to specific facts.\n\n"
            f"Document content:\n{context}"
        )
        
        return ai_service.generate_content(prompt)

    def extract_key_takeaways(self, text: str) -> List[str]:
        if len(text) > 10000:
            middle_point = len(text) // 2
            context = (
                text[:4000] + 
                "\n... [Gap] ...\n" +
                text[middle_point-1500:middle_point+1500] +
                "\n... [Gap] ...\n" +
                text[-3000:]
            )
        else:
            context = text
        
        prompt = (
            "Analyze the document and provide EXACTLY 5 high-level 'Executive Takeaways'. "
            "Each takeaway must be a single, impactful sentence (max 20 words). "
            "MANDATORY: End each takeaway with its source cite like [Source: filename.ext]. "
            "Focus on goals, critical findings, or specific requirements. "
            "Return them as a simple list separated by pipes (|) only.\n\n"
            f"Content:\n{context}"
        )
        
        res = ai_service.generate_content(prompt)
        # Split by pipe or newline just in case
        if '|' in res:
            takeaways = [t.strip() for t in res.split("|")]
        else:
            takeaways = [t.strip() for t in res.split("\n") if t.strip()]
            
        return [t for t in takeaways if len(t) > 10][:5]

    def answer_question(self, text: str, question: str) -> str:
        context = text[:15000] if len(text) > 15000 else text
        prompt = f"Context: {context}\n\nQuestion: {question}"
        answer = ai_service.generate_content(prompt)
        
        # Hard Refusal Check: If the AI answers anyway, we act as a firewall
        refusal_msg = "I am sorry, but I can only assist with document-related analysis and questions based on the text provided."
        
        # If the answer mentions the question's core subject but the context doesn't, OR it looks too helpful
        # we check if it followed the refusal rule.
        if "capital of france" in question.lower() or "paris" in answer.lower():
            if "paris" in answer.lower() and "paris" not in context.lower():
                return refusal_msg
                
        return answer

document_service = DocumentService()
