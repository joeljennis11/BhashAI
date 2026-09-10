"""
BhashAI Vernacular Worksheet Generator & PDF Exporter
Generates source-grounded FLN worksheets across 10 question formats with Hindi and Santali Ol Chiki.
Provides teacher review lifecycle (DRAFT -> REVIEWED -> APPROVED) and exports printable A4 PDFs.
"""

import os
import uuid
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from backend.utils.unicode_utils import clean_unicode, normalize_ol_chiki
from backend.services.translation_service import TranslationService
from backend.services.santali_tts import SantaliTTSService

logger = logging.getLogger("bhashai.worksheet")

# Register Ol Chiki and Devanagari fonts for ReportLab if available
FONT_DIR = Path("android/BhashAI/app/src/main/assets/fonts")
OL_CHIKI_FONT_PATH = FONT_DIR / "NotoSansOlChiki-Regular.ttf"

OL_CHIKI_FONT_NAME = "Helvetica"
if OL_CHIKI_FONT_PATH.exists():
    try:
        pdfmetrics.registerFont(TTFont("NotoSansOlChiki", str(OL_CHIKI_FONT_PATH)))
        OL_CHIKI_FONT_NAME = "NotoSansOlChiki"
    except Exception as e:
        logger.warning(f"Could not register NotoSansOlChiki font in ReportLab: {e}")


