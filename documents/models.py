from django.conf import settings
from django.db import models
from .choices import DESIGN_OWNERSHIP_CHOICES, MANUFACTURING_OPTIONS_CHOICES, FINISHED_DEVICE_CHOICES
from organization.models import Role, Location

class DocumentType(models.Model):
    display_name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.display_name} ({self.code})'

class DocumentRevisionPreviousRevisionActionTag(models.Model):
    display_name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f'{self.display_name}'

class DocumentChange(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason_for_change = models.TextField()
    description_of_change = models.TextField()

    def __str__(self):
        return f'DC-{self.pk} - {self.title}'

class Document(models.Model):
    control_number = models.CharField(max_length=255, unique=True)
    legacy_control_number = models.CharField(max_length=255, blank=True, unique=True)
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE)
    
    def __str__(self):
        if self.legacy_control_number:
            return f'{self.document_type.code}-{self.control_number} ({self.legacy_control_number})'
        else:
            return f'{self.document_type.code}-{self.control_number}'

class DocumentRevision(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    document_change = models.ForeignKey(DocumentChange, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    major_revision = models.CharField(max_length=255)
    legacy_revision = models.CharField(max_length=255, blank=True)
    design_ownership = models.CharField(max_length=255, choices=DESIGN_OWNERSHIP_CHOICES, default='SELF')
    manufacturing_options = models.CharField(max_length=255, choices=MANUFACTURING_OPTIONS_CHOICES, default='SELF')
    finished_device = models.CharField(max_length=255, choices=FINISHED_DEVICE_CHOICES, default='NO')
    
    # Change relevant
    change_description = models.TextField()
    previous_revision_disposition = models.TextField()
    previous_revision_action_tags = models.ManyToManyField(DocumentRevisionPreviousRevisionActionTag, blank=True)

    # Only used for documents with a process subsection
    process_purpose_and_scope = models.TextField(blank=True)
    process_set_roles_by_step = models.BooleanField(default=False)
    process_roles = models.ManyToManyField(Role, blank=True)
    process_set_locations_by_step = models.BooleanField(default=False)
    process_locations = models.ManyToManyField(Location, blank=True)

    # Only used for shippable finished device
    device_identifier_number = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('document', 'major_revision')
    
    def __str__(self):
        if self.legacy_revision:
            return f'{self.document} - Rev. {self.major_revision} (Legacy Rev. {self.legacy_revision})'
        else:
            return f'{self.document} - Rev. {self.major_revision}'

class DocumentRevisionInputPart(models.Model):
    document_revision = models.ForeignKey(DocumentRevision, on_delete=models.CASCADE)
    input_part = models.ForeignKey(Document, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.document_revision} Input Part: {self.input_part}'
    
    class Meta:
        unique_together = ('document_revision', 'input_part')

class DocumentRevisionOutputPart(models.Model):
    # Some process documents can describe how to make multiple parts.
    document_revision = models.ForeignKey(DocumentRevision, on_delete=models.CASCADE)
    output_part = models.ForeignKey(Document, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.document_revision} Output Part: {self.output_part}'
    
    class Meta:
        unique_together = ('document_revision', 'output_part')

class DocumentRevisionAttachedFile(models.Model):
    document_revision = models.ForeignKey(DocumentRevision, on_delete=models.CASCADE)
    file = models.FileField(upload_to='document_revision_attached_files/')
    description = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.document_revision} Attached File: {self.file.name}'

class DocumentRevisionProcessStep(models.Model):
    document_revision = models.ForeignKey(DocumentRevision, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    roles = models.ManyToManyField(Role, blank=True)
    locations = models.ManyToManyField(Location, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='document_revision_process_step_images/', blank=True)

    def __str__(self):
        return f'{self.document_revision} Process{self.process_document}'

class DocumentRevisionPolicySection(models.Model):
    document_revision = models.ForeignKey(DocumentRevision, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    order = models.PositiveIntegerField()
    header = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return f'{self.document_revision} Policy Section: {self.header}'