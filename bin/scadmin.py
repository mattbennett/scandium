#!/usr/bin/env python

import re
import os
import sys
import stat
import errno
import shutil

from optparse import OptionParser

import scandium


def make_writeable(filename):
    """
    Make sure that the file is writeable.
    Useful if our source is read-only.
    """
    if sys.platform.startswith('java'):
        # On Jython there is no os.access()
        return
    if not os.access(filename, os.W_OK):
        st = os.stat(filename)
        new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
        os.chmod(filename, new_permissions)


def handle_template(template, subdir):
    """
    Determines where the app or project templates are.
    Use scandium.__path__[0] as the default because we don't
    know into which directory Scandium has been installed.
    """
    if template is None:
        return os.path.join(scandium.__path__[0], 'tpl', subdir)
    else:
        if template.startswith('file://'):
            template = template[7:]
        expanded_template = os.path.expanduser(template)
        expanded_template = os.path.normpath(expanded_template)
        if os.path.isdir(expanded_template):
            return expanded_template
    raise Exception("couldn't handle project template %s." % template)


def create(options, project_name, target=None):

    # If it's not a valid directory name.
    if not re.search(r'^[_a-zA-Z]\w*$', project_name):
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', project_name):
            message = ('make sure the name begins '
                       'with a letter or underscore')
        else:
            message = 'use only numbers, letters and underscores'
        raise Exception("%r is not a valid project name. Please %s." %
                           (project_name, message))

    # if some directory is given, make sure it's nicely expanded
    if target is None:
        top_dir = os.path.join(os.getcwd(), "scandium-%s" % project_name)
        try:
            os.makedirs(top_dir)
        except OSError, e:
            if e.errno == errno.EEXIST:
                message = "'%s' already exists" % top_dir
            else:
                message = e
            raise Exception(message)
    else:
        top_dir = os.path.abspath(os.path.expanduser(target))
        if not os.path.exists(top_dir):
            raise Exception("Destination directory '%s' does not "
                               "exist, please create it first." % top_dir)

    template_dir = handle_template(None, "project_template")
    prefix_length = len(template_dir) + 1

    for root, dirs, files in os.walk(template_dir):
        path_rest = root[prefix_length:]
        relative_dir = path_rest.replace("project_name", project_name)
        if relative_dir:
            target_dir = os.path.join(top_dir, relative_dir)
            if not os.path.exists(target_dir):
                os.mkdir(target_dir)

        for dirname in dirs[:]:
            if dirname.startswith('.'):
                dirs.remove(dirname)

        for filename in files:
            if filename.endswith(('.pyo', '.pyc', '.py.class')):
                # Ignore some files as they cause various breakages.
                continue
            old_path = os.path.join(root, filename)
            new_path = os.path.join(top_dir, relative_dir, \
                                    filename.replace("project_name", \
                                                     project_name))
            if os.path.exists(new_path):
                raise Exception("%s already exists, overlaying a "
                                   "project or app into an existing "
                                   "directory won't replace conflicting "
                                   "files" % new_path)

            # Render .pyt files using string subsitutions
            context = dict({'project_name': project_name}, **options.__dict__)

            with open(old_path, 'r') as template_file:
                content = template_file.read()
            if filename.endswith("pyt"):
                for match, sub in context.items():
                    content = re.sub("{{%s}}" % match, sub, content)
                new_path = new_path[:-1]  # drop the 't' from the file ext
            with open(new_path, 'w') as new_file:
                new_file.write(content)

            try:
                shutil.copymode(old_path, new_path)
                make_writeable(new_path)
            except OSError:
                print "Notice: Couldn't set permission bits on %s. "\
                "You're probably using an uncommon filesystem setup. "\
                "No problem.\n" % new_path
                    
                    
if __name__ == "__main__":
    
    usage = "%s startproject [options] <project_name> [<target directory>]" % \
        sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-a", "--author",
                      dest="author",
                      default="",
                      help="Application Author")
    parser.add_option("-e", "--email",
                      dest="email",
                      default="",
                      help="Email Address")
    parser.add_option("-k", "--keywords",
                      dest="keywords",
                      default="",
                      help="Application Keywords")
    parser.add_option("-d", "--description",
                      dest="description",
                      default="",
                      help="Application Description")
    parser.add_option("-l", "--license",
                      dest="license",
                      default="",
                      help="Application License")
    
    options, args = parser.parse_args(sys.argv[1:])
    if args[0] != "startproject" or len(args) not in (2, 3):
        parser.error("Unrecognized input.")
    
    create(options, *args[1:])