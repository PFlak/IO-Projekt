# src/services/pdf_generator.py

import os
import json
import getpass
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from src.config import DATA_DIRECTORY
from src.utils.logger import app_logger

class PDFGenerator:
    @staticmethod
    def _setup_fonts():
        """Configure system fonts with fallbacks for Unicode support"""
        try:
            # Try Arial (common on Windows)
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
            pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))
            return 'Arial', 'Arial-Bold'
        except:
            try:
                # Fallback to Helvetica (common on macOS/Linux)
                pdfmetrics.registerFont(TTFont('Helvetica', 'Helvetica.ttf'))
                pdfmetrics.registerFont(TTFont('Helvetica-Bold', 'Helvetica-Bold.ttf'))
                return 'Helvetica', 'Helvetica-Bold'
            except:
                app_logger.warning("PDFGenerator: Using default fonts - Unicode support may be limited")
                return 'Helvetica', 'Helvetica-Bold'  # ReportLab's built-in fallback

    @staticmethod
    def generate_notes_pdf(ws_name: str):
        """
        Generates a PDF file for the specified workspace with notes in separate sections.
        
        Args:
            ws_name (str): Name of the workspace to process
        """
        ws_path = os.path.join(DATA_DIRECTORY, ws_name)
        options_path = os.path.join(ws_path, 'options.json')
        output_path = os.path.join(ws_path, f"{ws_name}_notes.pdf")

        # Configure fonts
        font_normal, font_bold = PDFGenerator._setup_fonts()

        # Load workspace options
        try:
            with open(options_path, 'r') as f:
                options = json.load(f)
        except Exception as e:
            app_logger.error(f"PDFGenerator: Failed to load options for {ws_name}: {e}")
            return False

        # Get header information
        assistant_name = options.get('assistant_name', 'N/A')
        note_paths = {
            'short': options.get('note_short_path', ''),
            'medium': options.get('note_medium_path', ''),
            'long': options.get('note_long_path', '')
        }

        # Create PDF document with metadata
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=25*mm,
            bottomMargin=15*mm,
            title=ws_name,
            author=getpass.getuser(),
            subject=f"Notes: {ws_name}"
        )

        # Custom styles with system fonts
        styles = getSampleStyleSheet()
        styles['Normal'].fontName = font_normal
        styles['Heading2'].fontName = font_bold
        styles['Heading2'].fontSize = 14
        styles['Heading2'].spaceAfter = 8

        story = []

        # Header template function
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont(font_bold, 10)
            
            # Left-aligned workspace name
            canvas.drawString(15*mm, A4[1] - 20*mm, ws_name)
            
            # Right-aligned assistant name
            canvas.drawRightString(
                A4[0] - 15*mm,
                A4[1] - 20*mm,
                f"Assistant: {assistant_name}"
            )
            canvas.restoreState()

        # Collect valid note types
        valid_notes = []
        for note_type in ['short', 'medium', 'long']:
            note_path = note_paths[note_type]
            if os.path.exists(note_path) and os.path.getsize(note_path) > 0:
                valid_notes.append(note_type)

        # Process each note type
        for idx, note_type in enumerate(valid_notes):
            note_path = note_paths[note_type]
            
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                # Add section header
                story.append(Paragraph(
                    f"{note_type.capitalize()} Notes",
                    styles['Heading2']
                ))
                
                # Add content with proper Unicode handling
                story.append(Paragraph(
                    content.replace('\n', '<br/>'),
                    styles['Normal']
                ))

                # Add page break if not last item
                if idx != len(valid_notes) - 1:
                    story.append(PageBreak())

            except Exception as e:
                app_logger.error(f"PDFGenerator: Failed to process {note_type} notes for {ws_name}: {e}")

        # Generate PDF if there's content
        if story:
            try:
                doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)
                app_logger.info(f"PDFGenerator: Successfully generated PDF for {ws_name}")
                return True
            except Exception as e:
                app_logger.error(f"PDFGenerator: PDF creation failed for {ws_name}: {e}")
                return False

        app_logger.warning(f"PDFGenerator: No valid notes found for {ws_name}")
        return False