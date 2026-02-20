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
from django.contrib.auth import get_user_model
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
    
    
    # Use ReportLab for high-quality PDF generation
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.units import cm, inch
        
        buffer = BytesIO()
        
        # Setup the canvas
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        width, height = landscape(A4)
        
        # Colors
        navy_blue = colors.HexColor('#1a237e')
        gold = colors.HexColor('#d4af37')
        dark_grey = colors.HexColor('#333333')
        light_grey = colors.HexColor('#555555')
        
        # --- Borders ---
        # Outer Border (Navy Blue)
        c.setStrokeColor(navy_blue)
        c.setLineWidth(15)
        c.rect(1*cm, 1*cm, width - 2*cm, height - 2*cm)
        
        # Inner Border (Gold)
        c.setStrokeColor(gold)
        c.setLineWidth(2)
        # 1cm outer margin + 15pt border (~0.5cm) + 5px padding (~0.2cm) -> approx 1.7cm
        # Let's adjust slightly for visual balance
        c.rect(1.8*cm, 1.8*cm, width - 3.6*cm, height - 3.6*cm)
        
        # --- Content ---
        center_x = width / 2
        
        # School Name
        c.setFont("Times-Bold", 32)
        c.setFillColor(navy_blue)
        school_name = settings.SCHOOL_NAME
        c.drawCentredString(center_x, height - 4*cm, school_name.upper())

        # School Address
        school_address = settings.SCHOOL_ADDRESS
        c.setFont("Times-Bold", 12)
        c.setFillColor(navy_blue)
        c.drawCentredString(center_x, height - 5*cm, school_address)
        
    
        
        # Certificate Title
        c.setFont("Times-BoldItalic", 56)
        c.setFillColor(gold)
        c.drawCentredString(center_x, height - 7*cm, "Certificate of Achievement")
        
        # Subtitle
        c.setFont("Helvetica-Oblique", 18)
        c.setFillColor(light_grey)
        c.drawCentredString(center_x, height - 8.5*cm, "This is to certify that")
        
        # Student Name
        c.setFont("Times-Bold", 42)
        c.setFillColor(navy_blue)
        student_name = f"{certificate.student.first_name} {certificate.student.last_name}"
        c.drawCentredString(center_x, height - 10.5*cm, student_name)
        
        # Underline for Student Name
        text_width = c.stringWidth(student_name, "Times-Bold", 42)
        c.setStrokeColor(gold)
        c.setLineWidth(2)
        c.line(center_x - text_width/2 - 20, height - 10.7*cm, center_x + text_width/2 + 20, height - 10.7*cm)
        
        # Achievement Text
        c.setFont("Helvetica", 18)
        c.setFillColor(colors.HexColor('#444444'))
        c.drawCentredString(center_x, height - 12.5*cm, "has successfully completed the exam")
        
        # Exam/Course Name
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(dark_grey)
        exam_name = certificate.exam.title if certificate.exam else "Examination"
        c.drawCentredString(center_x, height - 14*cm, exam_name)
        
        # Grade/Score
        c.setFont("Helvetica", 16)
        c.setFillColor(light_grey)
        score_text = f"Score: {certificate.score}/{certificate.total_marks} ({certificate.percentage:.1f}%)"
        if certificate.grade:
            score_text += f" - Grade: {certificate.grade}"
        c.drawCentredString(center_x, height - 15.5*cm, score_text)
        
        # --- Footer Section ---
        footer_y = 3.5*cm
        
        # Date Issued (Left)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(dark_grey)
        c.drawString(3*cm, footer_y + 1*cm, "Date Issued")
        c.setFont("Helvetica", 12)
        c.drawString(3*cm, footer_y, certificate.issued_at.strftime('%B %d, %Y'))
        
        # Seal (Center)
        seal_y = footer_y - 0.5*cm
        c.setStrokeColor(gold)
        c.setLineWidth(3)
        c.circle(center_x, seal_y + 1*cm, 1.5*cm) # Outer circle
        c.setLineWidth(1)
        c.circle(center_x, seal_y + 1*cm, 1.3*cm) # Inner circle
        
        c.setFont("Times-Bold", 14)
        c.setFillColor(gold)
        c.drawCentredString(center_x, seal_y + 0.9*cm, "OFFICIAL")
        c.drawCentredString(center_x, seal_y + 0.4*cm, "SEAL")
        
        # Signature (Right)
        c.setStrokeColor(dark_grey)
        c.setLineWidth(1)
        c.line(width - 9*cm, footer_y + 0.5*cm, width - 3*cm, footer_y + 0.5*cm)
        
        c.setFont("Helvetica", 12)
        c.setFillColor(dark_grey)
        c.drawCentredString(width - 6*cm, footer_y, "Authorized Signature")
        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width - 6*cm, footer_y - 0.5*cm, "Exam Controller")
        
        # Verification Code (Bottom Center, small)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.lightgrey)
        c.drawCentredString(center_x, 1*cm, f"Verification ID: {certificate.certificate_number} | Code: {certificate.verification_code}")

        c.showPage()
        c.save()
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
    except Exception as e:
        print(f"Error generating PDF with ReportLab: {e}")
        # Fallback to simple string if all else fails (should not happen if reportlab is installed)
        return None

    if pdf_content:
        filename = f"cert_{certificate.certificate_number}.pdf"
        # Save to ContentFile
        certificate.pdf_file.save(
            filename,
            ContentFile(pdf_content),
            save=True
        )
        return certificate.pdf_file
        
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
    
    User = get_user_model()
    
    for attempt in attempts:
        student_id = attempt.student_id
        if not student_id:
            continue
        try:
            student = User.objects.get(pk=student_id)
        except User.DoesNotExist:
            continue
        if attempt.total_score >= passing_marks:
            certificate = create_certificate(
                student=student,
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
