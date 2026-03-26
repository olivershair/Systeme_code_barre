from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, JsonResponse
from django.conf import settings
from .models import Product, CompanySettings
from .forms import ProductForm, ExcelImportForm, CompanySettingsForm
from .utils import (
    create_label_pdf, create_multiple_labels_pdf,
    import_products_from_excel, export_products_to_excel
)
import os
from io import BytesIO
from PIL import Image


def company_logo_api(request):
    """API pour récupérer le logo de l'entreprise"""
    try:
        company_settings = CompanySettings.objects.first()
        if company_settings:
            logo_url = None
            if company_settings.logo:
                try:
                    import os
                    if os.path.exists(company_settings.logo.path):
                        logo_url = company_settings.logo.url
                except Exception:
                    pass
            if not logo_url and company_settings.logo_data:
                logo_url = f'/logo/'
            return JsonResponse({
                'logo_url': logo_url,
                'company_name': company_settings.name
            })
        return JsonResponse({'logo_url': None})
    except:
        return JsonResponse({'logo_url': None})


@login_required
def barcode_serve(request, reference):
    """Génère et retourne l'image du code-barres à la volée"""
    import barcode as barcode_lib
    from barcode.writer import ImageWriter
    CODE128 = barcode_lib.get_barcode_class('code128')
    rv = BytesIO()
    CODE128(reference, writer=ImageWriter()).write(rv, options={
        'module_width': 0.13, 'module_height': 4.0, 'quiet_zone': 1.5,
        'font_size': 0, 'text_distance': 0, 'write_text': False,
    })
    rv.seek(0)
    return HttpResponse(rv.getvalue(), content_type='image/png')


@login_required
def logo_serve(request):
    """Sert le logo depuis la DB (base64) quand le fichier n'existe pas"""
    import base64
    company_settings = CompanySettings.objects.first()
    if company_settings and company_settings.logo_data:
        logo_bytes = base64.b64decode(company_settings.logo_data)
        return HttpResponse(logo_bytes, content_type='image/png')
    return HttpResponse(status=404)


@login_required
def product_list(request):
    """Liste tous les produits"""
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


@login_required
def product_create(request):
    """Créer un nouveau produit"""
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, 'Produit créé avec succès!')
            return redirect('preview_label', pk=product.pk)
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Nouveau Produit'})


@login_required
def product_update(request, pk):
    """Modifier un produit existant"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            product.generate_barcode()
            product.save()
            messages.success(request, 'Produit modifié avec succès!')
            return redirect('preview_label', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {
        'form': form, 
        'title': 'Modifier Produit',
        'product': product
    })


@login_required
def product_delete(request, pk):
    """Supprimer un produit"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produit supprimé avec succès!')
        return redirect('product_list')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
def preview_label(request, pk):
    """Prévisualiser l'étiquette d'un produit"""
    product = get_object_or_404(Product, pk=pk)
    company_settings = CompanySettings.objects.first()
    
    return render(request, 'products/preview_label.html', {
        'product': product,
        'company_settings': company_settings
    })


