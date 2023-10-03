import sys
import time
import serial.tools.list_ports
import serial
import math as math
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog


#marlin_speed = 1.7
waste = [177, 167.5]
k = 11.5 #Needle offset
valve_dead_volume = 0.27 #calibration offset
liquid_specefic_sleep = 7 #Time it takes for a full dosage to settle
X, Y, Z = None, None, None

def start_sequence(syringe_size,solvents,pump = True,offset = True):
    global arduino, waste, a, b, a_vol, b_vol, X, Y, Z, settings, vials, vial_info, syringe_info, marlin_speed, feedrate
    X, Y, Z = 0,0,0
    settings,vials,vial_info,syringe_info = readexcel()
    marlin_speed = settings.loc['marlin_speed','Setting_value']
    feedrate = settings.loc['feedrate','Setting_value']    

    try:
        a = syringe_info.loc[float('{}'.format(syringe_size)),'a']
        b = syringe_info.loc[float('{}'.format(syringe_size)),'b']
        a_vol = syringe_info.loc[float('{}'.format(syringe_size)),'a_vol']
        b_vol = syringe_info.loc[float('{}'.format(syringe_size)),'b_vol']
    except:
        print("Invalid syringe size --> choose valid size")
        sys.exit()

    port = serial.tools.list_ports.comports()
    print("port = " + port[0].device)
    arduino = serial.Serial(port[0].device,250000)
    time.sleep(2)
    arduino.write(b"G28 \n") ## homing command
    time.sleep(15)
    if offset == True:
        get_offset()
    #Prepping solvents
    if pump == True:
        for i in range(solvents):
            arduino.write("T{} \n".format(i).encode())
            pump_start(syringe_size,i)
    move_to(z = settings.loc['safety_height','Setting_value'])
    

def end_sequence(solvents, pump = True):
    move_to(x=100,y=100)
    time.sleep(5)
    if pump == True:  
        for i in range(solvents):
            arduino.write("T{} \n".format(i).encode())
            arduino.write("M104 T{} S100 \n".format(i).encode())
            time.sleep(1)
            arduino.write("G1 E-{} \n".format((10-b)/a).encode())
            time.sleep(10/(a_vol*100+b_vol)+1)
            arduino.write("M104 T{} S0 \n".format(i).encode())
            time.sleep(1)
            arduino.write(b"G1 E0 \n")
            time.sleep(10/(a_vol*100+b_vol)+1)
    
    arduino.write(b"M81 \n") ##Power off
            
    arduino.close()
    print("Thank you for chosing Jakob & Thorbjørn inc. ヽ(o⌣oヾ)")


def readexcel():
    root = tk.Tk()
    root.attributes('-topmost',1)
    root.withdraw()
    file_path = filedialog.askopenfilename()
    settingsdf = pd.read_excel(file_path,sheet_name=1)
    namelist = []
    for i in settingsdf['Settings']:
        namelist.append(i)
    settingsdf.index = namelist
    settingsdf.drop("Settings", axis=1, inplace=True)
    #Import the excel file and clean it from vials with 0 total volume
    vialdf = pd.read_excel(file_path)
    vialinformation = pd.read_excel(file_path)
    namelist = []
    for i in vialdf['Vials']:
        namelist.append(i)
    vialdf.index = namelist
    vialdf.drop("Vials", axis=1, inplace=True)
    namelist = []
    for i in vialinformation['Vials']:
        namelist.append(i)
    vialinformation.index = namelist
    vialinformation.drop("Vials", axis=1, inplace=True)
    vialdf.drop("Totale_volume", axis=1, inplace=True)
    vialdf.drop("x", axis=1, inplace=True)
    vialdf.drop("y", axis=1, inplace=True)
    try: #Try to see if the excel sheet has timers that needs to be cleaned
        for i in range(6):
            vialdf.drop("Sol {} timer".format(i+2), axis=1, inplace=True)
    except:
        pass
    for i in range(6):
        vialinformation.drop("sol {}".format(i+1), axis=1, inplace=True)
    syringe_info = pd.read_excel(file_path,sheet_name=2)
    namelist = []
    for i in syringe_info['Syringe_volume']:
        namelist.append(i)
    syringe_info.index = namelist
    syringe_info.drop("Syringe_volume", axis=1, inplace=True)

    # Save the position of the X and Y coordinates, remove the index and replace with the random, then conjoin them


    randomized_dataframes = vialdf.sample(frac=1)
    randomized_dataframes.to_csv(file_path.split("/")[-1].split(".")[0] + " - run data" + '.csv')
    vialdf = randomized_dataframes
    vialinformation.index = vialdf.index

    return(settingsdf,vialdf,vialinformation,syringe_info)

