from django.db import models

class PriorityType(models.TextChoices):
    low = "low", "Low"
    high = "high", "High"
    force = "force", "Force"
    
class TicketStatus(models.TextChoices):
    open = "open", "Open"
    close = "close", "Close"
    
class TicketCategory(models.TextChoices):
    technical = "technical", "Technical"
    course = "course", "Course"
    mentoring = "mentoring", "Mentoring"
