from django.db import models

class App(models.Model):
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name

class Plan(models.Model):
  name = models.CharField(max_length=50)
  price = models.DecimalField(max_digits=6, decimal_places=2)
  
  def __str__(self):
      return self.name
  
class Subscription(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.app.name} - {self.plan.name}'