def get_offset():
    global x_correct
    global y_correct
    
    with open('offsets.txt') as f:
        lines = f.readlines()
        
    x_correct = float(lines[0][11:-1])
    y_correct = float(lines[1][11:])

    arduino.write("M206 X{} Y{} \n".format(x_correct,y_correct).encode())

def pump_start(syringe_size,solvent,speed = 100): # X and Y are needed for the waste position, easily called in start up
    vol = syringe_size - 5
    print("Preparin pump {}".format(solvent))
    arduino.write(b"G92 E0 \n") ## sets current position to 'zero'. Make sure syringe is completly plunged
    arduino.write("G1 E-{} \n".format((vol-b)/a).encode()) ## set E-max here and incorporate maximum limit????
    time.sleep(vol/(a_vol*speed+b_vol)+10)
    
    move_to(z = settings.loc['safety_height','Setting_value'])
    move_to(x = waste[0], y = waste[1])
    move_to(z = settings.loc['Beaker_height','Setting_value'])
    #move_to(x = waste[0]+(2-solvent)*k, y = waste[1]) ##Used for older needle setup
    #Control valve with fan output
    # arduino.write(b"M106 S255 \n")
    
    #Make sure the liquid is settled in the syringe
    time.sleep(liquid_specefic_sleep)
    
    #Control valve with temp output
    arduino.write("M104 T{} S100 \n".format(solvent).encode())
    time.sleep(1)
    arduino.write(b"G1 E0 \n")
    time.sleep(vol/(a_vol*speed+b_vol)+5)
    #Control valve with temp output
    arduino.write("M104 T{} S0 \n".format(solvent).encode())
    #Dose three times into thrash to remove early error
    dose(1,solvent)
    dose(1,solvent)
    dose(1,solvent)
    print("Pump {} is now ready to be used".format(solvent))

def pump_rinse(syringe_size,solvent):
    pump_start(syringe_size, solvent)
    pump_start(syringe_size, solvent)
    pump_start(syringe_size, solvent)
    end_sequence()

def move_to(x = X, y = Y, z = Z):
    global X,Y,Z
    if x == None:
        x = X
    if y == None:
        y = Y
    if z == None:
        z = Z
    if z != Z:
        sleep = math.sqrt((z-Z)**2)
    else:
        sleep = math.sqrt(((x-X)**2+(y-Y)**2))
    arduino.write("G1 X{} Y{} Z{} \n".format(x,y,z).encode())
    time.sleep((sleep/feedrate)*2 + 1)
    #Update the printer head position
    X,Y,Z = x,y,z

def dose(volume,solvent,speed=100):
    # volume += valve_dead_volume
    air_vol = 5
    #Choose right extruder
    arduino.write("T{} \n".format(solvent).encode())
    
    #Change valve state
    #Control valve with fan output
    # arduino.write(b"M106 S255 \n")
    #Control valve with temp output
    arduino.write("M104 T{} S100 \n".format(solvent).encode())
    arduino.write("G1 E-{} \n".format((air_vol-b)/a).encode())
    time.sleep(air_vol/(a_vol*100+b_vol)+1)
    time.sleep(1)
    
    
    #Control valve with temp output
    arduino.write("M104 T{} S0 \n".format(solvent).encode())
    time.sleep(0.5)
    #Suck liquid
    arduino.write("G1 E-{} \n".format(((volume+air_vol)-b)/a).encode())
    time.sleep(volume/(a_vol*100+b_vol)+1)
    time.sleep(liquid_specefic_sleep)
    
    #Control valve with temp output
    arduino.write("M104 T{} S100 \n".format(solvent).encode())
    time.sleep(0.5)
    print("dosing: " + str(volume-valve_dead_volume) )
    #set speed
    arduino.write("M203 E{} \n".format((marlin_speed/100)*speed).encode())
    #dose
    arduino.write(b"G1 E0 \n")
    time.sleep((volume+air_vol)/(a_vol*speed+b_vol)+1)
    #Change valve state
    #Control valve with fan output
    #arduino.write(b"M106 S0 \n")
    #Control valve with temp output
    arduino.write("M104 T{} S0 \n".format(solvent).encode())
    arduino.write("M203 E{} \n".format(marlin_speed).encode())
    
    