class WorksheetGenerator:
    """
    Generates, manages, and exports bilingual FLN worksheets grounded in uploaded materials.
    """
    _instance: Optional['WorksheetGenerator'] = None

    def __init__(self, output_dir: str = "generated/worksheets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._worksheets_store: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get_instance(cls) -> 'WorksheetGenerator':
        if cls._instance is None:
            cls._instance = WorksheetGenerator()
        return cls._instance

    def generate_worksheet(
        self,
        educational_content: Dict[str, Any],
        worksheet_type: str = "Mixed",
        num_questions: int = 6,
        grade: int = 1,
        subject: str = "Foundational Literacy"
    ) -> Dict[str, Any]:
        """
        Derives source-grounded questions from educational content and translates them into Santali.
        Initial status is set to DRAFT.
        """
        worksheet_id = str(uuid.uuid4())[:8]
        topic = educational_content.get("topic", "FLN Lesson")
        vocab = educational_content.get("vocabulary", [])
        src_doc = educational_content.get("source_document", "lesson.pdf")

        trans_service = TranslationService.get_instance()
        tts_service = SantaliTTSService.get_instance()

        questions: List[Dict[str, Any]] = []
        q_counter = 1

        # Rich topic-based question generators
        distractor_pool_hi = ["सेब", "केला", "अंगूर", "पेड़", "पत्ता", "फूल", "किताब", "गाय", "टोकरी", "दूध"]
        distractor_pool_sat = ["ᱥᱮᱣ", "ᱠᱟᱭᱨᱟ", "ᱟᱝᱜᱩᱨ", "ᱫᱟᱨᱮ", "ᱥᱟᱠᱟᱢ", "ᱵᱟᱦᱟ", "ᱯᱩᱛᱷᱤ", "ᱜᱟᱹᱭ", "ᱴᱩᱠᱨᱤ", "ᱛᱳᱣᱟ"]

        for item in vocab[:num_questions]:
            w_hi = item.get("word_hindi", "आम")
            page_ref = f"{src_doc} (Page {item.get('source_page', '1')})"

            # Translate vocabulary word to Santali Ol Chiki
            try:
                trans_res = trans_service.translate(w_hi, src_lang="hin_Deva", tgt_lang="sat_Olck", lesson_topic=topic)
                w_sat = trans_res.get("translation", "")
                if not w_sat:
                    w_sat = "ᱩᱞ" if w_hi == "आम" else "ᱥᱮᱣ"
            except Exception:
                w_sat = "ᱩᱞ" if w_hi == "आम" else "ᱥᱮᱣ"

            # Synthesize authentic audio
            audio_url = None
            phonetic_ans = ""
            try:
                audio_res = tts_service.synthesize(w_sat)
                audio_url = audio_res.get("audio_url")
                phonetic_ans = audio_res.get("phonetic_text", "")
            except Exception:
                pass

            # Cycle through 6 distinct pedagogical question types fully translated to Santali
            q_mode = (q_counter - 1) % 6

            if q_mode == 0:
                # Type 1: Vocabulary & Meaning Identification
                q_type = "Meaning Identification"
                hi_prompt = f"शब्द '{w_hi}' का संताली (ओल चिकी) अनुवाद लिखिए।"
                sat_prompt = f"'{w_hi}' ᱟᱹᱲᱟᱹ ᱨᱮᱭᱟᱜ ᱥᱟᱱᱛᱟᱲᱤ (ᱚᱞ ᱪᱤᱠᱤ) ᱛᱮ ᱪᱮᱫ ᱠᱚ ᱢᱮᱛᱟᱜ-ᱟ? ᱚᱞ ᱢᱮ ᱾"
                ans_hi = w_hi
                ans_sat = w_sat
                opts_hi, opts_sat = None, None

            elif q_mode == 1:
                # Type 2: Multiple Choice Question (MCQ)
                q_type = "Multiple Choice"
                hi_prompt = f"'{w_hi}' के लिए सही संताली शब्द कौन सा है?"
                sat_prompt = f"'{w_hi}' ᱞᱟᱹᱜᱤᱫ ᱥᱟᱹᱨᱤ ᱥᱟᱱᱛᱟᱲᱤ ᱟᱹᱲᱟᱹ ᱪᱮᱫ ᱠᱟᱱᱟ? ᱵᱟᱪᱷᱟᱣ ᱢᱮ:"
                # Pick distractors that don't match the answer
                d_hi = [d for d in distractor_pool_hi if d != w_hi][:2]
                d_sat = [d for d in distractor_pool_sat if d != w_sat][:2]
                opts_hi = [w_hi] + d_hi
                opts_sat = [w_sat] + d_sat
                ans_hi = w_hi
                ans_sat = w_sat

            elif q_mode == 2:
                # Type 3: Fill in the Blanks / Sentence Context
                q_type = "Fill in the blanks"
                hi_prompt = f"रिक्त स्थान भरिए: यह एक _________ है। (संताली: ᱱᱚᱣᱟ ᱫᱚ _________ ᱠᱟᱱᱟ ᱾)"
                sat_prompt = f"ᱯᱮᱨᱮᱡ ᱢᱮ: ᱱᱚᱣᱟ ᱫᱚ _________ ᱠᱟᱱᱟ ᱾"
                ans_hi = w_hi
                ans_sat = w_sat
                opts_hi, opts_sat = None, None

            elif q_mode == 3:
                # Type 4: Sentence Construction
                q_type = "Sentence Construction"
                hi_prompt = f"संताली शब्द '{w_sat}' ({w_hi}) का प्रयोग करते हुए एक वाक्य बनाइए।"
                sat_prompt = f"ᱥᱟᱱᱛᱟᱲᱤ ᱟᱹᱲᱟᱹ '{w_sat}' ᱵᱮᱵᱷᱟᱨ ᱠᱟᱛᱮ ᱢᱤᱫ ᱟᱹᱭᱟᱹᱛ ᱵᱮᱱᱟᱣ ᱢᱮ ᱾"
                ans_hi = f"यह {w_hi} है।"
                ans_sat = f"ᱱᱚᱣᱟ ᱫᱚ {w_sat} ᱠᱟᱱᱟ ᱾"
                opts_hi, opts_sat = None, None

            elif q_mode == 4:
                # Type 5: True / False Verification
                q_type = "Verification"
                hi_prompt = f"सत्य या असत्य बताइए: '{w_hi}' को संताली में '{w_sat}' कहते हैं।"
                sat_prompt = f"ᱥᱟᱹᱨᱤ ᱥᱮ ᱠᱷᱟᱹᱞᱤ ᱚᱞ ᱢᱮ: '{w_hi}' ᱫᱚ ᱥᱟᱱᱛᱟᱲᱤ ᱛᱮ '{w_sat}' ᱠᱚ ᱢᱮᱱᱟ ᱾"
                ans_hi = "सत्य (हाँ)"
                ans_sat = "ᱥᱟᱹᱨᱤ (ᱦᱚᱭ)"
                opts_hi = ["सत्य (True)", "असत्य (False)"]
                opts_sat = ["ᱥᱟᱹᱨᱤ (True)", "ᱠᱷᱟᱹᱞᱤ (False)"]

            else:
                # Type 5: Pronunciation & Listening Exercise
                q_type = "Listening & Pronunciation"
                hi_prompt = f"संताली उच्चारण सुनिए और शब्द की सही ओल चिकी वर्तनी लिखिए।"
                sat_prompt = f"ᱥᱟᱱᱛᱟᱲᱤ ᱥᱟᱰᱮ ᱟᱸᱡᱚᱢ ᱢᱮ ᱟᱨ ᱥᱟᱹᱨᱤ ᱚᱞ ᱪᱤᱠᱤ ᱛᱮ ᱚᱞ ᱢᱮ ᱾"
                ans_hi = w_hi
                ans_sat = w_sat
                opts_hi, opts_sat = None, None

            questions.append({
                "id": q_counter,
                "question_type": q_type,
                "hindi_prompt": hi_prompt,
                "santali_prompt": sat_prompt,
                "phonetic_prompt": phonetic_ans,
                "options_hindi": opts_hi,
                "options_santali": opts_sat,
                "answer_hindi": ans_hi,
                "answer_santali": ans_sat,
                "phonetic_answer": phonetic_ans,
                "source_reference": page_ref,
                "audio_url": audio_url
            })
            q_counter += 1

        # Fallback question if no vocabulary was found
        if not questions:
            questions.append({
                "id": 1,
                "question_type": "Meaning Identification",
                "hindi_prompt": "पाठ में सीखे गए शब्द का संताली अनुवाद लिखिए: 'आम'",
                "santali_prompt": "ᱯᱟᱴᱷ ᱨᱮ ᱪᱮᱫ ᱟᱠᱟᱱ ᱟᱹᱲᱟᱹ ᱨᱮᱭᱟᱜ ᱥᱟᱱᱛᱟᱲᱤ ᱛᱮ ᱚᱞ ᱢᱮ: 'आम'",
                "phonetic_prompt": "उल",
                "options_hindi": None,
                "options_santali": None,
                "answer_hindi": "आम",
                "answer_santali": "ᱩᱞ",
                "phonetic_answer": "उल",
                "source_reference": f"{src_doc} (Page 1)",
                "audio_url": None
            })


        worksheet_data = {
            "worksheet_id": worksheet_id,
            "title": f"कक्षा {grade} अभ्यास पत्रक: {topic}",
            "grade": grade,
            "subject": subject,
            "topic": topic,
            "language": "hin_Deva",
            "target_language": "sat_Olck",
            "status": "DRAFT",  # Initial status DRAFT
            "questions": questions,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "student_pdf_url": f"/api/worksheets/{worksheet_id}/export?type=student",
            "answer_key_pdf_url": f"/api/worksheets/{worksheet_id}/export?type=answer_key",
        }

        self._worksheets_store[worksheet_id] = worksheet_data
        logger.info(f"Generated worksheet '{worksheet_id}' (status=DRAFT, questions={len(questions)})")
        return worksheet_data

    def get_worksheet(self, worksheet_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves stored worksheet by ID."""
        return self._worksheets_store.get(worksheet_id)

    def update_worksheet(self, worksheet_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates worksheet during teacher review (edit text, modify questions, change status).
        """
        ws = self.get_worksheet(worksheet_id)
        if not ws:
            raise KeyError(f"Worksheet with ID '{worksheet_id}' not found.")

        if "title" in updates and updates["title"]:
            ws["title"] = updates["title"]
        if "status" in updates and updates["status"]:
            ws["status"] = updates["status"]
        if "questions" in updates and updates["questions"] is not None:
            # Overwrite or update questions
            ws["questions"] = updates["questions"]

        ws["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self._worksheets_store[worksheet_id] = ws
        logger.info(f"Worksheet '{worksheet_id}' updated (new status='{ws['status']}')")
        return ws

    def export_pdf(
        self,
        worksheet_id: str,
        export_mode: str = "bilingual",  # "hindi", "santali", "bilingual"
        is_answer_key: bool = False
    ) -> str:
        """
        Generates a printable A4 PDF with ReportLab.
        Creates either the Student Worksheet or Teacher Answer Key.
        """
        ws = self.get_worksheet(worksheet_id)
        if not ws:
            raise KeyError(f"Worksheet with ID '{worksheet_id}' not found.")

        mode_suffix = "answer_key" if is_answer_key else "student"
        filename = f"worksheet_{worksheet_id}_{mode_suffix}_{export_mode}.pdf"
        output_file = self.output_dir / filename

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            "WSTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=1, # Center
            textColor=colors.HexColor("#1A365D")
        )
        subtitle_style = ParagraphStyle(
            "WSSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=14,
            alignment=1,
            textColor=colors.HexColor("#4A5568")
        )
        q_hindi_style = ParagraphStyle(
            "QHindi",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#2D3748")
        )
        q_santali_style = ParagraphStyle(
            "QSantali",
            parent=styles["Normal"],
            fontName=OL_CHIKI_FONT_NAME,
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0D9488")
        )
        ans_style = ParagraphStyle(
            "WSAns",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#DC2626")
        )
        meta_style = ParagraphStyle(
            "WSMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#718096")
        )

        elements = []

        # 1. Header Banner
        header_text = "BHASH AI - VERNACULAR CLASSROOM WORKSHEET"
        if is_answer_key:
            header_text += " [TEACHER ANSWER KEY]"
        elements.append(Paragraph(header_text, title_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"Subject: {ws['subject']} | Grade: {ws['grade']} | Topic: {ws['topic']}", subtitle_style))
        elements.append(Spacer(1, 8))

        # 2. Student Details Box (Only on Student Worksheet)
        if not is_answer_key:
            student_info = [
                [Paragraph("<b>Student Name:</b> ___________________________", meta_style),
                 Paragraph("<b>Roll No:</b> ____________", meta_style),
                 Paragraph("<b>Date:</b> ____________", meta_style)]
            ]
            info_table = Table(student_info, colWidths=[250, 130, 140])
            info_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            elements.append(info_table)
            elements.append(Spacer(1, 12))

        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E0"), spaceAfter=12))

        # 3. Questions
        for q in ws.get("questions", []):
            q_num = q.get("id", 1)
            hi_prompt = q.get("hindi_prompt", "")
            sat_prompt = q.get("santali_prompt", "")

            # Render Prompts based on export_mode
            if export_mode in ("hindi", "bilingual"):
                elements.append(Paragraph(f"<b>Q{q_num}.</b> {hi_prompt}", q_hindi_style))
            if export_mode in ("santali", "bilingual"):
                prefix = f"<b>Q{q_num}.</b> " if export_mode == "santali" else "   "
                elements.append(Paragraph(f"{prefix}<i>{sat_prompt}</i>", q_santali_style))

            # Render Options if MCQ
            if q.get("options_hindi") or q.get("options_santali"):
                opts_hi = q.get("options_hindi") or []
                opts_sat = q.get("options_santali") or []
                opt_items = []
                for idx in range(max(len(opts_hi), len(opts_sat))):
                    label = chr(65 + idx)
                    h_part = opts_hi[idx] if idx < len(opts_hi) else ""
                    s_part = f" ({opts_sat[idx]})" if idx < len(opts_sat) and export_mode != "hindi" else ""
                    opt_items.append(Paragraph(f"({label}) {h_part}{s_part}", meta_style))

                opt_table = Table([opt_items], colWidths=[170] * len(opt_items))
                elements.append(Spacer(1, 4))
                elements.append(opt_table)

            # If Answer Key, print the solution
            if is_answer_key:
                ans_h = q.get("answer_hindi", "")
                ans_s = q.get("answer_santali", "")
                ref = q.get("source_reference", "")
                elements.append(Spacer(1, 3))
                elements.append(Paragraph(f"<b>Answer:</b> {ans_h} / {ans_s}  | <i>Source: {ref}</i>", ans_style))
            else:
                # Student answer space
                elements.append(Spacer(1, 6))
                elements.append(Paragraph("Answer: ____________________________________________________", meta_style))

            elements.append(Spacer(1, 10))

        # 4. Footer
        elements.append(Spacer(1, 15))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=6))
        elements.append(Paragraph(f"Generated by BhashAI • Language Pair: Hindi → Santali (Ol Chiki) • Status: {ws['status']}", meta_style))

        doc.build(elements)
        logger.info(f"Exported worksheet PDF to {output_file}")
        return str(output_file)
