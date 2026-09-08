#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os

def create_pdf():
    """Generate KUROKO G-A-2 May 16 Primary Artifact Verification Report as PDF"""

    output_path = "/home/user/MoCKA/reports/KUROKO_G-A-2_MAY16_PRIMARY_ARTIFACT_VERIFICATION_REVISED.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2d5aa0'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )

    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#3d6ab8'),
        spaceAfter=6,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )

    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['BodyText'],
        fontSize=8,
        spaceAfter=6,
        fontName='Courier'
    )

    story = []

    # Title
    story.append(Paragraph("KUROKO G-A-2: May 16 Primary Artifact Verification Report", title_style))
    story.append(Spacer(1, 0.2*inch))

    # Metadata
    metadata_data = [
        ['Investigation ID:', 'KUROKO-GA2-MAY16-20260907'],
        ['Investigation Date:', '2026-09-07'],
        ['Primary Artifact:', 'TODO_147 (Relay Project)'],
        ['Artifact Creation:', '2026-05-16T10:20:27.298613'],
        ['Temporal Focus:', 'May 16, 2026'],
    ]

    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4788')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.3*inch))

    # Chapter 1
    story.append(Paragraph("Chapter 1: Evidence Correction & Methodology Note", heading2_style))
    story.append(Paragraph("Prior Identification Error", heading3_style))
    story.append(Paragraph(
        "Initial G-A investigation incorrectly identified TODO_169 (Orchestra) instead of TODO_147 (Relay) as the Relay project inception artifact. This error has been corrected, and all subsequent analysis uses TODO_147 as the correct primary artifact.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))

    # Six-Item Verification Matrix Summary
    story.append(Paragraph("Chapter 3: May 16 Six-Item Independent Verification Matrix Summary", heading2_style))

    matrix_data = [
        ['Item', 'Classification (May 16-Specific)', 'Confidence', 'Key Evidence'],
        ['1. Relay Existence', 'CONFIRMED', 'HIGH', 'TODO_147 record exists at May 16'],
        ['2. Handoff Concept', 'UNKNOWN', 'N/A', 'Current record contains text; field-level timing unknown'],
        ['3. Logbook Concept', 'UNKNOWN', 'MEDIUM', 'Not in May 16 record'],
        ['4. LB_001 Identifier', 'NOT FOUND', 'HIGH', 'No May 16 evidence; operational by May 31'],
        ['5. Predecessor System', 'NOT_FOUND_IN_EXAMINED_EVIDENCE', 'HIGH', 'Absence does not prove non-existence'],
        ['6A. Independent Implementation', 'UNKNOWN', 'N/A', 'Current record contains statement; field-level timing unknown'],
        ['6B-6D. Inheritance / Source', 'UNKNOWN', 'N/A', 'No evidence chain established'],
    ]

    matrix_table = Table(matrix_data, colWidths=[1.8*inch, 1.8*inch, 0.8*inch, 1.6*inch])
    matrix_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 0.2*inch))

    # Key Finding
    story.append(Paragraph("Chapter 5: Key Finding - mini MoCKA Series 製品2 Origin", heading2_style))
    story.append(Paragraph(
        "<b>Verdict: STRONGLY_SUPPORTED_AS_MAY16_CONTEXT</b>",
        body_style
    ))
    story.append(Paragraph(
        "The phrase 'mini MoCKA Series 製品2「Relay」' appears in the current record at created_at timestamp May 16 (not a June 1 addition). This strongly suggests May 16 product conception. However, field-level modification history is not available, so field-level timing cannot be independently verified. Contextual evidence is strong; absolute proof awaits field-level history.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))

    # Unresolved Unknowns
    story.append(Paragraph("Chapter 11: Uncertainty Preservation - Unresolved Questions", heading2_style))
    story.append(Paragraph(
        "The following questions remain UNKNOWN and require further investigation:",
        body_style
    ))

    unknowns_list = """
    <br/>1. <b>Handoff concept field-level timing:</b> Was description text present on May 16, or added later? (field-level history unavailable)
    <br/>2. <b>Independent implementation statement timing:</b> Was this statement in description on May 16? (field-level history unavailable)
    <br/>3. <b>LB_* naming origin:</b> When did LB_001 first emerge? May 16? May 20? May 31?
    <br/>4. <b>Logbook concept detail:</b> Was explicit logbook architecture designed May 16 or May 16-31?
    <br/>5. <b>Ultimate source:</b> What prior design or product inspired LB_* or handoff architecture?
    <br/>6. <b>Prerequisite mechanism:</b> Did Relay derive from prior product concepts?
    """
    story.append(Paragraph(unknowns_list, body_style))
    story.append(Spacer(1, 0.2*inch))

    # Next Steps
    story.append(Paragraph("Chapter 12: Evidence-Based Next Investigation Branches", heading2_style))
    story.append(Paragraph(
        "Four prioritized investigation branches are recommended:",
        body_style
    ))

    next_steps_list = """
    <br/><b>Priority 1:</b> Git archaeology for relay-logbook.js first commit (identify LB_* naming origin)
    <br/><b>Priority 2:</b> Design document search for May 16 logbook architecture
    <br/><b>Priority 3:</b> TODO timeline comparison for product series verification
    <br/><b>Priority 4:</b> Pre-May-16 code search for LB_* identifier usage
    """
    story.append(Paragraph(next_steps_list, body_style))
    story.append(Spacer(1, 0.2*inch))

    # Conclusion
    story.append(Paragraph("Chapter 15: G-A-2 Conclusion & Audit Judgment Request", heading2_style))
    story.append(Paragraph(
        "The G-A-2 May 16 Primary Artifact Verification investigation has completed the six-item classification matrix with clear CONFIRMED/STRONGLY SUPPORTED/UNKNOWN distinctions. The temporal separation of May 16 original evidence from June 1 retrospective updates has been rigorously maintained.",
        body_style
    ))
    story.append(Paragraph(
        "This report awaits audit judgment from きむら博士 and the review authority to determine: (1) methodological soundness, (2) evidence classification appropriateness, (3) next investigation branch authorization.",
        body_style
    ))
    story.append(Spacer(1, 0.3*inch))

    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        f"Report Generated: 2026-09-07 | Status: AWAITING AUDIT JUDGMENT",
        footer_style
    ))

    # Build PDF
    doc.build(story)
    print(f"PDF generated successfully: {output_path}")

    # Print file info
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"File size: {file_size} bytes")

if __name__ == "__main__":
    create_pdf()
