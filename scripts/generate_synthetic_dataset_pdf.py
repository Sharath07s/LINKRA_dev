"""
Script to generate the LINKRA SIH 2026 Synthetic Dataset PDF.
Creates the PDF in both root and backend/data/pdfs/ directories.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

RAW_SEED_TEXT = """-- LINKRA SIH 2026 SYNTHETIC DATASET
-- FICTIONAL / DEMONSTRATION ONLY
-- Do not treat as real criminal intelligence.

-- This seed is intentionally aligned to the accompanying casebook documents.
-- It assumes the project's existing table names/columns; adapt UUID column casts if required.

BEGIN;

-- Reference data is provided as CSV files. Import through the existing LINKRA ingestion pipeline
-- rather than bypassing application services in production.

-- Illustrative inserts for core domain concepts:
-- investigation: INV-1024 | CASE-1024 | Cross-source cargo theft network analysis | OPEN | HIGH | 2026-06-14 | LOC-001
-- person: ('P-001', 'Ravi Kumar', 'R. Kumar', 'PERSON', 'PH-001', 'LOC-001', 'ORG-001')
-- person: ('P-002', 'Suresh Sharma', 'S. Sharma', 'PERSON', 'PH-002', 'LOC-002', None)
-- person: ('P-003', 'Meera Nair', 'Meera N.', 'PERSON', 'PH-003', 'LOC-003', 'ORG-001')
-- organization: ('ORG-001', 'Metro Logistics', 'Transport / Logistics', 'LOC-004')
-- organization: ('ORG-002', 'Urban Resale Network', 'Retail / Resale', 'LOC-005')
-- vehicle: ('V-001', 'KA01AB1234', 'Toyota', 'Innova', 'White')
-- vehicle: ('V-002', 'KA05XY6789', 'Tata', 'Ace', 'Silver')
-- phone: ('PH-001', '+91-90000-10001', 'P-001')
-- phone: ('PH-002', '+91-90000-10002', 'P-002')
-- phone: ('PH-003', '+91-90000-10003', 'P-003')
-- location: ('LOC-001', 'Peenya Industrial Area', 'Bengaluru', 'Bengaluru Urban', 'Karnataka')
-- location: ('LOC-002', 'Yeshwanthpur', 'Bengaluru', 'Bengaluru Urban', 'Karnataka')
-- location: ('LOC-003', 'Whitefield', 'Bengaluru', 'Bengaluru Urban', 'Karnataka')
-- location: ('LOC-004', 'Tumakuru Road Logistics Hub', 'Bengaluru', 'Bengaluru Urban', 'Karnataka')
-- location: ('LOC-005', 'Industrial Resale Zone', 'Hyderabad', 'Hyderabad', 'Telangana')
-- account: ('ACC-1001', 'SYN-ACC-0001', 'P-001', 'Demo Bank')
-- account: ('ACC-1002', 'SYN-ACC-0002', 'P-002', 'Demo Bank')
-- account: ('ACC-1003', 'SYN-ACC-0003', None, 'Demo Bank')
-- relationship: ('REL-001', 'P-001', 'P-002', 'ASSOCIATED_WITH', 0.91, 'DOC-001', '7', 'FIR-1024')
-- relationship: ('REL-002', 'P-001', 'V-001', 'USES', 0.96, 'DOC-001', '7', 'FIR-1024')
-- relationship: ('REL-003', 'P-001', 'PH-001', 'USES', 0.99, 'DOC-001', '7', 'FIR-1024')
-- relationship: ('REL-004', 'P-002', 'PH-002', 'USES', 0.99, 'DOC-002', '', 'CDR-1024')
-- relationship: ('REL-005', 'P-003', 'PH-003', 'USES', 0.99, 'DOC-002', '', 'CDR-1024')
-- relationship: ('REL-006', 'P-002', 'P-003', 'COMMUNICATED_WITH', 0.88, 'DOC-002', '', 'CDR-1024')
-- relationship: ('REL-007', 'P-001', 'P-002', 'TRANSFERRED_TO', 0.93, 'DOC-003', '', 'TXN-1024')
-- relationship: ('REL-008', 'P-002', 'ORG-001', 'TRANSFERRED_TO', 0.86, 'DOC-003', '', 'TXN-1024')
-- relationship: ('REL-009', 'P-003', 'ORG-001', 'WORKS_FOR', 0.92, 'DOC-001', '7', 'FIR-1024')
-- relationship: ('REL-010', 'P-001', 'LOC-001', 'LOCATED_AT', 0.94, 'DOC-004', '3', 'SURV-1024')
-- relationship: ('REL-011', 'P-002', 'LOC-001', 'LOCATED_AT', 0.93, 'DOC-004', '3', 'SURV-1024')
-- relationship: ('REL-012', 'V-002', 'LOC-003', 'LOCATED_AT', 0.8, 'DOC-004', '3', 'SURV-1024')
-- relationship: ('REL-013', 'P-002', 'V-001', 'USES', 0.89, 'DOC-004', '3', 'SURV-1024')
-- relationship: ('REL-014', 'ORG-001', 'LOC-004', 'LOCATED_AT', 0.95, 'DOC-001', '7', 'FIR-1024')
-- relationship: ('REL-015', 'ORG-001', 'ACC-1003', 'OWNS', 0.9, 'DOC-003', '', 'TXN-1024')
-- transaction: ('TX-001', 'ACC-1001', 'ACC-1002', 84500, '2026-06-15 10:42:00', 'LOC-001', 'TRANSFER', 'CASE-1024')
-- transaction: ('TX-002', 'ACC-1002', 'ACC-1003', 62000, '2026-06-16 11:10:00', 'LOC-004', 'TRANSFER', 'CASE-1024')
-- cdr: ('CDR-001', 'PH-001', 'PH-002', '2026-06-14 20:12:00', 182, 'LOC-001', 'VOICE')
-- cdr: ('CDR-002', 'PH-001', 'PH-002', '2026-06-14 21:07:00', 341, 'LOC-001', 'VOICE')
-- cdr: ('CDR-003', 'PH-002', 'PH-003', '2026-06-15 09:18:00', 126, 'LOC-003', 'VOICE')
-- event: ('EVT-001', 'MEETING', '2026-06-14 20:05:00', 'LOC-001', 'INV-1024', 'Ravi Kumar and Suresh Sharma observed together near Peenya.')
-- event: ('EVT-002', 'CALL', '2026-06-14 21:07:00', 'LOC-001', 'INV-1024', 'CDR record shows communication between PH-001 and PH-002.')
-- event: ('EVT-003', 'TRANSFER', '2026-06-15 10:42:00', 'LOC-001', 'INV-1024', 'ACC-1001 transferred INR 84,500 to ACC-1002.')

