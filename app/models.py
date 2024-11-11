from tortoise import fields, models

class PDFDocument(models.Model):
    id = fields.IntField(pk=True)
    filename = fields.CharField(max_length=255)
    uploaded_at = fields.DatetimeField(auto_now_add=True)
    content = fields.TextField()  # Store extracted text for question answering

class QASession(models.Model):
    id = fields.IntField(pk=True)
    pdf_document = fields.ForeignKeyField("models.PDFDocument", related_name="qa_sessions")
    question = fields.TextField()
    answer = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)