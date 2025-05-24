import requests
from celery import shared_task
from django.conf import settings
from .models import Question, Answer

@shared_task(bind=True)
def analyze_text(self, model_name, instance_id):
    """
    Llama a la API externa de análisis y actualiza el campo `apto`
    model_name: 'question' o 'answer'
    instance_id: PK de la instancia
    """
    # Obtener objeto
    Model = Question if model_name == 'question' else Answer
    instance = Model.objects.get(pk=instance_id)

    # Preparar payload según tu API
    texts = []
    if model_name == 'question':
        texts = [
            {"id": "title", "text": instance.title},
            {"id": "descripcion", "text": instance.description}
        ]
    else:
        texts = [{"id": "description", "text": instance.description}]

    # Obtener token (si tu API lo necesita)
    auth = {"username": settings.ANALYZER_USER, "password": settings.ANALYZER_PASS}
    token_resp = requests.post(f"{settings.ANALYZER_BASE}/api/auth/token/", json=auth)
    token = token_resp.json().get('access')

    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    payload = {"texts_list": texts}

    # Llamada al endpoint de análisis
    resp = requests.post(f"{settings.ANALYZER_BASE}/api/analyzer/analysis/", json=payload, headers=headers)
    if resp.status_code == 201:
        result = resp.json()
        # Asumimos result like [{"id":"title","allowed":true}, ...]
        allowed = all(item.get('allowed', False) for item in result)
        instance.apto = allowed
        instance.save(update_fields=['apto'])
    else:
        # En caso de fallo, reintentar más tarde
        raise self.retry(countdown=60, max_retries=3)