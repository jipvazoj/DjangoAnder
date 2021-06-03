"""
Definition of views.
"""

from django.shortcuts import render,get_object_or_404
from django.http import HttpRequest, HttpResponseNotFound
from django.template import RequestContext
from datetime import datetime
from django.http.response import HttpResponse, Http404
from django.http import HttpResponseRedirect, HttpResponse
from .models import Question,Choice,User,Ranking
from django.template import loader
from django.core.urlresolvers import reverse
from app.forms import QuestionForm, ChoiceForm,UserForm
from django.shortcuts import redirect
import json
from django.contrib import messages
from django.http import JsonResponse


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
            'ranking' : Ranking.objects.order_by("-score")[:10]
      })

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(request,
        'app/contact.html',
        {
            'title':'Autor de la web',
            'message':'Datos de contacto',
            'year':datetime.now().year,
        })

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })

def index(request):
        latest_question_list = Question.objects.order_by('-pub_date')
        if request.user.is_authenticated:
            subjects = []
            for question in latest_question_list:
                if question.subject not in subjects:
                    subjects.append(question.subject)
            if request.method == "POST":
                    subject_selected = request.POST.get("subject","0")
                    if(subject_selected != "NoFiltrar"):
                        latest_question_list = Question.objects.order_by('-pub_date').filter(subject=subject_selected)
            context = {
                        'title':'Lista de preguntas de la encuesta',
                        'latest_question_list': latest_question_list,
                        'subjects' : subjects
                      }
        else:
            subjects = []
            for question in latest_question_list:
                contador = Choice.objects.filter(question_id = question.id).count()
                if question.subject not in subjects and (contador == 4 or (contador > 1 and Choice.objects.filter(question_id = question.id, correct=1).count() == 1)):
                    subjects.append(question.subject)
            if request.method == "POST":
                subject_selected = request.POST.get("subject","0")
                if(subject_selected != "NoFiltrar"):
                    latest_question_list = Question.objects.order_by('-pub_date').filter(subject=subject_selected)
                    latest_question_list = list(latest_question_list)
                    curated_question_list = list()
                    for question in latest_question_list:
                        contador = Choice.objects.filter(question_id = question.id).count()
                        if (contador == 4 or (contador > 1 and Choice.objects.filter(question_id = question.id, correct=1).count() == 1)):
                            curated_question_list.append(question)
                    context = {
                        'title':'Lista de preguntas de la encuesta',
                        'latest_question_list': curated_question_list,
                        'subjects' : subjects
                      }
                else:
                    context = {
                        'title':'Lista de preguntas de la encuesta',
                        'subjects' : subjects
                      }
            else:
                context = {
                        'title':'Lista de preguntas de la encuesta',
                        'subjects' : subjects
                      }
        template = loader.get_template('polls/index.html')
        return render(request, 'polls/index.html', context)

def detail(request, question_id):
     question = get_object_or_404(Question, pk=question_id)
     return render(request, 'polls/detail.html', {'title':'Respuestas asociadas a la pregunta:','question': question})

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/results.html', {'title':'Resultados de la pregunta:','question': question, })

