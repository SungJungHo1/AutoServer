from pymongo import MongoClient           # pymongo 임포트
from datetime import *
client = MongoClient('mongodb://zxc0214:asd64026@3.35.10.100', 27017)
db = client.PB_Auto
users = db.users
def Find_Data(ID,PW):

    user = users.find_one({'ID':str(ID)})
    
    if user == None:
        return {"code":3,"about":"유저없음","APIKEY":"",'Userble':False}
    else:
        if user["PW"] == str(PW):
            return {"code":1,"about":"PW일치","APIKEY":user["APIKEY"],'Userble':user['Userble']}
        else:
            return {"code":2,"about":"PW불일치","APIKEY":"",'Userble':False}

def insert_Data(ID,PW,APIKEY):

    Check = users.find_one({'ID':str(ID)})
    if Check == None:
        user = users.insert_one({'ID':str(ID),'PW':str(PW),'APIKEY':str(APIKEY),'Userble':True,})
        if user.acknowledged:
            return {"State":True,"about":"등록 되었습니다."}
        else:
            return {"State":False,"about":"등록실패 되었습니다."}
    else:
        return {"State":False,"about":"같은 아이디가 존재합니다."}
    


if __name__ == "__main__":
    # users.delete_many({})
    # print(insert_Data('auto119','12','LA4UW1BC78XVZT1JKFQKFEJHHVIYXQ'))
    # print(Find_Data('auto119',12))
    data = users.find()
    for i in data:
        print(i)
    

