import pprint
import json
import operator
import xml.etree.cElementTree as ET
import os

class ParseOsmFile:
    '''This class will extract data from an osm file and parse it so that the
    information can be sent to a MongoDB'''

    def __init__(self, osm_filename):
        self.osm_filename = osm_filename
        self.street_mapping_file = 'abbreviation_street_mapping.json'
        self.features_file = 'features_dict.json'
        self.street_mapping_dict = self._load_json_file_to_variable(
                                                   self.street_mapping_file)
        self.features_dict = self._load_json_file_to_variable(
                                                   self.features_file)
        self.features_set = self._make_features_set()
        self.features = ['way', 'node', 'relation']
        self.top_level = ['id', 'visible']
        self.created = [ 'version', 'changeset', 'timestamp', 'user', 'uid']
        self.top_tags = ['changeset', 'uid', 'timestamp', 'lon', 
                         'visible', 'version', 'user', 'lat', 'id']
        self.inelegible_count = {}

    def _load_json_file_to_variable(self, filename):
        '''load a json file and convert the json to a python object'''
        with open(filename) as f:
            return json.loads(f.read())

    def _make_features_set(self):
        '''takes the features dictionary and makes all of the types of
        features part of the a set'''
        features_list = set()
        for key, value in self.features_dict.iteritems():
            features_list.add(key)
            for v in value:
                features_list.add(v)
        return features_list

    def add_to_feature_set(self, new_feature_iterable):
        '''Takes an iterable and adds all of the elements to the
        features set.  Allows new fields to be elegible to be included
        in the DB'''
        for feature in new_feature_iterable:
            self.features_set.add(feature)

    def remove_from_feature_set(self, remove_feature_iterable):
        '''Takes an iterable and remove the items from the feature set'''
        for feature in remove_feature_iterable:
            if feature in features_set:
                self.features_set.remove(feature)


    def read_osm_file(self, use_filter = False, keep_statistics = False):
        '''Read the osm file and set the features in the Mongo database.  If use_filter
        is true only tags that are in the fields_set will be added otherwise all tags
        are added.  If keep_statistics is true statistics on what tags are used'''
        for event, element in ET.iterparse(self.osm_filename, events=('start', 'end')):
            if event == 'start':
                if element.tag in self.features:
                    el = self._get_feature_data(element, use_filter, keep_statistics)


            if event == 'end':
                element.clear()

    def _get_feature_data(self, element, use_filter, keep_statistics):
        '''Takes the element input and returns a dictionary of its values'''
        el = {}       
        el['type'] = element.tag.strip()
        for tag in self.top_level:
            el[tag] = element.get(tag)
        el['created'] = {}
        for tag in self.created:
            el['created'][tag] = element.get(tag).strip()
        el['pos'] = [element.get('lat'), element.get('lon')]       
        for i in range(len(el['pos'])):
            if el['pos'][i] <> None:
                el['pos'][i] = el['pos'][i].strip()
                if el['pos'][i].replace('.','').replace('-','').isdigit():
                    el['pos'][i] = float(el['pos'][i])
        el = self._get_second_features(element, el, use_filter, keep_statistics)
        return el

    def _get_second_features(self, element, el, use_filter, keep_statistics):
        '''Iterates over the tags within the element and adds the tags to the dictionary'''
        for tag in element.findall('.//tag'):
            if tag.attrib['k'][:5] == 'addr:':
                el = self._add_address_features(tag, el, use_filter, keep_statistics)
            else:
                el = self._add_tag_to_el(tag.attrib['k'].strip(),tag.attrib['k'].strip(), el, use_filter, keep_statistics)
        return el

    def _add_address_features(self, tag, el, use_filter, keep_statistics):
        if 'address' not in el:
            el['address'] = {}
        tag_split = tag.attrib['k'].split(':')
        tag_split = [x.strip() for x in tag_split]
        if len(tag_split) <> 2:
            return el
        el['address'] = self._add_tag_to_el(tag_split[1], tag.attrib['v'].strip(), el, use_filter, keep_statistics, address=True)
        return el

    def _add_tag_to_el(self, tag_name, tag_value, el, use_filter, keep_statistics, address=False):
        if use_filter:
            if tag_name in self.features_set:
                el[tag_name] = tag_value
            else:
                self._add_to_inelegible_dict(tag_name, address = address)
        else:
            el[tag_name] = tag_value
        return el

    def _add_to_inelegible_dict(self, key, address=False):
        '''Keeps count of the ineligible keys used.  This information can be used if you
        want to add new tags to the field_set'''
        if address:
            key = 'addr:' + key
        if key not in self.inelegible_count:
            self.inelegible_count[key] = 0
        self.inelegible_count[key] += 1




o = ParseOsmFile('oahu.osm')
#pprint.pprint(o.features_dict)
o.read_osm_file(True,True)
pprint.pprint(o.inelegible_count)
print 'done'
