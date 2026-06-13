# =============================================================================
# KRONOS — PDF BUILDER
# File: src/reporting/pdf_builder.py
# =============================================================================

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import (
    getSampleStyleSheet
)
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus.tables import (
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable
from datetime import datetime
import pandas as pd
import os

# =============================================================================
# PDF REPORT DIRECTORY
# =============================================================================

REPORT_OUTPUT_DIR = "reports"

os.makedirs(
    REPORT_OUTPUT_DIR,
    exist_ok=True
)

# =============================================================================
# DOCUMENT STYLES
# =============================================================================

styles = getSampleStyleSheet()

TITLE_STYLE = styles["Title"]

HEADING_STYLE = styles["Heading2"]

BODY_STYLE = styles["BodyText"]

# =============================================================================
# GENERATE REPORT HEADER
# =============================================================================

def generate_report_header():
    """
    Generate executive report title section.
    """

    timestamp = datetime.utcnow().strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    header = [

        Paragraph(
            "KRONOS — Enterprise Risk Intelligence Report",
            TITLE_STYLE
        ),

        Spacer(1, 12),

        Paragraph(
            f"Generated: {timestamp}",
            BODY_STYLE
        ),

        Spacer(1, 18),

        HRFlowable(
            width="100%",
            color=colors.black
        ),

        Spacer(1, 18),
    ]

    return header

# =============================================================================
# EXECUTIVE SUMMARY SECTION
# =============================================================================

def executive_summary_section(
    executive_summary
):
    """
    Build executive summary section.
    """

    content = [

        Paragraph(
            "Executive Summary",
            HEADING_STYLE
        ),

        Spacer(1, 10),
    ]

    for key, value in executive_summary.items():

        text = (
            f"<b>{key.replace('_', ' ').title()}</b>: "
            f"{value}"
        )

        content.append(
            Paragraph(
                text,
                BODY_STYLE
            )
        )

        content.append(
            Spacer(1, 6)
        )

    return content

# =============================================================================
# NARRATIVE SECTION
# =============================================================================

def narrative_section(
    narrative_results
):
    """
    Build executive narrative section.
    """

    content = [

        Spacer(1, 12),

        Paragraph(
            "Executive Intelligence Narratives",
            HEADING_STYLE
        ),

        Spacer(1, 10),
    ]

    for key, value in narrative_results.items():

        text = (
            f"<b>{key.replace('_', ' ').title()}</b><br/>"
            f"{value}"
        )

        content.append(
            Paragraph(
                text,
                BODY_STYLE
            )
        )

        content.append(
            Spacer(1, 8)
        )

    return content

# =============================================================================
# PORTFOLIO METRICS TABLE
# =============================================================================

def portfolio_metrics_table(
    metrics_df
):
    """
    Build institutional metrics table.
    """

    table_data = [

        list(metrics_df.columns)
    ]

    for _, row in metrics_df.iterrows():

        table_data.append(
            list(row.values)
        )

    table = Table(
        table_data,
        repeatRows=1
    )

    table.setStyle(

        TableStyle([

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.darkblue
            ),

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white
            ),

            (
                "GRID",
                (0, 0),
                (-1, -1),
                1,
                colors.black
            ),

            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, 0),
                10
            ),

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.beige
            ),

        ])
    )

    return [

        Spacer(1, 12),

        Paragraph(
            "Enterprise Portfolio Metrics",
            HEADING_STYLE
        ),

        Spacer(1, 10),

        table,
    ]

# =============================================================================
# GOVERNANCE SECTION
# =============================================================================

def governance_section(
    governance_summary
):
    """
    Build governance intelligence section.
    """

    content = [

        Spacer(1, 12),

        Paragraph(
            "Governance & Escalation Overview",
            HEADING_STYLE
        ),

        Spacer(1, 10),
    ]

    for key, value in governance_summary.items():

        text = (
            f"<b>{key.replace('_', ' ').title()}</b>: "
            f"{value}"
        )

        content.append(
            Paragraph(
                text,
                BODY_STYLE
            )
        )

        content.append(
            Spacer(1, 6)
        )

    return content

# =============================================================================
# ENTERPRISE SECTIONS
# =============================================================================

def enterprise_sections_section(
    enterprise_sections
):
    """
    Build additional institutional risk sections.
    """

    if not enterprise_sections:

        return []

    content = [

        Spacer(1, 12),

        Paragraph(
            "Institutional Risk Sections",
            HEADING_STYLE
        ),

        Spacer(1, 10),
    ]

    for section_name, section_values in enterprise_sections.items():

        content.append(
            Paragraph(
                section_name.replace("_", " ").title(),
                styles["Heading3"]
            )
        )

        content.append(
            Spacer(1, 6)
        )

        if isinstance(section_values, dict):

            for key, value in section_values.items():

                text = (
                    f"<b>{key.replace('_', ' ').title()}</b>: "
                    f"{value}"
                )

                content.append(
                    Paragraph(
                        text,
                        BODY_STYLE
                    )
                )

                content.append(
                    Spacer(1, 5)
                )

        elif isinstance(section_values, list):

            if section_values:

                for item in section_values:

                    content.append(
                        Paragraph(
                            str(item),
                            BODY_STYLE
                        )
                    )

                    content.append(
                        Spacer(1, 5)
                    )

            else:

                content.append(
                    Paragraph(
                        "No exposure records available.",
                        BODY_STYLE
                    )
                )

                content.append(
                    Spacer(1, 5)
                )

        else:

            content.append(
                Paragraph(
                    str(section_values),
                    BODY_STYLE
                )
            )

            content.append(
                Spacer(1, 5)
            )

        content.append(
            Spacer(1, 8)
        )

    return content

# =============================================================================
# BUILD PDF REPORT
# =============================================================================

def build_pdf_report(
    executive_summary,
    narrative_results,
    metrics_df,
    governance_summary,
    enterprise_sections=None,
    output_filename="kronos_report.pdf"
):
    """
    Build institutional executive PDF report.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] BUILDING EXECUTIVE PDF REPORT")
    print("=" * 80)

    output_path = os.path.join(
        REPORT_OUTPUT_DIR,
        output_filename
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter
    )

    elements = []

    # -------------------------------------------------------------------------
    # REPORT HEADER
    # -------------------------------------------------------------------------

    elements.extend(
        generate_report_header()
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------

    elements.extend(
        executive_summary_section(
            executive_summary
        )
    )

    # -------------------------------------------------------------------------
    # NARRATIVES
    # -------------------------------------------------------------------------

    elements.extend(
        narrative_section(
            narrative_results
        )
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO METRICS
    # -------------------------------------------------------------------------

    elements.extend(
        portfolio_metrics_table(
            metrics_df
        )
    )

    # -------------------------------------------------------------------------
    # INSTITUTIONAL RISK SECTIONS
    # -------------------------------------------------------------------------

    elements.extend(
        enterprise_sections_section(
            enterprise_sections
        )
    )

    # -------------------------------------------------------------------------
    # GOVERNANCE SECTION
    # -------------------------------------------------------------------------

    elements.append(
        PageBreak()
    )

    elements.extend(
        governance_section(
            governance_summary
        )
    )

    # -------------------------------------------------------------------------
    # FINALIZE PDF
    # -------------------------------------------------------------------------

    doc.build(elements)

    print(
        f"\n[KRONOS] PDF REPORT GENERATED:"
    )

    print(output_path)

    print("=" * 80)

    return output_path

# =============================================================================
# END OF FILE
# =============================================================================
