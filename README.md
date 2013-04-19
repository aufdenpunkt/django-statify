# django-statify #

Build out a static version of your django project and deploy it using ftp, ssh 
or on your localhost.

But at first ... if you like this tool and the idea behind, feel free to fork 
it, make pull requests and write issues.


## Index ##

1. [Installation](#1-installation)
2. [Configuration](#2-configuration)
3. [Using](#3-using)
4. [Roadmap](#4-roadmap)
5. [Changelog](#5-changelog)


- - -

## 1. Installation ##


### 1.1. Requirements ###

* Python 2.7 or higher
* Django 1.3 or higher
* django-medusa (https://github.com/christian-schweinhardt/django-medusa)
* requests 1.1.0 or higher
* paramiko 1.10.0 or higher
* scpclient 0.4 or higher


#### 1.1.1. On Ubuntu ####

If you're using Ubuntu this should work:

* `sudo pip install django-statify`


Additionally, you need the python driver for your selected database:

`sudo aptitude python-psycopg2` or `sudo aptitude install python-mysql`

This will your database’s driver globally.


#### 1.1.2. On Mac OS X ####

`sudo pip install django-statify` (see above)


### 1.2. Database ###

I recommend using SQLite, MySQL or PostgreSQL.


- - -

## 2. Configuration ##

Add the following app to your INSTALLED_APPS.

* `'statify'` django-statify itself

Now add `url(r'^', include('statify.urls'))` to your urls.py

and run `python manage.py syncdb --all`.


### 2.1. Required settings ###


#### `STATIFY_BUILD_SETTINGS` ####

This is your settings file for the release.

e.g. '--settings=build'

It should looks like the following example:

    # -*- coding: utf-8 -*-
    #

    # Project imports
    from conf.settings import *


    DEBUG = False
    STATIFY_ROOT_STATIC_URL = '/'

Default: `''`


#### `STATIFY_PROJECT_DIR` ####

The project dir should be the absolute path to your django project, where your 
manage.py is stored.

Default: `os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')`


#### `STATIFY_UPLOAD_PATH` ####

The upload path is relative to the MEDIA_ROOT. There will be stored all release 
archives. This should be always an absolute path.

Default: `os.path.join(u'statify/releases/')`


#### `STATIFY_EXCLUDED_MEDIA` ####

The listed folders will be ignored on release statics.
Optional I recommend to use django-pipeline for your assets like css, 
javascript and images.

Default: `[u'admin', u'statify', u'tmp', u'root']`


#### `STATIFY_ROOT_STATIC` ####

If you need some root files like robots.txt or crossdomain.xml you are able to 
store these files in this path. On release these files will be moved to the root 
of the final htdocs.

Default: `os.path.join(settings.MEDIA_ROOT, 'root')`


#### `STATIFY_ROOT_STATIC_URL ####

This setting is important for development. It should be overwritten 
in your build settings to `'/'`.

Default: `settings.STATIC_URL + 'root/'`


## 3. Using ##


### 3.1. URLs ###


#### 3.1.1. Register internal urls ####

You can register internal url's using the django admin backend.

Alternative you can register urls automatically by adding one of the below 
methods to your model classes.

The following example is for an single URL:

    def statify_url(self):
        return u'/%s/' % self.url_field


or you can register more then one URL for a Model with the following example:

    def statify_urls(self):
        url_list = list()
        url_list.append('/%s/' % self.locale)

        return url_list


The backend will validate the url on save. Only valid urls will be rendered.
This is important because only valid urls will be rendered on release.


#### 3.1.2. Register external urls ####

If you need some external content rendered to your site, you are able to 
register external urls. Use the target path to point the rendered file in 
your final htdocs folder.


### 3.2. Release ###


#### 3.2.1. Create new release ####

Using the django admin interface you can create new releases by clicking the 
button "Create new release" at the release overview.
After clicking you will see a loader. After the release is done the current 
page will reload automatically.


### 3.3. Deployment ###


#### 3.3.1. Manage deployment hosts ####

TODO


#### 3.3.2. Run deployment ####

There are two ways to deploy an release. First you have to click at the release 
overview on "Deploy this release". Afterwards you have to select an 
deployment host and click on "Run deployment".

Alternative you can navigate to the detail view of an release and do the same 
like below by clicking on "Run deployment".


- - -

## 4. Roadmap ##


### Version 1.0 ###

* Execute releases and deployments using django management commands
* Integrate logging for releases and deployments
* Extend deployment hosts to some cloud services (S3, etc.)


## 5. Changelog ##


### Version 0.1.6 ###

* Added german locale
* Some bugfixes


### Version 0.1.5 ###

* Added API / Method to register urls from Models
* Some bugfixes


### Version 0.1.4 ###

* Some bugfixes
