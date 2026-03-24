import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
import os
from django.conf import settings
from .models import Product
import logging

logger = logging.getLogger(__name__)

# Constantes pour une meilleure maintenabilité
# Dimensions standardisées pour toutes les étiquettes
STANDARD_LABEL_WIDTH = 70 * mm
STANDARD_LABEL_HEIGHT = 40 * mm

LABEL_CONFIG = {
    'single': {
        'width': STANDARD_LABEL_WIDTH,
        'height': STANDARD_LABEL_HEIGHT,
        'border_radius': 8,
        'font_sizes': {
            'product_name': 12,
            'info': 9,
            'reference': 7,
            'phone': 6
        }
    },
    'grid': {
        'cols': 3,
        'rows': 7,
        'width': STANDARD_LABEL_WIDTH,
        'height': STANDARD_LABEL_HEIGHT,
        'border_radius': 8,
        'font_sizes': {
            'product_name': 9,
            'info': 7,
            'reference': 6,
            'phone': 5
        }
    }
}

COLORS = {
    'border': Color(0.7, 0.7, 0.7),
    'text': HexColor("#C9098C"),       # Violet principal
    'text_light': HexColor('#C9098C'), # Violet secondaire
    'line': Color(0.8, 0.8, 0.8),
    'background': Color(1, 1, 1)
}


class BarcodeGenerator:
    """Gestionnaire de génération de codes-barres avec cache"""
    
    def __init__(self):
        self.cache = {}
    
    def generate(self, reference, force=False):
        """Génère un code-barres avec mise en cache"""
        if not force and reference in self.cache:
            return self.cache[reference]
        
        try:
            CODE128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            CODE128(reference, writer=ImageWriter()).write(rv)
            rv.seek(0)
            self.cache[reference] = rv
            return rv
        except Exception as e:
            logger.error(f"Erreur génération code-barres {reference}: {e}")
            return None

barcode_generator = BarcodeGenerator()


def generate_barcode_image(reference):
    """Génère une image de code-barres avec gestion d'erreurs"""
    return barcode_generator.generate(reference)


