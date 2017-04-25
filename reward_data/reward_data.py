# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:22:18 2017

@author: sajjad
"""

import csv, os
from datetime import datetime
import datetime as datte
import ConfigParser



def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return int(unix_time(dt) * 1000)


#Checks price dictionary and return correspondent price value against the item
def get_price_of_item(prices_file, item):
    price_dict = {}
    firstline = True
    with open(prices_file, 'rb') as csvfile:
        for line in csvfile.readlines():
            if firstline:    #skip first line
                firstline = False
                continue
            array = line.split(';')
            price_dict[array[3]] = array[10][:-2]
    
    return price_dict.get(item)
                            
def prepare_reward_data(source, logfile, data_file, csv_headers, prices, startDate):
   if os.path.exists(source) and os.path.exists(prices):
        print '\nSTARTING..........\n'
        file_count = 0
        source_dir = os.listdir(source_folder)    
        for source in source_dir:
           sub_dir = os.listdir(source_folder+'/'+source) 
           current_target_folder = source_folder+'/'+source
           if logfile in sub_dir:
               current_log_file = logfile
               output_data_file = data_file+source[4:]+'_filter.csv'
               if not os.path.exists(source_folder+'/'+source+'/filter'):
                   os.makedirs(source_folder+'/'+source+'/filter')
               if os.path.exists(source_folder+'/'+source+'/filter'): 
                    data = []
                    start = datetime.strptime(startDate, "%Y-%m-%d")
                    startmillis = unix_time_millis(start)
                    try:
                        with open(source_folder+'/'+source+'/filter/'+output_data_file, 'wb') as csvfile:
                            spamwriter = csv.writer(csvfile, delimiter=';')
                            spamwriter.writerow(csv_headers)
                            displays = ['diagram', 'wardrobe', 'arena', 'midway']
                            logs = open(current_target_folder+'/'+current_log_file, 'r')
                            for line in logs:
                                if 'marbles' in line:
                                    marbles = int(line.split(";")[4])
                                if 'power' in line:
                                    power = line.split(";")[4]
                                for j in displays:
                                    if j in line:
                                        #print line.strip()
                                        current = datetime.strptime(line.split(";")[1], "%Y-%m-%d %H:%M:%S")
                                        currentmillis = unix_time_millis(current)
                                        delta = datte.date.fromtimestamp(currentmillis/1000) - datte.date.fromtimestamp(startmillis/1000)
                                        data.append(line.split(";")[1][:10])            #Date
                                        data.append(line.split(";")[1][11:19])          #Time
                                        data.append(marbles)                            #Marbles
                                        data.append(power)                              #Power
                                        if delta.days >= 0 and delta.days < 7:          #Level
                                            data.append(1)
                                        elif delta.days >= 7 and delta.days < 14:
                                            data.append(2)
                                        elif delta.days >= 14 and delta.days < 21:
                                            data.append(3)
                                        elif delta.days >= 21:
                                            data.append(4)
                                        else:
                                            data.append(1)
                                        data.append(line.split(";")[3])
                                        data.append(line.split(";")[4])                 #Action
                                        if line.split(";")[4] == 'buy':                 #updating marbles again
                                            marbles = int(marbles) -  int(get_price_of_item(prices, line.split(";")[5][:-1]))
                                            data[2] = marbles
                                        elif line.split(";")[4] == 'sell':
                                            marbles = int(marbles) +  int(get_price_of_item(prices, line.split(";")[5][:-1]))/2
                                            data[2] = marbles
                                        data.append(line.split(";")[5][:-1])            #Object
                                        spamwriter.writerow(data)
                                del data[:]
                        print str(file_count + 1)+'--------'+source+'---------Data extracted successfully!!!\n'
                        logs.close()
                        file_count = file_count + 1
                    except IOError as e:
                        print 'IO ERROR: "'+e.filename+'" does not exist or already opened by another program!!!'
                        print source+'--------Data could not extracted successfully!!!\n'
               else:
                    print 'ERROR: "filter" folder does not exist...!!!'
           else:
               print source+'------Log file not found!!!\n'
        print 'Process finished---------Total files covered: '+str(file_count)
   else:
       print '\nSome files are not existing'
        
if __name__ == '__main__':
    configParser = ConfigParser.RawConfigParser()
    configFilePath = r'config.txt'
    if os.path.exists(configFilePath):  
        configParser.read(configFilePath)
        logfile = configParser.get('config-values', 'logfile')
        source_folder = configParser.get('config-values', 'source_folder')
        data_file = configParser.get('config-values', 'data_file')  
        csv_headers = configParser.get('config-values', 'csv_headers')
        csv_headers = csv_headers.split(',')
        prices = configParser.get('config-values', 'prices')
        startDate = configParser.get('config-values', 'startDate')
        prepare_reward_data(source_folder, logfile, data_file, csv_headers, prices, startDate)
    else:
        print '\nconfig file does not exist...'