from typing import Sequence
import requests
import smtplib
import time
import json

def get_state_id():
    get_state_url = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "accept": "application/json",
    }
    r = requests.get("https://cdn-api.co-vin.in/api/v2/admin/location/states",headers=headers).json()
    concerned_states = ['Madhya Pradesh']
    for state in r['states']:
        if state['state_name'] == concerned_states[0]:
            return state['state_id']

def get_district_id():
    state_id = get_state_id()
    get_district_url = f'https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}'
    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "accept": "application/json",
    }
    r = requests.get(get_district_url,headers=headers).json()
    concerned_district = ['Indore']
    for district in r['districts']:
        if district['district_name'] == concerned_district[0]:
            return district['district_id']

def check_slots(pincode,vaccine_slots,by_district=False):
    headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "accept": "application/json",
    }
    if by_district:
        district_id = str(get_district_id())
        check_slots_url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarDistrict?district_id={district_id}&date=13-05-2021"
    else:
        check_slots_url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date=13-05-2021"
    r = requests.get(check_slots_url,headers=headers).json()
    for centre in r['centers']:
        centre_name = centre['name']
        for session in centre['sessions']:
            if session['available_capacity'] > 0 and session['min_age_limit']==18:
                sess = session
                sess['name'] = centre_name
                vaccine_slots.append(sess)
    return vaccine_slots
def make_str(res):
    # print(len(res))
    relevant_info = ['name','available_capacity','vaccine']
    s = ""
    for session in res:
        for desc in session:
            if desc in relevant_info:
                s+=str(desc) + ':' + "   "
                s+=str(session[desc])
                s+="\n"
                # print(desc,s,"asdasd")
        s+='\n'
    return s

def send_mail(recepients,vaccine_slots):
    sender = 'mshahroz161099@gmail.com'
    password = 'dyzfrznrqzmitpcs'
    subject = "Hurry!! Vaccine Slots available in your area"
    message = 'Subject: {}\n\n{}'.format(subject, make_str(vaccine_slots))
    smtp_server = smtplib.SMTP('smtp.gmail.com',587)
    smtp_server.starttls()
    print("server on")
    smtp_server.login(sender,password)
    print("logged in")
    try:
        smtp_server.sendmail(sender,recepients,message)
        print("mail sent")
    except Exception as e:
        print("failed")
    smtp_server.quit()

if __name__ == '__main__':
    cities = {
        'Indore' : {
            'pincodes' : ['452001','452002','452003','452004','452004','452005','452006','452007','452008','452009','452010','452011'],
            'recepients' : [
                'anuragraghuvanshi65@gmail.com','monilbrahamwanshi@gmail.com','anuragraghucode@gmail.com','arpitspatil@gmail.com','mshahroz8@gmail.com',
                'shrinivasagrawal2001@gmail.com'
                ],
            'flag' : True,
        },
        'Bhopal' : {
            'pincodes' : ['462023'],
            'recepients' : ['shreyanshmehra786@gmail.com'],
            'flag' : True,
        },
        'Shegaon' : {
            'pincodes' : ['444203'],
            'recepients' : ['mshahroz8@gmail.com'],
            'flag' : True,
        }
    }
    curr_time = time.time()
    while True:
        duration = 300
        if time.time() - curr_time >= duration:
            curr_time = time.time()
            for city in cities:
                vaccine_slots = []
                if cities[city]['flag'] == True:
                    for pincode in cities[city]['pincodes']:
                        vaccine_slots = check_slots(pincode,vaccine_slots)
                    if len(vaccine_slots)>0:
                        send_mail(cities[city]['recepients'],vaccine_slots)
                        cities[city]['flag'] = False

            