COMMIT;

-- Recommended demo method:
-- 1) Upload the provided TXT/PDF/CSV source files through LINKRA ingestion.
-- 2) Let the ingestion + NLP + entity-resolution pipeline create canonical records.
-- 3) Project canonical entities and relationships into Neo4j.
-- 4) Verify the generated graph against the casebook relationship map."""


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        # Header
        self.drawString(36, 762, "LINKRA AI INVESTIGATION PLATFORM — SYNTHETIC CASEBOOK DATASET (SIH 2026)")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(36, 756, 576, 756)

        # Footer
        self.line(36, 42, 576, 42)
        self.drawString(36, 30, "CONFIDENTIAL / FICTIONAL DEMONSTRATION DATA ONLY — DO NOT DISTRIBUTE AS REAL INTELLIGENCE")
        self.drawRightString(576, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf(output_path: Path):
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4,
    )

    badge_style = ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#DC2626'),
        spaceAfter=10,
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=4,
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#334155'),
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#0F172A'),
    )

    flowables = []

    # Title Banner
    flowables.append(Paragraph("LINKRA SIH 2026 SYNTHETIC DATASET", title_style))
    flowables.append(Paragraph("DEMONSTRATION CASEBOOK &amp; BENCHMARK SEED • FICTIONAL / DEMO ONLY", badge_style))
    flowables.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=8))

    # Overview Box
    overview_text = (
        "<b>Case ID:</b> CASE-1024 &nbsp;|&nbsp; <b>Investigation ID:</b> INV-1024 &nbsp;|&nbsp; "
        "<b>Title:</b> Cross-source cargo theft network analysis<br/>"
        "<b>Status:</b> OPEN &nbsp;|&nbsp; <b>Priority:</b> HIGH &nbsp;|&nbsp; "
        "<b>Incident Date:</b> 2026-06-14 &nbsp;|&nbsp; <b>Primary Jurisdiction:</b> Peenya Industrial Area (LOC-001), Bengaluru"
    )
    overview_table = Table(
        [[Paragraph(overview_text, body_style)]],
        colWidths=[540]
    )
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F5F9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    flowables.append(overview_table)
    flowables.append(Spacer(1, 8))

    # Core Entities Table
    flowables.append(Paragraph("1. Core Canonical Entities", section_heading))
    entities_data = [
        ["Entity Type", "ID", "Primary Label / Name", "Secondary Attribute", "Associated Links"],
        ["Investigation", "INV-1024", "Cargo theft network analysis", "Status: OPEN | High Priority", "LOC-001"],
        ["Person", "P-001", "Ravi Kumar (R. Kumar)", "Role: PERSON", "PH-001, LOC-001, ORG-001"],
        ["Person", "P-002", "Suresh Sharma (S. Sharma)", "Role: PERSON", "PH-002, LOC-002"],
        ["Person", "P-003", "Meera Nair (Meera N.)", "Role: PERSON", "PH-003, LOC-003, ORG-001"],
        ["Organization", "ORG-001", "Metro Logistics", "Transport / Logistics", "LOC-004"],
        ["Organization", "ORG-002", "Urban Resale Network", "Retail / Resale", "LOC-005"],
        ["Vehicle", "V-001", "Toyota Innova (KA01AB1234)", "Color: White", "Used by P-001, P-002"],
        ["Vehicle", "V-002", "Tata Ace (KA05XY6789)", "Color: Silver", "Located at LOC-003"],
        ["Phone", "PH-001", "+91-90000-10001", "Assigned: P-001", "Peenya CDRs"],
        ["Phone", "PH-002", "+91-90000-10002", "Assigned: P-002", "Yeshwanthpur CDRs"],
        ["Phone", "PH-003", "+91-90000-10003", "Assigned: P-003", "Whitefield CDRs"],
        ["Location", "LOC-001", "Peenya Industrial Area", "Bengaluru Urban, KA", "Meeting & Primary site"],
        ["Location", "LOC-002", "Yeshwanthpur", "Bengaluru Urban, KA", "Suresh Sharma Base"],
        ["Location", "LOC-003", "Whitefield", "Bengaluru Urban, KA", "Meera Nair & V-002 Base"],
        ["Location", "LOC-004", "Tumakuru Road Logistics Hub", "Bengaluru Urban, KA", "Metro Logistics Facility"],
        ["Location", "LOC-005", "Industrial Resale Zone", "Hyderabad, Telangana", "Urban Resale Hub"],
        ["Account", "ACC-1001", "SYN-ACC-0001 (Demo Bank)", "Owner: P-001 (Ravi Kumar)", "Transfers out"],
        ["Account", "ACC-1002", "SYN-ACC-0002 (Demo Bank)", "Owner: P-002 (Suresh Sharma)", "Intermediary Account"],
        ["Account", "ACC-1003", "SYN-ACC-0003 (Demo Bank)", "Owner: ORG-001 (Metro Log.)", "Corporate Beneficiary"],
    ]

    t_entities = Table(entities_data, colWidths=[65, 55, 150, 130, 140])
    t_entities.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    flowables.append(t_entities)
    flowables.append(Spacer(1, 8))

    # Relationships Table
    flowables.append(Paragraph("2. Canonical Relationships &amp; Graph Edges", section_heading))
    rel_data = [
        ["Rel ID", "Source", "Target", "Relationship Type", "Conf", "Doc ID", "Page", "Source Document"],
        ["REL-001", "P-001 (Ravi)", "P-002 (Suresh)", "ASSOCIATED_WITH", "0.91", "DOC-001", "7", "FIR-1024"],
        ["REL-002", "P-001 (Ravi)", "V-001 (Innova)", "USES", "0.96", "DOC-001", "7", "FIR-1024"],
        ["REL-003", "P-001 (Ravi)", "PH-001 (Phone)", "USES", "0.99", "DOC-001", "7", "FIR-1024"],
        ["REL-004", "P-002 (Suresh)", "PH-002 (Phone)", "USES", "0.99", "DOC-002", "-", "CDR-1024"],
        ["REL-005", "P-003 (Meera)", "PH-003 (Phone)", "USES", "0.99", "DOC-002", "-", "CDR-1024"],
        ["REL-006", "P-002 (Suresh)", "P-003 (Meera)", "COMMUNICATED_WITH", "0.88", "DOC-002", "-", "CDR-1024"],
        ["REL-007", "P-001 (Ravi)", "P-002 (Suresh)", "TRANSFERRED_TO", "0.93", "DOC-003", "-", "TXN-1024"],
        ["REL-008", "P-002 (Suresh)", "ORG-001 (Metro)", "TRANSFERRED_TO", "0.86", "DOC-003", "-", "TXN-1024"],
        ["REL-009", "P-003 (Meera)", "ORG-001 (Metro)", "WORKS_FOR", "0.92", "DOC-001", "7", "FIR-1024"],
        ["REL-010", "P-001 (Ravi)", "LOC-001 (Peenya)", "LOCATED_AT", "0.94", "DOC-004", "3", "SURV-1024"],
        ["REL-011", "P-002 (Suresh)", "LOC-001 (Peenya)", "LOCATED_AT", "0.93", "DOC-004", "3", "SURV-1024"],
        ["REL-012", "V-002 (Tata Ace)", "LOC-003 (Whitefield)", "LOCATED_AT", "0.80", "DOC-004", "3", "SURV-1024"],
        ["REL-013", "P-002 (Suresh)", "V-001 (Innova)", "USES", "0.89", "DOC-004", "3", "SURV-1024"],
        ["REL-014", "ORG-001 (Metro)", "LOC-004 (Tumakuru)", "LOCATED_AT", "0.95", "DOC-001", "7", "FIR-1024"],
        ["REL-015", "ORG-001 (Metro)", "ACC-1003 (Account)", "OWNS", "0.90", "DOC-003", "-", "TXN-1024"],
    ]

    t_rel = Table(rel_data, colWidths=[45, 80, 80, 115, 35, 45, 30, 110])
    t_rel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    flowables.append(t_rel)

    flowables.append(PageBreak())

    # Transactions & CDRs & Events
    flowables.append(Paragraph("3. Transactions, CDRs &amp; Timeline Events", section_heading))

    txn_cdr_data = [
        ["Type", "Record ID", "Primary Participants", "Timestamp", "Detail / Volume", "Location / Case"],
        ["TXN", "TX-001", "ACC-1001 -> ACC-1002", "2026-06-15 10:42:00", "Amount: INR 84,500 (TRANSFER)", "LOC-001 | CASE-1024"],
        ["TXN", "TX-002", "ACC-1002 -> ACC-1003", "2026-06-16 11:10:00", "Amount: INR 62,000 (TRANSFER)", "LOC-004 | CASE-1024"],
        ["CDR", "CDR-001", "PH-001 -> PH-002", "2026-06-14 20:12:00", "Duration: 182s (VOICE)", "LOC-001 (Peenya)"],
        ["CDR", "CDR-002", "PH-001 -> PH-002", "2026-06-14 21:07:00", "Duration: 341s (VOICE)", "LOC-001 (Peenya)"],
        ["CDR", "CDR-003", "PH-002 -> PH-003", "2026-06-15 09:18:00", "Duration: 126s (VOICE)", "LOC-003 (Whitefield)"],
        ["EVENT", "EVT-001", "MEETING: Ravi Kumar & Suresh Sharma", "2026-06-14 20:05:00", "Observed together near Peenya", "LOC-001 | INV-1024"],
        ["EVENT", "EVT-002", "CALL: PH-001 & PH-002", "2026-06-14 21:07:00", "CDR record shows active communication", "LOC-001 | INV-1024"],
        ["EVENT", "EVT-003", "TRANSFER: ACC-1001 -> ACC-1002", "2026-06-15 10:42:00", "ACC-1001 transferred INR 84,500", "LOC-001 | INV-1024"],
    ]

    t_txn = Table(txn_cdr_data, colWidths=[40, 50, 140, 95, 120, 95])
    t_txn.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    flowables.append(t_txn)
    flowables.append(Spacer(1, 10))

    # Recommended Demo Method Box
    flowables.append(Paragraph("4. Recommended LINKRA Ingestion &amp; Demo Workflow", section_heading))
    method_text = (
        "<b>Step 1: Ingestion</b> &mdash; Upload the provided TXT/PDF/CSV source files through the LINKRA ingestion pipeline.<br/>"
        "<b>Step 2: NLP &amp; Entity Resolution</b> &mdash; Run the NLP extraction and entity-resolution pipeline to generate canonical records.<br/>"
        "<b>Step 3: Graph Projection</b> &mdash; Project resolved canonical entities and relationships into Neo4j.<br/>"
        "<b>Step 4: Verification</b> &mdash; Verify the generated knowledge graph against the casebook relationship map."
    )
    method_table = Table([[Paragraph(method_text, body_style)]], colWidths=[540])
    method_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EFF6FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3B82F6')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    flowables.append(method_table)
    flowables.append(Spacer(1, 10))

    # Exact Raw SQL Seed Text
    flowables.append(Paragraph("5. Exact Verbatim Seed Script (Raw Ingestion Text)", section_heading))
    seed_table = Table([[Preformatted(RAW_SEED_TEXT, code_style)]], colWidths=[540])
    seed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    flowables.append(seed_table)

    doc.build(flowables, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {output_path} ({output_path.stat().st_size} bytes)")


if __name__ == "__main__":
    targets = [
        Path("d:/LINKRA-SIH/linkra_sih_2026_synthetic_dataset.pdf"),
        Path("d:/LINKRA-SIH/LINKRA_dev/backend/data/pdfs/linkra_sih_2026_synthetic_dataset.pdf"),
    ]
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        build_pdf(target)
