#!/usr/bin/python3
import pydbus
import sys
from fnmatch import fnmatch
from gi.repository import GLib
from xml.etree import ElementTree

loop = GLib.MainLoop()
bus = pydbus.SystemBus()
svc = 'org.bluez'
root = bus.get(svc, '/')
known_devpaths = []
verbose = '-v' in sys.argv
def noop(*args, **kwargs): None
log = print if verbose else noop

# Assert that a path looks like a bluez device and handle it
def handle_dev(devpath, ifaces_props = dict()):
    global bus, svc
    # A device is of the form /org/bluez/hci0/dev_01_23_45_67_89_AB
    if not fnmatch(devpath, '/org/bluez/*/dev' + '[!/]' * (6 * 3)):
        log('Not a device object:', devpath)
        return
    if devpath in known_devpaths:
        log('Device already tracked:', devpath)
        return
    known_devpaths.append(devpath)
    print('Tracking device at:', devpath)
    dev = bus.get(svc, devpath)
    # Assert that the event was fired due to Connected changing to true, then handle it
    def handle_prop_change(interface, changed_properties, invalidated_properties):
        if interface != 'org.bluez.Device1':
            log('Wrong interface of', devpath, interface)
            return
        if 'Connected' not in changed_properties:
            log('Connected did not change in', devpath)
            return
        if not changed_properties['Connected']:
            log('Device disconnected:', devpath)
            return
        log('Scheduling second connection to', devpath)
        # Repeat the connection command
        def dblconnect():
            print('Second connection to', devpath)
            dev.Connect()
        # Wait 1s before doing so to make sure the device isn't busy
        GLib.timeout_add(1000, dblconnect)
    dev.PropertiesChanged.connect(handle_prop_change)

# Recursively introspect objects for subobjects and construct a list of all paths
def rec_intro(bus, service, object_path, collection = []):
    collection.append(object_path)
    obj = bus.get(service, object_path)
    xml_string = obj.Introspect()
    for child in ElementTree.fromstring(xml_string):
        if child.tag == 'node':
            if object_path == '/':
                object_path = ''
            new_path = '/'.join((object_path, child.attrib['name']))
            rec_intro(bus, service, new_path)
    return collection


root.InterfacesAdded.connect(handle_dev) # Listen for new devices
# Handle old devices
paths = rec_intro(bus, svc, '/org/bluez')
for path in paths:
    handle_dev(path)
# Run the GLib listener
try:
    loop.run()
except KeyboardInterrupt:
    log('\nTerminating')
