import urllib2
import pprint
import json
import xml.etree.ElementTree as ET


web_addr = 'http://wiki.openstreetmap.org/wiki/Map_Features#Amenity'
filename = 'map_features_html.txt'

FEATURE_TYPES = ['aerialway', 'aeroway', 'amenity', 'barrier', 'boundary', 
                 'building', 'craft', 'emergency', 'geological', 'historic', 
                 'landuse', 'leisure', 'man_made', 'military', 'natural', 
                 'office', 'place', 'public_transport','power','railway', 
                 'route', 'sport', 'tourism', 'waterway']

def html_save_as_txt(web_addr, filename):
    '''save the html of a website to text file'''
    response = urllib2.urlopen(web_addr)
    html = response.read()
    with open(filename, 'w') as f:
        f.write(html)

def parse_file(file_in):
    '''takes the text from the osm website and tries to get the features'''
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
    features_dict = parse_file(file_in)
    f_d_json = json.dumps(features_dict)
    with open(file_out, 'w') as f:
        f.write(f_d_json)
    with open(file_out, 'r') as f:
        f_d = f.read()
    pprint.pprint(f_d)
    

save_features_dict('page_copy.txt', 'features_dict.json')