def vote(request, question_id):
    p = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Vuelve a mostrar el form.
        return render(request, 'polls/detail.html', {
            'question': p,
            'error_message': "ERROR: No se ha seleccionado una opcion",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Siempre devolver un HttpResponseRedirect despues de procesar
        # exitosamente el POST de un form.  Esto evita que los datos se
        # puedan postear dos veces si el usuario vuelve atras en su browser.
        return HttpResponseRedirect(reverse('results', args=(p.id,selected_choice.id)))

def question_new(request):
        if request.method == "POST":
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.pub_date = datetime.now()
                question.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html',
                #{'title':'Respuestas posibles','question': question})
        else:
            form = QuestionForm()
        return render(request, 'polls/question_new.html', {'form': form})

def choice_add(request, question_id):
        question = Question.objects.get(id = question_id)
        error_message = ''
        if request.method == 'POST':
            form = ChoiceForm(request.POST)
            if form.is_valid() and Choice.objects.filter(question_id = question_id).count() < 4:
                choice = form.save(commit = False)
                choice.question = question
                choice.vote = 0
                if choice.correct and Choice.objects.filter(question_id = question_id, correct=1).count() == 1:
                    error_message = {'texto':'La pregunta ya tiene una opcion correcta','color':'red'}
                    #return render(request, 'polls/choice_new.html',
                    #{'title':'Pregunta:' + question.question_text,'form':
                    #form})
                elif Choice.objects.filter(question_id = question_id).count() == 3:
                    if (choice.correct and Choice.objects.filter(question_id = question_id, correct=1).count() == 0) or (not choice.correct and Choice.objects.filter(question_id = question_id, correct=1).count() == 1):
                        choice.save()
                    else:
                        error_message = {'texto':'La pregunta carece de opciones correctas','color':'red'}
                        #return render(request, 'polls/choice_new.html',
                        #{'title':'Pregunta:' + question.question_text,'form':
                        #form})
                else:
                    choice.save()         
                    error_message = {'texto':'La opcion se ha añadido correctamente.','color':'green'}
        else: 
            form = ChoiceForm()
        contador = Choice.objects.filter(question_id = question_id).count()
        if (contador < 2):
            valid = {'texto':'La pregunta no es valida todavia, ha de tener como minimo 2 opciones.','color':'red'}
        elif (contador > 3):
            valid = {'texto':'La pregunta ya tiene 4 opciones y es valida.','color':'green'}
            return render(request, 'polls/choice_new.html', {'title':'Pregunta:' + question.question_text,'valid':valid})
        elif (Choice.objects.filter(question_id = question_id, correct=1).count() == 0):
            valid = {'texto':'La pregunta no es valida todavia, carece de opcion correcta.','color':'red'}
        else:
            valid = {'texto':'La pregunta es valida, pero puedes añadir mas opciones incorrectas.','color':'green'}
        return render(request, 'polls/choice_new.html', {'title':'Pregunta:' + question.question_text,'form': form , 'error_message':error_message, 'valid':valid})
        #return render_to_response ('choice_new.html', {'form': form,
        #'poll_id': poll_id,}, context_instance = RequestContext(request),)
def chart(request, question_id):
    q = Question.objects.get(id = question_id)
    qs = Choice.objects.filter(question=q)
    dates = [obj.choice_text for obj in qs]
    counts = [obj.votes for obj in qs]
    context = {
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
    }

    return render(request, 'polls/grafico.html', context)

def user_new(request):
        if request.method == "POST":
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.save()
                #return redirect('detail', pk=question_id)
                #return render(request, 'polls/index.html',
                #{'title':'Respuestas posibles','question': question})
        else:
            form = UserForm()
        return render(request, 'polls/user_new.html', {'form': form})

def users_detail(request):
    latest_user_list = User.objects.order_by('email')
    template = loader.get_template('polls/users.html')
    context = {
                'title':'Lista de usuarios',
                'latest_user_list': latest_user_list,
              }
    return render(request, 'polls/users.html', context)

def api(request,action):
    if(action == 'procesarVoto'):
       return procesarVoto(request)
    elif(action == 'procesarFiltro'):
       return procesarFiltro(request)
    elif(action == 'procesarRanking'):
       return procesarRanking(request)
    else:
        return HttpResponseNotFound("API Incorrecta")  

def procesarVoto(request):
    p = get_object_or_404(Question, pk=request.POST['question_id'])
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Vuelve a mostrar el form.
        codigo = -1
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Siempre devolver un HttpResponseRedirect despues de procesar
        # exitosamente el POST de un form.  Esto evita que los datos se
        # puedan postear dos veces si el usuario vuelve atras en su browser.
        codigo = 1 if selected_choice.correct else 0
        #return HttpResponseRedirect(reverse('results',
        #args=(p.id,selected_choice.id)))
    data = {'codigo': codigo,}
    return JsonResponse(data)

def procesarFiltro(request):
        latest_question_list = Question.objects.order_by('-pub_date')
        if request.user.is_authenticated:
            subjects = []
            for question in latest_question_list:
                if question.subject not in subjects:
                    subjects.append(question.subject)
            if request.method == "POST":
                    subject_selected = request.POST.get("subject","0")
                    if(subject_selected != "NoFiltrar"):
                        latest_question_list = Question.objects.order_by('-pub_date').filter(subject=subject_selected)
            context = {
                        'title':'Lista de preguntas de la encuesta',
                        'latest_question_list': latest_question_list,
                        'subjects' : subjects
                      }
        else:
            subjects = []
            for question in latest_question_list:
                contador = Choice.objects.filter(question_id = question.id).count()
                if question.subject not in subjects and (contador == 4 or (contador > 1 and Choice.objects.filter(question_id = question.id, correct=1).count() == 1)):
                    subjects.append(question.subject)
            if request.method == "POST":
                subject_selected = request.POST.get("subject","0")
                if(subject_selected != "NoFiltrar"):
                    latest_question_list = Question.objects.order_by('-pub_date').filter(subject=subject_selected)
                    latest_question_list = list(latest_question_list)
                    curated_question_list = list()
                    for question in latest_question_list:
                        contador = Choice.objects.filter(question_id = question.id).count()
                        if (contador == 4 or (contador > 1 and Choice.objects.filter(question_id = question.id, correct=1).count() == 1)):
                            curated_question_list.append(question)
                    context = {
                        'title':'Lista de preguntas de la encuesta',
                        'latest_question_list': curated_question_list,
                        'subjects' : subjects
                      }
                else:
                    context = {
                        'title':'Lista de preguntas de la encuesta',
                        'subjects' : subjects
                      }
            else:
                context = {
                        'title':'Lista de preguntas de la encuesta',
                        'subjects' : subjects
                      }
        template = loader.get_template('polls/preguntasAJAX.html')
        return render(request, 'polls/preguntasAJAX.html', context)

def procesarRanking(request):
    name = Ranking.objects.filter(nombre = request.POST.get("name","0")).first()
    if (name):
        name.score+=1
    else:
        name = Ranking()
        name.nombre = request.POST.get("name","0")
    name.save()
    return JsonResponse({}) #Devolvemos una respuesta vacia para indicarle al AJAX de que la peticion ha sido correcta
