import csv
import datetime
from io import BytesIO
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q

from income.models import Income
from expenses.models import Expense, Category

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def get_filtered_transactions(user, period, start_date=None, end_date=None):
    today = datetime.date.today()
    incomes = Income.objects.filter(user=user)
    expenses = Expense.objects.filter(user=user)

    if period == 'daily':
        target_date = start_date or today
        incomes = incomes.filter(date=target_date)
        expenses = expenses.filter(date=target_date)
    elif period == 'weekly':
        s_date = start_date or (today - datetime.timedelta(days=7))
        e_date = end_date or today
        incomes = incomes.filter(date__gte=s_date, date__lte=e_date)
        expenses = expenses.filter(date__gte=s_date, date__lte=e_date)
    elif period == 'monthly':
        month = start_date.month if start_date else today.month
        year = start_date.year if start_date else today.year
        incomes = incomes.filter(date__year=year, date__month=month)
        expenses = expenses.filter(date__year=year, date__month=month)
    elif period == 'yearly':
        year = start_date.year if start_date else today.year
        incomes = incomes.filter(date__year=year)
        expenses = expenses.filter(date__year=year)

    return incomes, expenses

@login_required
def reports_dashboard(request):
    period = request.GET.get('period', 'monthly')
    date_str = request.GET.get('date', '')
    
    start_date = None
    if date_str:
        try:
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    incomes, expenses = get_filtered_transactions(request.user, period, start_date)

    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
    net_savings = total_income - total_expense

    # Category breakdown for expenses
    cat_summary = expenses.values('category__category_name', 'category__color') \
                          .annotate(total=Sum('amount')) \
                          .order_by('-total')

    context = {
        'period': period,
        'date_str': date_str,
        'incomes': incomes,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
        'net_savings': net_savings,
        'cat_summary': cat_summary,
    }
    return render(request, 'reports/reports.html', context)

@login_required
def export_csv(request):
    period = request.GET.get('period', 'monthly')
    date_str = request.GET.get('date', '')
    start_date = None
    if date_str:
        try:
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    incomes, expenses = get_filtered_transactions(request.user, period, start_date)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="financial_report_{period}_{datetime.date.today()}.csv"'

    writer = csv.writer(response)
    writer.writerow(['SMART EXPENSE TRACKER - FINANCIAL STATEMENT'])
    writer.writerow(['Export Date:', datetime.date.today()])
    writer.writerow(['Period:', period.capitalize()])
    writer.writerow([])

    # Income Section
    writer.writerow(['INCOME TRANSACTIONS'])
    writer.writerow(['Date', 'Title', 'Source', 'Amount', 'Description'])
    for inc in incomes:
        writer.writerow([inc.date, inc.title, inc.source, inc.amount, inc.description])
    writer.writerow(['Total Income', '', '', incomes.aggregate(t=Sum('amount'))['t'] or 0])
    writer.writerow([])

    # Expense Section
    writer.writerow(['EXPENSE TRANSACTIONS'])
    writer.writerow(['Date', 'Title', 'Category', 'Payment Method', 'Amount', 'Description'])
    for exp in expenses:
        cat_name = exp.category.category_name if exp.category else 'Uncategorized'
        writer.writerow([exp.date, exp.title, cat_name, exp.payment_method, exp.amount, exp.description])
    writer.writerow(['Total Expenses', '', '', '', expenses.aggregate(t=Sum('amount'))['t'] or 0])

    return response

@login_required
def export_pdf(request):
    period = request.GET.get('period', 'monthly')
    date_str = request.GET.get('date', '')
    start_date = None
    if date_str:
        try:
            start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    incomes, expenses = get_filtered_transactions(request.user, period, start_date)

    total_income = incomes.aggregate(t=Sum('amount'))['t'] or 0
    total_expense = expenses.aggregate(t=Sum('amount'))['t'] or 0
    net_savings = total_income - total_expense
    currency = request.user.profile.currency if hasattr(request.user, 'profile') else '₹'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12
    )
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=15
    )

    story.append(Paragraph("Smart Expense Tracker - Financial Statement", title_style))
    story.append(Paragraph(f"User: {request.user.username} | Period: {period.capitalize()} | Date Generated: {datetime.date.today()}", meta_style))
    story.append(Spacer(1, 10))

    # Summary Table
    summary_data = [
        ['Total Income', 'Total Expenses', 'Net Balance'],
        [f"{currency}{total_income:,.2f}", f"{currency}{total_expense:,.2f}", f"{currency}{net_savings:,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4e73df')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8f9fc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e3e6f0')),
        ('FONTSIZE', (0, 1), (-1, 1), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # Expense List Section
    story.append(Paragraph("Expense Breakdown", styles['Heading2']))
    story.append(Spacer(1, 8))

    exp_data = [['Date', 'Title', 'Category', 'Payment Method', f'Amount ({currency})']]
    for exp in expenses:
        cat_name = exp.category.category_name if exp.category else 'Uncategorized'
        exp_data.append([str(exp.date), exp.title[:25], cat_name, exp.payment_method, f"{currency}{exp.amount:,.2f}"])

    if len(exp_data) == 1:
        exp_data.append(['No expenses recorded for this period', '', '', '', ''])

    exp_table = Table(exp_data, colWidths=[80, 160, 110, 110, 80])
    exp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eaecf4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#5a5c69')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e3e6f0')),
    ]))
    story.append(exp_table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="financial_statement_{period}_{datetime.date.today()}.pdf"'
    response.write(pdf)
    return response