class LabelDrawer:
    """Classe pour dessiner des étiquettes de manière cohérente"""
    
    def __init__(self, canvas_obj):
        self.canvas = canvas_obj
    
    def draw_rounded_rect(self, x, y, width, height, radius, color=COLORS['border'], fill=False):
        """Dessine un rectangle arrondi avec bordure fine"""
        self.canvas.setStrokeColor(color)
        self.canvas.setLineWidth(0.14)
        self.canvas.roundRect(x, y, width, height, radius, stroke=1, fill=1 if fill else 0)
    
    def draw_simple_line(self, x1, x2, y, color=COLORS['line'], width=0.2):
        """Dessine une ligne simple"""
        self.canvas.setStrokeColor(color)
        self.canvas.setLineWidth(width)
        self.canvas.line(x1, y, x2, y)
    
    def draw_centered_text(self, text, x, y, font_name="Helvetica", font_size=10, 
                          color=COLORS['text'], max_width=None):
        """Dessine un texte centré"""
        self.canvas.setFont(font_name, font_size)
        self.canvas.setFillColor(color)
        
        if max_width and self.canvas.stringWidth(text, font_name, font_size) > max_width:
            # Tronquer le texte si trop long
            while self.canvas.stringWidth(text + "...", font_name, font_size) > max_width and len(text) > 3:
                text = text[:-1]
            text += "..."
        
        text_width = self.canvas.stringWidth(text, font_name, font_size)
        self.canvas.drawString(x - text_width / 2, y, text)
        return text
    
    def draw_centered_multiline_text(self, text, x, y, font_name="Helvetica", font_size=10, 
                                     color=COLORS['text'], max_width=None, line_height=None):
        """Dessine un texte centré avec retour à la ligne automatique"""
        self.canvas.setFont(font_name, font_size)
        self.canvas.setFillColor(color)
        
        if line_height is None:
            line_height = font_size * 1.2
        
        if not max_width or self.canvas.stringWidth(text, font_name, font_size) <= max_width:
            # Texte tient sur une ligne
            text_width = self.canvas.stringWidth(text, font_name, font_size)
            self.canvas.drawString(x - text_width / 2, y, text)
            return 1  # Retourne le nombre de lignes
        
        # Découper le texte en plusieurs lignes
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.canvas.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Mot trop long, le tronquer
                    lines.append(word[:int(len(word) * max_width / self.canvas.stringWidth(word, font_name, font_size))])
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Dessiner chaque ligne
        for i, line in enumerate(lines):
            line_width = self.canvas.stringWidth(line, font_name, font_size)
            self.canvas.drawString(x - line_width / 2, y - (i * line_height), line)
        
        return len(lines)  # Retourne le nombre de lignes
    
    def draw_line_separator(self, x1, x2, y, color=COLORS['line'], width=0.3):
        """Dessine une ligne de séparation"""
        self.canvas.setStrokeColor(color)
        self.canvas.setLineWidth(width)
        self.canvas.line(x1, y, x2, y)
    
    def draw_logo(self, logo_path, x, y, max_width, max_height, logo_data=None):
        """Dessine un logo — utilise le base64 en DB si le fichier n'existe pas"""
        try:
            if logo_path and os.path.exists(logo_path):
                self.canvas.drawImage(logo_path, x, y, width=max_width, height=max_height,
                                     preserveAspectRatio=True, mask='auto')
                return True
            if logo_data:
                import base64 as b64mod
                logo_io = BytesIO(b64mod.b64decode(logo_data))
                self.canvas.drawImage(ImageReader(logo_io), x, y, width=max_width, height=max_height,
                                     preserveAspectRatio=True, mask='auto')
                return True
        except Exception as e:
            logger.warning(f"Erreur chargement logo: {e}")
        return False
    
    def draw_barcode(self, reference, x, y, width, height, barcode_path=None):
        """Dessine un code-barres — génère en mémoire si le fichier n'existe pas"""
        try:
            if barcode_path and os.path.exists(barcode_path):
                self.canvas.drawImage(barcode_path, x, y, width=width, height=height,
                                     preserveAspectRatio=True)
                return True
            CODE128 = barcode.get_barcode_class('code128')
            rv = BytesIO()
            CODE128(reference, writer=ImageWriter()).write(rv, options={
                'module_width': 0.13, 'module_height': 4.0, 'quiet_zone': 1.5,
                'font_size': 0, 'text_distance': 0, 'write_text': False,
            })
            rv.seek(0)
            self.canvas.drawImage(ImageReader(rv), x, y, width=width, height=height,
                                 preserveAspectRatio=True)
            return True
        except Exception as e:
            logger.warning(f"Erreur chargement code-barres: {e}")
        return False


