# Kind-Pi

This uses an old kindle touch to display the time, weather, and whatever is trending on Reddit. The code is very old, so don't judge it too hard!

It would probably be better to run a web application in the docker container that exposes /images rather than delivering the image to the kindle via SCP.

---

### Kindle Setup

You will need to jailbreak your kindle and get root access. Once you have root access and have enabled SSH do the following:

    Scripts are stored in /usr

    After restarting kindle it may be neccessary to make the file system writable using this command:
    mount -o rw,remount /

    Steps for starting kindle scripts:

    1. ssh into kindle (user: root, pw: fionac28) <- This password can be found based on your Kindle's serial #
    2. navigate to /usr
    3. mount -o rw,remount /
    4. Manually create the scripts (display-out-sch.sh, start-display.sh)
    5. tmux
    6. ./start-display.sh
    7. Ctrl+b, d to detach

---

### Environment Varaibles and Configuration Files

Setup config.env file in root directory according to config.ex.env

Setup praw.ini and place in ./src