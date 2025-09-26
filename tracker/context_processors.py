from .models import Month

def global_months(request):
    return {'months': Month.objects.all()}