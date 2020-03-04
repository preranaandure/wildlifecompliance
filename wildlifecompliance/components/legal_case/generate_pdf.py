# -*- coding: utf-8 -*-
import os

from decimal import Decimal as D
from io import BytesIO

from django.core.files.storage import default_storage
from oscar.templatetags.currency_filters import currency
from reportlab.lib import enums
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
        BaseDocTemplate, 
        PageTemplate, 
        Frame, 
        Paragraph, 
        Spacer, 
        Table, 
        TableStyle, 
        ListFlowable,
        KeepTogether, 
        PageBreak, 
        Flowable, 
        NextPageTemplate, 
        FrameBreak,
        ListItem,
        )
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, StyleSheet1
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch, mm
from reportlab.lib import colors

from django.core.files import File
from django.conf import settings

from ledger.accounts.models import Document
from ledger.checkout.utils import calculate_excl_gst
from wildlifecompliance.components.main.pdf_utils import FlowableRect, ParagraphCheckbox, ParagraphOffeset

PAGE_MARGIN = 5 * mm
PAGE_WIDTH, PAGE_HEIGHT = A4


def _create_pdf(invoice_buffer, legal_case, request_data):
    # 'report' variable set according to whether document_type is 'brief_of_evidence' or 'prosecution_brief'
    # 'report_document_artifacts' variable set according to whether document_type is 'brief_of_evidence' or 'prosecution_brief'
    document_type = request_data.get('document_type')
    include_statement_of_facts = request_data.get('include_statement_of_facts')
    include_case_information_form = request_data.get('include_case_information_form')
    include_offences_offenders_roi = request_data.get('include_offences_offenders_roi')
    include_witness_officer_other_statements = request_data.get('include_witness_officer_other_statements')
    include_physical_artifacts = request_data.get('include_physical_artifacts')
    include_document_artifacts = request_data.get('include_document_artifacts')
    report = None
    report_document_artifacts = None
    report_physical_artifacts = None
    record_of_interviews = None
    other_statements = None
    if document_type == 'brief_of_evidence':
        report = legal_case.brief_of_evidence
        report_document_artifacts = legal_case.briefofevidencedocumentartifacts_set.all()
        report_physical_artifacts = legal_case.briefofevidencephysicalartifacts_set.all()
        record_of_interviews = legal_case.legal_case_boe_roi.all()
        other_statements = legal_case.legal_case_boe_other_statements.all()
    elif document_type == 'prosecution_brief':
        report = legal_case.prosecution_brief
        report_document_artifacts = legal_case.prosecutionbriefdocumentartifacts_set.all()
        report_physical_artifacts = legal_case.prosecutionbriefphysicalartifacts_set.all()
        record_of_interviews = legal_case.legal_case_pb_roi.all()
        other_statements = legal_case.legal_case_pb_other_statements.all()

    every_page_frame = Frame(PAGE_MARGIN, PAGE_MARGIN, PAGE_WIDTH - 2 * PAGE_MARGIN, PAGE_HEIGHT - 2 * PAGE_MARGIN, id='EveryPagesFrame', )  #showBoundary=Color(0, 1, 0))
    every_page_template = PageTemplate(id='EveryPages', frames=[every_page_frame,], )
    doc = BaseDocTemplate(invoice_buffer, pageTemplates=[every_page_template, ], pagesize=A4,)  # showBoundary=Color(1, 0, 0))

    # Common
    col_width_head = [85*mm, 25*mm, 85*mm,]
    col_width_details = [27*mm, 27*mm, 71*mm, 30*mm, 36*mm]
    col_width_for_court = [27*mm, 24*mm, 18*mm, 58*mm, 47*mm, 17*mm]
    FONT_SIZE_L = 11
    FONT_SIZE_M = 10
    FONT_SIZE_S = 8

    styles = StyleSheet1()
    styles.add(ParagraphStyle(name='Normal',
                              fontName='Helvetica',
                              fontSize=FONT_SIZE_M,
                              spaceBefore=7,  # space before paragraph
                              spaceAfter=7,   # space after paragraph
                              leading=12))       # space between lines
    styles.add(ParagraphStyle(name='BodyText',
                              parent=styles['Normal'],
                              spaceBefore=6))
    styles.add(ParagraphStyle(name='Italic',
                              parent=styles['BodyText'],
                              fontName='Helvetica-Italic'))
    styles.add(ParagraphStyle(name='Bold',
                              parent=styles['BodyText'],
                              fontName='Helvetica-Bold',
                              alignment = TA_CENTER))
    styles.add(ParagraphStyle(name='BoldLeft',
                              parent=styles['BodyText'],
                              fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='Right',
                              parent=styles['BodyText'],
                              alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name='Centre',
                              parent=styles['BodyText'],
                              alignment=TA_CENTER))

    # Details of alleged offence
    #rowHeights = [6*mm, 6*mm, 6*mm, 30*mm, 6*mm]
    #style_tbl_details = TableStyle([
    #    ('VALIGN', (0, 0), (0, 0), 'TOP'),
    #    ('VALIGN', (1, 0), (-1, -1), 'MIDDLE'),
    #    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    #    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    #    ('SPAN', (0, 0), (0, 4)),
    #    ('SPAN', (2, 0), (4, 0)),
    #    ('SPAN', (2, 1), (4, 1)),
    #    ('SPAN', (2, 2), (4, 2)),
    #    ('SPAN', (2, 3), (4, 3)),
    #    ('SPAN', (2, 4), (4, 4)),
    #])

    #case_information_header_data = []
    #case_information_header_data.append([
     #   Paragraph('Case Information Form', styles['Bold']),
    #])

    #tbl_details = Table(data, style=style_tbl_details, colWidths=col_width_details, rowHeights=rowHeights)
    #tbl_statement = Table(data, style=style_tbl_details, colWidths=col_width_details, rowHeights=rowHeights)
    #tbl_case_information_header = Table(case_information_header_data)

    #tbl_case_information_data = ListFlowable(
     #       [
      #          Paragraph
    statement_of_facts_data = []
    statement_of_facts_data.append([
        Paragraph('Statement of Facts', styles['BoldLeft']),
    ])
    statement_of_facts_data.append([
            Paragraph(report.statement_of_facts, styles['Normal'])
            ])
    tbl_statement_of_facts = Table(statement_of_facts_data)

    case_information_data = []
    case_information_data.append([
        Paragraph('Case Information Form', styles['BoldLeft']),
    ])

    case_information_data.append([
            ParagraphCheckbox("Victim impact statement to be taken?", x_offset=5, checked=report.victim_impact_statement_taken, style=styles['Normal'])
            ])
    if report.victim_impact_statement_taken:
        string_field = report.victim_impact_statement_taken_details if report.victim_impact_statement_taken_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Witness (including expert statements) still to be taken?", x_offset=5, checked=report.statements_pending, style=styles['Normal'])
            ])
    if report.statements_pending:
        string_field = report.statements_pending_details if report.statements_pending_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Vulnerable / hostile witnesses?", x_offset=5, checked=report.vulnerable_hostile_witnesses, style=styles['Normal'])
            ])
    if report.vulnerable_hostile_witnesses:
        string_field = report.vulnerable_hostile_witnesses_details if report.vulnerable_hostile_witnesses_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Witnesses refusing to make statements?", x_offset=5, checked=report.witness_refusing_statement, style=styles['Normal'])
            ])
    if report.witness_refusing_statement:
        string_field = report.witness_refusing_statement_details if report.witness_refusing_statement_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Specific problems / needs of prosecution witnesses, e.g. interpreters?", 
                x_offset=5, 
                checked=report.problems_needs_prosecution_witnesses, 
                style=styles['Normal'])
            ])
    if report.problems_needs_prosecution_witnesses:
        string_field = report.problems_needs_prosecution_witnesses_details if report.problems_needs_prosecution_witnesses_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("History of bad character / propensity (similar fact) evidence involving accused?", 
                x_offset=5, 
                checked=report.accused_bad_character, 
                style=styles['Normal'])
            ])
    if report.accused_bad_character:
        string_field = report.accused_bad_character_details if report.accused_bad_character_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Further persons (witness or suspect) to be interviewed?", 
                x_offset=5, 
                checked=report.further_persons_interviews_pending, 
                style=styles['Normal'])
            ])
    if report.further_persons_interviews_pending:
        string_field = report.further_persons_interviews_pending_details if report.further_persons_interviews_pending_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Other persons whose details do not appear on this brief who have been interviewed?", 
                x_offset=5, 
                checked=report.other_interviews, 
                style=styles['Normal'])
            ])
    if report.other_interviews:
        string_field = report.other_interviews_details if report.other_interviews_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Other relevant persons charged or yet to be charged?", 
                x_offset=5, 
                checked=report.relevant_persons_pending_charges, 
                style=styles['Normal'])
            ])
    if report.other_interviews:
        string_field = report.relevant_persons_pending_charges_details if report.relevant_persons_pending_charges_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Others receiving Infringement / Warning arising out of the same incident?", 
                x_offset=5, 
                checked=report.other_persons_receiving_sanction_outcome, 
                style=styles['Normal'])
            ])
    if report.other_persons_receiving_sanction_outcome:
        string_field = report.other_persons_receiving_sanction_outcome_details if report.other_persons_receiving_sanction_outcome_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Matters of local / public interest?",
                x_offset=5, 
                checked=report.local_public_interest,
                style=styles['Normal'])
            ])
    if report.local_public_interest:
        string_field = report.local_public_interest_details if report.local_public_interest_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Other applications / orders on conviction requests?",
                x_offset=5, 
                checked=report.applications_orders_requests,
                style=styles['Normal'])
            ])
    if report.applications_orders_requests:
        string_field = report.applications_orders_requests_details if report.applications_orders_requests_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Are there any other applications / orders on conviction required?",
                x_offset=5, 
                checked=report.applications_orders_required,
                style=styles['Normal'])
            ])
    if report.applications_orders_required:
        string_field = report.applications_orders_required_details if report.applications_orders_required_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    case_information_data.append([
            ParagraphCheckbox("Is there any statutory notice, DEC licence, ministerial statement or policy etc. re the matter, premise or person subject to this brief?",
                x_offset=5, 
                checked=report.other_legal_matters,
                style=styles['Normal'])
            ])
    if report.other_legal_matters:
        string_field = report.other_legal_matters_details if report.other_legal_matters_details else ''
        case_information_data.append([
                ParagraphOffeset(
                    string_field,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])

    tbl_case_information = Table(case_information_data)

    record_of_interviews_data = []
    record_of_interviews_data.append([
        Paragraph('Offences, Offenders and Records of Interview', styles['BoldLeft']),
    ])
    #offence_list = []
    for offence_level_record in record_of_interviews.filter(offender=None):

        record_of_interviews_data.append([
        ParagraphCheckbox(offence_level_record.label, x_offset=5, checked=offence_level_record.ticked, style=styles['Normal']),
        ])
        for offender_level_record in offence_level_record.children.all():

            record_of_interviews_data.append([
            ParagraphCheckbox(offender_level_record.label, x_offset=15, checked=offender_level_record.ticked, style=styles['Normal']),
            ])
            for roi_level_record in offender_level_record.children.all():

                record_of_interviews_data.append([
                ParagraphCheckbox(roi_level_record.label, x_offset=25, checked=roi_level_record.ticked, style=styles['Normal']),
                ])

                for doc_artifact_level_record in roi_level_record.children.all():
                    record_of_interviews_data.append([
                    ParagraphCheckbox(doc_artifact_level_record.label, x_offset=35, checked=doc_artifact_level_record.ticked, style=styles['Normal']),
                    ])

    tbl_record_of_interviews = Table(record_of_interviews_data)

    other_statements_data = []
    other_statements_data.append([
        Paragraph('Witness Statements, Officer Statements, Expert Statements', styles['BoldLeft']),
    ])
    for person_level_record in other_statements.filter(statement=None):

        other_statements_data.append([
        ParagraphCheckbox(person_level_record.label, x_offset=5, checked=person_level_record.ticked, style=styles['Normal']),
        ])
        for statement_level_record in person_level_record.children.all():

            other_statements_data.append([
            ParagraphCheckbox(statement_level_record.label, x_offset=15, checked=statement_level_record.ticked, style=styles['Normal']),
            ])

            for doc_artifact_level_record in statement_level_record.children.all():
                other_statements_data.append([
                ParagraphCheckbox(doc_artifact_level_record.label, x_offset=35, checked=doc_artifact_level_record.ticked, style=styles['Normal']),
                ])
    tbl_other_statements = Table(other_statements_data)

    physical_artifacts_data = []
    physical_artifacts_data.append([
        Paragraph('List of Exhibits, Sensitive Unused and Non-sensitive Unused Materials', styles['BoldLeft']),
    ])
    physical_artifacts_data.append([
        Paragraph('Select the objects to be included on the list of exhibits', styles['Normal']),
    ])
    for artifact in report_physical_artifacts:
        legal_case_physical_artifact_link = legal_case.physicalartifactlegalcases_set.get(
                legal_case_id=legal_case.id,
                physical_artifact_id=artifact.physical_artifact.id)
        if legal_case_physical_artifact_link.used_within_case:
            physical_artifacts_data.append([
                ParagraphCheckbox(artifact.physical_artifact.identifier, x_offset=5, checked=artifact.ticked, style=styles['Normal'])
                #ParagraphOffeset(
                 #   artifact.physical_artifact.identifier,
                  #  styles['Normal'],
                   # x_offset=5,
                   # )
                ])
    physical_artifacts_data.append([
        Paragraph('Select the objects to be included on the sensitive unused list of materials', styles['Normal']),
    ])
    for artifact in report_physical_artifacts:
        legal_case_physical_artifact_link = legal_case.physicalartifactlegalcases_set.get(
                legal_case_id=legal_case.id,
                physical_artifact_id=artifact.physical_artifact.id)
        if (not legal_case_physical_artifact_link.used_within_case and 
                legal_case_physical_artifact_link.sensitive_non_disclosable
                ):
            physical_artifacts_data.append([
                ParagraphCheckbox(artifact.physical_artifact.identifier, x_offset=5, checked=artifact.ticked, style=styles['Normal'])
                ])
            physical_artifacts_data.append([
                ParagraphOffeset(
                    artifact.reason_sensitive_non_disclosable,
                    styles['Normal'],
                    x_offset=25,
                    )
                ])
    physical_artifacts_data.append([
        Paragraph('Select the objects to be included on the non-sensitive unused list of materials', styles['Normal']),
    ])
    for artifact in report_physical_artifacts:
        legal_case_physical_artifact_link = legal_case.physicalartifactlegalcases_set.get(
                legal_case_id=legal_case.id,
                physical_artifact_id=artifact.physical_artifact.id)
        if (not legal_case_physical_artifact_link.used_within_case and not
                legal_case_physical_artifact_link.sensitive_non_disclosable
                ):
            physical_artifacts_data.append([
                ParagraphCheckbox(artifact.physical_artifact.identifier, x_offset=5, checked=artifact.ticked, style=styles['Normal'])
                ])

    tbl_physical_artifacts = Table(physical_artifacts_data)

    document_artifacts_data = []
    document_artifacts_data.append([
        Paragraph('Additional Documents', styles['BoldLeft']),
    ])
    for artifact in report_document_artifacts:
        document_artifacts_data.append([
            ParagraphCheckbox(artifact.document_artifact.identifier, x_offset=5, checked=artifact.ticked, style=styles['Normal'])
            ])
        for attachment in artifact.document_artifact.documents.all():
            print(attachment.name)
            if attachment.name:
                document_artifacts_data.append([
                    ParagraphOffeset(
                        attachment.name,
                        styles['Normal'],
                        x_offset=25,
                        )
                    ])

    tbl_document_artifacts = Table(document_artifacts_data)

    # Append tables to the elements to build
    gap_between_tables = 1.5*mm
    elements = []
    #elements.append(tbl_case_information_header)
    elements.append(Spacer(0, gap_between_tables))
    elements.append(tbl_statement_of_facts)
    elements.append(Spacer(0, gap_between_tables))
    elements.append(tbl_case_information)
    elements.append(Spacer(0, gap_between_tables))
    elements.append(tbl_record_of_interviews)
    #elements.append(offence_list_flowable)
    #elements.append(records_of_interview_data)
    elements.append(Spacer(0, gap_between_tables))
    elements.append(tbl_other_statements)
    elements.append(tbl_physical_artifacts)
    elements.append(Spacer(0, gap_between_tables))
    elements.append(tbl_document_artifacts)
    elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_head)
    #elements.append(tbl_statement)
    #elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_notice)
    #elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_accused)
    #elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_prosecutor)
    #elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_for_court)
    #elements.append(PageBreak())
    #elements.append(tbl_for_court_number)
    #elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_above)
    #elements.append(Spacer(0, gap_between_tables))
    #elements.append(tbl_below)

    doc.build(elements)
    return invoice_buffer


