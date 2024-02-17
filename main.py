import pexpect
import re
import sys
import time
import traceback
from datetime import datetime

# configure options for your command
wallet = "your wallet name"       # wallet name of your coldkey
hotkeys = ["your hotkeys"]        # a list with the names of all the hotkeys you want to register
highest_cost = 2.0                # the maximal amount of tao you are willing to burn to register
password = "your password"        # password for your coldkey
netuid = 1                        # subnet uid you want to register
iterate = False

# start registraion bot
while True:
    for hotkey in hotkeys:
        while True:
            try:
                iterate = False
                command = 'btcli subnet register --subtensor.network local --netuid {} --wallet.name {} --wallet.hotkey {}'.format(netuid, wallet, hotkey)
                
                # Format the time as HH:MM:SS
                formatted_time = datetime.now().time().strftime("%H:%M:%S")
                
                # Print the formatted time
                print("\nColdkey: ", wallet, "Hotkey: ", hotkey, flush=True)
                print(formatted_time, flush=True)

                child = pexpect.spawn(command)
                child.logfile_read = sys.stdout.buffer
                                
                child.expect(r'The cost to register by recycle is (.*?)(?:\n|$)')
                cost_str = child.match.group(1).decode('utf-8').replace('τ', '')
                clean_cost_str = re.sub(r'\x1b\[[0-9;]*m', '', cost_str).strip()
                cost = float(clean_cost_str)
                
                if cost > highest_cost:
                    print("Not registering: n", flush=True)
                    child.sendline('n')
                    continue
                else:
                    print("Sending1: y", flush=True)
                    child.sendline('y')
                
                child.expect('Enter password to unlock key')
                print("\nSending: password")
                child.sendline(password)
                print("\nPassword sent")
                try:
                    child.expect(r'Recycle (.*?) to register on subnet')
                except:
                    break
                    
                recycle_cost_str = child.match.group(1).decode('utf-8').replace('τ', '')
                clean_recycle_cost_str = re.sub(r'\x1b\[[0-9;]*m', '', recycle_cost_str).strip()
                recycle_cost = float(clean_recycle_cost_str)
                print("Recycle cost:", recycle_cost)
                
                if recycle_cost > highest_cost:
                    print("Sending: n", flush=True)
                    child.sendline('n')
                else:
                    print("Sending2: y", flush=True)
                    child.sendline('y')
                    
                    child.expect(r'Registered', timeout=120)
                    break
            except Exception as e:
                print("An error occured", e)
                print(traceback.format_exc())
                child.sendintr()             # Send Ctrl+C
                child.expect(pexpect.EOF)    # Wait for the command to exit
                if iterate:
                    break
                else:
                    continue
                    
