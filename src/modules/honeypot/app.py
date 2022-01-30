from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from subprocess import Popen, PIPE, check_output
import datetime
import time
import os
import json
import sys

app = Flask(__name__)
bg = BackgroundScheduler()
bg.start()

user_count = {}
ip_users = {}

net_interface = 'wlp36s0'

try:
    with open('user_count.json') as f:
        user_count = json.load(f)
except Exception as e:
    print("[-] Failed to load user_count.json")
    print(e)
    user_count = {}

try:
    with open('ip_users.json') as f:
        ip_users = json.load(f)
except Exception as e:
    print("[-] Failed to load ip_users.json")
    print(e)
    ip_users = {}

last_ip = "0.0.0.0.0"
last_user = ""
filename = '/var/log/auth.log'

rx_d = ""
tx_d = ""

rx_m = ""
tx_m = ""

@app.route('/attacks', methods=['GET'])
def get_attacks():
    global user_count
    global ip_users
    global last_ip
    global last_user

    j = {'users':user_count, 'ips':ip_users, 'last_ip':last_ip, 'last_user':last_user}
    return jsonify(j)

@app.route('/traffic', methods=['GET'])
def get_traffic():
    global rx_d
    global tx_d
    global rx_m
    global tx_m

    j = {'rx_m':rx_m, 'rx_d':rx_d, 'tx_m':tx_m, 'tx_d':tx_d}
    return jsonify(j)

@bg.scheduled_job('interval', seconds=45)
def update_network():
    # Daily
    try:
        print("[-] Trying to check daily netstat output")

        global rx_d
        global tx_d
        global rx_m
        global tx_m

        netstat = check_output(["vnstat", "-d", "-i", net_interface]).decode("utf-8")
        splits = netstat.split('\n')
        stats = splits[5].split()

        rx_d = stats[1] + " " + stats[2]
        tx_d = stats[4] + " " + stats[5]

        print("[-] Done!")

        print("[-] Trying to check monthly netstat output")
        netstat = check_output(["vnstat", "-m", "-i", net_interface]).decode("utf-8")
        splits = netstat.split('\n')

        stats = splits[5].split()
        
        rx_m = stats[2] + " " + stats[3]
        tx_m = stats[5] + " " + stats[6]

        print("[-] Done!")

    except Exception as e:
        print("[-] An exception occured when updating the network...")
        print(e)

@bg.scheduled_job('interval', minutes=1)
def update_logs():
    timeout = time.time() + 59
    print("[-] Opening log file...")
    #Set the filename and open the file
    f = open(filename,'r')

    #Find the size of the file and move to the end
    st_results = os.stat(filename)
    st_size = st_results[6]
    f.seek(st_size)

    global user_count
    global ip_users

    while True:
        if time.time() > timeout:
            break

        where = f.tell()
        line = f.readline()
        if not line:
            time.sleep(1)
            f.seek(where)
        else:
            try:
                # print(line)
                if("Failed password" in line):
                    print("[-] Invalid login attempt discovered!")
                    user = "none"
                    ip = "0.0.0.0.0"

                    if ("invalid user" in line):
                        splits = line.split(' ')
                        user = splits[splits.index('user') + 1]
                        ip = splits[splits.index('from') + 1]
                        print(f"{user} : {ip}")

                    else:
                        splits = line.split(' ')
                        user = splits[splits.index('for') + 1]
                        ip = splits[splits.index('from') + 1]
                        print(f"{user} : {ip}")
                        # print(line)

                    if user not in user_count.keys():
                        user_count[user] = 1
                    else:
                        user_count[user] += 1

                    if ip not in ip_users.keys():
                        ip_users[ip] = [user]
                    else:
                        ip_users[ip].append(user)
                    
                    global last_ip
                    global last_user
                    last_ip = ip
                    last_user = user

            except Exception as e:
                print(e)

    print("[-] Saving json's")
    with open('user_count.json', 'w', encoding='utf-8') as f:
        json.dump(user_count, f, ensure_ascii=False, indent=4)
    with open('ip_users.json', 'w', encoding='utf-8') as f:
        json.dump(ip_users, f, ensure_ascii=False, indent=4)
    print("[-] Done!")


if __name__ == "__main__":
    port = sys.argv[1]

    if len(sys.argv > 2):
        net_interface = sys.argv[2]

    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=54663)

    


