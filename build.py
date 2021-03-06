# -*- coding: utf-8 -*-

from os import path, getcwd, makedirs, listdir, remove
from sys import argv
from yaml import load
from shutil import rmtree
from slugify import slugify
from datetime import date, datetime
from staticjinja import make_site
from unidecode import unidecode

_AUTO_RELOAD = True

_TODAY = date.today()

# Define constants for the deployment.
_SEARCHPATH = path.join(getcwd(), 'templates')
_OUTPUTPATH = path.join(getcwd(), 'site')

# Load the data we want to use in the templates.
_EVENTS = path.join(getcwd(), 'data/events.yaml')
_PROJECTS = path.join(getcwd(), 'data/projects.yaml')
_TEAM = path.join(getcwd(), 'data/team.yaml')
_FUNDERS = path.join(getcwd(), 'data/funders.yaml')

_SLUG = lambda x: slugify(unidecode(x.lower()) if x else '')

def filters():
    return {'slug': _SLUG}


def context():
    dic = {}

    dic['events'] = load(open(_EVENTS))
    dic['projects'] = load(open(_PROJECTS))
    dic['team'] = load(open(_TEAM))
    dic['funders'] = load(open(_FUNDERS))
    dic['events_slider_counter'] = 0
    dic['projects_slider_counter'] = 0

    for x in dic['events']:
        x['date'] = datetime.strptime(x['date'], '%m-%d-%Y').date()
        x['has_passed'] = x['date'] < _TODAY
        x['is_featured'] = str(x.get('is_featured', '')).lower()

        if x['is_featured'] in ['1', 'true', 'yes', 'on']:
            x['is_featured'] = True

            if x['date'] >= _TODAY:
                dic['events_slider_counter'] += 1

        else:
            x['is_featured'] = False

    for x in dic['projects']:
        x['is_featured'] = str(x.get('is_featured', '')).lower()

        if x['is_featured'] in ['1', 'true', 'yes', 'on']:
            x['is_featured'] = True
            dic['projects_slider_counter'] += 1

        else:
            x['is_featured'] = False

    dic['events'].sort(key=lambda x: x['date'])

    return dic


def cleanup():
    # Remove templates that are no longer needed.
    for filename in listdir(_SEARCHPATH):
        filepath = '%s/%s' % (_SEARCHPATH, filename)

        if filename.startswith('project-') and path.isfile(filepath):
            remove(filepath)

    # Clean the output folder.
    if path.exists(_OUTPUTPATH):
        rmtree(_OUTPUTPATH)

    makedirs(_OUTPUTPATH)


def create_custom_templates(projects):
    template = open('%s/project.html' % _SEARCHPATH).read()

    for index, project in enumerate(projects):
        filename = _SLUG(project['title'])
        new_file = open('%s/project-%s.html' % (_SEARCHPATH, filename), 'w+')
        new_page = template.replace('projects[0]', 'projects[%d]' % index)

        new_file.write(new_page)
        new_file.close()


if __name__ == '__main__':
    auto = _AUTO_RELOAD
    ctxt = context()
    site = {}

    cleanup()
    create_custom_templates(ctxt['projects'])

    # Accept CLI parameter to turn the auto reloader on and off.
    if len(argv) == 2:
        arg = argv[1].lower()

        if arg in ['0', 'false', 'off', 'no']:
            auto = False

        elif arg in ['1', 'true', 'on', 'yes']:
            auto = True

    site['filters'] = filters()
    site['outpath'] = _OUTPUTPATH
    site['contexts'] = [(r'.*.html', lambda: ctxt)]
    site['searchpath'] = _SEARCHPATH
    site['staticpaths'] = ['static']

    make_site(**site).render(use_reloader=auto)
