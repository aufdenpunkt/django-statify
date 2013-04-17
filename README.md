django-statify
==============

Build out a static version of your website and deploy it.


Install
-------

First you have to run: `pip install django-statify


Settings
--------

### STATIFY_PROJECT_DIR ###

The project dir should be the absolute path to your django project, where your 
manage.py is stored.

Default: `os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')`


### STATIFY_UPLOAD_PATH ###

The upload path is relative to the MEDIA_ROOT. There will be stored all release 
archives. This should be always an absolute path.

Default: `os.path.join(u'statify/releases/')`


### STATIFY_EXCLUDED_MEDIA ###

The listed dirs will be ignored on generate the release statics.
Optional I recommend to use django-pipeline for your assets like css, 
javascript and images.

Default: `[u'admin', u'statify', u'tmp', u'root']`


### STATIFY_ROOT_STATIC ###

Default: `os.path.join(settings.MEDIA_ROOT, 'root')`


### STATIFY_ROOT_STATIC_URL ###

Default: `settings.STATIC_URL + 'root/'`


Roadmap for version 1.0
-----------------------

* Execute releases and deployments using management commands
* Integrate logging for releases and deployments
* Extend deployment hosts to some cloud services (S3, etc.)