def gap(num):
    ret = ''
    for i in range(num):
        ret = ret + '&nbsp;'
    return ret


def create_document_pdf_bytes(legal_case, request_data):
    with BytesIO() as invoice_buffer:
        _create_pdf(invoice_buffer, legal_case, request_data)
        document_type = request_data.get('document_type')
        filename = document_type + '_' + legal_case.number + '.pdf'

        # Get the value of the BytesIO buffer
        value = invoice_buffer.getvalue()

        # START: Save the pdf file to the database
        ## delete existing document
        document = None
        path = 'wildlifecompliance/{}/{}/generated_documents/{}'.format(legal_case._meta.model_name, legal_case.id, filename)
        document_exists = default_storage.exists(path)
        if document_exists:
            print("delete " + path)
            # delete file
            default_storage.delete(path)
        document, created = legal_case.generated_documents.get_or_create(name=filename)
        stored_file = default_storage.save(path, invoice_buffer)
        document._file = stored_file
        # save file object
        document.save()

    return document


class OffsetTable(Table, object):

    def __init__(self, data, colWidths=None, rowHeights=None, style=None,
                 repeatRows=0, repeatCols=0, splitByRow=1, emptyTableAction=None, ident=None,
                 hAlign=None, vAlign=None, normalizedData=0, cellStyles=None, rowSplitRange=None,
                 spaceBefore=None, spaceAfter=None, longTableOptimize=None, minRowHeights=None, x_offset=0, y_offset=0):
        self.x_offset = x_offset
        self.y_offset = y_offset
        super(OffsetTable, self).__init__(data, colWidths, rowHeights, style,
                                          repeatRows, repeatCols, splitByRow, emptyTableAction, ident,
                                          hAlign, vAlign, normalizedData, cellStyles, rowSplitRange,
                                          spaceBefore, spaceAfter, longTableOptimize, minRowHeights)

    def drawOn(self, canvas, x, y, _sW=0):
        x = x + self.x_offset
        y = y + self.y_offset
        super(OffsetTable, self).drawOn(canvas, x, y, _sW)


