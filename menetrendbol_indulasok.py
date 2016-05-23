#!/usr/bin/env python

'''
menetrendbol_indulasok.py - a BKK GTFS menetrendjebol egy jarat
indulasi idejeit veszi ki

Irta: Majdan Andras <majdan.andras@gmail.com>
Licenc: BSD
'''

import os, sys, getopt, csv
from datetime import datetime, timedelta

def help_and_exit(exitcode=0):
    print('menetrendbol_indulasok.py -g <gtfsmappa> -r <jarat> -m <megallo> -f <felirat> -s <kezdetidatum> -e <vegedatum> -o <kimenetifajl>')
    sys.exit(exitcode)
    
def set_param(paramset, mask):
    if paramset & mask:
        print('Hiba: parameter tobbszor szerepel')
        help_and_exit(1)
    else:
        paramset |= mask
    return paramset 

def get_route_id(routesfile, route):
    print('Jarat azonosito keresese a "' +  routesfile + '" fajlban ..')
    
    with open(routesfile, encoding="utf8") as rfh:
        routes_reader = csv.reader(rfh, delimiter=',', quotechar='"')
        routes_header = next(routes_reader)
        routes_header_id = {}
        
        for idx, val in enumerate(routes_header):
            routes_header_id[val] = idx

        for row in routes_reader:
            if row[routes_header_id['route_short_name']] == route:
                return row[routes_header_id['route_id']]
            
    print('Hiba: nem talaltam meg a jaratot')
    sys.exit(0)

def get_stop_ids(stopsfile, stop):
    print('Megallo keresese a "' +  stopsfile + '" fajlban ..')
    stop_ids = set()
    
    with open(stopsfile, encoding="utf8") as sfh:
        stops_reader = csv.reader(sfh, delimiter=',', quotechar='"')
        stops_header = next(stops_reader)
        stops_header_id = {}
        
        for idx, val in enumerate(stops_header):
            stops_header_id[val] = idx

        for row in stops_reader:
            if row[stops_header_id['stop_name']] == stop:
                stop_ids.add(row[stops_header_id['stop_id']])

    if len(stop_ids) == 0:
        print('Hiba: nem talaltam egyetlen egy ilyen nevu megallot sem')
        sys.exit(0)
    else:
        return stop_ids

def get_trip_and_service_ids(tripsfile, route_id, headsign):
    print('Utazasok es szolgaltatasok keresese a "' +  tripsfile + '" fajlban ..')
    service_with_trip_ids = {}
    
    with open(tripsfile, encoding="utf8") as tfh:
        trips_reader = csv.reader(tfh, delimiter=',', quotechar='"')
        trips_header = next(trips_reader)
        trips_header_id = {}
        
        for idx, val in enumerate(trips_header):
            trips_header_id[val] = idx

        for row in trips_reader:
            if (row[trips_header_id['route_id']] == route_id) and (row[trips_header_id['trip_headsign']] == headsign):
                cservice_id = row[trips_header_id['service_id']]
                if not cservice_id in service_with_trip_ids:
                    service_with_trip_ids[cservice_id] = set()
                service_with_trip_ids[cservice_id].add(row[trips_header_id['trip_id']])

    if len(service_with_trip_ids) == 0:
        print('Hiba: nem talaltam egyetlen utazast sem')
        sys.exit(0)
    else:
        return service_with_trip_ids

def join_date_and_trip_ids(calendarfile, service_with_trip_ids, startdate, enddate):
    print('Utazas es datum parositasa a "' +  calendarfile + '" fajlbol ..')
    date_and_trip_ids = {}
    
    startdate_time = datetime.strptime(startdate, "%Y%m%d")
    enddate_time = datetime.strptime(enddate, "%Y%m%d")
    
    delta_time = enddate_time - startdate_time
    days = set()

    for i in range(delta_time.days + 1):
        cday = startdate_time + timedelta(days=i)
        days.add(str(cday.year) + "{0:0>2}".format(cday.month) + "{0:0>2}".format(cday.day))

    date_and_trip_ids = {}

    with open(calendarfile, encoding="utf8") as cfh:
        calendar_reader = csv.reader(cfh, delimiter=',', quotechar='"')
        calendar_header = next(calendar_reader)
        calendar_header_id = {}
        
        for idx, val in enumerate(calendar_header):
            calendar_header_id[val] = idx

        for row in calendar_reader:
            rservice_id = row[calendar_header_id['service_id']]
            rdate = row[calendar_header_id['date']]
            if (rservice_id in service_with_trip_ids) and (rdate in days):
                if rdate in date_and_trip_ids:
                    print('Hiba: egy nap tobb szolgaltatas nem lehetseges (TODO)')
                    sys.exit(1)
                else:
                    date_and_trip_ids[rdate] = service_with_trip_ids[rservice_id]

    if len(date_and_trip_ids) == 0:
        print('Hiba: nem talaltam egyetlen datumot sem')
        sys.exit(0)
    else:
        return date_and_trip_ids
    
