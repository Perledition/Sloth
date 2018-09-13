
from datetime import*
import pandas as pd

from PIL import Image, ImageOps, ImageDraw
from django.shortcuts import render, redirect, render_to_response
from django.views.decorators.http import require_POST
from django.views.generic import View, UpdateView
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.http import HttpResponseRedirect
import operator


from rest_framework.views import APIView
from rest_framework.response import Response


from .forms import TodoForm, ItemForm, UserForm, UserLoginForm
from .forms import ProjectForm, RegistrationForm, UserAgree
from .models import Task, Project, ChecklistItem, UserProfile, UserMsg, Subscriber, UserFeed, User, FirstFeed, LearnLike


# Ansicht Dashboard
class Dashboard(View):
    form_class = Task
    template_name = 'todo/Dashboard.html'

    def get(self, request):
        form = self.form_class(None)

        if request.user.is_authenticated:
            if username_present(request.user.username) is True:

                all_todo = Task.objects.filter(user=request.user)
                all_pro = Project.objects.filter(user=request.user)
                form = TodoForm()

                wnd = []
                wd = []
                nwd = []
                nwnd = []
                receivable =[]

                for done in all_todo:

                    if done.complete is False:
                        receivable.append(done)

                for do in receivable:
                    if int(do.task_imp) > 5:
                        if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                                hours=2*int(round(do.task_eff))):
                            wnd.append(do)
                        else:
                            wd.append(do)

                    elif int(do.task_imp) <= 5:
                        if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                                hours=2*int(round(do.task_eff))):
                            nwnd.append(do)
                        else:
                            nwd.append(do)

                return render(request, self.template_name, {'wd': wd, 'wnd': wnd, 'nwd': nwd,'nwnd': nwnd, 'form':form, 'all_pro':all_pro})
            else:
                return redirect('login')
        else:
            return redirect('login')

    def post(self, request):
        form = self.form_class(None)
        todo_rng = 4

        if request.user.is_authenticated:
            all_todo = Task.objects.filter(user=request.user)
            all_pro = Project.objects.filter(user=request.user)
            form = TodoForm()

            # Greift auf die Stats-Klasse zu, um die Range für die Todo-Ansicht zu bestimmen
            rng = Stats()

            # Call für den abgefragten Rangebereich

            if int(request.POST['rng']) is 1:
                todo_rng = [date.today(), date.today()]
            elif int(request.POST['rng']) is 2:
                todo_rng = rng.week_range(date.today())
            elif int(request.POST['rng']) is 3:
                todo_rng = rng.month_range(date.today())
            elif int(request.POST['rng']) is 4:
                todo_rng = [date.today(), date(date.today().year, 12, 31)]

            wnd = []
            wd = []
            nwd = []
            nwnd = []
            receivable =[]

            for done in all_todo:
                if done.complete is False:
                    if done.task_dead <= datetime.combine(todo_rng[1], datetime.min.time().max).replace(tzinfo=timezone.utc).astimezone(tz=None):
                        receivable.append(done)

            for do in receivable:
                if int(do.task_imp) > 5:
                    if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                            hours=2*int(round(do.task_eff))):
                        wnd.append(do)
                    else:
                        wd.append(do)

                elif int(do.task_imp) <= 5:
                    if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                            hours=2*int(round(do.task_eff))):
                        nwnd.append(do)
                    else:
                        nwd.append(do)
        return render(request, self.template_name, {'wd': wd, 'wnd': wnd, 'nwd': nwd, 'nwnd': nwnd, 'form': form, 'all_pro': all_pro})


@require_POST
def addTodo(request):
    #Sidebarfunktion
    form = TodoForm(request.POST)
    if request.method == 'POST':
        dead = request.POST['date']
        time = dead.split('-')

        eff = float(request.POST['task_eff_hour'])+(int(request.POST['task_eff_minutes'])/60)

        all_pro = Project.objects.filter(user=request.user)
        project = all_pro.get(pro_title=request.POST['pro_id'])
        project.task_set.create(task_title=request.POST['task_title'],
                                task_imp=request.POST['task_imp'],
                                task_explain=request.POST['task_explain'],
                                task_dead=datetime(int(time[0]), int(time[1]), int(time[2]), int(request.POST['hour']), int(request.POST['minutes'])),
                                task_eff=float(eff),
                                user=request.user)

        next = request.POST.get('next', '/')

    return redirect(next)