@login_required
def download_label_x21_pdf(request, pk):
    """Télécharger 21 copies de la même étiquette sur une page A4"""
    product = get_object_or_404(Product, pk=pk)
    company_settings = CompanySettings.objects.first()
    output_path = os.path.join(settings.MEDIA_ROOT, f'label_x21_{product.reference}.pdf')
    create_multiple_labels_pdf([product] * 21, company_settings, output_path)
    with open(output_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="etiquette_x21_{product.reference}.pdf"'
        return response


@login_required
def download_label_pdf(request, pk):
    """Télécharger l'étiquette en PDF"""
    product = get_object_or_404(Product, pk=pk)
    company_settings = CompanySettings.objects.first()
    
    # Créer le PDF
    buffer = BytesIO()
    output_path = os.path.join(settings.MEDIA_ROOT, f'label_{product.reference}.pdf')
    create_label_pdf(product, company_settings, output_path)
    
    # Retourner le fichier
    with open(output_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="etiquette_{product.reference}.pdf"'
        return response


@login_required
def download_label_image(request, pk):
    """Télécharger l'étiquette en image PNG"""
    product = get_object_or_404(Product, pk=pk)
    
    if product.barcode_image:
        response = FileResponse(product.barcode_image.open('rb'), content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="barcode_{product.reference}.png"'
        return response
    
    messages.error(request, 'Code-barres non disponible')
    return redirect('preview_label', pk=pk)


@login_required
def import_excel(request):
    """Importer des produits depuis Excel"""
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            
            # Sauvegarder temporairement le fichier
            temp_path = os.path.join(settings.MEDIA_ROOT, 'temp_import.xlsx')
            with open(temp_path, 'wb+') as destination:
                for chunk in excel_file.chunks():
                    destination.write(chunk)
            
            # Importer les produits
            created_products, errors = import_products_from_excel(temp_path, request.user)
            
            # Supprimer le fichier temporaire
            os.remove(temp_path)
            
            if created_products:
                messages.success(request, f'{len(created_products)} produits importés avec succès!')
            
            if errors:
                for error in errors:
                    messages.warning(request, error)
            
            return redirect('product_list')
    else:
        form = ExcelImportForm()
    
    return render(request, 'products/import_excel.html', {'form': form})


@login_required
def export_excel(request):
    """Exporter tous les produits vers Excel"""
    products = Product.objects.all()
    output_path = os.path.join(settings.MEDIA_ROOT, 'export_produits.xlsx')
    
    export_products_to_excel(products, output_path)
    
    with open(output_path, 'rb') as excel:
        response = HttpResponse(excel.read(), 
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="export_produits.xlsx"'
        return response


@login_required
def print_multiple_labels(request):
    """Afficher directement la prévisualisation de toutes les étiquettes avec pagination par 21"""
    # Prendre tous les produits et les grouper par 21
    all_products = Product.objects.all()
    company_settings = CompanySettings.objects.first()
    
    # Grouper les produits par pages de 21
    pages = []
    for i in range(0, len(all_products), 21):
        page_products = all_products[i:i+21]
        pages.append({
            'products': page_products,
            'product_ids': [str(p.id) for p in page_products],
            'page_number': (i // 21) + 1
        })
    
    return render(request, 'products/preview_multiple_labels.html', {
        'pages': pages,
        'company_settings': company_settings,
        'total_products': len(all_products),
        'total_pages': len(pages)
    })


@login_required
def select_products_for_printing(request):
    """Sélectionner des produits spécifiques pour l'impression"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        products = Product.objects.filter(id__in=product_ids)[:21]  # Limiter à 21
        company_settings = CompanySettings.objects.first()
        
        return render(request, 'products/preview_multiple_labels.html', {
            'products': products,
            'company_settings': company_settings,
            'product_ids': [str(p.id) for p in products],
            'show_all_products': False
        })
    
    products = Product.objects.all()
    return render(request, 'products/select_products.html', {'products': products})


@login_required
def preview_multiple_labels(request):
    """Prévisualiser les étiquettes multiples avant impression"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        products = Product.objects.filter(id__in=product_ids)[:21]  # Limiter à 21
        company_settings = CompanySettings.objects.first()
        
        return render(request, 'products/preview_multiple_labels.html', {
            'products': products,
            'company_settings': company_settings,
            'product_ids': [str(p.id) for p in products]
        })
    
    return redirect('print_multiple_labels')


@login_required
def download_multiple_labels_pdf(request):
    """Télécharger directement le PDF des étiquettes multiples"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        products = Product.objects.filter(id__in=product_ids)[:21]  # Limiter à 21
        company_settings = CompanySettings.objects.first()
        
        output_path = os.path.join(settings.MEDIA_ROOT, 'etiquettes_multiples.pdf')
        create_multiple_labels_pdf(list(products), company_settings, output_path)
        
        with open(output_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="etiquettes_multiples.pdf"'
            return response
    
    return redirect('print_multiple_labels')


@login_required
def download_all_labels_pdf(request):
    """Télécharger toutes les étiquettes en PDF (toutes les pages)"""
    all_products = Product.objects.all()
    company_settings = CompanySettings.objects.first()
    
    output_path = os.path.join(settings.MEDIA_ROOT, 'toutes_etiquettes.pdf')
    create_multiple_labels_pdf(list(all_products), company_settings, output_path)
    
    with open(output_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="toutes_etiquettes.pdf"'
        return response


@login_required
def print_multiple_labels_pdf(request):
    """Imprimer directement le PDF des étiquettes multiples"""
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        products = Product.objects.filter(id__in=product_ids)[:21]  # Limiter à 21
        company_settings = CompanySettings.objects.first()
        
        output_path = os.path.join(settings.MEDIA_ROOT, 'etiquettes_multiples.pdf')
        create_multiple_labels_pdf(list(products), company_settings, output_path)
        
        with open(output_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="etiquettes_multiples.pdf"'
            return response
    
    return redirect('print_multiple_labels')


@login_required
def download_single_label_from_multiple(request, pk):
    """Télécharger une étiquette individuelle depuis la prévisualisation multiple"""
    product = get_object_or_404(Product, pk=pk)
    company_settings = CompanySettings.objects.first()
    
    # Créer le PDF
    output_path = os.path.join(settings.MEDIA_ROOT, f'etiquette_{product.reference}.pdf')
    create_label_pdf(product, company_settings, output_path)
    
    # Retourner le fichier
    with open(output_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="etiquette_{product.reference}.pdf"'
        return response


@login_required
def print_single_label_from_multiple(request, pk):
    """Imprimer une étiquette individuelle depuis la prévisualisation multiple"""
    product = get_object_or_404(Product, pk=pk)
    company_settings = CompanySettings.objects.first()
    
    # Créer le PDF
    output_path = os.path.join(settings.MEDIA_ROOT, f'etiquette_{product.reference}.pdf')
    create_label_pdf(product, company_settings, output_path)
    
    # Retourner le fichier pour impression (ouverture dans le navigateur)
    with open(output_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="etiquette_{product.reference}.pdf"'
        return response


@login_required
def scan_barcode(request):
    """Page de scan de code-barres"""
    product = None
    
    if request.method == 'POST':
        barcode_value = request.POST.get('barcode_value')
        try:
            product = Product.objects.get(reference=barcode_value)
        except Product.DoesNotExist:
            messages.error(request, 'Produit non trouvé')
    
    return render(request, 'products/scan_barcode.html', {'product': product})


@login_required
def company_settings_view(request):
    """Gérer les paramètres de l'entreprise"""
    company_settings = CompanySettings.objects.first()
    
    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=company_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paramètres mis à jour avec succès!')
            return redirect('company_settings')
    else:
        form = CompanySettingsForm(instance=company_settings)
    
    return render(request, 'products/company_settings.html', {'form': form})
