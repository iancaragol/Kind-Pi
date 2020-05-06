from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from subprocess import Popen, PIPE
import datetime
import time
import os

app = Flask(__name__)
bg = BackgroundScheduler()
bg.start()

user_count = {}
ip_users = {}
filename = '/var/log/auth.log'

@app.route('/attacks', methods=['GET'])
def get_attacks():
    j = {'users':user_count, 'ips':ip_users}
    return jsonify(j)

@bg.scheduled_job('interval', minutes=1)
def update_logs():
    timeout = time.time() + 59
    print("Opening log file...")
    #Set the filename and open the file
    f = open(filename,'r')

    #Find the size of the file and move to the end
    st_results = os.stat(filename)
    st_size = st_results[6]
    f.seek(st_size)


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
                    print("Invalid login attempt discovered!")
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

            except Exception as e:
                print(e)

    print("Done!")


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=54663)

    


