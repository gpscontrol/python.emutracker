import socket
import math
import random
import time
from datetime import datetime,timedelta

def crc(source):
    #print("Source:{}".format(source))
    b=0
    for i in source:
        b=b+ord(i)
    #print("Sum:{}".format(b))
    #print("module:{}".format(b%256))
    ret=hex(b%256)
    ret=ret.upper()
    ret=ret.replace("0X","")
    return(ret)

def charcounter(source):
    c=0
    for i in source:
        c=c+1
    return(c)

class identifier:
    idCounter = 64
    def __init__(self):
        if identifier.idCounter<123:
            identifier.idCounter += 1
        else:
            identifier.idCounter = 65

def getMVT380(imei,accuracy,speed,latitude,longitude,myutc,event,port_status_string,azimuth):
    battery=10
    ner=event
    if (speed<0):
        speed=0
    #MVT380
    batt=hex((int(battery*1024)/6)).replace("0","").replace("x","")
    batt=batt.upper()
    batt=batt.zfill(4)
    imei=imei.strip()
    newIdentifier=identifier()
    mydataidentifier=str(unichr(newIdentifier.idCounter))
    #myutc=datetime.utcnow().strftime('%y%m%d%H%M%S')
    state="A"
    #port_status_string="0000"
    runtime="1348"
    mcc="0"
    mnc="0"
    lac="0000"
    cell_id="0000"
    myspeed=str(int(speed))
    myaltitude="0"
    mymileage="0"
    first_output=","+imei+",AAA,"+ner+","+latitude+","+longitude+","+myutc+","+state+",11,14,"+myspeed+","+azimuth+","+accuracy+","+myaltitude+","+mymileage+","+runtime+","+mcc+"|"+mnc+"|"+lac+"|"+cell_id+","+port_status_string+",0000|0000|0000|"+batt+"|0000,00000000,*"
    totalchar=charcounter(first_output)+4
    header="$$"+mydataidentifier+str(totalchar)
    preoutput=header+first_output
    output=preoutput+crc(preoutput)+chr(13)+chr(10)
    print(output)
    return output


def getTrackerCmd(imei,cmd):
    pre=","+imei+","+cmd+"*"
    totalchar = len(pre) + 4
    header="@@"+"A"+str(totalchar)
    preoutput=header+pre
    print(preoutput)
    output=preoutput+crc(preoutput)+chr(13)+chr(10)
    return output


position=[]
position.append({'x':-10,'y':0,'azimuth':'270.0'})
position.append({'x':10,'y':0,'azimuth':'90'})
position.append({'x':0,'y':-10,'azimuth':'180.0'})
position.append({'x':0,'y':10,'azimuth':'0'})
def offset(lat,lon,dx,dy):
    Pi = math.pi
    print("passed:{},{},{},{}".format(lat,lon,dx,dy))
    # Earths radius, sphere
    R = 6378137.0
    # Coordinate offsets in radians
    dLat = dy / R
    print(dLat)
    dLon = dx / (R * math.cos(Pi * lat / 180))
    print("dLat,dLon {},{}".format(dLat,dLon))
    # OffsetPosition, dxcimal dxgrees
    latO = lat + dLat * 180 / Pi
    lonO = lon + dLon * 180 / Pi
    output_latitude = "{0:.6f}".format(latO)
    output_longitude = "{0:.6f}".format(lonO)
    return "{},{}".format(output_latitude,output_longitude)

server='localhost'
port = 8500
lat=19.539186
lon=-99.196765
imei="357042061712320"
speed=0
bearing="180.0"
altitude="2313.800048828125"
accuracy="1"
batt="0.0"
portStatus="0000"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server, port))
while True:
    number = random.randrange(0, 4)
    speed = random.randrange(0,80)
    direction=position[number]
    print(direction['x'])
    #print("number:{}".format(number))
    for item in range(1,5):
        unix_epoch=int(time.time())
        timeStamp=unix_epoch
        print("coordinates: {},{}, {},{}".format(lat, lon,direction['x'],direction['y']))
        newPosition=offset(lat,lon,direction['x'],direction['y'])
        print("NEW pos:{}".format(newPosition))
        coordinates=newPosition.split(",")
        lat=float(coordinates[0])
        lon=float(coordinates[1 ])
        print("coordinates: {},{}".format(lat,lon))
        output=getMVT380(imei, accuracy, speed, str(lat), str(lon), datetime.utcnow().strftime("%y%m%d%H%M%S"),
                  "35", portStatus,str(direction['x']))
        s.sendall(output)
        ###########
        #output=raw_input("Press Enter to continue...")
        #print(output)
        time.sleep(2)
s.close
