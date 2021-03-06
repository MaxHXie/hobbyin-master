# HOBBYIN
---------------
Author: Max Xie, max.xie@accenture.com

# About the project
---------------
This website is an event management platform. Where people can create events based on different hobbies and other users can RSVP to these events. Functionalities include:
* Creating and editing events
* Managing guestlist
* All users have and can manage their profile page
* Having profiles
* Messaging each other
* Signup and login
* Email verification
* Password recovery
* Email notifications
* Edit user
* Comprehensive information about events
* Searching for events

# Openshift Deployment (Using web console)
---------------
1. Start a project and name it whatever you like
2. Choose "Browse Catalog"
3. Choose "Python"
4. Enter the following in configurations:

| Field  | Value |
| ------------- | ------------- |
| Version  | 3.6  |
| Application Name  | hobbyin-master  |
| Git Repository  | https://github.com/MaxHXie/hobbyin-master/  |

commit 070ac056f3f223ddcee565cf9e811f16128c7b16

5. Click "Create"
6. Wait until the build is done
7. Navigate to the pod
8. Click the "Terminal" tab
9. In the Terminal, type the following commands:

```
...> python manage.py makemigrations
...> python manage.py migrate --run-syncdb
...> python manage.py loaddata fixtures/default_data.json
```

10. Access the exposed application url and hopefully everything is set up and working.

# Openshift deployment (Using CLI)
---------------
1. Pull repository and store in a local folder
2. Navigate to that folder in Powershell or Command Line
3. `...> oc login ...`
4. Enter the following commands
```
...> oc new-project hobbyin-master
...> oc create imagestream hobbyin-master
...> oc apply -f hobbyin-master.yaml
...> oc start-build hobbyin-master
```
Wait until image is done building
```
...> oc new-app hobbyin-master:latest
...> oc expose svc/hobbyin-master
```
5. The application should now be up and running.

### Copy pasteable version

```
oc new-project hobbyin-master
oc create imagestream hobbyin-master
oc apply -f hobbyin-master.yaml
oc start-build hobbyin-master
```
Wait until image is done building
```
oc new-app hobbyin-master:latest
oc expose svc/hobbyin-master
```