def create_label_pdf(product, company_settings, output_path):
    """Crée un PDF d'étiquette simple et professionnelle avec design épuré"""
    try:
        c = canvas.Canvas(output_path, pagesize=A4)
        drawer = LabelDrawer(c)
        width, height = A4
        
        config = LABEL_CONFIG['single']
        label_width = config['width']
        label_height = config['height']
        
        # Centrer l'étiquette
        x_start = (width - label_width) / 2
        y_start = (height + label_height) / 2
        y_bottom = y_start - label_height
        
        # Bordure simple
        drawer.draw_rounded_rect(x_start, y_bottom, label_width, label_height, config['border_radius'])
        
        # Marges internes de sécurité
        margin = 4
        x_left = x_start + margin
        x_right = x_start + label_width - margin
        x_center = x_start + label_width / 2
        y = y_start - margin - 2
        
        # === LOGO CENTRÉ ===
        if company_settings:
            logo_width = 20 * mm
            logo_height = 10 * mm
            logo_x = x_center - logo_width / 2
            logo_path = company_settings.logo.path if company_settings.logo else ''
            logo_data = getattr(company_settings, 'logo_data', None)
            if drawer.draw_logo(logo_path, logo_x, y - logo_height, logo_width, logo_height, logo_data=logo_data):
                y -= logo_height + 3
                
                # Slogan
                c.setFont("Helvetica-Oblique", 6)
                c.setFillColor(COLORS['text_light'])
                slogan = '"Where beauty evokes confidence"'
                slogan_width = c.stringWidth(slogan, "Helvetica-Oblique", 6)
                c.drawString(x_center - slogan_width / 2, y, slogan)
                y -= 10
        
        # === NOM DU PRODUIT ===
        num_lines = drawer.draw_centered_multiline_text(
            product.name, x_center, y,
            "Helvetica-Bold", config['font_sizes']['product_name'],
            COLORS['text'],
            max_width=label_width - 2 * margin,
            line_height=config['font_sizes']['product_name'] * 1.2
        )
        y -= (num_lines * config['font_sizes']['product_name'] * 1.2) + 3
        
        # === TAILLE ===
        c.setFont("Helvetica", config['font_sizes']['info'])
        c.setFillColor(COLORS['text'])
        taille_text = f"Taille: {product.size}"
        taille_width = c.stringWidth(taille_text, "Helvetica", config['font_sizes']['info'])
        c.drawString(x_center - taille_width / 2, y, taille_text)
        y -= 8
        
        # === PRIX (EN GRAS) ===
        c.setFont("Helvetica-Bold", config['font_sizes']['info'] + 1)
        c.setFillColor(COLORS['text'])
        price_text = f"Prix: {product.price:,.0f} FCFA".replace(",", " ")
        price_width = c.stringWidth(price_text, "Helvetica-Bold", config['font_sizes']['info'] + 1)
        c.drawString(x_center - price_width / 2, y, price_text)
        y -= 8
        
        # === RÉFÉRENCE ===
        c.setFont("Helvetica", config['font_sizes']['reference'])
        c.setFillColor(COLORS['text_light'])
        ref_text = f"Réf: {product.reference}"
        ref_width = c.stringWidth(ref_text, "Helvetica", config['font_sizes']['reference'])
        c.drawString(x_center - ref_width / 2, y, ref_text)
        y -= 4
        
        # === CODE-BARRES ===
        barcode_width = 30 * mm
        barcode_height = 6 * mm
        barcode_x = x_center - barcode_width / 2
        barcode_path = product.barcode_image.path if product.barcode_image else None
        if drawer.draw_barcode(product.reference, barcode_x, y - barcode_height, barcode_width, barcode_height, barcode_path=barcode_path):
            y -= barcode_height
        
        y -= 8  # Espace supplémentaire après le code-barres
        
        # === TÉLÉPHONES ===
        if company_settings:
            c.setFont("Helvetica", config['font_sizes']['phone'])
            c.setFillColor(COLORS['text_light'])
            
            phone_text = f"{company_settings.phone_number_1}"
            if company_settings.phone_number_2:
                phone_text += f" / {company_settings.phone_number_2}"
            
            phone_width = c.stringWidth(phone_text, "Helvetica", config['font_sizes']['phone'])
            c.drawString(x_center - phone_width / 2, y, phone_text)
        
        c.save()
        return True
        
    except Exception as e:
        logger.error(f"Erreur création PDF étiquette: {e}")
        raise


def create_multiple_labels_pdf(products, company_settings, output_path):
    """Crée un PDF avec 21 étiquettes par page A4 (grille 3x7)"""
    try:
        c = canvas.Canvas(output_path, pagesize=A4)
        page_w, page_h = A4

        COLS = 3
        ROWS = 7
        PAGE_MARGIN = 5 * mm
        GAP = 2 * mm

        label_w = (page_w - 2 * PAGE_MARGIN - (COLS - 1) * GAP) / COLS
        label_h = (page_h - 2 * PAGE_MARGIN - (ROWS - 1) * GAP) / ROWS

        idx = 0
        total = len(products)

        while idx < total:
            for row in range(ROWS):
                for col in range(COLS):
                    if idx >= total:
                        break
                    lx = PAGE_MARGIN + col * (label_w + GAP)
                    ly = page_h - PAGE_MARGIN - (row + 1) * label_h - row * GAP
                    _draw_label_pdf(c, products[idx], company_settings, lx, ly, label_w, label_h)
                    idx += 1
                if idx >= total:
                    break
            if idx < total:
                c.showPage()

        c.save()
        return True

    except Exception as e:
        logger.error(f"Erreur création PDF multiples étiquettes: {e}")
        raise


