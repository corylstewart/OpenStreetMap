import urllib2
import pprint
import json
import operator
import xml.etree.cElementTree as ET
import time

'''The funcitons of this file are just for getting some of the common
tags and values out of an open street map file.  The information gleaned
here will be used to clean the data up from the osm files before the
information is saved to the database.'''

def html_save_as_txt(web_addr, filename):
    '''save the html of a website to text file'''
    response = urllib2.urlopen(web_addr)
    html = response.read()
    with open(filename, 'w') as f:
        f.write(html)

#html_save_as_txt('http://wiki.openstreetmap.org/wiki/Map_Features#Amenity', 
#                 'map_features_html.txt')


#list of feature type values from the existing list of Map Features 
FEATURE_TYPES = ['aerialway', 'aeroway', 'amenity', 'barrier', 'boundary', 
                 'building', 'craft', 'emergency', 'geological', 'historic', 
                 'landuse', 'leisure', 'man_made', 'military', 'natural', 
                 'office', 'place', 'public_transport','power','railway', 
                 'route', 'sport', 'tourism', 'waterway']

def create_feature_dict_from_web_scrape(file_in):
    '''takes the text from the osm website and tries to get the features
    returns a dict of all of the standard feature type key, values pairs
    where the key is the feature and the value is a list of the possible
    values that the feature can take'''
    features_dict = {}
    #add the single word types in the dict
    for f in FEATURE_TYPES:
        features_dict[f] = set()
    #put the types for each feature
    for f_t in FEATURE_TYPES:
        with open(file_in, 'r') as f:
            for line in f:
                line = line.lower()
                l = line.split()
                if len(l) == 0:
                    continue
                if l[0] == f_t and len(l) <> 1:
                    features_dict[f_t].add(l[1])
    #remove .png, .jpg from dict:
    for f in features_dict.keys():
        for t in features_dict[f].copy():
            if t[-4:] == '.png':
                features_dict[f].remove(t)
            if t[-4:] == '.jpg':
                features_dict[f].remove(t)
    #add addr to the dict
    features_dict['addr'] = set(['addr:housenumber', 'addr:housename', 
                                'addr:place', 'addr:postcode', 
                                'addr:city', 'addr:country', 'addr:full', 
                                'addr:hamlet', 'addr:suburb', 'addr:subdistrict',
                                'addr:district', 'addr:province', 'addr:state', 
                                'addr:interpolation', 'addr:interpolation', 
                                'addr:inclusion'])
    #add annotation to the dict
    features_dict['annotation'] = set(['attribution', 'comment', 'description',
                                       'email', 'fax', 'fixme', 'image', 'note', 
                                       'phone', 'source', 'source:name', 
                                       'source:ref', 'source_ref', 'todo', 
                                       'website', 'wikipedia'])
    #add names to the dict
    features_dict['name'] = set(['name', 'name:<lg>',  'alt_name', 'alt_name:<lg>',
                               'int_name', 'loc_name', 'nat_name', 'official_name', 
                               'old_name', 'old_name:<lg>', 'reg_name', 
                               'short_name', 'sorting_name', 'ignoring', 
                               'lowering', 'ignoring'])
    #add names to the dict
    features_dict['porperties'] = set(['area', 'bridge', 'covered', 'crossing', 
                                       'cutting', 'disused', 'drive_through', 
                                       'drive_in', 'ele', 'embankment', 
                                       'end_date', 'est_width', 'internet_access', 
                                       'narrow', 'opening_hours', 'operator', 
                                       'start_date', 'TMC:LocationCode', 
                                       'tunnel', 'toilets:wheelchair', 
                                       'wheelchair', 'width', 'wood'])
    #add references to the dict
    features_dict['references'] = set(['iata', 'icao', 'int_ref', 'lcn_ref', 
                                       'loc_ref', 'nat_ref', 'ncn_ref', 'old_ref', 
                                       'rcn_ref', 'ref', 'reg_ref', 'source_ref'])
    #add restrictions to the dict
    features_dict['restrictions'] = set(['access', 'agricultural', 'delivery', 
                                         'designated', 'destination', 'forestry', 
                                         'no', 'official', 'permissive', 
                                         'private', 'unknown', 'yes', 
                                         'agricultural', 'atv', 'bdouble', 
                                         'bicycle', 'boat', 'emergency', 'foot', 
                                         'forestry', 'goods', 'hazmat', 'hgv', 
                                         'horse', 'inline_skates', 'lhv', 
                                         'motorboat', 'motorcar', 'motorcycle', 
                                         'motor_vehicle', 'psv', 'roadtrain', 
                                         'tank', 'vehicle', '4wd_only', 'charge', 
                                         'disused', 'maxheight', 'maxlength', 
                                         'maxspeed', 'maxstay', 'maxweight', 
                                         'maxwidth', 'minspeed', 'noexit', 
                                         'oneway', 'traffic_sign'])
    for f in features_dict:
        features_dict[f] = list(features_dict[f])
        features_dict[f].sort()

    return features_dict

def save_features_dict(file_in, file_out):
    '''save the feature dict to file as a json object for future use'''
    features_dict = parse_file(file_in)
    f_d_json = json.dumps(features_dict)
    with open(file_out, 'w') as f:
        f.write(f_d_json)
    with open(file_out, 'r') as f:
        f_d = f.read()
    pprint.pprint(f_d)
    