class TodoDetail(View):
    template_name = 'todo/detail.html'

    # Detailansicht einzelner Aufgaben
    def get(self, request, todo_id):
        form = TodoForm()
        item_input = ItemForm()
        todo = Task.objects.get(pk=todo_id)
        items_done = 0
        csum = 0

        if todo.user == request.user:
            all_pro = Project.objects.filter(user=request.user)
            items = todo.checklistitem_set.all()

            for item in items:
                csum += 1
                if item.checked is True:
                    items_done += 1

            chat = todo.usermsg_set.all

            eff = round(todo.task_eff, 2)
            timestamp = todo.task_dead.strftime("%b %d, %Y %X")
            form = TodoForm(initial={'task_title': todo.task_title, 'task_explain': todo.task_explain,'task_imp': todo.task_imp, })

            return render(request, self.template_name, {'todo': todo, 'form': form, 'all_pro': all_pro, 'timestamp': timestamp,
                                                        'Items': items, 'ItemInput': item_input, 'eff': eff, 'chat': chat,
                                                        'checked': items_done, 'sum': csum})
        else:
            return redirect('login')

    # modifizierungsfunktion für Aufgaben
    def post(self, request, todo_id):
        todo = Task.objects.get(pk=todo_id)
        if request.user == todo.user:
            if request.POST:
                if request.POST['date']:
                        time = request.POST['date'].split('-')
                        todo.shifted = True
                        todo.shift_time = datetime.now()
                        todo.task_dead = datetime(int(time[0]), int(time[1]), int(time[2]), int(request.POST['hour']),
                                                  int(request.POST['minutes']))

                new_time = int(request.POST['task_eff_hour']) + int(request.POST['task_eff_minutes'])
                if new_time is not 0:
                    effort = float(request.POST['task_eff_hour']) + (int(request.POST['task_eff_minutes']) / 60)
                    todo.task_eff = float(effort)

                todo.task_title = request.POST['task_title']
                todo.task_imp = request.POST['task_imp']
                todo.task_explain = request.POST['task_explain']

                todo.save()
                next = request.POST['next']
            return redirect(next)
        else:
            return redirect('login')


# Detailansicht für die einzelenen Aufgaben


#Todo abschließen
def completeTodo(request, todo_id):
    #Abschlussbutton
    todo = Task.objects.get(pk=todo_id)
    todo.complete = True
    todo.task_end = datetime.now()
    todo.save()

    return redirect('index')


# todo löschen
def deleteTodo(request, todo_id):
    # deletes the object
    if request.user.is_authenticated:
        todo = Task.objects.get(pk=todo_id)
        todo.delete()

        return redirect('index')
    else:
        return redirect('login')


# Ansicht Trophypage
def TrophyIndex(request):
    template_name='todo/trophy.html'
    form = TodoForm()
    if request.user.is_authenticated:
        all_pro = Project.objects.filter(user=request.user)

        return render(request, template_name, {'all_pro': all_pro, 'form': form})
    else:
        return redirect('login')


