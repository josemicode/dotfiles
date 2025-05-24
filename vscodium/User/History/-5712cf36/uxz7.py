import requests
from celery import shared_task
from django.conf import settings
from users.models import Question, Answer

# @shared_task(bind=True)
# def create_reminders(self):
#     print("Creating reminders...")
#     toDos = ToDoItem.objects.filter(completed=False)
    
@shared_task(bind=True)
def send_notifications(self, instance_id):
    print("Wait...")
    print("Id: ", instance_id)

@shared_task(bind=True)
def analyze_text(self, model_name, instance_id):
    """
    # Llamada: API externa de analisis y actualiza el campo apto
    # model_name: 'question' o 'answer'
    # instance_id: PK de la instancia
    """
    #* Preparar objeto e instancia
    Model = Question if model_name == 'question' else Answer
    instance = Model.objects.get(pk=instance_id)

    #* Preparar payload, depende del API
    texts = []
    if model_name == 'question':
        texts = [
            {"id": "title", "text": instance.title},
            {"id": "descripcion", "text": instance.description}
        ]
    else:
        texts = [{"id": "description", "text": instance.description}]

    #* Obtener token de auth (autorizar)
    auth = {"username": settings.ANALYZER_USER, "password": settings.ANALYZER_PASS}
    token_resp = requests.post(
        f"{settings.ANALYZER_BASE}/api/auth/token/",
        json=auth,
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )
    
    token = token_resp.json().get('access')

    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }

    payload = {"texts_list": texts}

    #* Llamada al endpoint (metodo GET del API para analizar)
    resp = requests.post(
            f"{settings.ANALYZER_BASE}/api/analyzer/analysis/",
            json=payload,
            headers=headers
            )

    if resp.status_code == 201:
        data = resp.json()
        # El array de resultados viene bajo 'retrieved_result'
        results_list = data.get('retrieved_result') or []
        final = data.get('final_result')
        if final is not None:
            instance.apto = final
        else:
            # Si no, marcamos apto = True sólo cuando ninguna parte del text contenga palabrotas. Cada item en retrieved_result tiene: item['palabrotas']['contains'] == True|False
            contains_any_swear = any(
                entry.get('palabrotas', {}).get('contains', False)
                for entry in results_list
            )
            # Si encontramos palabrostia, apto = False; en caso contrario, True
            instance.apto = not contains_any_swear
        instance.save(update_fields=['apto'])
    else:
        #* En caso de fallo, reintentar mas tarde (3 reintentos)
        raise self.retry(countdown=60, max_retries=3)

#// TODO Actualizar modelos -> campo apto
#//TOD0: Crear vistas que ejecuten la tarea...
#//TOD0: Filtros de queries en los modelos (visibilidad)
#TODO: give context somewhere, the Obj.objects.create