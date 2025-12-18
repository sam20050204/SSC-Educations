from django.db import models

class Enquiry(models.Model):
    COURSE_CHOICES = [
        ('MS-CIT', 'MS-CIT'),
        ('Tally', 'Tally'),
        ('Advance Excel', 'Advance Excel'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    education = models.CharField(max_length=100)   # ✅ NEW FIELD
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
