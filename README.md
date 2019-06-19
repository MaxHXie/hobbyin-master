# HOBBYIN
---------------
Author: Max Xie, max.xie@accenture.com

# Openshift Deployment (Using the user interface)
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

/Max
