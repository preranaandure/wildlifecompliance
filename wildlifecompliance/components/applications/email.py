import logging
import mimetypes

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice

from wildlifecompliance.components.main.utils import (
    get_choice_value,
    add_url_internal_request,
    remove_url_internal_request,
    get_dob,
    get_first_name,
    get_last_name,
)

from wildlifecompliance.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'Wildlife Licensing Automated Message'


class ApplicationSubmitterNotificationEmail(TemplateEmailBase):
    subject = 'Your application has been submitted'
    html_template = 'wildlifecompliance/emails/send_application_submitter_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_submitter_notification.txt'


class ApplicationInvoiceNotificationEmail(TemplateEmailBase):
    subject = 'Your payment for your application has been received'
    html_template = 'wildlifecompliance/emails/send_application_invoice_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_invoice_notification.txt'


class ActivityInvoiceNotificationEmail(TemplateEmailBase):
    subject = 'Your payment for your licensed activity has been received.'
    html_template = 'wildlifecompliance/emails/send_activity_invoice_notification.html'
    txt_template = 'wildlifecompliance/emails/send_activity_invoice_notification.txt'


class ActivityProposeIssueNotificationEmail(TemplateEmailBase):
    subject = 'Your approval for a licensed activity is required.'
    html_template = 'wildlifecompliance/emails/send_activity_propose_issue_notification.html'
    txt_template = 'wildlifecompliance/emails/send_activity_propose_issue_notification.txt'


class ActivityRefundIssueNotificationEmail(TemplateEmailBase):
    subject = 'Refund payment for a declined license activity is required.'
    html_template = 'wildlifecompliance/emails/send_activity_refund_issue_notification.html'
    txt_template = 'wildlifecompliance/emails/send_activity_refund_issue_notification.txt'


class ActivityInvoiceIssueNotificationEmail(TemplateEmailBase):
    subject = 'Issuance of your licence activity is pending payment.'
    html_template = 'wildlifecompliance/emails/send_activity_invoice_issue_notification.html'
    txt_template = 'wildlifecompliance/emails/send_activity_invoice_issue_notification.txt'


class ApplicationSubmitNotificationEmail(TemplateEmailBase):
    subject = 'A new application has been submitted'
    html_template = 'wildlifecompliance/emails/send_application_submit_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_submit_notification.txt'


class ApplicationRefundNotificationEmail(TemplateEmailBase):
    subject = 'An application requiring a refund has been submitted'
    html_template = 'wildlifecompliance/emails/send_application_refund_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_refund_notification.txt'


class AmendmentSubmitNotificationEmail(TemplateEmailBase):
    subject = 'An amendment has been submitted'
    html_template = 'wildlifecompliance/emails/send_amendment_submit_notification.html'
    txt_template = 'wildlifecompliance/emails/send_amendment_submit_notification.txt'


class ApplicationAmendmentRequestNotificationEmail(TemplateEmailBase):
    subject = 'An amendment has been requested for your application'
    html_template = 'wildlifecompliance/emails/send_application_amendment_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_amendment_notification.txt'


class ApplicationIssueNotificationEmail(TemplateEmailBase):
    subject = 'A licence activity has been issued for your application.'
    html_template = 'wildlifecompliance/emails/send_application_issue_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_issue_notification.txt'


class ApplicationDeclineNotificationEmail(TemplateEmailBase):
    subject = 'A licence activity has been declined for your application.'
    html_template = 'wildlifecompliance/emails/send_application_decline_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_decline_notification.txt'


class ApplicationAssessmentRequestedEmail(TemplateEmailBase):
    subject = 'An application has been sent to you for assessment'
    html_template = 'wildlifecompliance/emails/send_application_assessment_request_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_assessment_request_notification.txt'


class ApplicationAssessmentReminderEmail(TemplateEmailBase):
    subject = 'An application is currently awaiting your assessment'
    html_template = 'wildlifecompliance/emails/send_application_assessment_remind_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_assessment_remind_notification.txt'


class ApplicationAssessmentRecallEmail(TemplateEmailBase):
    subject = 'An application for your assessment has been recalled'
    html_template = 'wildlifecompliance/emails/send_application_assessment_recall_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_assessment_recall_notification.txt'


class ApplicationAssessmentCompletedEmail(TemplateEmailBase):
    subject = 'An application assessment has been completed'
    html_template = 'wildlifecompliance/emails/send_application_assessment_complete_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_assessment_complete_notification.txt'


class ApplicationIdUpdateRequestEmail(TemplateEmailBase):
    subject = 'An update for your user identification has been requested'
    html_template = 'wildlifecompliance/emails/send_id_update_request_notification.html'
    txt_template = 'wildlifecompliance/emails/send_id_update_request_notification.txt'


class ApplicationIdUpdatedEmail(TemplateEmailBase):
    subject = 'A user has updated their identification'
    html_template = 'wildlifecompliance/emails/send_id_updated_notification.html'
    txt_template = 'wildlifecompliance/emails/send_id_updated_notification.txt'


