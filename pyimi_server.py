#!/usr/bin/python3

import bottle
from bottle import response, request
from pyimi import IMI, Directories, Devices
import json

imi = IMI(server='192.168.56.12', user='igel', password='igel#123')
directories = Directories(imi)
devices = Devices(imi)


class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if bottle.request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

app = bottle.app()

@app.route('/directories', method=['OPTIONS', 'GET'])
def get_directories():
    response.headers['Content-type'] = 'application/json'
    names = [directory.name for directory in directories]
    return json.dumps(names)

@app.route('/directory/<unitid>', method=['OPTIONS', 'GET'])
def get_device_directory(unitid):
    response.headers['Content-type'] = 'text/plain'
    print("unitid that will find is", unitid)
    device = devices.find(unitid=unitid)
    parent_folder_id = device.info['parentID']
    directory = directories.find(id=parent_folder_id)
    return directory.name

@app.route('/directory/<name>', method=['OPTIONS', 'PUT'])
def tc_to_directory(name):
    response.headers['Content-type'] = 'text/plain'
    directory = directories.find(name=name)
    unit_id = request.json['unitid']
    device = devices.find(unitid=unit_id)
    device.move(directory)
    device.settings2tc()
    return "success"

app.install(EnableCors())
app.run(host='0.0.0.0', port=8000, debug=True)