# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, Http404, HttpResponseRedirect, render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.template import Context, RequestContext, loader
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.core.files.base import ContentFile
from vj.models import *
from django.utils import timezone
from collections import OrderedDict
import datetime
import pytz
import re
import json
import pymysql
import time
import base64

LIST_NUMBER_EVERY_PAGE = 20
PAGE_NUMBER_EVERY_PAGE = 7

LANG_DICT = {0: 'G++', 1: 'GCC', 2: 'C++', 3: 'C', 4: 'Pascal', 5: 'Java', 6: 'C#', 7: 'Python'}
LANGUAGE = {
        'G++' : '0',
        'GCC' : '1',
        'C++' : '2',
        'C' : '3',
        'Pascal' : '4',
        'Java' : '5',
        'C#' : '6',
        'Python' : '7',
        }

def ren2res(template, req, dict={}):
    if req.user.is_authenticated():
        p = re.compile('^[0-9a-zA-Z_]+$')
        dict.update({'user': {  'id': req.user.id, 
                                'username': req.user.get_username(),
                                'is_staff':req.user.is_staff,
                                #'sid':req.user.info.sid,
                                #'nickname':req.user.info.nickname,
                                #'school':req.user.info.school
                                }})
    else:
        dict.update({'user': False})
    """
    if req:
        return render_to_response(template, dict, context_instance=RequestContext(req))
    else:
        return render_to_response(template, dict)
        """
    return render(req,template,dict);
def home(req):
    return ren2res("home.html", req, {})

