from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify


class TaskList(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название списка")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name="Описание")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='created_lists', verbose_name="Создатель")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='task_lists',
                                     verbose_name="Участники")
    color = models.CharField(max_length=7, default="#3498db", verbose_name="Цвет")
    is_archived = models.BooleanField(default=False, verbose_name="В архиве")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Список задач"
        verbose_name_plural = "Списки задач"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure slug uniqueness
            original_slug = self.slug
            counter = 1
            while TaskList.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_active_tasks(self):
        return self.tasks.filter(is_archived=False)


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', '⏳ Ожидает'),
        ('in_progress', '🔄 В работе'),
        ('completed', '✅ Завершена'),
        ('cancelled', '❌ Отменена'),
    ]

    PRIORITY_CHOICES = [
        ('low', '🔵 Низкий'),
        ('medium', '🟡 Средний'),
        ('high', '🟠 Высокий'),
        ('urgent', '🔴 Срочный'),
    ]

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    task_list = models.ForeignKey(TaskList, on_delete=models.CASCADE,
                                  related_name='tasks', verbose_name="Список задач")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='created_tasks', verbose_name="Создатель")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='assigned_tasks',
                                    verbose_name="Исполнитель")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending', verbose_name="Статус")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES,
                                default='medium', verbose_name="Приоритет")
    due_date = models.DateTimeField(null=True, blank=True, verbose_name="Срок выполнения")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    is_archived = models.BooleanField(default=False, verbose_name="В архиве")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['assigned_to', 'status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False

    def mark_as_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def get_time_until_due(self):
        if self.due_date:
            now = timezone.now()
            if self.due_date > now:
                return self.due_date - now
        return None


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"