def get_stoptimes(stoptimesfile, trip_to_date, stop_ids):
    print('Indulasok keresese a "' +  stoptimesfile + '" fajlban ..')
    stoptimes = set()

    with open(stoptimesfile, encoding="utf8") as sfh:
        stoptimes_reader = csv.reader(sfh, delimiter=',', quotechar='"')
        stoptimes_header = next(stoptimes_reader)
        stoptimes_header_id = {}
        
        for idx, val in enumerate(stoptimes_header):
            stoptimes_header_id[val] = idx

        for row in stoptimes_reader:
            rtrip_id = row[stoptimes_header_id['trip_id']]
            rstop_id = row[stoptimes_header_id['stop_id']]
            rdeparture_time = row[stoptimes_header_id['departure_time']]

            if (rstop_id in stop_ids) and (rtrip_id in trip_to_date):
                for cdate in trip_to_date[rtrip_id]:
                    stoptimes.add(cdate + " " + rdeparture_time)
                    
    return stoptimes

def main(argv):
    gtfsdir = ''
    route = ''
    stop = ''
    headsign = ''
    startdate = ''
    enddate = ''
    outputfile = ''
    paramset = 0
    
    try:
        opts, args = getopt.getopt(argv,'hg:r:m:f:s:e:o:',['gtfsdir=','route=','stop=','headsign=','startdate=', 'enddate=', 'outputfile='])
    except getopt.GetoptError:
        help_and_exit(2) 
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help_and_exit()
        elif opt in ('-g', '--gtfsdir'):
            gtfsdir = arg
            paramset = set_param(paramset, 1)
        elif opt in ('-r', '--route'):
            route = arg
            paramset = set_param(paramset, 2)
        elif opt in ('-m', '--stop'):
            stop = arg
            paramset = set_param(paramset, 4)
        elif opt in ('-f', '--headsign'):
            headsign = arg
            paramset = set_param(paramset, 8)
        elif opt in ('-s', '--startdate'):
            startdate = arg
            paramset = set_param(paramset, 16)
        elif opt in ('-e', '--enddate'):
            enddate = arg
            paramset = set_param(paramset, 32)
        elif opt in ('-o', '--outputfile'):
            outputfile = arg
            paramset = set_param(paramset, 64)

    if paramset != (1+2+4+8+16+32+64):
        print('Hiba: nincs beallitva minden parameter')
        help_and_exit(2)
            
    print('GTFS konyvtar:', gtfsdir)
    print('Jarat:', route)
    print('Megallo:', stop)
    print('Felirat:', headsign)
    print('Kezdeti datum:', startdate)
    print('Vege datum:', enddate)
    print('Kimeneti fajl:', outputfile)
    print('')

    routesfile = os.path.join(gtfsdir, 'routes.txt')
    route_id = get_route_id(routesfile, route)

    stopsfile = os.path.join(gtfsdir, 'stops.txt')
    stop_ids = get_stop_ids(stopsfile, stop)

    tripsfile = os.path.join(gtfsdir, 'trips.txt')
    service_with_trip_ids = get_trip_and_service_ids(tripsfile, route_id, headsign)

    calendarfile = os.path.join(gtfsdir, 'calendar_dates.txt')
    date_and_trip_ids = join_date_and_trip_ids(calendarfile, service_with_trip_ids, startdate, enddate)

    trip_to_date = {}
    for cdate, val in date_and_trip_ids.items():
        for ctrip in val:
            if not ctrip in trip_to_date:
                trip_to_date[ctrip] = set()
            trip_to_date[ctrip].add(cdate)
    
    stoptimesfile = os.path.join(gtfsdir, "stop_times.txt")
    stoptimes = get_stoptimes(stoptimesfile, trip_to_date, stop_ids)

    print("Talalt indulasok szama: " + str(len(stoptimes)))
    sorted_stoptimes = sorted(stoptimes)

    print("Kimeneti fajlba iras ..")
    with open(outputfile, "w", encoding="utf8") as ofh:
        for cstop in sorted_stoptimes:
            ofh.write(cstop + "\n")

if __name__ == '__main__':
    main(sys.argv[1:])
