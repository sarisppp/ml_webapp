from django.shortcuts import render
import numpy as np
import pandas as pd 
import json 

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