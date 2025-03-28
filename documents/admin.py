from django.contrib import admin
from .models import DocumentType, DocumentChange, Document, DocumentRevision, DocumentRevisionPreviousRevisionActionTag, DocumentRevisionInputPart, DocumentRevisionOutputPart, DocumentRevisionAttachedFile, DocumentRevisionProcessStep

admin.site.register(DocumentType)
admin.site.register(DocumentChange)
admin.site.register(Document)
admin.site.register(DocumentRevision)
admin.site.register(DocumentRevisionPreviousRevisionActionTag)
admin.site.register(DocumentRevisionInputPart)
admin.site.register(DocumentRevisionOutputPart)
admin.site.register(DocumentRevisionAttachedFile)
admin.site.register(DocumentRevisionProcessStep)