def _draw_label_pdf(c, product, company_settings, x, y, w, h):
    """
    Dessine une étiquette.
    x, y  = coin bas-gauche  (système ReportLab, y=0 en bas)
    w, h  = largeur / hauteur de la cellule
    """
    PAD = 1.5 * mm
    cx  = x + w / 2

    # --- Bordure arrondie ---
    c.setStrokeColor(COLORS['border'])
    c.setFillColor(COLORS['background'])
    c.setLineWidth(0.3)
    c.roundRect(x, y, w, h, 4, stroke=1, fill=1)

    # ================================================================
    # SECTION DU BAS — ancrée depuis le bas de l'étiquette
    # ================================================================
    cur_bottom = y + PAD   # curseur remontant vers le haut

    # Téléphones (tout en bas)
    phones = []
    if company_settings:
        if company_settings.phone_number_1:
            phones.append(company_settings.phone_number_1)
        if company_settings.phone_number_2:
            phones.append(company_settings.phone_number_2)
    if phones:
        phone_str = " / ".join(phones)
        c.setFont("Helvetica", 5)
        c.setFillColor(COLORS['text_light'])
        pw = c.stringWidth(phone_str, "Helvetica", 5)
        c.drawString(cx - pw / 2, cur_bottom, phone_str)
        cur_bottom += 5 + 1 * mm

    # Code-barres (généré en mémoire, pas besoin de fichier)
    BC_H = 5 * mm
    BC_W = min(22 * mm, w - 2 * PAD)
    try:
        CODE128 = barcode.get_barcode_class('code128')
        barcode_io = BytesIO()
        CODE128(product.reference, writer=ImageWriter()).write(barcode_io, options={
            'module_width': 0.13, 'module_height': 4.0, 'quiet_zone': 1.5,
            'font_size': 0, 'text_distance': 0, 'write_text': False,
        })
        barcode_io.seek(0)
        c.drawImage(ImageReader(barcode_io), cx - BC_W / 2, cur_bottom,
                    width=BC_W, height=BC_H, preserveAspectRatio=True)
        cur_bottom += BC_H + 1 * mm
    except Exception:
        pass

    # Référence
    ref_str = f"Réf: {product.reference}"
    c.setFont("Helvetica", 5.5)
    c.setFillColor(COLORS['text_light'])
    rw = c.stringWidth(ref_str, "Helvetica", 5.5)
    c.drawString(cx - rw / 2, cur_bottom, ref_str)
    cur_bottom += 5.5 + 1 * mm

    # Prix
    price_str = f"Prix: {product.price:,.0f} FCFA".replace(",", " ")
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(COLORS['text'])
    pw2 = c.stringWidth(price_str, "Helvetica-Bold", 7)
    c.drawString(cx - pw2 / 2, cur_bottom, price_str)
    cur_bottom += 7 + 1 * mm

    # Taille
    size_str = f"Taille: {product.size}"
    c.setFont("Helvetica", 6)
    c.setFillColor(COLORS['text'])
    sw = c.stringWidth(size_str, "Helvetica", 6)
    c.drawString(cx - sw / 2, cur_bottom, size_str)
    cur_bottom += 6 + 1 * mm   # <- limite supérieure de la section basse

    # ================================================================
    # SECTION DU HAUT — ancrée depuis le haut de l'étiquette
    # ================================================================
    cur_top = y + h - PAD   # curseur descendant vers le bas

    # Logo (utilise base64 en DB si le fichier n'existe pas)
    has_logo = False
    if company_settings:
        LOGO_H = 7 * mm
        LOGO_W = 14 * mm
        logo_img = None
        try:
            if company_settings.logo and os.path.exists(company_settings.logo.path):
                logo_img = company_settings.logo.path
            elif getattr(company_settings, 'logo_data', None):
                import base64 as b64mod
                logo_io = BytesIO(b64mod.b64decode(company_settings.logo_data))
                logo_img = ImageReader(logo_io)
        except Exception:
            pass
        if logo_img:
            try:
                c.drawImage(logo_img, cx - LOGO_W / 2, cur_top - LOGO_H,
                            width=LOGO_W, height=LOGO_H,
                            preserveAspectRatio=True, mask='auto')
                has_logo = True
                cur_top -= LOGO_H + 0.5 * mm
            except Exception:
                pass

    # Slogan (seulement si logo présent)
    if has_logo:
        slogan = '"Where beauty evokes confidence"'
        c.setFont("Helvetica-Oblique", 4)
        c.setFillColor(COLORS['text_light'])
        cur_top -= 4
        slogan_w = c.stringWidth(slogan, "Helvetica-Oblique", 4)
        c.drawString(cx - slogan_w / 2, cur_top, slogan)
        cur_top -= 1 * mm

    # Nom du produit (max 2 lignes, descend depuis cur_top)
    NAME_SIZE = 7
    LINE_H = NAME_SIZE * 1.3
    inner_w = w - 2 * PAD
    words = product.name.split()
    lines, current = [], []
    for word in words:
        test = ' '.join(current + [word])
        if c.stringWidth(test, "Helvetica-Bold", NAME_SIZE) <= inner_w:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
                current = [word]
            else:
                lines.append(word)
    if current:
        lines.append(' '.join(current))
    lines = lines[:2]

    c.setFont("Helvetica-Bold", NAME_SIZE)
    c.setFillColor(COLORS['text'])
    for i, line in enumerate(lines):
        lw_val = c.stringWidth(line, "Helvetica-Bold", NAME_SIZE)
        c.drawString(cx - lw_val / 2, cur_top - (i + 1) * LINE_H, line)



