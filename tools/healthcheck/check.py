import requests,sys, os

def check():
    exit_code = os.EX_OK
    health_url = os.getenv("HEALTH_URL","http://localhost:8000/drugs/")
    try:
        r = requests.get(health_url)
        if r.status_code != 200 :
            raise Exception("The probe has failed")
        set_tries("0")
    except:
        notify()
        exit_code = os.EX_SOFTWARE
    sys.exit(exit_code)

def notify():
    url = os.getenv("HEALTH_ALERT_URL","")
    if url!="":
        tries = get_tries()
        tries = tries+1
        headers = {'Content-Type': 'application/json'}
        message="Modulector: Health check failed {} times.".format(tries)
        if tries==3:
            message = message + " The container has been marked as unhealthy."
            set_tries(0)
        data = { "content": message }
        try:
            r = requests.post(url,headers=headers, json=data)
        except:
            pass
        set_tries(str(tries))

def get_tries():
    tries=0
    try:
        with open("tries.txt","r") as f:
            tries=f.read()
    except FileNotFoundError:
        set_tries(0)
    return int(tries)

def set_tries(tries):
    with open("tries.txt","w") as f:
        f.write(str(tries))

if __name__=="__main__":
    check()
