#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

TOP_LEVEL = ['id', 'visible']
CREATED = [ 'version', 'changeset', 'timestamp', 'user', 'uid']
TOP_TAGS = ['changeset', 'uid', 'timestamp', 'lon', 'visible', 'version', 'user', 'lat', 'id']
SECOND_TAGS = ['shop', 'tiger:county', 'golf', 'gnis:ST_num', 'man_made', 'tiger:source', 
               'tiger:zip_right_1', 'tiger:tlid', 'gnis:id', 'addr:housenumber', 'tiger:zip_left_4', 
               'tiger:zip_left_3', 'tiger:zip_left_2', 'tiger:zip_left_1', 'gnis:feature_type', 
               'addr:state', 'ele', 'tiger:name_type', 'covered', 'gnis:feature_id', 'junction',
               'leisure', 'barrier', 'tiger:separated', 'foot', 'gnis:County', 'faa', 'tourism', 
               'addr:street', 'name', 'tiger:zip_left', 'addr:postcode', 'roof:material', 
               'tiger:zip_right_3', 'roof:orientation', 'tiger:zip_right_2', 'tiger:name_base_1', 
               'is_in:continent', 'bicycle', 'gnis:county_name', 'roof:height', 'cycleway', 'spor', 
               'is_in:ocean', 'access', 'religion', 'boundary', 'artwork_type', 'ref', 'highway', 
               'tiger:reviewed', 'denomination', 'water', 'roof:shape', 'addr:city', 'gnis:Class', 
               'place', 'roof:alignment', 'tiger:name_direction_prefix', 'tiger:name_type_2', 
               'military', 'railway', 'gnis:County_num', 'building:part', 'tiger:zip_right_300', 
               'image','layer', 'height', 'operator', 'tiger:name_direction_prefix_1', 
               'tiger:upload_uuid', 'service', 'attraction', 'tiger:name_type_1', 'addr:housename', 
               'width', 'tiger:name_base_2', 'website', 'lanes', 'alt_name', 'phone', 'gnis:import_uuid', 
               'Heading', 'population', 'tunnel', 'tiger:zip_right_4', 'building:color', 'gnis:reviewed', 
               'aeroway', 'landuse', 'tracktype', 'bridge', 'amenity', 'wifi', 'parking', 'surface', 
               'waterway', 'tiger:cfcc', 'cuisine', 'is_in:country', 'building:levels', 'species', 'note', 
               'governance_type', 'tiger:zip_right', 'building:material', 'is_in:country_code', 'min_height', 
               'tiger:name_base', 'abutters', 'gnis:created', 'building', 'gnis:ST_alpha', 'natural', 'wheelchair',
               'historic', 'oneway', 'addr:country']

WAY_TYPE_DICT = {'dr.' : 'Drive', 'dr' : 'Drive',
                'rd.' : 'Road', 'rd' : 'Road',
                'st.' : 'Street', 'st' : 'Street',
                'pkwy.' : 'Parkway', 'prky' : 'Parkway',
                'ave.' : 'Avenue', 'ave' : 'Avenue',
                'blvd.' : 'Boulevard', 'blvd' : 'Boulevard',
                'pl.' : 'Place', 'pl' : 'Place',

                'king' : 'King', 'queen' : 'Queen'
                }

def find_tags(file_in):
    top_tags = set()
    second_tags = set()
    for _, element in ET.iterparse(file_in):
        if element.tag == "node" or element.tag == "way" :
            [top_tags.add(x) for x in element.keys()]
            for tag in element.findall('.//tag'):
                second_tags.add(tag.get('k'))
                #print tag.get('k'), ' : ', tag.get('v')
    return {'top_tags': top_tags, 'second_tags' : second_tags}

def find_tag_types(file_in, print_it = False):
    types = {}
    ks = set()
    for _, element in ET.iterparse(file_in):
        if element.tag == "node" or element.tag == "way" :
            for tag in element.findall('.//tag'):
                ks.add(tag.attrib['k'])
                if tag.attrib['k'] not in types:
                    types[tag.attrib['k']] = {}
                if tag.attrib['v'] not in types[tag.attrib['k']]:
                    types[tag.attrib['k']][tag.attrib['v']] = 0
                types[tag.attrib['k']][tag.attrib['v']] += 1
    if print_it:
        for t in types:
            print '*****************', t, '*********************'
            for t2 in types[t]:
                print t2, ' : ', types[t][t2]
        print ks

    return types

def shape_element(element):
    node = {}   
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        for field in TOP_LEVEL:
            node[field] = element.get(field)
        node['created'] = {}
        for field in CREATED:
            node['created'][field] = element.get(field)
        node['pos'] = [element.get('lat'), element.get('lon')]
        node['address'] = {'housenumber' : None,
                           'postcode' : None,
                           'street' : None}
        for tag in element.findall('.//tag'):
            if tag.attrib['k'] == 'addr:housenumber':
                node['address']['housenumber'] = tag.get('v')
            if tag.attrib['k'] == 'addr:street':
                node['address']['street'] = tag.get('v')
            if tag.attrib['k'] == 'addr:postcode':
                node['address']['postcode'] = tag.get('v')
            if tag.attrib['k'] == 'amenity':
                node['amenity'] = tag.get('v')
            if tag.attrib['k'] == 'name':
                node['name'] = tag.get('v')
            if tag.attrib['k'] == 'cuisine':
                node['cuisine'] = tag.get('v')
            if tag.attrib['k'] == 'phone':
                node['phone'] = tag.get('v')
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test(filename):

    #data = process_map(filename, True)
    #find_tags(filename)
    
    #for tag in SECOND_TAGS:
    #    print '*********************', tag, '**************************'
    #    find_tag_types(filename, tag)

    find_tag_types(filename, print_it = True)

    print 'done'


if __name__ == "__main__":
    filename = 'oahu.osm'
    test(filename)