class DetailTrophy(View):
    template_name = 'todo/trophychart.html'

    def get(self, request, project_id):
        # Detailansicht eines Projektes
        form = TodoForm()
        many = 0
        pdict = {}
        pareto_list_keys = []
        pareto_list_values = []
        end_pareto_list=[]
        counter = 0
        pareto = 0
        index = 0
        count = 0
        i = 0
        value = 0
        all_pro = Project.objects.filter(user=request.user)

        trophy = Project.objects.get(pk=project_id)
        editform = ProjectForm(initial={'pro_title': trophy.pro_title, 'pro_desc': trophy.pro_desc})

        if trophy.user == request.user:
            do = trophy.task_set.all()
            for todos in do:
                many +=1
                if todos.complete == True:
                    count +=1

            if many == 0:
                status = '0%'
                par = '0%'
                reto = '0%'
                dopart = 0
                perpart = 0
            elif many == count:
                status = '100%'
                par = '0%'
                reto = '0%'
                dopart = 0
                perpart = 0

            else:
                status = str(round(100 * (count / many))) + '%'
                for task in do:
                    if task.complete == False:
                        pdict[task] = float(task.task_eff)
                        index += 1

                for y in range(len(pdict)):
                    pareto_list_keys.append(max(pdict.items(), key=operator.itemgetter(1))[0])
                    pareto_list_values.append(pdict.get(max(pdict.items(), key=operator.itemgetter(1))[0]))
                    del pdict[max(pdict.items(), key=operator.itemgetter(1))[0]]

                for integer in pareto_list_values:
                    counter = counter + float(integer)

                while pareto < 0.70:
                    value = value + float(pareto_list_values[i])
                    pareto = value / counter
                    i += 1

                par = str(round(100*pareto, 2))+'%'
                reto = str(round(100*i/index, 2))+'%'
                dopart = round(pareto, 2)
                perpart = (1-round(i/index, 2))
                for item in range(i):
                    end_pareto_list.append(pareto_list_keys[item])

            Series = self.pro_activity(request, project_id)

            return render(request, self.template_name, {'do': do, 'form': form, 'trophy': trophy, 'all_pro': all_pro, 'count': count,
                                                        'many': many, 'status': status, 'par': par, 'end_pareto_list': end_pareto_list,
                                                        'reto': reto, 'dopart': dopart, 'perpart': perpart, 'editform': editform,
                                                        'SeriesDates': Series[0], 'SeriesValues': Series[1]})
        else:
            return redirect('login')

    def pro_activity(self, request, project_id):
        trophy = Project.objects.get(pk=project_id)

        if trophy.user == request.user:
            todo = trophy.task_set.all()

        df = pd.DataFrame([do for do in todo if do.complete is True])
        df['date'] = pd.to_datetime([do.task_end.date() for do in todo if do.complete is True])
        df['date'] = df['date'].dt.strftime('%d/%m/%Y')
        df['count'] = 1
        df = df.groupby('date')['count'].sum().reset_index()

        return [df['date'].tolist(), df['count'].tolist()]

    def post(self, request, project_id):
        if request.user.is_authenticated:
            form = ProjectForm()
            if form.is_valid:
                update_pro = Project.objects.get(pk=project_id)
                update_pro.pro_title = request.POST['pro_title']
                update_pro.pro_desc = request.POST['pro_desc']
                pic = request.POST.get('pro_img', None)
                if pic != '':
                    update_pro.pro_pic = request.FILES['pro_img']
                    update_pro.save()
                else:
                    update_pro.save()

                next = request.POST['next']

                return redirect(next)

        else:
            return redirect('login')


def createProject(request):
    new_pro=Project()
    if request.method == 'POST':
        new_pro.pro_title=request.POST['pro_title']
        new_pro.pro_desc=request.POST['pro_desc']
        try:
            new_pro.pro_pic = request.FILES['pro_img']
            new_pro.user = request.user
            new_pro.save()
        except:
            print('pic does not work')
            new_pro.user = request.user
            new_pro.save()

    return redirect('trophy')


def delete_Trophy(request, project_id):
    project = Project.objects.get(pk=project_id)
    if project.user == request.user:
        project.delete()
        # project = Project.objects.filter(user=request.user)
        return redirect('trophy')
    else:
        return redirect('login')


def done_Trophy(request, project_id):
    project = Project.objects.get(pk=project_id)
    if project.user == request.user:
        project.pro_complete = True
        project.save()
        return redirect('trophy')
    else:
        return redirect('login')

@require_POST
def addItem(request, todo_id):

    task = Task.objects.get(pk=todo_id)

    if request.method == 'POST':

        task.checklistitem_set.create(Item_title=request.POST['ItemInput'],
                                      user=request.user,)
        next = request.POST.get('next', '/')

    return redirect(next)


@require_POST
def addmsg(request, todo_id):

    task = Task.objects.get(pk=todo_id)

    if request.method == 'POST':

        task.usermsg_set.create(textmsg=request.POST['msg_text'], sender=request.user,
                                post_time=datetime.now())
        next = request.POST.get('next', '/')

    return redirect(next)


# Item abschließen
def checkItem(request, Item_id):#Anpassungsbedarf!

    item = ChecklistItem.objects.get(pk=Item_id)
    item.checked = True
    item.save()

    # Anpassungsbedarf, der View soll zur richitgen Url redirecten, also zur Detailpage
    return redirect('/sloth/' + str(item.task.pk) + '/')


