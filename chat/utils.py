import uuid
import zipfile
import mimetypes
from django.core.exceptions import ValidationError
import jdatetime

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helper function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def validate_attachment_file(value):
    valid_mime_types = [
        'image/jpeg', 'image/png', 'image/gif',
        'text/plain',
        'application/pdf',
        'application/zip',
    ]

    file_obj = getattr(value, 'file', value)
    
    file_mime_type, _ = mimetypes.guess_type(value.name)

    if file_mime_type not in valid_mime_types:
        raise ValidationError('Invalid file type. Only images, text, PDF, and ZIP files are allowed.')

    if file_mime_type == 'application/zip':
        
        try:
            file_obj.seek(0)
            with zipfile.ZipFile(file_obj, 'r') as zip_ref:
                zip_ref.testzip()
                if len(zip_ref.namelist()) > 100:
                    
                    raise ValidationError('ZIP file contains too many files.')
                
        except zipfile.BadZipFile:
            
            raise ValidationError('Invalid ZIP file.')
        
def generate_ticket_number():
    year = jdatetime.date.today().year
    return f"{year}-{uuid.uuid4().hex[:8]}"