class ApplicationReturnedToOfficerEmail(TemplateEmailBase):
    subject = 'A licensed activity has been returned to officer for review'
    html_template = 'wildlifecompliance/emails/send_application_return_to_officer_conditions.html'
    txt_template = 'wildlifecompliance/emails/send_application_return_to_officer_conditions.txt'


def send_assessment_recall_email(select_group, assessment, request=None):
    # An email reminding assessors of a pending assessment request
    application = assessment.application
    email = ApplicationAssessmentRecallEmail()

    context = {
        'application_id': application.id
    }
    email_group = [item.email for item in select_group]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_assessment_reminder_email(select_group, assessment, request=None):
    # An email reminding assessors of a pending assessment request
    application = assessment.application
    email = ApplicationAssessmentReminderEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-assessment-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'url': add_url_internal_request(request, url)
    }
    email_group = [item.email for item in select_group]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_assessment_email_notification(select_group, assessment, request):
    # An email notifying assessors of a new assessment request
    application = assessment.application
    text = assessment.text
    email = ApplicationAssessmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-assessment-detail',
            kwargs={
                ''
                'application_pk': application.id}))

    context = {
        'text': text,
        'url': add_url_internal_request(request, url)
    }

    email_group = [item.email for item in select_group]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_assessment_completed_email(select_group, assessment, request):
    """
    Notification for completed application assessments.
    """
    application = assessment.application
    text = assessment.final_comment
    email = ApplicationAssessmentCompletedEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-assessment-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'text': text,
        'url': add_url_internal_request(request, url)
    }

    email_group = [item.email for item in select_group]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_application_invoice_email_notification(
        application, invoice_ref, request):
    # An email with application invoice to submitter
    email = ApplicationInvoiceNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'external-application-detail',
            kwargs={
                'application_pk': application.id}))
    invoice_url = request.build_absolute_uri(
        reverse(
            'payments:invoice-pdf',
            kwargs={
                'reference': invoice_ref}))
    filename = 'invoice-{}-{}({}).pdf'.format(application.id,
                                              application.licence_type_short_name.replace(" ",
                                                                                          "-"),
                                              application.lodgement_date.date())
    references = [a.invoice_reference for a in application.invoices.all()]
    invoice = Invoice.objects.filter(
        reference__in=references).order_by('-created')[0]
    invoice_pdf = create_invoice_pdf_bytes(filename, invoice)

    context = {
        'application': application,
        'url': remove_url_internal_request(request, url),
        'invoice_url': invoice_url
    }
    recipients = [application.submitter.email]
    msg = email.send(recipients, context=context, attachments=[
                     (filename, invoice_pdf, 'application/pdf')])
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_activity_invoice_email_notification(
        application, activity, invoice_ref, request):
    # An email with application invoice to submitter
    email = ActivityInvoiceNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'external-application-detail',
            kwargs={
                'application_pk': application.id}))
    invoice_url = request.build_absolute_uri(
        reverse(
            'payments:invoice-pdf',
            kwargs={
                'reference': invoice_ref}))
    filename = 'invoice-{}-{}-({}).pdf'.format(
        application.id,
        activity.licence_activity.name.replace(" ", ""),
        application.lodgement_date.date()
    )
    references = [a.invoice_reference for a in activity.activity_invoices.all()]
    invoice = Invoice.objects.filter(
        reference__in=references).order_by('-created')[0]
    invoice_pdf = create_invoice_pdf_bytes(filename, invoice)

    context = {
        'application': application,
        'url': remove_url_internal_request(request, url),
        'invoice_url': invoice_url
    }
    recipients = [application.submitter.email]
    msg = email.send(recipients, context=context, attachments=[
                     (filename, invoice_pdf, 'application/pdf')])
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)
    return True


def send_activity_invoice_issue_notification(
        application, activity, request):

    email = ActivityInvoiceIssueNotificationEmail()
    url = request.build_absolute_uri(
        '/external/#'
    )

    context = {
        'application': application,
        'url': remove_url_internal_request(request, url),
    }
    recipients = [application.submitter.email]
    msg = email.send(recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)
    return True