# Vorzugsweise nutzen, sobald aussreichend Verständnis vorhanden ist.
# class ChartData(APIView):
#
#    def get(self, request):
#        labels=["Anteil der Aufgaben", "Anteil des Fortschritts"]
#        data={
#            "labels": labels,
#            "default": [.2, .8],
#            "major": [.8, .2],
#        }
#        return Response(data)


# Statistik page
class Stats(View):

    template_name = 'todo/statistik_mobile.html'
    form_class = TodoForm

    def get(self, request):
        all_pro = Project.objects.filter(user=request.user)
        if request.user.is_authenticated:
            form = self.form_class(None)

            all_todo = Task.objects.filter(user=request.user)
            # variablen
            wnd = []
            wd = []
            nwd = []
            nwnd = []
            liste =[]
            set_bubble = False

            for undone in all_todo:
                if undone.complete is False:
                    liste.append(undone)
                else:
                    set_bubble = True

            for do in liste:
                if int(do.task_imp) > 5:
                    if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                            hours=2*int(round(do.task_eff))):
                        wnd.append(do)
                    else:
                        wd.append(do)

                elif int(do.task_imp) <= 5:
                    if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                            hours=2*int(round(do.task_eff))):
                        nwnd.append(do)
                    else:
                        nwd.append(do)

            # prozentualer Anteil
            i = 0
            percentlist = ['per'+str(x) for x in range(1,5)]
            for section in [wd, wnd, nwd, nwnd]:
                if not section:
                    percentlist[i] = 0
                    i+=1
                else:
                    percentlist[i] = int(round(len(section)/len(liste),2)*100)
                    i+=1

            if set_bubble is True:
                bubble = self.get_bubble_df(request, 'total', 'total')
            else:
                bubble = [(0, 0)]
            table_stats = self.table_stats(request)
            timeseries = self.user_activity_df(request)
            pros = self.get_projects_list(request)

            pro_bar = self.get_projects_effort(request)

            return render(request, self.template_name, {'per1': percentlist[0],'per2': percentlist[1],'per3': percentlist[2],
                                                        'per4': percentlist[3],

                                                        # Tabellenwerte
                                                        'done': table_stats['Total'][0], 'done_perc': table_stats['Total'][1],
                                                        'dl': table_stats['Total'][2], 'dl_perc': table_stats['Total'][3],
                                                        'shift': table_stats['Total'][4], 'shift_perc': table_stats['Total'][5],

                                                        # timeSeries
                                                        'df_times': timeseries['Total'][0], 'df_values': timeseries['Total'][1],

                                                        #bubbleChart
                                                        'bubble': bubble,

                                                        # Projektkacheln
                                                        'done_pro': pros[0], 'pros': pros[1], 'pro_ten': pros[2],

                                                        # Projektbarchart
                                                        'projekte': pro_bar[0], 'pro_effort': pro_bar[1], 'colorlist': ["#0a80e2"]*len(pro_bar[0]),

                                                        'form': form, 'all_pro': all_pro,

                                                        })
        else:
            return redirect('login')

    def post(self, request):

        all_pro = Project.objects.filter(user=request.user)
        if request.user.is_authenticated:
            form = self.form_class(None)

            all_todo = Task.objects.filter(user=request.user)
            # variablen
            wnd = []
            wd = []
            nwd = []
            nwnd = []
            liste =[]
            set_bubble = False

            for undone in all_todo:
                if undone.complete is False:
                    liste.append(undone)
                else:
                    set_bubble = True

            # Call für den abgefragten Rangebereich

            quarter = self.quarter_range(date.today())
            week = self.week_range(date.today())

            if set_bubble is True:
                if int(request.POST['rng']) is 1:
                    rng = 'week'
                    bubble = self.get_bubble_df(request, week[0], week[1])
                elif int(request.POST['rng']) is 2:
                    rng = 'month'
                    bubble = self.get_bubble_df(request, self.get_first_day(date.today()), self.get_last_day(date.today()))
                elif int(request.POST['rng']) is 3:
                    rng = 'Quarter'
                    bubble = self.get_bubble_df(request, quarter[0], quarter[1])
                elif int(request.POST['rng']) is 4:
                    rng = 'Total'
                    bubble = self.get_bubble_df(request, 'total', 'total')
            else:
                bubble = [(0, 0)]


            for do in liste:
                if int(do.task_imp) > 5:
                    if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                            hours=2*int(round(do.task_eff))):
                        wnd.append(do)
                    else:
                        wd.append(do)

                elif int(do.task_imp) <= 5:
                    if do.task_dead - datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None) > timedelta(
                            hours=2*int(round(do.task_eff))):
                        nwnd.append(do)
                    else:
                        nwd.append(do)

            # prozentualer Anteil
            i = 0
            percentlist = ['per'+str(x) for x in range(1, 5)]
            for section in [wd, wnd, nwd, nwnd]:
                if not section:
                    percentlist[i] = 0
                    i += 1
                else:
                    percentlist[i] = int(round(len(section)/len(liste), 2)*100)
                    i += 1

            table_stats = self.table_stats(request)
            timeseries = self.user_activity_df(request)
            pros = self.get_projects_list(request)

            pro_bar = self.get_projects_effort(request)

            return render(request, self.template_name, {'per1': percentlist[0], 'per2': percentlist[1], 'per3': percentlist[2],
                                                        'per4': percentlist[3],

                                                        # Tabellenwerte
                                                        'done': table_stats[rng][0], 'done_perc': table_stats[rng][1],
                                                        'dl': table_stats[rng][2], 'dl_perc': table_stats[rng][3],
                                                        'shift': table_stats[rng][4], 'shift_perc': table_stats[rng][5],

                                                        # timeSeries
                                                        'df_times': timeseries[rng][0], 'df_values': timeseries[rng][1],

                                                        # bubbleChart
                                                        'bubble': bubble,

                                                        # Projektkacheln
                                                        'done_pro': pros[0], 'pros': pros[1], 'pro_ten': pros[2],

                                                        # Projektbarchart
                                                        'projekte': pro_bar[0], 'pro_effort': pro_bar[1], 'colorlist': ["#0a80e2"]*len(pro_bar[0]),

                                                        'form': form, 'all_pro': all_pro,

                                                        })
        else:
            return redirect('login')

    def get_bubble_df(self, request, s_range, e_range):
        # erstellt einen df für die Auswertung des BubbleChart
        all_todo = Task.objects.filter(user=request.user)

        task_end = []
        task_dead = []
        task_imp = []
        task_eff = []

        for do in all_todo:
            if do.complete is True:
                task_end.append(do.task_end)
                task_eff.append(do.task_eff)
                task_dead.append(do.task_dead)
                task_imp.append(do.task_imp)

        df = pd.DataFrame(task_imp)
        df = df.rename(columns={0: 'task_imp'})
        df['task_dead'] = task_dead
        df['task_eff'] = task_eff
        df['task_end'] = task_end
        df['timedelta'] = df['task_dead'] - df['task_end']
        df['td_sec'] = df['timedelta'].dt.total_seconds().astype(float)//3600*(-1)
        df['ddelata'] = df['task_eff']/df['td_sec']

        if s_range is not 'total':
            df = df[(df['task_end'].dt.date <= e_range) & (df['task_end'].dt.date >= s_range)]

        imp = df['task_imp'].tolist()
        delt = df['td_sec'].tolist()
        bub_list = []

        for row in range(0, len(imp)):
            bub_list.append((round(delt[row]), imp[row]))

        return bub_list

    def table_stats(self, request):

        columns = {'today': '', 'week': '', 'month': '', 'Quarter': '', 'Total': '', }

        quarter = self.quarter_range(date.today())
        week = self.week_range(date.today())
        columns['today'] = self.table_calcualtion(request, date.today(), date.today())
        columns['week'] = self.table_calcualtion(request, week[0], week[1])
        columns['month'] = self.table_calcualtion(request, self.get_first_day(date.today()), self.get_last_day(date.today()))
        columns['Quarter'] = self.table_calcualtion(request, quarter[0], quarter[1])
        columns['Total'] = self.table_calcualtion(request, 'total', 'total')

        return columns

    def table_calcualtion(self, request, time_start, time_end):
        all_todo = Task.objects.filter(user=request.user)

        done = 0
        dl = 0
        shift = 0
        full_stack = 0
        if time_start == time_end:
            for do in all_todo:
                full_stack += 1
                if time_start == 'total':
                    if do.complete is True:
                        done += 1
                        if do.task_dead < do.task_end:
                            dl += 1

                    if do.shifted is True:
                        shift += 1
                else:
                    if do.complete is True and do.task_end.date() == date.today():
                        done += 1
                        if do.task_dead < do.task_end:
                            dl += 1

                    if do.shifted is True and do.shift_time.date() == date.today():
                        shift += 1
        else:
            for do in all_todo:
                if time_start <= do.task_dead.date() and do.task_dead.date() <= time_end:
                    full_stack += 1

                if time_start <= do.task_end.date() and do.task_end.date() <= time_end:
                    if do.complete is True:
                        done += 1
                        if do.task_dead < do.task_end:
                            dl += 1

                    if do.shifted is True:
                        shift += 1

        return [done, self.get_perc(done, full_stack), dl, self.get_perc(dl, done), shift, self.get_perc(shift, full_stack)]

    def week_range(self, date):
        end = date + timedelta(days=6-date.weekday())
        start = end - timedelta(days=6)

        return [start, end]

    def month_range(self, any_day):
        next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
        end_date = next_month - timedelta(days=1)
        start_date = date(any_day.year, any_day.month, 1)
        return [start_date, end_date]

    def quarter_range(self, any_date):
        this_month = self.month_range(any_date.today())
        start = this_month[0]
        end = this_month[1] + timedelta(3*365/12)

        return [start, end]

    def get_first_day(self, dt, d_years=0, d_months=0):
        y, m = dt.year + d_years, dt.month + d_months
        a, m = divmod(m-1, 12)

        return date(y+a, m+1, 1)

    def get_last_day(self, dt):

        return self.get_first_day(dt, 0, 1) + timedelta(-1)

    def user_activity_df(self, request):
        all_todo = Task.objects.filter(user=request.user)

        # Erstellt einen DataFrame für das gesamte Aufgabenverzeichnis
        df = pd.DataFrame([do for do in all_todo if do.complete is True])
        df['date'] = pd.to_datetime([do.task_end.date() for do in all_todo if do.complete is True])
        df['count'] = 1
        df = df.groupby('date')['count'].sum().reset_index()

        week = self.week_range(date.today())
        month = self.month_range(date.today())
        quarter = self.quarter_range(date.today())
        year = pd.date_range(start='1-1-'+str(date.today().year), end='12-31-'+str(date.today().year))
        time_horz = {'week': self.get_timeseries(week[0], week[-1], df),
                     'month': self.get_timeseries(month[0], month[-1], df),
                     'Quarter': self.get_timeseries(quarter[0], quarter[-1], df),
                     'Total': self.get_timeseries(year[0], year[-1], df), }

        return time_horz

    def get_timeseries(self, start_date, end_date, df):

        d = pd.date_range(start=start_date, end=end_date)
        df2 = pd.DataFrame(pd.to_datetime(d))
        df2['day'] = [x for x in range(1, len(d)+1)]
        df2 = df2.rename(columns={0: 'date'})

        df3 = df2.merge(df, on='date', how='outer').fillna(0)
        df3 = df3[df3['day'] != 0]

        return [df3['date'].dt.date.tolist(), df3['count'].tolist()]

    def get_projects_list(self, request):
        all_pro = Project.objects.filter(user=request.user)
        done_pro = 0
        pros = 0
        pro_ten = 0

        for pro in all_pro:
            if pro.pro_complete is True:
                done_pro += 1
            elif pro.pro_title != 'Kein Projekt':
                pros += 1

            if pro.pro_title != 'Kein Projekt' and pro.task_set.all().count() >= 10:
                pro_ten += 1

        return [done_pro, pros, pro_ten]

    def get_projects_effort(self, request):
        all_pro = Project.objects.filter(user=request.user)
        projects = []
        efforts = []

        for project in all_pro:
            if project.pro_complete is False:
                projects.append(str(project.pro_title))

                effort = 0.0
                for task in project.task_set.all():
                    if task.complete is False:
                        effort = effort + float(task.task_eff)
                efforts.append(effort)

        return [projects, efforts]

    def get_perc(self, var1, var2):
        if var1 is not 0:
            per = round(var1/var2*100)
        else:
            per = 0
        return per


