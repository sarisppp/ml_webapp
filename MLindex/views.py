from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponse
from MLindex.models import *
from django.urls import reverse
import numpy as np
import pandas as pd 
import json 
from django.http import JsonResponse
from .models import Member
from django.contrib.auth.models import User



def home1(request):
    return render(request, "home.html")

def Hello(request):
    return render(request,"hello.html")


def signal(datatrain,periods=16):
    datatrain['output']=0
    for index,row in datatrain.iterrows():
        if row['MACD13']>row['Signal'] and row['RSI14']>row['EMAVRSI13'] and row['RSI14']<70:
            signalPre=1
        elif row['MACD13']<row['Signal'] and row['RSI14']<row['EMAVRSI13'] and row['RSI14']>30:
            if row['Close']<row['EMAV']:
                signalPre=-1
            else:
                signalPre=0
        else:
            signalPre=0
        datatrain.at[index,'output']= signalPre

    return datatrain
def predict(data,df):
    data=data.dropna()
    data_X = data.drop('output',axis=1)
    data_Y = data.output
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    train_X, test_X, train_y,test_y = train_test_split(data_X,data_Y,test_size=0.20, random_state=0)

    print("===============step predict======================")

    RandomForest = RandomForestClassifier(n_estimators=100)
    RandomForest.fit(train_X, train_y)  
    y_predict=RandomForest.predict(test_X)
    
    from sklearn.metrics import classification_report 
    report = classification_report(test_y,y_predict)
    print(report) 
    df.info()
    df=df.dropna()
    df_predict=RandomForest.predict(df)
    df['signal_predict']=df_predict
  
    return df
def buy_hole_sell(data_update2):
        data_update2['pricebuy']=0
        data_update2['pricesell']=0
        data_update2['macdbuy']=0
        data_update2['macdsell']=0
        data_update2['rsibuy']=0
        data_update2['rsisell']=0
        data_update2['Alert']=0
        data_update2=data_update2.astype(float)
        status=0
        for index,row in data_update2.iterrows():
            if status==0:
                if row['signal_predict']==1:
                    status=1
                    close=row['Close']
                    buy=0
                    pricebuy=close
                    pricesell=0
                    sell=0
                    Alert=1
                    macdbuy=row['MACD13']
                    macdsell=0
                    rsibuy=row['RSI14']
                    rsisell=0
                elif row['signal_predict']==-1:
                    status=-1
                    close=row['Close']
                    pricebuy=0
                    pricesell=close
                    buy=0
                    sell=0
                    Alert=-1
                    macdbuy=0
                    macdsell=row['MACD13']
                    rsibuy=0
                    rsisell=row['RSI14']
                else:
                    status=0
                    buy=0
                    sell=0
                    Alert=0
                    pricebuy=0
                    pricesell=0
                    macdbuy=0
                    macdsell=0
                    rsibuy=0
                    rsisell=0
            else :
                if status==1:
                    if row['signal_predict']==1:
                        buy=0
                        sell=0
                        pricebuy=0
                        pricesell=0
                        Alert=0
                        macdbuy=0
                        macdsell=0
                        rsibuy=0
                        rsisell=0
                    elif row['signal_predict']==-1:
                        status=-1
                        sell=row['Close']-close
                        close=row['Close']
                        pricebuy=0
                        pricesell=close
                        buy=0
                        Alert=-1
                        macdbuy=0
                        macdsell=row['MACD13']
                        rsibuy=0
                        rsisell=row['RSI14']
                    else:
                        buy=0
                        sell=0
                        Alert=0
                        pricebuy=0
                        pricesell=0
                        macdbuy=0
                        macdsell=0
                        rsibuy=0
                        rsisell=0
                elif status==-1:
                    if row['signal_predict']==1:
                        status=1
                        buy=close-row['Close']
                        close=row['Close']
                        sell=0
                        Alert=1
                        pricebuy=close
                        pricesell=0
                        macdbuy=row['MACD13']
                        macdsell=0
                        rsibuy=row['RSI14']
                        rsisell=0
                    elif row['signal_predict']==-1:
                        buy=0
                        sell=0
                        Alert=0
                        pricebuy=0
                        pricesell=0
                        macdbuy=0
                        macdsell=0
                        rsibuy=0
                        rsisell=0
                    else:
                        buy=0
                        sell=0
                        Alert=0
                        pricebuy=0
                        pricesell=0
                        macdbuy=0
                        macdsell=0
                        rsibuy=0
                        rsisell=0
                else:
                    buy=0
                    sell=0
                    price=0
                    pricebuy=0
                    pricesell=0
                    macdbuy=0
                    macdsell=0
                    rsibuy=0
                    rsisell=0
            data_update2.at[index,'Alert']=Alert
            data_update2.at[index,'pricebuy']=pricebuy
            data_update2.at[index,'pricesell']=pricesell
            data_update2.at[index,'macdbuy']=macdbuy
            data_update2.at[index,'macdsell']=macdsell
            data_update2.at[index,'rsibuy']=rsibuy
            data_update2.at[index,'rsisell']=rsisell
        return data_update2
