import sys
sys.path.append('../')
from Common.project_library import *

# Modify the information below according to you setup and uncomment the entire section

# 1. Interface Configuration
project_identifier = 'P3B' # enter a string corresponding to P0, P2A, P2A, P3A, or P3B
ip_address = '169.254.214.84' # enter your computer's IP address
hardware = False # True when working with hardware. False when working in the simulation

# 2. Servo Table configuration
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180#270# enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# 3. Qbot Configuration
bot_camera_angle = -21.5 # angle in degrees between -21.5 and 0

# 4. Bin Configuration
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.25 # offset in meters
bin1_color = [1,0,0] # e.g. [1,0,0] for red
bin2_offset = 0.25
bin2_color = [0,1,0]
bin3_offset = 0.25
bin3_color = [0,0,1]
bin4_offset = 0.25
bin4_color = [1,1,1]

#--------------- DO NOT modify the information below -----------------------------

if project_identifier == 'P0':
    QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
    bot = qbot(0.1,ip_address,QLabs,None,hardware)
    
elif project_identifier in ["P2A","P2B"]:
    QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
    arm = qarm(project_identifier,ip_address,QLabs,hardware)

elif project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration,None, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    
elif project_identifier == 'P3B':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    qbot_configuration = [bot_camera_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color]]
    configuration_information = [table_configuration,qbot_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bins = bins(bin_configuration)
    bot = qbot(0.1,ip_address,QLabs,bins,hardware)
    

#---------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------
#Functions
def load_container():
    container_mass = 0
    container_destination = 0
    qbot_mass = main_container_mass
    containers_on_qbot = 0
    container_destination = main_container_destination
    while qbot_mass + container_mass <= 90 and containers_on_qbot + 1 <= 3 and qbot_destination == container_destination:    
        #While loop checks all of the contstraints (checks that the mass does not exceed 90 grams, checks that the Q-bot
        #doesn't exceed 3 containers checks that and all the containers have the same bin destination -Juan-

        #If all the constraints are met the Q-arm loads the container onto the Q-bot -Stephanie-
        arm.move_arm(0.64,0.0,0.275)  
        time.sleep(1.5)
        arm.control_gripper(45)
        time.sleep(1.5)
        arm.move_arm(0.00,-0.370,0.54)
        time.sleep(1.5)
        arm.move_arm(0.00,-0.44,0.475)
        time.sleep(1.5)
        arm.control_gripper(-45)
        time.sleep(1.5)
        arm.move_arm(0.00,-0.370,0.54)
        time.sleep(1.5)
        arm.move_arm(0.406,0.0,0.53)
        time.sleep(1.5)

        containers_on_qbot += 1 
        qbot_mass += container_mass
        #The two lines of code above update the number of containers on  
        #the Q-bot and the total mass on the Q-bot for the next loop -Juan-
        
        #Dispenses the next container and prints containers attributes, each attribute is attached to a variable -Juan-
        container_attributes = table.dispense_container(random.randint(1,6),True)
        print(container_attributes)
        container_material = container_attributes[0] 
        container_mass = container_attributes[1]
        container_destination = container_attributes[2]
        
        
        #the code below checks if any of the constraints are not met. If this is the case the 
        #while loop stops and the containers destination and mass are returned -Juan-
        if container_destination != qbot_destination or qbot_mass + container_mass > 90 or containers_on_qbot +1 > 3:
            return container_destination, container_mass
        
        
#The function below takes the container destination and returns the specific
#colour of the bin depending on container destination -Stephanie-
def transfer_container(destination_bin):
    if destination_bin == 'Bin01':
        destination_bin_color = [1,0,0]
    else:
        if destination_bin == 'Bin02':
            destination_bin_color = [0,1,0]
        else:
            if destination_bin == 'Bin03':
                destination_bin_color = [0,0,1]
            else:
                if destination_bin == 'Bin04':
                    destination_bin_color = [1,1,1]
    return destination_bin_color
 

def deposit_container():
    if sensor_reading[0] == transfer_container(main_container_destination): 
        bot.deactivate_color_sensor()
        #The function only works if the sensor reading is the same as the returned destination
        #bin colour from the transfer container function -Juan-
        
        
        #The while loop below runs to allow the bot to move forward through 48 more loops.This aids 
        #in accuracy making sure that the bot stops perpendicular to the box when turning around corners -Juan-
        loops = 0
        while loops != 48:
            line_presence = bot.line_following_sensors()
            if line_presence == [1,1]:
                bot.set_wheel_speed([0.1,0.1])
            else:
                if line_presence == [1,0]:
                    bot.set_wheel_speed([0.05,0.1])
                elif line_presence == [0,1]:
                    bot.set_wheel_speed([0.1,0.05])
            loops += 1
            print(loops)
            line_presence = bot.read_color_sensor()
            
        #After the while loop, the bot turns to a position to deposit the 
        #container and then returns to the yellow line for the return home code -Stephanie-
        bot.deactivate_color_sensor()
        bot.stop()
        bot.forward_distance(0.1)
        bot.rotate(-97)
        bot.forward_distance(0.18)
        bot.rotate(97)
        bot.activate_linear_actuator()
        bot.dump()
        bot.deactivate_linear_actuator()
        bot.rotate(97)
        bot.forward_distance(0.165)
        bot.rotate(-97)

#Pre-defined functions allows for the code to run with minimal errors

#------------------------------Beginning of Code-----------------------------

import random

#-------------------Dispense Container
main_container_attributes = table.dispense_container(random.randint(1,6),True) 
print(main_container_attributes)

main_container_material = main_container_attributes[0]
main_container_mass = main_container_attributes[1]
main_container_destination = main_container_attributes[2]
#This dispenses the first container to be used in the first cycle of the load container function. After this, it
#does not run again in the code as it is unecessary because the load container function dispenses new containers -Stephanie-

#-------------------Load Container Function
runs_forever = True
while runs_forever == True:
    #the entire code from this point on is in a while loop so there can be infinite cycles of recycling -Juan-
    
    qbot_destination = main_container_destination
    new_main = load_container()
    print(new_main)   
    #The code above uses the data from the first dispensed container and runs the load container function,
    #the mass and destination of the remaining container returned by the function after it has run 
    #is saved to a variable to be used in the next cycle -Stephanie-
    
    #------------------Transfer Container Function - Q-bot Line Following
    bot.activate_color_sensor()
    sensor_reading = bot.read_color_sensor()
    while sensor_reading[0] != transfer_container(main_container_destination):
        line_presence = bot.line_following_sensors()
        if line_presence == [1,1]:
            bot.set_wheel_speed([0.1,0.1])
        else:
            if line_presence == [1,0]:
                bot.set_wheel_speed([0.05,0.1])
            elif line_presence == [0,1]:
                bot.set_wheel_speed([0.1,0.05])
        sensor_reading = bot.read_color_sensor()
        #This block of code uses the line following sensors to dictate the appropriate wheel speed of the Q-bot
        #If the Q-bot detects the yellow line only on one side(L or R), it adjusts its wheel speeds accordingly to return back to 
        #the yellow line. As the while loop is running, after each cycle, their is a colour sensor reading returned to check if 
        #the Q-bot has reached its destination(the destination being the returned value of the tranfer_container function when the 
        #bin destinatian of the bottles mounted on the Q-bot is input into it) -Juan

    #-----------------------Deposit Container Function
    
    deposit_container() 
    #Once the destination bin is detected, this calls the deposit container function to deposit container(s) 
    
    #----------------------Return Home
    white_bin = [1,1,1]
    bot.activate_color_sensor()
    sensor_home = bot.read_color_sensor()
    
    while sensor_home[0] != white_bin:
        line_presence = bot.line_following_sensors()
        if line_presence == [1,1]:
            bot.set_wheel_speed([0.1,0.1])
        else:
            if line_presence == [1,0]:
                bot.set_wheel_speed([0.05,0.1])
            elif line_presence == [0,1]:
                bot.set_wheel_speed([0.1,0.05])
        sensor_home = bot.read_color_sensor()
        #A while loop is activated again, similar to the one to determine the destination bin, but here it runs until 
        #the white bing(the last bin before returning home) is detected -Stephanie-

    Y_home_position = -0.010
    qbot_position = bot.position()
    while qbot_position[1] < Y_home_position:
        qbot_position = bot.position()
        print(qbot_position)
        line_presence = bot.line_following_sensors()
        if line_presence == [1,1]:
            bot.set_wheel_speed([0.1,0.1])
        else:
            if line_presence == [1,0]:
                bot.set_wheel_speed([0.05,0.1])
            elif line_presence == [0,1]:
                bot.set_wheel_speed([0.1,0.05])
    bot.stop()
    #After the Q-bot detects the white container it continues using line following but now it is also getting it's position
    #This block of code makes the Q-bot follow the line until it reaches the Y position it needs to be at to load more
    #containers -Juan-

    X_home_position = 1.5
    qbot_position = bot.position()
    if qbot_position[0] < 1.5:
        bot.rotate(-97.3)
        bot.forward_distance(0.025)
        bot.rotate(97.3)
        #This code makes the Q-bot adjust itself so it is closer to the Q-arms drop off location to prevent 
        #error(dropping of containers) -Stephanie-

    main_container_destination = new_main[0]
    main_container_mass = new_main[1]
    #These are the two main container functions for destination and mass to be used in the next cycle within the load container
    #function -Stephanie-

#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
