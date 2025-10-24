# Add these views to your core/views.py file

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models, transaction
from .models import Bill, BillItem
from datetime import datetime
from decimal import Decimal
import json
import openpyxl

def new_bill(request):
    """Create new bill page"""
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Get form data
            bill_date = request.POST.get('bill_date', '').strip()
            customer_name = request.POST.get('customer_name', '').strip()
            customer_mobile = request.POST.get('customer_mobile', '').strip()
            items_json = request.POST.get('items', '[]')
            
            # Validation
            if not bill_date or not customer_name or not customer_mobile:
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required'
                })
            
            if len(customer_mobile) != 10 or not customer_mobile.isdigit():
                return JsonResponse({
                    'success': False,
                    'error': 'Mobile number must be 10 digits'
                })
            
            # Parse items
            items = json.loads(items_json)
            if not items or len(items) == 0:
                return JsonResponse({
                    'success': False,
                    'error': 'At least one item is required'
                })
            
            # Calculate total
            total_amount = Decimal('0.00')
            for item in items:
                amount = Decimal(str(item['amount']))
                total_amount += amount
            
            # Create bill and items in a transaction
            with transaction.atomic():
                # Create bill
                bill = Bill.objects.create(
                    bill_date=bill_date,
                    customer_name=customer_name,
                    customer_mobile=customer_mobile,
                    total_amount=total_amount,
                    created_by=request.session.get('student_name', 'Admin')
                )
                
                # Create bill items
                for item in items:
                    BillItem.objects.create(
                        bill=bill,
                        item_name=item['item_name'],
                        quantity=Decimal(str(item['quantity'])),
                        rate=Decimal(str(item['rate'])),
                        amount=Decimal(str(item['amount']))
                    )
            
            return JsonResponse({
                'success': True,
                'bill_id': bill.id,
                'receipt_no': bill.receipt_no,
                'message': 'Bill created successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET request
    return render(request, 'new_bill.html', {
        'student_name': request.session.get('student_name')
    })


def bills_list(request):
    """View all bills page"""
    if 'student_id' not in request.session:
        messages.error(request, 'Please login to access this page.')
        return redirect('login')
    
    return render(request, 'bills.html', {
        'student_name': request.session.get('student_name')
    })


@csrf_exempt
def get_bills(request):
    """API endpoint to get filtered bills"""
    if 'student_id' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        date = request.GET.get('date', '')
        customer = request.GET.get('customer', '').strip().lower()
        
        if not date:
            return JsonResponse({
                'success': False,
                'error': 'Date is required'
            })
        
        # Filter bills by date
        bills = Bill.objects.filter(bill_date=date)
        
        # Filter by customer name if provided
        if customer:
            bills = bills.filter(
                models.Q(customer_name__icontains=customer)
            )
        
        # Prepare bills data
        bills_data = []
        for bill in bills:
            items_count = bill.items.count()
            bills_data.append({
                'id': bill.id,
                'receipt_no': bill.receipt_no,
                'bill_date': bill.bill_date.strftime('%Y-%m-%d'),
                'customer_name': bill.customer_name,
                'customer_mobile': bill.customer_mobile,
                'total_amount': float(bill.total_amount),
                'items_count': items_count
            })
        
        return JsonResponse({
            'success': True,
            'bills': bills_data,
            'count': len(bills_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def print_bill(request, bill_id):
    """Print bill page"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    try:
        bill = get_object_or_404(Bill, id=bill_id)
        items = bill.items.all()
        
        # Convert amount to words
        amount_in_words = convert_amount_to_words(float(bill.total_amount))
        
        context = {
            'bill': bill,
            'items': items,
            'amount_in_words': amount_in_words
        }
        
        return render(request, 'print_bill.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading bill: {str(e)}')
        return redirect('bills_list')


def export_bills(request):
    """Export bills to Excel"""
    if 'student_id' not in request.session:
        return redirect('login')
    
    try:
        date = request.GET.get('date', '')
        customer = request.GET.get('customer', '').strip().lower()
        
        if not date:
            messages.error(request, 'Date is required for export')
            return redirect('bills_list')
        
        # Filter bills by date
        bills = Bill.objects.filter(bill_date=date)
        
        # Filter by customer name if provided
        if customer:
            bills = bills.filter(
                models.Q(customer_name__icontains=customer)
            )
        
        # Create workbook
        wb = openpyxl.Workbook()
        
        # Sheet 1: Bills Summary
        ws_summary = wb.active
        ws_summary.title = "Bills Summary"
        
        # Headers for summary
        summary_headers = [
            'Receipt No', 'Date', 'Customer Name', 
            'Mobile', 'Items Count', 'Total Amount'
        ]
        
        # Write summary headers
        for col, header in enumerate(summary_headers, 1):
            cell = ws_summary.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
            cell.fill = openpyxl.styles.PatternFill(
                start_color="4472C4",
                end_color="4472C4",
                fill_type="solid"
            )
        
        # Write summary data
        row = 2
        for bill in bills:
            items_count = bill.items.count()
            ws_summary.cell(row=row, column=1, value=bill.receipt_no)
            ws_summary.cell(row=row, column=2, value=bill.bill_date.strftime('%d/%m/%Y'))
            ws_summary.cell(row=row, column=3, value=bill.customer_name)
            ws_summary.cell(row=row, column=4, value=bill.customer_mobile)
            ws_summary.cell(row=row, column=5, value=items_count)
            ws_summary.cell(row=row, column=6, value=float(bill.total_amount))
            row += 1
        
        # Auto-adjust column widths for summary
        for column in ws_summary.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_summary.column_dimensions[column_letter].width = adjusted_width
        
        # Sheet 2: Items Details
        ws_items = wb.create_sheet(title="Items Details")
        
        # Headers for items
        items_headers = [
            'Receipt No', 'Bill Date', 'Customer Name',
            'Item Name', 'Quantity', 'Rate', 'Amount'
        ]
        
        # Write items headers
        for col, header in enumerate(items_headers, 1):
            cell = ws_items.cell(row=1, column=col, value=header)
            cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
            cell.fill = openpyxl.styles.PatternFill(
                start_color="27AE60",
                end_color="27AE60",
                fill_type="solid"
            )
        
        # Write items data
        row = 2
        for bill in bills:
            for item in bill.items.all():
                ws_items.cell(row=row, column=1, value=bill.receipt_no)
                ws_items.cell(row=row, column=2, value=bill.bill_date.strftime('%d/%m/%Y'))
                ws_items.cell(row=row, column=3, value=bill.customer_name)
                ws_items.cell(row=row, column=4, value=item.item_name)
                ws_items.cell(row=row, column=5, value=float(item.quantity))
                ws_items.cell(row=row, column=6, value=float(item.rate))
                ws_items.cell(row=row, column=7, value=float(item.amount))
                row += 1
        
        # Auto-adjust column widths for items
        for column in ws_items.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws_items.column_dimensions[column_letter].width = adjusted_width
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        filename = f"bills_{date_obj.strftime('%d%m%Y')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Save workbook
        wb.save(response)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting bills: {str(e)}')
        return redirect('bills_list')


def convert_amount_to_words(amount):
    """Convert numeric amount to words (Indian numbering system)"""
    def num_to_words(n):
        under_20 = ['Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 
                   'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 
                   'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if n < 20:
            return under_20[n]
        elif n < 100:
            return tens[n // 10] + ('' if n % 10 == 0 else ' ' + under_20[n % 10])
        elif n < 1000:
            return under_20[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' ' + num_to_words(n % 100))
        elif n < 100000:
            return num_to_words(n // 1000) + ' Thousand' + ('' if n % 1000 == 0 else ' ' + num_to_words(n % 1000))
        elif n < 10000000:
            return num_to_words(n // 100000) + ' Lakh' + ('' if n % 100000 == 0 else ' ' + num_to_words(n % 100000))
        else:
            return num_to_words(n // 10000000) + ' Crore' + ('' if n % 10000000 == 0 else ' ' + num_to_words(n % 10000000))
    
    try:
        rupees = int(amount)
        paise = int((amount - rupees) * 100)
        
        words = num_to_words(rupees) + ' Rupees'
        if paise > 0:
            words += ' and ' + num_to_words(paise) + ' Paise'
        
        return words + ' Only'
    except:
        return 'Amount conversion error'