class Learn(View):
    template_name = 'todo/Learn.html'
    form_class = TodoForm

    def get(self, request):
        if request.user.is_authenticated:
            all_pro = Project.objects.filter(user=request.user)
            likes = LearnLike.objects.filter(like=True).count()
            dislikes = LearnLike.objects.filter(like=False).count()
            return render(request, self.template_name, {'like': likes, 'dislike': dislikes, 'form': self.form_class, 'all_pro': all_pro, })
        else:
            return redirect('login')


def like(request):
    if request.user.is_authenticated:
        try:
            model = LearnLike.objects.get(user=request.user)
            model.user = request.user
            model.like = True
            model.save()

        except LearnLike.DoesNotExist:
            model = LearnLike()
            model.user = request.user
            model.like = True
            model.save()

        return redirect('learn')
    else:
        return redirect('login')


def dislike(request):
    if request.user.is_authenticated:
        try:
            model = LearnLike.objects.get(user=request.user)
            model.user = request.user
            model.like = False
            model.save()

        except LearnLike.DoesNotExist:
            model = LearnLike()
            model.user = request.user
            model.like = False
            model.save()
        return redirect('learn')
    else:
        return redirect('login')


# Alle Aktionen zur Erstellung oder Verifizierung von Accounts
# User registration
def UserFormView(request):
    template_name = 'todo/register.html'

    if request.method =='POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    trophy = Project(pro_title="Kein Projekt", user=request.user)
                    trophy.save()
                    return redirect('index')
        else:
            return render(request, template_name, {'form': form})
    else:
        form = RegistrationForm()
        return render(request, template_name, {'form':form})


