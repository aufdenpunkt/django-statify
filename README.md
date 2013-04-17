# django-statify #

Build out a static version of your django project and deploy it using ftp, ssh 
or on your localhost.


## Index ##

1. [Installation](#1-installation)
2. [Configuration](#2-configuration)
3. [Roadmap](#3-roadmap)


- - -

## 1. Installation ##


### 1.1. Requirements ###

* Python 2.7 or higher
* Django 1.3 or higher
* django-medusa (https://github.com/christian-schweinhardt/django-medusa)
* futures==2.1.3
* requests==1.1.0
* paramiko==1.10.0
* scpclient==0.4
* pycrypto==2.6


#### 1.1.1. On Ubuntu ####

If you're using Ubuntu this should work:

1. `sudo pip install django-statify`
2. `python manage.py syncdb --all`

Additionally, you need the python driver for your selected database:

`sudo aptitude python-psycopg2`

or

`sudo aptitude install python-mysql`

This will install PIL and your database’s driver globally.


#### 1.1.2 On Mac OS X ####

`sudo pip install django-statify` (see above)


### 1.2. Database ###

I recommend using SQLite, MySQL or PostgreSQL.


- - -

## 2. Configuration ##


### 2.1. Required settings ###


#### 2.1.1. STATIFY_PROJECT_DIR ####

The project dir should be the absolute path to your django project, where your 
manage.py is stored.

Default: `os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')`


#### 2.1.2. STATIFY_UPLOAD_PATH ####

The upload path is relative to the MEDIA_ROOT. There will be stored all release 
archives. This should be always an absolute path.

Default: `os.path.join(u'statify/releases/')`


#### 2.1.3. STATIFY_EXCLUDED_MEDIA ####

The listed dirs will be ignored on generate the release statics.
Optional I recommend to use django-pipeline for your assets like css, 
javascript and images.

Default: `[u'admin', u'statify', u'tmp', u'root']`


#### 2.1.4. STATIFY_ROOT_STATIC ####

If you need some root files like robots.txt or crossdomain.xml you are able to 
to store it in this path.

Default: `os.path.join(settings.MEDIA_ROOT, 'root')`


#### 2.1.5. STATIFY_ROOT_STATIC_URL ####

This setting is important for development. This settings should be overwritten 
in your build settings to: `/`.

Default: `settings.STATIC_URL + 'root/'`


- - -

## 3. Roadmap ##


### 3.1. Version 1.0 ###

* Execute releases and deployments using django management commands
* Integrate logging for releases and deployments
* Extend deployment hosts to some cloud services (S3, etc.)
* German translation
* API to catch objects/models with urls on save
