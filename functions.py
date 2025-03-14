import socket
import json

bible = json.loads(open("data.JSON").read())

def Generate_Checksum(data: str):
    a = data[:-2]
    b = [a[i:i+2] for i in range(0, len(a), 2)] # ['10', 'F8', '00', ...
    sum = "0"
    for i in b:
        sum = hex(int(sum, 16) ^ int(i, 16))
    return str(sum).replace("0x", "").upper().zfill(2)

def Generate_Command(Control_ID: str, Group: str, Command: str, Data):
    temp_command = ""
    temp_command += str(len(Data) + 5).zfill(2)
    temp_command += Control_ID
    temp_command += Group
    temp_command += Command
    for i in Data:
        temp_command += Data[i]
    Full_command = temp_command + Generate_Checksum(temp_command)
    print("Command:", Full_command)
    Decode_Hex(Full_command, "command")
    return Full_command

def Decode_Hex(Hex, Hex_type="response"):
    print("Decoding", Hex_type)
    a = Hex
    b = [a[i:i+2] for i in range(0, len(a), 2)] # ['10', 'F8', '00', ...
    size = int(b[0])
    control_id = int(b[1])
    print("Control ID:", int(control_id))
    group = int(b[2])
    print("Group ID:", int(group))
    data = b[3:-1]
    command = data[0]
    checksum = b[-1]
    if  int(Generate_Checksum(Hex), 16) == int(checksum, 16):
        print("\033[92mChecksum OK\033[0m")
    else:
        print("\033[91mChecksum failed\033[0m")
    print("Command:", bible[command]['name'])
    if command in bible:
        for byte in bible[command][Hex_type]:
            type = bible[command][Hex_type][byte]['type']
            match type:
                case "list":
                    print(f"{bible[command][Hex_type][byte]['Description']}: {bible[command][Hex_type][byte]['Options'][data[int(byte)]]}")
                case "number":
                    print(f"{bible[command][Hex_type][byte]['Description']}: {data[int(byte)]}")
                case "ASCII":
                    print(f"{bible[command][Hex_type][byte]['Description']}: {bytes.fromhex(data[int(byte)]).decode('ascii')}")

def check_response(control_ID, group_ID, response):
    a = data
    b = [a[i:i+2] for i in range(0, len(a), 2)] # ['10', 'F8', '00', ...
    size = int(b[0])
    control_id_check = int(b[1]) == control_ID
    group_id_check = int(b[2]) == group_ID
    data = b[3:-1]
    command = data[0]
    checksum_check = b[-1] == Generate_Checksum(response[-2])
    return control_id_check, group_id_check, data, checksum_check

def retrieve_command(command_name, type):
    for command in bible:
        if bible[command]["name"] == command_name:
            if bible[command]["type"] == type:
                print(command)
                return command

class device:
    def __init__(self, ip, port, control_ID, group_ID):
        self.ip = ip
        self.port = port
        self.control_ID = hex(control_ID)
        self.group_ID = hex(group_ID)

    def connect(self):
        host = self.ip
        port = self.port
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting to", host, "on port", port)
        try:
            self.connection.connect((host, port))
        except:
            print("\033[91mConnection failed\033[0m")
            exit()
        print("\033[92mConnected\033[0m")

    def disconnect(self):
        print("Disconnecting")
        self.connection.close()
        print("\033[91mDisconnected\033[0m")

    def get(self, command: str, *args: int):
        print("Sending data")
        hex = Generate_Command(self.control_ID, self.group_ID, retrieve_command(command, "Get"), *args)
        self.connection.send(bytes.fromhex(hex))
        print("Waiting for response")
        data_temp = str(self.connection.recv(1024).hex())
        data = data_temp.replace("\\x", "").replace("b'", "").replace("'", "").upper()
        print('Received:', data)
        check_response(data)
        return data

    def set(self, command: str, *args: str):
        print("Sending data")
        hex = Generate_Command(self.control_ID, self.group_ID, retrieve_command(command, "Set"), *args)
        self.connection.send(bytes.fromhex(hex))
        print("Waiting for response")
        data_temp = str(self.connection.recv(1024).hex())
        data = data_temp.replace("\\x", "").replace("b'", "").replace("'", "").upper()
        print('Received:', data)
        check_response(data)
        return data

#set commands
#Set_Power_Standby = "06010018011E"
#Set_Power_On = "06010018021D"
#Set_Reboot = "060100570050"
#Set_Volume_Mute_On = "060100470141"
#Set_Volume_Mute_Off = "060100470040"
#Set_tune_to_Channel = "070100C200" # + channel number + Xor checksum
#Set_Channel_Up_Tune = "060100C301C5"
#Set_Channel_Down_Tune = "060100C300C4"
#Set_Volume_Up = "07010041010244"
#Set_Volume_Down = "07010041000245"
#Set_Input_Source_Tuner = "090100AC220901008E"
#Set_Input_Source_HDMI1 = "090100AC0D090100A1"
#Set_Input_Source_HDMI2 = "090100AC06090100AA"
#Set_Input_Source_HDMI3 = "090100AC0F090100A3"
#Set_Input_Source_HDMI4 = "090100AC19090100B5"
#Set_Input_Source_USB = "090100AC0C090100A0"
#Set_Input_Source_Smart_Info = "090100AC210901008D"
#Set_Input_Source_Googlecast = "090100AC230901008F"
#Set_Input_Source_Custom = "090000AC18000100BC"

#get commands
#Get_Volume_Mute = "0501004642"
#Get_Current_Channel_Number = "050100C1C5"
#Get_Current_Input_Source = "050100ADA9"

TV = device("10.0.0.121", 5000, 1, 0)
TV.connect()
print("Sending data")
#TV.connection.send(bytes.fromhex(Generate_Command("01", "00", "AC", {1: "05", 2: "00", 3: "01", 4: "00"})))
#print("")
#print("Waiting for response")
#data_temp = str(TV.connection.recv(1024).hex())
#data = data_temp.replace("\\x", "").replace("b'", "").replace("'", "").upper()
#print('Received:', data)
TV.get("Power State")
TV.disconnect()
#print("")
#Decode_Hex(data)