def send_activity_propose_issue_notification(
        request, application, text, documents):

    application = application
    email = ActivityProposeIssueNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'detail': text,
        'url': add_url_internal_request(request, url)
    }

    recipients = [a.email for a in application.licence_approvers]
    activity = application.activities[0]
    email_copy = [activity.cc_email] if activity.cc_email else None

    msg = email.send(
        recipients,
        context=context, attachments=documents,
        bcc=email_copy,
    )

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_activity_refund_issue_notification(
        request, application, amount):

    application = application
    email = ActivityRefundIssueNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'amount': amount,
        'url': add_url_internal_request(request, url)
    }

    recipients = [a.email for a in application.licence_officers]
    activity = application.activities[0]
    email_copy = [activity.cc_email] if activity.cc_email else None

    msg = email.send(
        recipients,
        context=context,
        bcc=email_copy,
    )

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_application_submitter_email_notification(application, request):
    # An email to submitter notifying about new application is submitted
    email = ApplicationSubmitterNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'external-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'url': remove_url_internal_request(request, url)
    }
    recipients = [application.submitter.email]
    msg = email.send(recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_amendment_refund_email_notification(
        group_email, application, request):
    # An email to internal users notifying about required refund.
    over_paid = application.get_refund_amount()

    email = ApplicationRefundNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'amount': '${:0,.2f}'.format(over_paid).replace('$-', '-$'),
        'url': add_url_internal_request(request, url)
    }
    email_group = [item.email for item in group_email]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_application_submit_email_notification(
        group_email, application, request):
    # An email to internal users notifying about new application is submitted
    email = ApplicationSubmitNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'url': add_url_internal_request(request, url)
    }
    email_group = [item.email for item in group_email]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_amendment_submit_email_notification(
        group_email, application, request):
    # An email to internal users notifying about application amendment being submitted
    email = AmendmentSubmitNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'url': add_url_internal_request(request, url)
    }
    email_group = [item.email for item in group_email]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_application_amendment_notification(amendment_data, application, request):
    from wildlifecompliance.components.applications.models import AmendmentRequest

    # An email to submitter notifying about amendment request for an application
    email = ApplicationAmendmentRequestNotificationEmail()
    reason = get_choice_value(
        amendment_data['reason'],
        AmendmentRequest.REASON_CHOICES
    )
    url = request.build_absolute_uri(
        reverse(
            'external-application-detail',
            kwargs={
                'application_pk': application.id}))
    context = {
        'application': application,
        'reason': reason,
        'amendment_details': amendment_data['text'],
        'url': remove_url_internal_request(request, url)
    }

    msg = email.send(application.submitter.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_application_issue_notification(
        activities,
        application,
        request,
        licence):

    email = ApplicationIssueNotificationEmail()

    url = request.build_absolute_uri(
        reverse(
            'external-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'activities': activities,
        'url': remove_url_internal_request(request, url)
    }

    documents = []
    documents.append((
        licence.licence_document.name,
        licence.licence_document._file.read(),
        'application/pdf'
    ))
    copy_emails = None
    for activity in activities:
        for document in activity.issuance_documents.all():
            content = document._file.read()
            mime = mimetypes.guess_type(document.name)[0]
            documents.append((document.name, content, mime))
        
        if not copy_emails and activity.cc_email:
            copy_emails = activity.cc_email.split(',')

    msg = email.send(
        application.submitter.email,
        context=context, attachments=documents,
        bcc=copy_emails
        # bcc=[activities[0].cc_email] if activities[0].cc_email else None
    )

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_application_decline_notification(
        activities, application, request):
    # An email to submitter users notifying about an application activity being declined
    email = ApplicationDeclineNotificationEmail()

    url = request.build_absolute_uri(
        reverse(
            'external-application-detail',
            kwargs={
                'application_pk': application.id}))
    context = {
        'application': application,
        'activities': activities,
        'url': remove_url_internal_request(request, url)
    }

    msg = email.send(
        application.submitter.email,
        context=context,
        bcc=[activities[0].cc_email] if activities[0].cc_email else None
    )

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_id_update_request_notification(application, request):
    # An email to submitter requesting an update to the user identification
    email = ApplicationIdUpdateRequestEmail()

    url = request.build_absolute_uri(
        reverse(
            'manage-account')
    )
    context = {
        'application': application,
        'url': remove_url_internal_request(request, url)
    }

    msg = email.send(application.submitter.email, context=context)

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def send_id_updated_notification(user, applications, assigned_officers, request):
    # An email to internal users notifying about a user identification being updated
    email = ApplicationIdUpdatedEmail()
    url = request.build_absolute_uri(
        '/internal/users/{}'.format(user.id)
    )

    applications_list_string = ', '.join([str(application.id) for application in applications])
    context = {
        'user': '{first_name} {last_name}'.format(
            first_name=get_first_name(user),
            last_name=get_last_name(user)),
        'url': add_url_internal_request(request, url),
        'applications': applications_list_string
    }
    email_list = [o.email for o in assigned_officers]
    msg = email.send(email_list, context=context)

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    for application in applications:
        _log_application_email(msg, application, sender=sender)


def send_application_return_to_officer_conditions_notification(
        email_list, application, text, request):
    # An email to internal users notifying about an application returning to the officer - conditions stage
    email = ApplicationReturnedToOfficerEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-application-detail',
            kwargs={
                'application_pk': application.id}))

    context = {
        'application': application,
        'text': text,
        'url': add_url_internal_request(request, url)
    }
    msg = email.send(email_list, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def _log_application_email(email_message, application, sender=None):
    from wildlifecompliance.components.applications.models import ApplicationLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html
        # instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(
            email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ','
        # comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ''
        to = application.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = application.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'application': application,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ApplicationLogEntry.objects.create(**kwargs)

    return email_entry


def _log_org_email(email_message, organisation, customer, sender=None):
    from wildlifecompliance.components.organisations.models import OrganisationLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html
        # instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(
            email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ','
        # comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ''
        to = request.requester.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = customer

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'organisation': organisation,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = OrganisationLogEntry.objects.create(**kwargs)

    return email_entry