def login(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res("login.html", req, {})
        else:
            return HttpResponseRedirect("/")
    elif req.method == 'POST':
        user = auth.authenticate(username=req.POST.get('username'), password=req.POST.get('password'))
        if user is not None:
            auth.login(req, user)
            next = req.session.get('next')
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/')
        else:
            return ren2res("login.html", req, {'err': "Wrong Username or Password!"})

def register(req):
    if req.method == 'GET':
        if req.user.is_anonymous():
            if req.GET.get('next'):
                req.session['next'] = req.GET.get('next')
            return ren2res('register.html', req, {})
        else:
            return HttpResponseRedirect('/')
    elif req.method == 'POST':
        username = req.POST.get("username")
        school = req.POST.get('school')
        sid = req.POST.get('sid')
        nickname = req.POST.get('nickname')
        result = User.objects.filter(username=username);
        p = re.compile('^[0-9a-zA-Z_]+$')
        if len(username) == 0 or p.match(username)==None:
            return ren2res('register.html', req, {'err': "Invalid username"})
        elif len(result) != 0:
            return ren2res('register.html', req, {'err': "This username has been registered! Try another"})
        else:
            pw1 = req.POST.get('pw1')
            if pw1 == "":
                return ren2res('register.html', req, {'err': "Password can't be null", 'account': account})
            pw2 = req.POST.get('pw2')
            if pw1 != pw2:
                return ren2res('register.html', req, {'err': "Password not consistent", 'account': account})
            else:
                newuser = User()
                newuser.username = username
                newuser.set_password(pw1)
                newuser.is_staff = 0
                newuser.is_active = 1
                newuser.is_superuser = 0
                newuser.save()
                newuser = auth.authenticate(username=username, password=pw1)
                auth.login(req, newuser)

                newuserinfo = UserInfo(id=newuser)
                newuserinfo.school = school 
                newuserinfo.sid = sid 
                newuserinfo.nickname = nickname 
                newuserinfo.save()
                next = req.session.get('next')
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect('/')


def logout(req):
    auth.logout(req)
    return HttpResponseRedirect('/')

def function():
    pass

def problem(req):
    pg = int(req.GET.get('pg', 1))
    search = req.GET.get('search', "")
    originoj= req.POST.get('originoj',"")
    problemid=req.POST.get('problemid',"")
    title=req.POST.get('title',"")
    if search:
        qs = Problem.objects.filter(Q(proid__icontains=search) | Q(title__icontains=search))
    elif originoj or problemid or title:
        qs = Problem.objects.filter(Q(originoj__icontains=originoj) & Q(problemid__icontains=problemid) & Q(title__icontains=title))
    else:
        qs = Problem.objects.all()

    idxstart = (pg - 1) * LIST_NUMBER_EVERY_PAGE
    idxend = pg * LIST_NUMBER_EVERY_PAGE

    max = qs.count() // 20 + 1

    if (pg > max):
        raise Http404("no such page")
    start = pg - PAGE_NUMBER_EVERY_PAGE
    if start < 1:
        start = 1
    end = pg + PAGE_NUMBER_EVERY_PAGE
    if end > max:
        end = max

    lst = qs[idxstart:idxend]
    lst = list(lst)
    aclst = []
    trylst = []
    '''
    if req.user.is_authenticated():
        user = req.user
        for item in lst:
            if item.aceduser.filter(id=user.info.id):
                aclst.append(item.id)
            elif item.trieduser.filter(id=user.info.id):
                trylst.append(item.id)
    '''
#        print(aclst)
#        print('trylst')
#        print(trylst)
    return ren2res("problem.html", req, {'pg': pg, 'page': list(range(start, end + 1)), 'list': lst, 'aclst':aclst, 'trylst':trylst
        ,'originoj':originoj ,'problemid':problemid ,'title':title })


#db = pymysql.connect("211.87.227.207","vj","vDpAZE74bJrYahZKmcvZxwc","vj")

def problem_detail(req, proid):
    problem = Problem.objects.get(proid=proid)
    return ren2res("problem/problem_detail.html", req, {'problem': problem})
#    smp = TestCase.objects.filter(pid__exact=pid).filter(sample__exact=True)
#    return ren2res("problem/problem_detail.html", req, {'problem': problem, 'sample': smp})


@login_required
def problem_submit(req, proid):
    if req.method == 'GET':
        return ren2res("problem/problem_submit.html", req, {'problem': Problem.objects.get(proid=proid)})
    elif req.method == 'POST':
        status = Status(user=req.user, pro=Problem.objects.get(proid=proid), lang=req.POST.get('lang'), result='Waiting', 
            time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        if req.POST.get('code'):
            # f = open('JudgeFiles/source/' + str(sub.id), 'w')
            # f.write(req.POST.get('code'))
            status.code = base64.b64encode(bytes(req.POST.get('code'), 'utf-8'))
        else:
            return ren2res("problem/problem_submit.html", req,
                           {'problem': Problem.objects.get(proid=proid), 'err': "No Submit!"})
        # f.close()
        status.save()
        #sub.source_code.save(name=str(sub.id), content=content_file)
        #sub.save()
        #judger.Judger(sub);

        return HttpResponseRedirect("/status/")

def status(req):
    pro_id = req.GET.get('pro_id')
    if pro_id:
        query = Status.objects.filter(pro_id=pro_id).all().order_by('-runid')
    else:
        query = Status.objects.all().order_by('-runid')

    search = req.GET.get('search')
    if search:
        query = query.filter(Q(pro__title__icontains=search) | Q(user__username__icontains=search))

    #print(len(query))

    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count() // 20 + 1
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]
    #print(len(lst))

    return ren2res('status.html', req, {'pro_id': pro_id, 'page': range(start, end + 1), 'list': lst })


@login_required
def profile(req):
    userinfo = UserInfo.objects.get(id=req.user)
    if req.method == 'GET':
        return ren2res('profile.html',req,{"userinfo":userinfo})
    else:
        user = req.user
        if not user:
            return ren2res('profile.html',req,{})
        else:
            pw = req.POST.get('password')
            if not user.check_password(pw):
                return ren2res('profile.html', req, {'err': "Wrong password", "userinfo":userinfo})
            
            userinfo.nickname = req.POST.get('nickname')
            if len(user.info.nickname)==0:
                return ren2res('profile.html', req, {'err': "Nickname can't be null", "userinfo":userinfo})
            userinfo.school = req.POST.get('school')
            userinfo.sid = req.POST.get('sid')
            userinfo.save()
            
            npw1 = req.POST.get('npw1')
            if npw1 == "":
                return ren2res('profile.html', req, {'err': "User Profile Updated", "userinfo":userinfo})
            npw2 = req.POST.get('npw2')
            if npw1 != npw2:
                return ren2res('profile.html', req, {'err': "New Password not consistent", "userinfo":userinfo})
            else:
                user.set_password(npw1)
                user.save()
                return ren2res("login.html", req, {"userinfo":userinfo})
        return HttpResponseRedirect('/')

@login_required
def show_source(req):
    solution_id = req.GET.get('solution_id')
    query = Status.objects.filter(runid=solution_id)
    if len(query) == 0:
        raise Http404
    elif query[0].user.id != req.user.id and not req.user.is_staff:
        raise Http404
    else:
        status = query[0]
        code = base64.b64decode(bytes(status.code, 'utf-8'))
        '''
        err = ""
        try:
            f = open('/home/sduacm/OnlineJudge/JudgeFiles/result/' + str(submit.id), 'r')
            err = f.read()
            f.close()
        except IOError:
            pass
        err = err.replace("/tmp","...")
        err = err.replace("/sduoj/source","")
        print('error:')
        print(err)
        if err == '':
            err = 'Successful'
        '''
        return ren2res('show_source.html', req, {'status': status, 'code': code, 'lang': LANG_DICT[status.lang]})

#new add ,need change

def contest(req):
    search = req.GET.get('search')
    if search:
        query = Contest.objects.filter(Q(name__icontains=search) | Q(uid__username__icontains=search))
    else:
        query = Contest.objects.all()
    pg = req.GET.get('pg')
    if not pg:
        pg = 1
    pg = int(pg)

    max_cnt = query.count()
    start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
    end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

    lst = query[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

    return ren2res('contest.html', req, {'page': range(start, end + 1), 'list': lst})


@login_required
def contest_detail(req, cid):
    contest = Contest.objects.get(id=cid)
    # time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    # time = datetime.datetime.now()
    time = timezone.now()
    if time > contest.start_time:
        start = True
    else:
        start = False
    if contest.private:
        #print(problems)
        # print('contest.accounts')
        # print(contest.accounts.all())
        if req.user.is_superuser==False and req.user.info not in contest.accounts.all() :
            return ren2res("contest/contest.html", req, {'contest': contest, 'err': "You do not have access to this contest."})
    if start:
        problems = contest.get_problem_list()
        length = len(problems)
        problems_status = [0 for i in range(length)]

        for i in range(length):
            problems[i].append(len(Status.objects.filter(user = req.user).filter(pro = problems[i][2]).filter(result = 'Accepted')))#changes
        return ren2res("contest/contest.html", req, {'contest': contest, 'problems': problems, 'problem': problems[0][2]})
    else:
        return ren2res("contest/contest.html", req, {'contest': contest, 'err': "Just wait."})


@login_required
def contest_get_problem(req, cid):
    if req.is_ajax():
        contest = Contest.objects.get(id=cid)
        pid = req.GET.get('pid')
        t = loader.get_template('contest/contest_problem.html')
        problem = Problem.objects.get(proid=pid)
        if contest.private:
            if req.user.is_superuser==False and req.user.info not in contest.accounts.all() :
                problem = []
        #content_html = t.render(Context({'problem': problem, 'user' : req.user}))
        # return HttpResponse(content_html)
        return render(req,'contest/contest_problem.html',{'problem': problem, 'user' : req.user})

@login_required
def contest_status(req, cid):#has understood
    if req.is_ajax():
        contest = Contest.objects.get(id=cid)
        t = loader.get_template('contest/contest_status.html')
        status_list = Status.objects.filter(cid=cid).order_by('-time')#need change
        if contest.private:
            if req.user.is_superuser==False and req.user.info not in contest.accounts.all() :
                status_list = []
        pg = req.GET.get('pg')
        if not pg:
            pg = 1
        pg = int(pg)

        max_cnt = status_list.count() // 20 + 1
        start = max(pg - PAGE_NUMBER_EVERY_PAGE, 1)
        end = min(pg + PAGE_NUMBER_EVERY_PAGE, max_cnt)

        lst = status_list[(pg - 1) * LIST_NUMBER_EVERY_PAGE:pg * LIST_NUMBER_EVERY_PAGE]

        # content_html = t.render(Context({'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user}))
        # return HttpResponse(content_html)
        return render(req,'contest/contest_status.html',{'status_list': lst, 'page': range(start, end + 1), 'contest_id': cid, 'user': req.user})
    else:
        raise Http404


@login_required
def contest_submit(req, cid):
    contest = Contest.objects.get(id=cid)
    #time = datetime.datetime.now(pytz.timezone(pytz.country_timezones('cn')[0]))
    # time1=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    time=timezone.now()
    # print(contest.start_time + contest.duration_time)
    if time > contest.start_time + contest.duration_time:
        finish = True
    else:
        finish = False

    if contest.private:
        if req.user.is_superuser==False and req.user.info not in contest.accounts.all() :
            return HttpResponseRedirect("/contest/" + cid + "/")

    if req.method == 'GET':
        return ren2res("contest/contest_submit.html", req, {'contest': contest, 'problems': contest.get_problem_list()})
    elif req.method == 'POST':
        pid = req.POST.get('pid')
        #need change start
        # sub = Status(pro=Problem.objects.get(proid=pid), user=req.user, lang=req.POST.get('lang'))
        sub = Status(user=req.user, pro=Problem.objects.get(proid=pid), lang=req.POST.get('lang'), result='Waiting', 
            time=time)

        if not finish:
            sub.cid = contest.id
        else:
            sub.cid = -1
        sub.save()
        if req.POST.get('code'):
            content_file = ContentFile(req.POST.get('code'))
        elif req.FILES:
            content_file = ContentFile(req.FILES['file'].read())
        else:
            return ren2res("contest/contest_submit.html", req,
                           {'contest': contest, 'problems': contest.get_problem_list(), 'err': 'No Submit!'})
        #sub.source_code.save(name=str(sub.runid), content=content_file)
        sub.save()
        #judger.Judger(sub)
        #result=judge_delay.delay(sub)
    if not finish:
        return HttpResponseRedirect("/contest/" + cid + "/")
    else:
        return HttpResponseRedirect("/contest/"+cid+"/status?pid=" + pid)
        #need change end

def contest_time(req, cid):#don't need change
    if req.is_ajax():
        contest = Contest.objects.get(id = cid)
        startTime = contest.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')

        days = contest.duration_time.days
        seconds = contest.duration_time.seconds

        durationTime = days * 3600 * 24 + seconds;

        timeData = {'start' : startTime,
                    'duration' : durationTime}

        print(timeData)
        return JsonResponse(timeData)

@login_required
def contest_rank(req, cid):
    if req.is_ajax():
        contest = Contest.objects.get(id = cid)
        if contest.private:
            if req.user.is_superuser==False and req.user.info not in contest.accounts.all() :
                return JsonResponse("{}")
        rank_cache = contest.rank
        # print("rank_cache:")
        # print(rank_cache)
        status_list = Status.objects.filter(cid = cid).filter(runid__gt = contest.last_submit_id).order_by("time")
        # print("status_list")
        # print(status_list)
        rank_dict = json.loads(rank_cache)
        # print("rank_dict")
        # print(rank_dict)
        statsinfo = {}
        pos = 0
        problem_list = contest.get_problem_list()
        length = len(problem_list)

        
        if contest.last_submit_id==0:
            rank_dict["statsinfo"] = [{} for i in range(length)]
            for item in problem_list:
                rank_dict["statsinfo"][pos] = {"probid" : chr(pos + 65) ,"acNum" : 0, "tryNum" : 0}
                statsinfo[item[2].title] = {"pos" : pos}
                pos += 1
        else:
            for item in problem_list:
                statsinfo[item[2].title] = {"pos" : pos}
                pos += 1

        for item in status_list:
            if item.user.is_staff :
                continue
            name = item.user.username
            contest.last_submit_id = max(contest.last_submit_id, item.runid)
            if name not in rank_dict.keys():
                rank_dict[name] = {"name" : name, "solved":0, "penalty":0, "probs" : [{"failNum" : 0, "acNum" : 0, "acTime" : 0} for i in range(length)]}

            pos = statsinfo[item.pro.title]["pos"]

            if item.result == 3: #Waiting
                break

            if item.result == 0: #Accepted
                rank_dict["statsinfo"][pos]["acNum"] += 1
            rank_dict["statsinfo"][pos]["tryNum"] += 1

            if rank_dict[name]["probs"][pos]["acNum"] == 0:
                if item.result == 0:
                    rank_dict[name]["probs"][pos]["acNum"] += 1
                    rank_dict[name]["probs"][pos]["acTime"] = dateToInt(item.timec - contest.start_time, 1)
                    rank_dict[name]["penalty"] += 20 * rank_dict[name]["probs"][pos]["failNum"] + dateToInt(item.timec - contest.start_time, 0)
                    rank_dict[name]["solved"] += 1
                else:
                    rank_dict[name]["probs"][pos]["failNum"] += 1
        contest.rank = json.dumps(rank_dict)
        # print("contest.rank")
        # print(contest.rank)
        contest.save()
        return JsonResponse(rank_dict)

def page_not_found(req):
    return ren2res("404.html", req, {})