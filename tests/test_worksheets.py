"""
Unit tests for BhashAI Document Processing & Vernacular Worksheet Generation
Contains 5 verification tests.
"""

import os
import unittest
from pathlib import Path

from backend.services.document_processor import DocumentProcessor
from backend.services.worksheet_generator import WorksheetGenerator


class TestWorksheetPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.doc_proc = DocumentProcessor.get_instance()
        cls.ws_gen = WorksheetGenerator.get_instance()
        cls.sample_pdf = "sample_materials/class1_fruits_hindi.pdf"

    def test_01_pdf_processing_extraction(self):
        """Extracts text and metadata from sample curriculum PDF."""
        self.assertTrue(os.path.exists(self.sample_pdf), "Sample PDF must exist.")
        res = self.doc_proc.process_pdf(self.sample_pdf, filename="class1_fruits_hindi.pdf")
        self.assertIn("document_id", res)
        self.assertGreater(res["extracted_text_length"], 50)
        self.assertIn("content", res)

    def test_02_educational_content_structure(self):
        """Validates FLN educational content schema and vocabulary extraction."""
        doc = self.doc_proc.process_pdf(self.sample_pdf, filename="class1_fruits_hindi.pdf")
        content = doc["content"]
        self.assertEqual(content["grade"], 1)
        self.assertIn("Fruits", content["topic"])
        self.assertIsInstance(content["vocabulary"], list)
        self.assertGreater(len(content["vocabulary"]), 0)

    def test_03_worksheet_generation_draft(self):
        """Generates source-grounded worksheet with DRAFT initial status."""
        doc = self.doc_proc.process_pdf(self.sample_pdf, filename="class1_fruits_hindi.pdf")
        ws = self.ws_gen.generate_worksheet(
            educational_content=doc["content"],
            num_questions=4,
            grade=1
        )
        self.assertEqual(ws["status"], "DRAFT")
        self.assertEqual(len(ws["questions"]), 4)
        for q in ws["questions"]:
            self.assertIn("hindi_prompt", q)
            self.assertIn("santali_prompt", q)
            self.assertIsNotNone(q["source_reference"])

    def test_04_teacher_review_workflow(self):
        """Teacher can edit and approve worksheet (DRAFT -> APPROVED)."""
        doc = self.doc_proc.process_pdf(self.sample_pdf, filename="class1_fruits_hindi.pdf")
        ws = self.ws_gen.generate_worksheet(educational_content=doc["content"], num_questions=2)
        ws_id = ws["worksheet_id"]

        updated = self.ws_gen.update_worksheet(
            worksheet_id=ws_id,
            updates={"status": "APPROVED", "title": "कक्षा 1 संताली कार्यपत्रक - स्वीकृत"}
        )
        self.assertEqual(updated["status"], "APPROVED")
        self.assertIn("स्वीकृत", updated["title"])

    def test_05_pdf_export_student_and_answer_key(self):
        """Exports printable A4 PDF for both student worksheet and teacher answer key."""
        doc = self.doc_proc.process_pdf(self.sample_pdf, filename="class1_fruits_hindi.pdf")
        ws = self.ws_gen.generate_worksheet(educational_content=doc["content"], num_questions=3)
        ws_id = ws["worksheet_id"]

        # Export Student Worksheet
        student_pdf = self.ws_gen.export_pdf(ws_id, export_mode="bilingual", is_answer_key=False)
        self.assertTrue(os.path.exists(student_pdf))
        self.assertGreater(os.path.getsize(student_pdf), 1000)

        # Export Answer Key
        answer_key_pdf = self.ws_gen.export_pdf(ws_id, export_mode="bilingual", is_answer_key=True)
        self.assertTrue(os.path.exists(answer_key_pdf))
        self.assertGreater(os.path.getsize(answer_key_pdf), 1000)


if __name__ == "__main__":
    unittest.main()