#save_features_dict('page_copy.txt', 'features_dict.json')

def count_tag_values(file_in, print_it = False):
    '''returns a dict of each tag type in the osm file as well as
    a count of the types of each tags value'''
    types = {'node': {}, 'way': {}, 'relation': {}}
    ks = set()
    for event, element in ET.iterparse(file_in, events=('start', 'end')):
        if event == 'start':
            if element.tag in types:
                for tag in element.findall('.//tag'):
                    ks.add(tag.attrib['k'])
                    if tag.attrib['k'] not in types[element.tag]:
                        types[element.tag][tag.attrib['k']] = {}
                    if tag.attrib['v'] not in types[element.tag][tag.attrib['k']]:
                        types[element.tag][tag.attrib['k']][tag.attrib['v']] = 0
                    types[element.tag][tag.attrib['k']][tag.attrib['v']] += 1
        if event == 'end':
            element.clear()
    if print_it:
        for k in types:
            for t in types[k]:
                print '*****************',k ,t, '*********************'
                for t2 in types[k][t]:
                    print t2, ' : ', types[k][t][t2]
            print ks
    return types


def save_variable_to_json_file(file_in, name_append, function_name):
    '''Save the value returned from the function "function_name" called
    as a json object with the name of the osm file appended with the 
    name "name_append"'''
    filename = '{0}'.format(file_in + '.' + name_append + '.json')
    with open(filename, 'w') as f:
        f.write(json.dumps(function_name(file_in)))
    print 'done'

#save_variable_to_json_file('chicago.osm', 'tag_with_count', count_tag_values)

def load_variable_from_json_file(filename):
    '''load a json file and convert the json to a python object'''
    with open(filename) as f:
        return json.loads(f.read())

#o = load_variable_from_json_file('oahu.osm.tag_with_count.json')

def create_list_of_street_abbreviations(filename, print_it = False):
    '''Use an already parsed osm file saved as a dict to find the ways that
    have a name field and check if the last word of the name is already in
    the street mapping and if it is not make a count of the number of times
    that word occurs, if print_it is true allow the user to enter the words
    into the stret mapping'''
    abb_dict = load_variable_from_json_file('abbreviation_street_mapping.json')
    tags = load_variable_from_json_file(filename)
    not_in = {}
    for name in tags['way']['name']:
        name_list = [word.lower() for word in name.split()]
        if  name_list[-1] not in abb_dict:
            if name_list[-1] not in not_in:
                not_in[name_list[-1]] = 0
            not_in[name_list[-1]] += 1
    not_in_sorted = sorted(not_in.iteritems(), key=operator.itemgetter(1))
    not_in_sorted.reverse()
    if print_it:
        for (word, num) in not_in_sorted:
            Word = word[0].upper() + word[1:]
            q = raw_input('Add ' + word + ' as ' + Word + ' there were ' 
                          + str(num) + ' occurances? y/n/q: ')
            if q == 'y':
                add_to_abb_street_map(word, Word)
            if q == 'q':
                break
    return not_in

#not_in = create_list_of_street_abbreviations('menlo_park.osm.tag_with_count.json')

def add_to_abb_street_map(key, value):
    '''add a key value pair to the street mapping'''
    abb_dict = load_variable_from_json_file('abbreviation_street_mapping.json')
    abb_dict[key] = value
    with open('abbreviation_street_mapping.json', 'w') as f:
        f.write(json.dumps(abb_dict))

def remove_from_abb_street_map(key, value):
    '''remove a key vale pairs to the street mapping'''
    abb_dict = load_variable_from_json_file('abbreviation_street_mapping.json')
    abb_dict.pop(key, None)
    with open('abbreviation_street_mapping.json', 'w') as f:
        f.write(json.dumps(abb_dict))

def no_json_file_street_count(file_in, print_it = False):
    '''pase the osm file looking for ways that have a name field, if the last word
    in the name is not in the current street mapping make a count of how many times
    that word appears and return the dictionary of those values.  print_it will
    let the user enter those values directlt to the street mapping'''
    abb_dict = load_variable_from_json_file('abbreviation_street_mapping.json')
    not_in = {}
    for event, element in ET.iterparse(file_in, events=('start', 'end')):
        if event == 'start':
            if element.tag == 'way':
                print len(not_in)
                for tag in element.findall('.//tag'):
                    if tag.attrib['k'] == 'name':
                        name_list = [word.lower() for word in tag.attrib['v'].split()]
                        if  name_list[-1] not in abb_dict:
                            if name_list[-1] not in not_in:
                                not_in[name_list[-1]] = 0
                            not_in[name_list[-1]] += 1
        if event == 'end':
            element.clear()
    not_in_sorted = sorted(not_in.iteritems(), key=operator.itemgetter(1))
    not_in_sorted.reverse()
    if print_it:
        for (word, num) in not_in_sorted:
            Word = word[0].upper() + word[1:]
            q = raw_input('Add ' + word + ' as ' + Word + ' there were ' 
                            + str(num) + ' occurances? y/n/q: ')
            if q == 'y':
                add_to_abb_street_map(word, Word)
            if q == 'q':
                break
    return not_in

#not_in = no_json_file_street_count('chicago.osm')



print 'done'