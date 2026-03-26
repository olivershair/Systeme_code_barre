from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:pk>/preview/', views.preview_label, name='preview_label'),
    path('product/<int:pk>/download-pdf/', views.download_label_pdf, name='download_label_pdf'),
    path('product/<int:pk>/download-x21-pdf/', views.download_label_x21_pdf, name='download_label_x21_pdf'),
    path('product/<int:pk>/download-image/', views.download_label_image, name='download_label_image'),
    path('import/', views.import_excel, name='import_excel'),
    path('export/', views.export_excel, name='export_excel'),
    path('print-multiple/', views.print_multiple_labels, name='print_multiple_labels'),
    path('select-products/', views.select_products_for_printing, name='select_products_for_printing'),
    path('preview-multiple/', views.preview_multiple_labels, name='preview_multiple_labels'),
    path('download-multiple-pdf/', views.download_multiple_labels_pdf, name='download_multiple_labels_pdf'),
    path('download-all-labels/', views.download_all_labels_pdf, name='download_all_labels_pdf'),
    path('print-multiple-pdf/', views.print_multiple_labels_pdf, name='print_multiple_labels_pdf'),
    path('download-single-from-multiple/<int:pk>/', views.download_single_label_from_multiple, name='download_single_label_from_multiple'),
    path('print-single-from-multiple/<int:pk>/', views.print_single_label_from_multiple, name='print_single_label_from_multiple'),
    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('settings/', views.company_settings_view, name='company_settings'),
    path('api/company-logo/', views.company_logo_api, name='company_logo_api'),
    path('barcode/<str:reference>/', views.barcode_serve, name='barcode_serve'),
    path('logo/', views.logo_serve, name='logo_serve'),
]
