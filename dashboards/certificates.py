"""
Certificate generation and management module
"""
import os
import uuid
from io import BytesIO
from django.template.loader import render_to_string
from django.http import FileResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Certificate, CertificateTemplate
import secrets
from django.conf import settings


def generate_certificate_number():
    """Generate unique certificate number"""
    return f"CERT-{uuid.uuid4().hex[:12].upper()}-{timezone.now().strftime('%Y%m%d')}"


def generate_verification_code():
    """Generate 12-character verification code"""
    return secrets.token_hex(6).upper()


def create_certificate(student, exam, attempt, grade=None):
    """Create certificate for student upon passing exam"""
    if Certificate.objects.filter(student=student, exam=exam).exists():
        return Certificate.objects.get(student=student, exam=exam)
    
    total_marks = sum([q.marks for q in exam.questions.all()])
    percentage = (attempt.total_score / total_marks * 100) if total_marks > 0 else 0
    
    # Determine grade based on percentage
    if grade is None:
        if percentage >= 90:
            grade = 'A'
        elif percentage >= 80:
            grade = 'B'
        elif percentage >= 70:
            grade = 'C'
        elif percentage >= 60:
            grade = 'D'
        else:
            grade = 'F'
    
    certificate = Certificate.objects.create(
        student=student,
        exam=exam,
        attempt=attempt,
        certificate_number=generate_certificate_number(),
        score=attempt.total_score,
        total_marks=total_marks,
        percentage=percentage,
        grade=grade,
        verification_code=generate_verification_code(),
    )
    
    # Generate PDF
    generate_certificate_pdf(certificate)
    
    return certificate


def generate_certificate_pdf(certificate):
    """Generate PDF certificate using HTML template"""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        # Fallback if weasyprint not installed
        return None
    
    # Get certificate template or use default
    template = CertificateTemplate.objects.filter(is_default=True).first()
    
    if not template:
        template = CertificateTemplate.objects.create(
            name='Default',
            school='School of Excellence',
            text_color='#333333',
            font_family='Arial',
            is_default=True,
        )
    
    context = {
        'certificate': certificate,
        'template': template,
        'issued_date': certificate.issued_at.strftime('%B %d, %Y'),
    }
    
    html_string = render_to_string('certificates/certificate_template.html', context)
    
    try:
        html = HTML(string=html_string)
        pdf_bytes = html.write_pdf()
        
        filename = f"cert_{certificate.certificate_number}.pdf"
        certificate.pdf_file.save(
            filename,
            ContentFile(pdf_bytes),
            save=True
        )
        
        return certificate.pdf_file
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def verify_certificate(certificate_number, verification_code):
    """Verify certificate authenticity"""
    try:
        certificate = Certificate.objects.get(
            certificate_number=certificate_number,
            verification_code=verification_code
        )
        certificate.is_digitally_verified = True
        certificate.save(update_fields=['is_digitally_verified'])
        return certificate
    except Certificate.DoesNotExist:
        return None


def get_student_certificates(student):
    """Get all certificates for a student"""
    return Certificate.objects.filter(student=student).order_by('-issued_at')


def revoke_certificate(certificate, reason=''):
    """Revoke a certificate (soft delete)"""
    certificate.is_digitally_verified = False
    certificate.save(update_fields=['is_digitally_verified'])


def export_certificate_pdf(certificate):
    """Export certificate PDF"""
    if certificate.pdf_file:
        return FileResponse(
            certificate.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"{certificate.certificate_number}.pdf"
        )
    else:
        # Generate on-the-fly if not saved
        generate_certificate_pdf(certificate)
        if certificate.pdf_file:
            return FileResponse(
                certificate.pdf_file.open('rb'),
                as_attachment=True,
                filename=f"{certificate.certificate_number}.pdf"
            )
    return None


def batch_generate_certificates(exam, passing_percentage=60):
    """Generate certificates for all students who passed"""
    from exams.models import ExamAttempt
    
    attempts = ExamAttempt.objects.filter(
        exam=exam,
        status='submitted'
    )
    
    total_marks = sum([q.marks for q in exam.questions.all()])
    passing_marks = (passing_percentage / 100) * total_marks
    
    certificates_created = []
    
    for attempt in attempts:
        if attempt.total_score >= passing_marks:
            certificate = create_certificate(
                student=attempt.student,
                exam=exam,
                attempt=attempt
            )
            certificates_created.append(certificate)
    
    return certificates_created


def get_certificate_statistics(exam):
    """Get certificate statistics for an exam"""
    total_issued = Certificate.objects.filter(exam=exam).count()
    verified = Certificate.objects.filter(exam=exam, is_digitally_verified=True).count()
    
    return {
        'total_issued': total_issued,
        'verified': verified,
        'verification_rate': (verified / total_issued * 100) if total_issued > 0 else 0,
    }
