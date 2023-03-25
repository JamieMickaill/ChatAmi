# --------------------------------------------------------------
# Django imports
# --------------------------------------------------------------
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.http import JsonResponse
from django.views import generic
from django.utils.decorators import method_decorator
from django.conf import settings

# --------------------------------------------------------------
# App imports
# --------------------------------------------------------------
from .forms import AnimalForm
from .models import Choice, Question, ChatMessage


# --------------------------------------------------------------
# Project imports
# --------------------------------------------------------------
from polls.utils.decorators import ajax_required
from polls.utils.mixins import FormErrors

# --------------------------------------------------------------
# 3rd Party imports
# --------------------------------------------------------------
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = "org-0vzNOhyz2JWD9Ib3EYtmMBC5"
openai.Model.list()

class IndexView(generic.FormView):
    """
    FormView used for our home page.

    **Template:**

    :template:`polls/index.html`
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    form_class = AnimalForm
    success_url = "/"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]
        
    def generate_prompt(self, userInput, assistantFlag):
        if assistantFlag:
            return {"role": "assistant", "content": userInput} 
        else:
            return {"role": "user", "content": userInput}
        
    
    def update_messages(self,role, message):
        ChatMessage.objects.create(
            role=role,
            content=message
        )

    def get_messages(self):
        messages = ChatMessage.objects.all()
        message_list = []
        for message in messages:
            message_dict = {
                'role': message.role,
                'content': message.content
            }
            message_list.append(message_dict)
        return message_list

    # def chat_view(request):
    #     messages = ChatMessage.objects.all()
    #     context = {
    #         'messages': messages
    #     }
    #     return render(request, 'chat.html', context)
        
    @method_decorator(ajax_required)
    def post(self, request,*args, **kwargs):
        print("hi")
        data = {'result': 'Error', 'message': "Something went wrong, please try again", "redirect": False, "data":None}
        form = AnimalForm(request.POST)
        messages=self.get_messages()

        if form.is_valid():

            prompt = form.cleaned_data.get("prompt")
            self.update_messages("user",prompt)
            print(self.get_messages())

            response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=self.get_messages())

            print(response)
            responseText= response.choices[0].message.content
                    
            data.update({
                'result': "Success",
                'message': "ChatGPT has responded",
                'data': responseText
            })

            # print(responseText)
            self.update_messages("assistant",responseText)

            messages = ChatMessage.objects.all()
            context = {
                'messages': messages
            }
            # messages.append()
            return JsonResponse(data)
        else:
            data["message"] = FormErrors(form)
            return JsonResponse(data, status=400)



class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# def index(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # template = loader.get_template('polls/index.html')
    # context = {
    #     'latest_question_list': latest_question_list,
    # }
    # return HttpResponse(template.render(context, request))

# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)

# def detail(request, question_id):
#     # try:
#     #     question = Question.objects.get(pk=question_id)
#     # except Question.DoesNotExist:
#     #     raise Http404("Question does not exist")
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

    


# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})



def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))