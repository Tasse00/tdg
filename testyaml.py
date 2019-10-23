from pprint import pprint

import yaml

with open("./testcfh.yml")  as fr:
    tc = yaml.load(fr, yaml.BaseLoader)

pprint(tc)