class Registration(View):
    template_name = 'todo/sloth_register.html'
    class_form = RegistrationForm
    class_sub_form = UserAgree

    def get(self, request):
        form = self.class_form
        sub_form = self.class_form
        return render(request, self.template_name, {'form': form, 'sub_form': sub_form})

    def post(self, request):
        form = self.class_form(request.POST)
        sub_form = self.class_form
        username = request.POST['username']
        password = request.POST['password1']
        accpet = request.POST['agree']
        accpet2 = request.POST['agree2']
        if accpet == 'True':
            if accpet2 == 'True':
                if form.is_valid():
                    form.save()
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            profile = UserProfile.objects.get(user=request.user)
                            profile.agree = True
                            profile.agree2 = True
                            profile.country = request.POST['country']
                            profile.age = request.POST['birthday']
                            profile.save()
                            trophy = Project(pro_title="Kein Projekt", user=request.user)
                            trophy.save()
                            trophy.task_set.create(
                                task_title='Klicke auf "Lernen"',
                                task_imp=10,
                                task_explain='Herzlich Willkommen bei Sloth! Um alles notwendige über Sloth zu lernen schaue in dem Reiter "Lernen" nach, wie du am besten mit Sloth arbeiten kannst.',
                                task_dead=datetime.now(),
                                task_eff=0.25,
                                user=request.user)

                            return redirect('index')
                    else:
                        return render(request, self.template_name, {'form': form})
                else:
                    msg = 'Hoppala, da hat etwas nicht gepasst. Versuche es nochmal'
                    return render(request, self.template_name, {'form': form, 'msg': msg, 'sub_form': sub_form})
            else:
                msg = 'Bitte akzeptiere die Datenschutzbedingungen'
                return render(request, self.template_name, {'form': form, 'msg': msg, 'sub_form': sub_form})
        else:
            msg = 'Bitte akzeptiere die Nutzungsbedingungen'
            return render(request, self.template_name, {'form': form, 'msg': msg, 'sub_form': sub_form})


