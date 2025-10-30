"""Módulo para generar el diagrama y documento Word con los flujos.

Funciones públicas:
- generate_diagram(output_dir=None): genera PNG y DOCX en output_dir y devuelve (img_path, doc_path)
- main(): ejecuta generate_diagram() usando el directorio de salida por defecto
"""
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches
import os


def _load_fonts():
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_box = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 16)
    except Exception:
        # si no hay fuentes disponibles, usar la fuente por defecto de PIL
        font_title = ImageFont.load_default()
        font_box = ImageFont.load_default()
        font_small = ImageFont.load_default()
    return font_title, font_box, font_small


def _generate_png_diagram(img_path):
    """Genera únicamente la imagen PNG del diagrama.
    
    Args:
        img_path (str): ruta completa donde guardar la imagen PNG
        
    Returns:
        str: ruta de la imagen generada
    """
    # Create an image with PIL for clean boxes and arrows
    width, height = 1600, 800  # Hacer más grande para mejor visibilidad
    bg_color = (255, 255, 255)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    font_title, font_box, font_small = _load_fonts()

    # Colors (user specified)
    color_gestor = (14, 82, 160)       # dark blue for GestorMapeos
    color_erp = (54, 126, 223)         # medium blue for ERP Académico
    color_expedientes = (142, 199, 125)  # green for Expedientes
    border_color = (20, 60, 100)

    # Positions for boxes - Updated layout with more space
    x_gestor, y_gestor = 100, 250
    w_box, h_box = 350, 100  # Cajas más grandes

    x_api, y_api = 550, 150
    x_api_ampliacion, y_api_ampliacion = 550, 470  # Nueva caja para ampliación

    # Three green boxes stacked vertically on the right with more space
    x_expe_post1, y_expe_post1 = 1050, 150  # Expedientes general
    x_expe_post2, y_expe_post2 = 1050, 280  # POST /api/v1/expedientes-alumnos  
    x_expe_post3, y_expe_post3 = 1050, 410  # POST /api/v1/expedientes-alumnos/matricula-realizada

    # Draw title
    draw.text((width // 2 - 220, 20), "Flujos: GestorMapeos → ERP Académico → Expedientes", font=font_title, fill=(10,10,10))

    # Helper to draw rounded rectangle with text
    def draw_box(x, y, w, h, fill, text, font, outline=(20,60,100)):
        radius = 12
        # outer rect
        draw.rounded_rectangle([x, y, x+w, y+h], radius=radius, fill=fill, outline=outline, width=3)
        # center text (multilínea)
        lines = text.split("\n")
        line_sizes = []
        for line in lines:
            if line.strip() == "":
                bbox = draw.textbbox((0, 0), "A", font=font)
            else:
                bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            line_sizes.append((tw, th))

        total_h = sum(hgt for _, hgt in line_sizes)
        start_y = y + (h - total_h) / 2
        y_offset = 0
        for (line, (tw, th)) in zip(lines, line_sizes):
            draw.text((x + (w - tw) / 2, start_y + y_offset), line, font=font,
                      fill=(255,255,255) if sum(fill[:3]) < 400 else (0,0,0))
            y_offset += th

    # Draw boxes
    draw_box(x_gestor, y_gestor, w_box, h_box, color_gestor, "GestorMapeos", font_box)
    draw_box(x_api, y_api, w_box, h_box, color_erp,
             "API Primera Matrícula\nPOST /api/v1/migrar\nhttps://erpacademico.unir.net",
             font_box)
    draw_box(x_api_ampliacion, y_api_ampliacion, w_box, h_box, color_erp,
             "API Ampliación\nPOST /api/v1/migrar/ampliacion\nhttps://erpacademico.unir.net",
             font_box)
    # Three green boxes stacked vertically
    draw_box(x_expe_post1, y_expe_post1, w_box, h_box, color_expedientes, 
             "Expedientes\nhttps://expedientesacademico.unir.net", font_box)
    draw_box(x_expe_post2, y_expe_post2, w_box, h_box, color_expedientes, 
             "POST /api/v1/expedientes-alumnos", font_box)
    draw_box(x_expe_post3, y_expe_post3, w_box, h_box, color_expedientes, 
             "POST /api/v1/expedientes-alumnos/matricula-realizada", font_box)

    # Draw arrows (lines with triangles)
    def draw_arrow(x1, y1, x2, y2, fill=(10,10,10), width_line=4):
        draw.line((x1, y1, x2, y2), fill=fill, width=width_line)
        # draw triangle head
        import math
        angle = math.atan2(y2 - y1, x2 - x1)
        head_len = 14
        left = (x2 - head_len * math.cos(angle) + head_len/2 * math.sin(angle),
                y2 - head_len * math.sin(angle) - head_len/2 * math.cos(angle))
        right = (x2 - head_len * math.cos(angle) - head_len/2 * math.sin(angle),
                 y2 - head_len * math.sin(angle) + head_len/2 * math.cos(angle))
        draw.polygon([ (x2,y2), left, right ], fill=fill)

    # Function to draw text on arrows
    def draw_arrow_with_text(x1, y1, x2, y2, text, fill=(10,10,10), width_line=4):
        draw_arrow(x1, y1, x2, y2, fill, width_line)
        # Calculate text position (middle of the arrow)
        text_x = (x1 + x2) // 2 - 50  # Ajustar posición horizontal
        text_y = (y1 + y2) // 2 - 20  # Más arriba de la línea
        # Fondo blanco para el texto
        bbox = draw.textbbox((text_x, text_y), text, font=font_small)
        draw.rectangle([bbox[0]-3, bbox[1]-2, bbox[2]+3, bbox[3]+2], fill=(255,255,255), outline=(200,200,200))
        draw.text((text_x, text_y), text, font=font_small, fill=fill)

    # Flow 1: GestorMapeos -> API Primera Matrícula -> Two green boxes (not matricula-realizada)
    draw_arrow_with_text(x_gestor + w_box, y_gestor + h_box/2, 
                         x_api, y_api + h_box/2, 
                         "Primera Matrícula")
    
    # From API Primera Matrícula to only the first two green boxes
    draw_arrow_with_text(x_api + w_box, y_api + h_box/2, 
                         x_expe_post1, y_expe_post1 + h_box/2, 
                         "Crear/Actualizar")
    
    draw_arrow_with_text(x_api + w_box, y_api + h_box/2 + 10, 
                         x_expe_post2, y_expe_post2 + h_box/2, 
                         "Crear Expediente")

    # Flow 2: GestorMapeos -> API Ampliación -> Last green box only
    draw_arrow_with_text(x_gestor + w_box, y_gestor + h_box/2 + 40, 
                         x_api_ampliacion, y_api_ampliacion + h_box/2, 
                         "Ampliación")
    
    draw_arrow_with_text(x_api_ampliacion + w_box, y_api_ampliacion + h_box/2, 
                         x_expe_post3, y_expe_post3 + h_box/2, 
                         "Matricula Realizada")

    # Add legends at bottom
    legend_y = 650  # Ajustar posición para el nuevo layout más grande
    draw.rectangle([80, legend_y, 80+24, legend_y+24], fill=color_gestor)
    draw.text((115, legend_y), "GestorMapeos", font=font_small, fill=(0,0,0))
    draw.rectangle([300, legend_y, 300+24, legend_y+24], fill=color_erp)
    draw.text((335, legend_y), "ERP Académico", font=font_small, fill=(0,0,0))
    draw.rectangle([520, legend_y, 520+24, legend_y+24], fill=color_expedientes)
    draw.text((555, legend_y), "Expedientes", font=font_small, fill=(0,0,0))

    # Save image
    img.save(img_path)
    return img_path


def _generate_word_document(doc_path, img_path):
    """Genera únicamente el documento Word con documentación detallada.
    
    Args:
        doc_path (str): ruta completa donde guardar el documento DOCX
        img_path (str): ruta de la imagen PNG para embeber en el documento
        
    Returns:
        str: ruta del documento generado
    """
    # Create Word doc and embed image and textual info
    doc = Document()
    doc.add_heading('Esquema de Flujos: GestorMapeos → ERP Académico → Expedientes', level=1)
    doc.add_paragraph('Diagrama con colores diferenciados por sistema y URLs completas. Incluye los flujos de "Primera Matrícula" y "Ampliación".')

    doc.add_heading('URLs usadas', level=2)
    doc.add_paragraph('• ERP - Primera migración (crear/actualizar expediente): https://erpacademico.unir.net/api/v1/migrar')
    doc.add_paragraph('• ERP - Ampliación (no primera matrícula): https://erpacademico.unir.net/api/v1/migrar/ampliacion')
    doc.add_paragraph('• Expedientes - crear expediente (POST): https://expedientesacademico.unir.net/api/v1/expedientes-alumnos')
    doc.add_paragraph('• Expedientes - modificar por integración (PUT): https://expedientesacademico.unir.net/api/v1/expedientes-alumnos/{id}/por-integracion')
    doc.add_paragraph('• Expedientes - matrícula realizada (POST): https://expedientesacademico.unir.net/api/v1/expedientes-alumnos/matricula-realizada')

    doc.add_heading('Descripción de los flujos', level=2)
    doc.add_paragraph('Flujo 1 — Primera Matrícula:')
    doc.add_paragraph('GestorMapeos -> POST https://erpacademico.unir.net/api/v1/migrar -> ERP guarda matrícula (objeto).')
    doc.add_paragraph('  - Si es PRIMERA matrícula: el ERP puede CREAR o ACTUALIZAR el expediente en el servicio de Expedientes:')
    doc.add_paragraph('    • Crear expediente: POST https://expedientesacademico.unir.net/api/v1/expedientes-alumnos')
    doc.add_paragraph('    • Actualizar expediente existente: PUT https://expedientesacademico.unir.net/api/v1/expedientes-alumnos/{id}/por-integracion')

    doc.add_paragraph('Flujo 2 — Ampliación:')
    doc.add_paragraph('Si NO es la primera matrícula (ampliación): GestorMapeos -> POST https://erpacademico.unir.net/api/v1/migrar/ampliacion -> ERP guarda matrícula -> ERP llama a Expedientes para notificar matrícula realizada:')
    doc.add_paragraph('  - Notificar matrícula realizada (Expedientes): POST https://expedientesacademico.unir.net/api/v1/expedientes-alumnos/matricula-realizada')

    doc.add_heading('PlantUML (código)', level=2)
    plantuml_code = """
@startuml
skinparam rectangle {
  BackgroundColor<<Gestor>> #0E52A0
  BackgroundColor<<ERP>> #367EDF
  BackgroundColor<<Expedientes>> #8EC77D
  FontColor white
}
actor "GestorMapeos" as GM <<Gestor>>
rectangle "ERP Académico\nPOST /api/v1/migrar (primera)\nPOST /api/v1/migrar/ampliacion (no primera)" as ERP <<ERP>>
rectangle "Expedientes\nhttps://expedientesacademico.unir.net" as EXP <<Expedientes>>
GM --> ERP : POST /api/v1/migrar
ERP --> EXP : "Primera matrícula -> crear/actualizar expediente"
note right of ERP
    - Crear: POST /api/v1/expedientes-alumnos
    - Actualizar: PUT /api/v1/expedientes-alumnos/{id}/por-integracion
end note
GM --> ERP : POST /api/v1/migrar/ampliacion
ERP --> EXP : POST /api/v1/expedientes-alumnos/matricula-realizada
@enduml
"""
    doc.add_paragraph(plantuml_code)

    doc.add_heading('Imagen del diagrama', level=2)
    doc.add_picture(img_path, width=Inches(6.5))

    doc.add_paragraph('\nColores:\n - GestorMapeos: azul oscuro\n - ERP Académico: azul medio\n - Expedientes: verde\n')

    doc.save(doc_path)
    return doc_path


def generate_png_only(output_dir=None):
    """Genera únicamente la imagen PNG del diagrama.

    Args:
        output_dir (str): carpeta donde guardar el resultado. Si es None, se usa
            el subdirectorio `output` dentro del paquete.

    Returns:
        str: ruta de la imagen PNG generada
    """
    pkg_dir = os.path.dirname(__file__)
    if output_dir is None:
        output_dir = os.path.join(pkg_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    img_path = os.path.join(output_dir, "diagram_expedientes_flow.png")
    return _generate_png_diagram(img_path)


def generate_word_only(output_dir=None, img_path=None):
    """Genera únicamente el documento Word.

    Args:
        output_dir (str): carpeta donde guardar el resultado. Si es None, se usa
            el subdirectorio `output` dentro del paquete.
        img_path (str): ruta de la imagen PNG para embeber. Si es None, se busca
            en el directorio de salida.

    Returns:
        str: ruta del documento DOCX generado
    """
    pkg_dir = os.path.dirname(__file__)
    if output_dir is None:
        output_dir = os.path.join(pkg_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    doc_path = os.path.join(output_dir, "Esquema_Flujos_GestorMapeos_ERP_Expedientes.docx")
    
    if img_path is None:
        img_path = os.path.join(output_dir, "diagram_expedientes_flow.png")
        # Si no existe la imagen, crearla primero
        if not os.path.exists(img_path):
            _generate_png_diagram(img_path)
    
    return _generate_word_document(doc_path, img_path)


def generate_diagram(output_dir=None):
    """Genera la imagen PNG y el documento DOCX.

    Args:
        output_dir (str): carpeta donde guardar los resultados. Si es None, se usa
            el subdirectorio `output` dentro del paquete.

    Returns:
        tuple: (img_path, doc_path)
    """
    pkg_dir = os.path.dirname(__file__)
    if output_dir is None:
        output_dir = os.path.join(pkg_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    img_path = os.path.join(output_dir, "diagram_expedientes_flow.png")
    doc_path = os.path.join(output_dir, "Esquema_Flujos_GestorMapeos_ERP_Expedientes.docx")

    # Generar la imagen PNG
    img_path = _generate_png_diagram(img_path)
    
    # Generar el documento Word
    doc_path = _generate_word_document(doc_path, img_path)

    return img_path, doc_path


def main():
    img, doc = generate_diagram()
    print(f"image:{img}")
    print(f"doc:{doc}")


if __name__ == '__main__':
    main()