def hello(request):
    used_features = ["Timestamp","Close","EMAV","RSI14","MACD13","EMAVRSI13","Signal"]
    df = pd.read_csv("Set50_20190314_20200820_1minute.csv",usecols =used_features,encoding= 'unicode_escape')
    df.set_index("Timestamp",inplace=True)
    df=df.dropna()
    df_trian=signal(df)
    used_features = ["Timestamp","Close","EMAV","RSI14","MACD13","EMAVRSI13","Signal"]
    df_new = pd.read_csv("Set50_20190314_20200820_1minute.csv",usecols =used_features,encoding= 'unicode_escape')
    df_new.set_index("Timestamp",inplace=True)
    df_new=df_new.dropna()
    df_new=predict(df_trian,df_new)
    df_new=buy_hole_sell(df_new.head(100))
    df_new=df_new.head(100)
    print("===============step 2======================")

    json_records = df_new.reset_index().to_json(orient ='records') 
    data = [] 
    data = json.loads(json_records) 
    context = {'d': data,} 
    
    return render(request,'index.html',context)

def history1(request):
    return render(request,"history.html")


def Login(request):
    return render(request,"login.html")

def Regitser(request):
    if request.method == 'POST':
        data = request.POST.copy()
        fisrt_name = data.get('fisrtname')
        last_name = data.get('lastname')
        email = data.get('email')
        password = data.get('password')

        newuser = User()
        newuser.username = email
        newuser.first_name = fisrt_name
        newuser.last_name = last_name
        newuser.email = email
        newuser.set_password(password)
        newuser.save()
        return redirect("login")
    return render(request,"register.html")









"""

def check_email_exist(em1):
    row = Member.objects.filter(email=em1)
    if row.count() == 0:
        return False
    else:
        return True

def member_signup(request):
    if request.is_ajax():
        email = request.GET.get('email','')
        exist = check_email_exist(email)
        return JsonResponse({'exist':exist})

    if 'id' in request.session:
        return redirect(reverse('home-page'))

    err_msg = ''
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            if not check_email_exist(request.POST['email']):
                r = form.save()
                request.session['id'] = r.id
                request.seesion['name'] = r.firstname
                return redirect(reverse('home-page'))
            else:
                err_msg = 'อีเมลนี้มีผู้ใช้แล้ว'
        else:
            err_msg = 'ข้อมูลไมถูกต้อง'
    else:
        form = MemberForm()
        action = reverse('home-page')
    return render(request, 'register.html', {'form': form, 'action':action, 'err_msg':err_msg})
            
def addname(request):
    firstname = request.POST['fisrtname']
    lastname = request.POST['lastname']
    email = request.POST['email']
    password = request.POST['password']
    repassword = request.POST['confirmpswd']

    user=User.objects.create_user(
        username = username,
        firstname = firstname,
        lastname = lastname,
        email = email,
        password = password
        )
    user.save()

    return render(request,'home.html')


def usercreate(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = MemberForm()
    return render(request,'home.html')



 <script>
  function formSubmit(bt) {
      var pswd = document.getElementById('password').value;
      var pswd_cf = document.getElementById('confirm_pswd').value;
      if (pswd != pswd_cf) {
          alert('รหัสผ่านทั้งสองช่องไม่ตรงกัน');        
      } else {
          document.querySelector('form').submit();
      }
  }

  var el = document.getElementById('email');
  el.onblur = function() {
      if (el.value.trim() == '') {
          return;
      }

      axios({
          url:'',      
          params:{'email':el.value},
          timeout: 3000,
          headers: {'X-Requested-With': 'XMLHttpRequest'}
      })
      .then(response => {
          if (response.data.exist == true) {
              el.value = '';
              alert('อีเมลนี้มีผู้ใช้แล้ว');
          } else {
              //...
          }
      })
      .catch(error => {
          alert(error);
      });
  }
  </script>
   

"""