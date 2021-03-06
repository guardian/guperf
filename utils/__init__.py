import httplib
import datetime
import logging
import yaml
import yaml.constructor
from xml.dom import minidom
from urlparse import urlparse

from google.appengine.ext import db

import models

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict

def check_http_200(url):

    parsed_url = urlparse(url)

    try:
        conn = httplib.HTTPConnection(parsed_url.netloc)
        conn.request("HEAD", parsed_url.path)
        return conn.getresponse().status == 200
    except:
        return False

def xml_to_json(result):

    result = result.replace("\n", "")
    xml = minidom.parseString(result)

    runs = []

    def parse_xml(xml):
        data = {}
        for child in xml.childNodes:
            if len(child.childNodes) > 0:
                if len(child.childNodes) > 1:
                    if child.nodeName == 'run':
                        runs.append(parse_xml(child))
                        if len(runs) == 10:
                            data['runs'] = runs
                    else:
                        data[child.nodeName] = parse_xml(child)
                else:
                    data[child.nodeName] = child.childNodes[0].data

        return data

    data = parse_xml(xml.getElementsByTagName('response')[0])

    data['data']['median']['firstView']['loadTime'] = round(float(data['data']['median']['firstView']['loadTime']) / 1000, 1)
    data['data']['median']['repeatView']['loadTime'] = round(float(data['data']['median']['repeatView']['loadTime']) / 1000, 1)
    data['data']['median']['firstView']['render'] = round(float(data['data']['median']['firstView']['render']) / 1000, 1)
    data['data']['median']['repeatView']['render'] = round(float(data['data']['median']['repeatView']['render']) / 1000, 1)

    return data

class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

def add_message(message):
    m = models.UserMessage(body=message, dt=datetime.datetime.now())
    m.put()

def get_messages():
    messages = models.UserMessage.all()
    if messages.count() > 0:
        m = [message.body for message in messages]
        db.delete(messages)
        return m
    return None


