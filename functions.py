import socket
import json


def Generate_Checksum(data: str):
    a = data
    b = [a[i:i+2] for i in range(0, len(a), 2)] # ['10', 'F8', '00', ...
    sum = "0"
    for i in b:
        sum = hex(int(sum, 16) ^ int(i, 16))
    return str(sum).replace("0x", "").upper().zfill(2)

def Generate_Command(Control_ID: str, Group: str, Command: str, bible, Data: int=[]):
    temp_command = ""
    temp_command += str(len(Data) + 5).zfill(2)
    temp_command += Control_ID
    temp_command += Group
    temp_command += Command
    for i in Data:
        temp_command += str(i).zfill(2)
    Full_command = temp_command + Generate_Checksum(temp_command)
    print("Command:", Full_command)
    Decode_Hex(Full_command, bible, "command")
    return Full_command

def Decode_Hex(Hex, bible, Hex_type="response"):
    print("Decoding", Hex_type)
    a = Hex
    b = [a[i:i+2] for i in range(0, len(a), 2)] # ['10', 'F8', '00', ...
    size = int(b[0])
    control_id = int(b[1])
    print("- Control ID:", int(control_id))
    group = int(b[2])
    print("- Group ID:", int(group))
    data = b[3:-1]
    command = data[0]
    checksum = b[-1]
    if  int(Generate_Checksum(Hex[:-2]), 16) == int(checksum, 16):
        print("- \033[92mChecksum OK\033[0m")
    else:
        print("- \033[91mChecksum failed\033[0m")
    print("- Command:", bible[command]['name'])
    if command in bible:
        for byte in bible[command][Hex_type]:
            type = bible[command][Hex_type][byte]['type']
            match type:
                case "list":
                    print(f"- {bible[command][Hex_type][byte]['Description']}: {bible[command][Hex_type][byte]['Options'][data[int(byte)]]}")
                case "number":
                    print(f"- {bible[command][Hex_type][byte]['Description']}: {data[int(byte)]}")
                case "ASCII":
                    print(f"- {bible[command][Hex_type][byte]['Description']}: {bytes.fromhex(data[int(byte)]).decode('ascii')}")

def check_response(control_ID, group_ID, response):
    a = response
    b = [a[i:i+2] for i in range(0, len(a), 2)] # ['10', 'F8', '00', ...
    size = int(b[0])
    control_id_check = str(b[1]).zfill(2) == control_ID
    group_id_check = str(b[2]).zfill(2) == group_ID
    data = b[3:-1]
    command = data[0]
    checksum_check = int(Generate_Checksum(response[:-2]), 16) == int(b[-1], 16)
    return control_id_check, group_id_check, data, checksum_check

def retrieve_command(command_name, type, bible):
    for command in bible:
        if bible[command]["name"] == command_name:
            if bible[command]["type"] == type:
                return command

class device:
    def __init__(self, ip, port, control_ID, group_ID, biblefile):
        self.ip = ip
        self.port = port
        self.control_ID = str(control_ID).zfill(2)
        self.group_ID = str(group_ID).zfill(2)
        self.bible = json.loads(open(biblefile).read())

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
        hex = Generate_Command(self.control_ID, self.group_ID, retrieve_command(command, "Get", self.bible), self.bible, args)
        self.connection.send(bytes.fromhex(hex))
        print("Waiting for response")
        data_temp = str(self.connection.recv(1024).hex())
        data = data_temp.replace("\\x", "").replace("b'", "").replace("'", "").upper()
        print('Received:', data)
        Decode_Hex(data, self.bible)
        return data

    def set(self, command: str, *args: int):
        print("Sending data")
        hex = Generate_Command(self.control_ID, self.group_ID, retrieve_command(command, "Set", self.bible), self.bible, args)
        self.connection.send(bytes.fromhex(hex))
        print("Waiting for response")
        data_temp = str(self.connection.recv(1024).hex())
        data = data_temp.replace("\\x", "").replace("b'", "").replace("'", "").upper()
        print('Received:', data)
        Decode_Hex(data, self.bible)
        return data


TV = device("10.0.0.123", 5000, 1, 0, "data.json")
TV.connect()
TV.get("Power State")
input("enter to continue")
TV.set("Power State", 1) 
TV.disconnect()