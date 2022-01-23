import json

def get_towers_fixture():
    # URL:
    # ?s1=[{"0":[154]}]&s2=[{"0":[88]}]&rows=500&cols=200
    s1 = '[{"0":[154]}]'
    s2 = '[{"0":[88]}]'
    return s1, s2

def get_minitowers_fixture():
    # URL:
    # ?s1=[{"0":[10]}]&s2=[{"0":[22]}]&rows=150&cols=50
    s1 = '[{"0":[10]}]'
    s2 = '[{"0":[22]}]'
    return s1, s2


def get_rule30():
    # Rule 30 Electric Dove
    rule = "000000002000000001222111210"
    return rule

def get_rule60():
    # Rule 60 quantum jumping spider
    rule = "000000211000000212211212000"
    return rule

