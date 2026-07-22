from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generar_pdf(request, template_src, context_dict={}):
    """
    Función de utilidad para generar un archivo PDF a partir de una plantilla HTML.
    Utiliza xhtml2pdf para compilar HTML simple y CSS en formato PDF imprimible.
    Devuelve un HttpResponse con tipo de contenido 'application/pdf'.
    """
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    
    # Se codifica a UTF-8 para garantizar el soporte de acentos y caracteres especiales en español
    pdf = pisa.pisaDocument(
        BytesIO(html.encode("utf-8")), 
        result, 
        encoding='utf-8'
    )
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    return None