# User login
class LoginUser(View):
    form_class = UserLoginForm
    template_name = 'todo/login_landing_mobile.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('index')
                else:
                    return render(request, self.template_name, {'error_message': 'Dein Account ist zur Zeit nicht aktiv!', 'form': form})
            else:
                return render(request, self.template_name, {'error_message': 'Uups.. Versuch es nochmal', 'form': form})

        return render(request, self.template_name, {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login')


class UserAccount(View):
    form_class = UserForm
    template_name = 'todo/Account.html'

    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if request.user.is_authenticated:
            form = self.form_class(request.POST, instance=request.user)
            if request.method:
                form.save()

                profile = UserProfile.objects.get(user=request.user)
                picture = request.POST.get('acc_pic_file', None)
                msg ='Die Änderungen wurden erfolgreich übernommen!'
                if picture is not '':

                    try:
                        image = request.FILES['acc_pic_file']
                        self.crop_to_png(image, request.user.username)
                        profile.icon = 'profile_image/thumbnail' + str(request.user.username) + '.png'
                        msg ='Die Änderungen wurden erfolgreich übernommen!'
                        profile.cust_icon = True

                    except:
                        msg = 'etwas mit deinem Bild hat nicht funktioniert, bitte stell sicher, dass es sich um eine Datei im Format JPG, JEPG oder PNG handelt'

                profile.save()

                return render(request, self.template_name, {'form': form, 'msg': msg})

            else:
                msg = 'Da hat etwas nicht funktioniert. Versuche es nochmal'
                return render(request, self.template_name, {'form': form, 'msg': msg})

        else:
            return redirect('login')

    def crop_to_png(self, picture, username):
        size = (300, 300)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        im = Image.open(picture)
        output = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output.save('media/profile_image/thumbnail' + str(username) + '.png')


class ChangePassword(View):
    form_class = PasswordChangeForm
    template_name = 'todo/change_password.html'

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {'form':form})

    def post(self, request):
        form = self.form_class(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('account')
        else:
            error='Da ist etwas scheif gegangen. Versuch es nochmal'
            return render(request, self.template_name, {'error':error, 'form':form})

@require_POST
def delete_user(request):
    if request.user.is_authenticated:
        if request.user.check_password(request.POST['password']):
            user = authenticate(username=request.user.username, password=request.POST['password'])
            if user is not None:
                user.delete()
                return redirect('delete_info')
            else:
                return redirect('login')
        else:
            print(request.POST['password'])
            return redirect('account')
    else:
        return redirect('login')


# Kontakt und Informationen
def contact(request):
    contact = Subscriber()
    # print(request.POST.get['contact'])

    if request.method == 'POST':
        next = request.POST['next']
        if request.POST['contact'] != '':
                exist = Subscriber.objects.filter(email=request.POST['contact']).count()
                if exist >= 1:
                    return redirect('contact_info')

                else:
                    contact.email = request.POST['contact']
                    contact.save()
                    return redirect('contact')
        else:
            return redirect(next)
    else:
        return redirect('login')


def info(request):
    return render(request, 'todo/information_already.html')


def feedback_info(request):
    return render(request, 'todo/thanks_for_Feedback.html')


def delete_info(request):
    return render(request, 'todo/information_delete.html')


class Feedback(View):
    template_name = 'todo/Feedback.html'

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, self.template_name)
        else:
            return redirect('login')

    def post(self, request):
        if request.user.is_authenticated:
            if request.method:
                try:
                    feedback = UserFeed.objects.get(user=request.user)
                    feedback.promotion = request.POST['promotion']
                    feedback.control = request.POST['control']
                    feedback.feature = request.POST['feature']
                    feedback.like = request.POST['like']
                    feedback.post_time = datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None)
                    feedback.save()
                    return redirect('feedback_info')

                except UserFeed.DoesNotExist:
                    feedback = UserFeed()
                    feedback.promotion = request.POST['promotion']
                    feedback.control = request.POST['control']
                    feedback.feature = request.POST['feature']
                    feedback.like = request.POST['like']
                    feedback.user = request.user
                    feedback.post_time = datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None)
                    feedback.save()
                    return redirect('feedback_info')

            else:
                return render(request, self.template_name)
        else:
            return redirect('login')


class FirstFeedback(View):
    template_name = 'todo/FirstFeedback.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if request.method:
            feedback = FirstFeed()
            feedback.impress = request.POST['impression']
            feedback.impact = request.POST['impact']
            feedback.opinion = request.POST['feature']
            feedback.how = request.POST['how']
            feedback.post_time = datetime.now().replace(tzinfo=timezone.utc).astimezone(tz=None)
            feedback.save()
            return redirect('feedback_info')

        else:
            return render(request, self.template_name)


def username_present(username):
    if User.objects.filter(username=username).exists():
        return True

    return False