def import_products_from_excel(file_path, user):
    """Importe des produits depuis un fichier Excel avec validation améliorée"""
    try:
        df = pd.read_excel(file_path)
        
        # Mapping des noms de colonnes possibles
        column_mapping = {
            'reference': ['reference', 'ref', 'code', 'sku'],
            'nom': ['nom', 'name', 'produit', 'product', 'designation'],
            'taille': ['taille', 'size', 'dimension'],
            'prix': ['prix', 'price', 'cout', 'cost']
        }
        
        # Normaliser les noms de colonnes
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Trouver les colonnes correspondantes
        used_columns = {}
        for target, possible_names in column_mapping.items():
            for col in df.columns:
                if col in possible_names:
                    used_columns[target] = col
                    break
        
        # Vérifier les colonnes requises
        required = ['reference', 'nom', 'taille', 'prix']
        missing = [col for col in required if col not in used_columns]
        if missing:
            raise ValueError(f"Colonnes manquantes: {', '.join(missing)}")
        
        created_products = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Nettoyage des données
                reference = str(row[used_columns['reference']]).strip()
                if not reference:
                    raise ValueError("Référence vide")
                
                name = str(row[used_columns['nom']]).strip()
                if not name:
                    raise ValueError("Nom vide")
                
                size = str(row[used_columns['taille']]).strip()
                
                # Conversion du prix
                price_value = row[used_columns['prix']]
                if isinstance(price_value, str):
                    price_value = price_value.replace(' ', '').replace(',', '.')
                price = float(price_value)
                
                if price < 0:
                    raise ValueError("Prix négatif")
                
                # Créer ou mettre à jour le produit
                product, created = Product.objects.update_or_create(
                    reference=reference,
                    defaults={
                        'name': name,
                        'size': size,
                        'price': price,
                        'created_by': user
                    }
                )
                
                # Générer le code-barres si nécessaire
                if not product.barcode_image:
                    product.generate_barcode()
                    product.save()
                
                created_products.append(product)
                
            except Exception as e:
                errors.append(f"Ligne {index + 2}: {str(e)}")
        
        return created_products, errors
        
    except Exception as e:
        logger.error(f"Erreur import Excel: {e}")
        raise


def export_products_to_excel(products, output_path):
    """Exporte les produits vers un fichier Excel avec formatage"""
    try:
        data = []
        for product in products:
            data.append({
                'Référence': product.reference,
                'Nom': product.name,
                'Taille': product.size,
                'Prix': product.price,
                'Date de création': product.created_at.strftime('%d/%m/%Y %H:%M'),
                'Créé par': product.created_by.username if product.created_by else ''
            })
        
        df = pd.DataFrame(data)
        
        # Formatage Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Produits')
            
            # Ajuster la largeur des colonnes
            worksheet = writer.sheets['Produits']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # Format monétaire pour la colonne prix
            for row in range(2, len(df) + 2):
                cell = worksheet[f'D{row}']
                cell.number_format = '#,##0.00 FCFA'
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur export Excel: {e}")
        raise