def calibration_dose(E_value,solvent,speed=100):
    air_E= 15
    
    #Choose right extruder
    arduino.write("T{} \n".format(solvent).encode())
    
    #Change valve state
    #Control valve with fan output
    # arduino.write(b"M106 S255 \n")
    #Control valve with temp output
    print("switch to get air")
    arduino.write("M104 T{} S100 \n".format(solvent).encode())
    print("getting 5 ml of air")
    arduino.write("G1 E-{} \n".format(air_E-b).encode())
    time.sleep(5/(a_vol*100+b_vol)+1)
    time.sleep(2)
    
    
    #Control valve with temp output
    arduino.write("M104 T{} S0 \n".format(solvent).encode())
    time.sleep(0.5)
    #Suck liquid
    print("getting {} ml".format(E_value))    
    arduino.write("G1 E-{} \n".format(float(E_value+air_E)).encode())
    time.sleep(5/(a_vol*100+b_vol)+1)
    time.sleep(liquid_specefic_sleep)
    
    #Control valve with temp output
    arduino.write("M104 T{} S100 \n".format(solvent).encode())
    #set speed
    arduino.write("M203 E{} \n".format((marlin_speed/100)*speed).encode())
    #dose
    arduino.write(b"G1 E0 \n")
    time.sleep((10)/(a_vol*speed+b_vol)+1)
    #Change valve state
    #Control valve with fan output
    #arduino.write(b"M106 S0 \n")
    #Control valve with temp output
    arduino.write("M104 T{} S0 \n".format(solvent).encode())
    arduino.write("M203 E{} \n".format(marlin_speed).encode())

    
def standard_dosage(speed=100):
    start = time.time()
    timer_dic = {}
    for i in range(len(vials)):
        extruder=0 #Solvent counter
        if vial_info.loc['vial {}'.format(i+1),'Totale_volume'] == 0:
            continue
        x = vial_info.loc['vial {}'.format(i+1),'x']
        y = vial_info.loc['vial {}'.format(i+1),'y']
        start_vial_timer = time.time() - start
        move_to(x,y)
        move_to(z = settings.loc['Vial_height','Setting_value'])

        for volume in vials.loc['vial {}'.format(i+1)]:
            if volume == 0:
                extruder+=1
            if volume != 0:
                dose(volume,extruder,speed)
                duration_timer = time.time() - start - start_vial_timer
                timer_dic["Vial {} Sol {}".format(i+1,extruder+1)] = [(start_vial_timer,duration_timer)]
                start_vial_timer = time.time() - start
                extruder+=1
        move_to(z = settings.loc['safety_height','Setting_value'])
    #For Gantt diagram
    Gantt_diagram(timer_dic)
    
def calibration_dosage(speed=100):
    for i in range(len(vials)):
        extruder=0 #Solvent counter
        if vial_info.loc['vial {}'.format(i+1),'Totale_volume'] == 0:
            continue
        x = vial_info.loc['vial {}'.format(i+1),'x']
        y = vial_info.loc['vial {}'.format(i+1),'y']

        move_to(x,y)
        move_to(z = settings.loc['Vial_height','Setting_value'])

        for volume in vials.loc['vial {}'.format(i+1)]:
            print(extruder)
            if volume == 0:
                extruder+=1
            if volume != 0:
                #move_to(x+(2-extruder)*k)
                calibration_dose(volume, extruder,speed)
                extruder += 1
        move_to(z = settings.loc['safety_height','Setting_value'])


###################### Experimental section #######################
#To measure the time taken for each solution dosage into a vial
def Gantt_diagram(dictionary):
    fig, gnt = plt.subplots()
    gnt.set_xlabel('Time [s]')
    gnt.set_ylabel('Vials')
    # gnt.set_ylim(0, 20*len(dictionary))
    ytick_list = []
    ytickname_list = []
    for i in range(len(vials)):
        ytick_list.append(15+(10*i))
        ytickname_list.append("%i"%(i+1))
    gnt.set_yticks(ytick_list)
    gnt.set_yticklabels(ytickname_list)
    j = 0
    for solvents in vials:
        j +=1
        for i in range(len(vials)):
            if vials[solvents][i] ==0:
                continue
            gnt.broken_barh(dictionary["Vial {} Sol {}".format(i+1,j)], (15+10*i, 9),facecolors = (0.15*j,0.15*j,0.15*j,0.15*j))





    


