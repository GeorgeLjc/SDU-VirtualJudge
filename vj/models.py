# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User




class Problem(models.Model):
    proid = models.AutoField(primary_key=True)
    originoj = models.CharField(max_length=10)
    problemid = models.CharField(max_length=10)
    problemurl = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    timelimit = models.CharField(max_length=50)
    memorylimit = models.CharField(max_length=50)
    description = models.TextField()
    input = models.TextField()
    output = models.TextField()
    sampleinput = models.TextField()
    sampleoutput = models.TextField()
    updatetime = models.DateTimeField()
    note = models.TextField(null=True)

    def __str__(self):
        return self.title

    def accepted(self):
        query = Status.objects.filter(pro_id=self, result= 'Accepted')
        return query.count()

    def submitted(self):
        query = Status.objects.filter(pro_id=self)
        return query.count()
    # class Meta:
    #     managed = True
    #     #db_table = 'problem'

class UserInfo(models.Model):
    id = models.OneToOneField(User, primary_key=True, related_name='info')
    school = models.CharField(max_length=50, blank=True)
    sid = models.CharField(max_length=50, blank=True)
    nickname = models.CharField(max_length=50, blank=True)
    problem_ac = models.IntegerField(default = 0)
    problem_try = models.IntegerField(default = 0)
    problems_ac = models.ManyToManyField(Problem, related_name='aceduser')
    problems_try = models.ManyToManyField(Problem, related_name='trieduser')

    def __str__(self):
        return str(self.id)
    def cnt_ac(self):
        return self.problems_ac.count()
    def cnt_try(self):
        return self.problems_try.count()
    def ratio(self):
        if self.problem_try==0:
            return 0
        return int(self.problem_ac/self.problem_try*100)
    # class Meta:
    #     managed = True
    #     #db_table = 'userinfo'

class Contest(models.Model):
    """contestid = models.AutoField(primary_key=True)
    contestname = models.CharField(max_length=45)
    contestpro = models.CharField(max_length=255)
    contest_s_time = models.DateTimeField()
    contest_l_time = models.IntegerField()
    contest_admin = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'contest'"""
    uid = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    start_time = models.DateTimeField()
    duration_time = models.DurationField()
    problems = models.ManyToManyField(Problem, related_name="contests")
    rank = models.TextField(default="{}")   #cached rank
    last_submit_id = models.IntegerField(default = 0)   #last submit id add to rank
    private = models.BooleanField(default=False)
    password = models.CharField(max_length=256,blank=True)
    accounts = models.ManyToManyField(UserInfo, related_name="accessable_contests",blank=True)
#    users = models.ManyToManyField(User, related_name="contests")

    def __str__(self):
        return str(self.name)

    class Meta:
        #managed = True
        ordering = ['start_time']
        # db_table = 'contest'

    def get_submits(self):
        return Submit.objects.filter(cid=self.id)

    def get_problem_list(self):
        problems = self.problems.all()
        lst = []
        cnt = 0
        for problem in problems:
            lst.append([cnt, chr(cnt + 65), problem])
            cnt += 1
        return lst


class Status(models.Model):
    runid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    pro = models.ForeignKey(Problem)
    source_code = models.FileField()
    lang = models.IntegerField(blank=True, null=True)
    result = models.CharField(max_length=50)
    timec = models.CharField(max_length=50, blank=True, null=True)
    memoryc = models.CharField(max_length=50, blank=True, null=True)
    time = models.DateTimeField()
    cid = models.IntegerField(default=-1) 

    # class Meta:
    #     managed = True
    #     db_table = 'status'
