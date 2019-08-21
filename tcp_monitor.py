################## Import
import socket
import multiprocessing
import time
import tkinter as tk
import colorama
import ctypes

################## global
PORT = 4545
HIST = ""
READ = "NULL"
shared_data = multiprocessing.Array('i', 2)     # [is_connected, is_new_value]
temp = ".xxxxxxx.txt"

#---------------------------------------------------------------------#



################## functions
def update_form():
    global HIST
    global READ

    if shared_data[0] == 0:
        STATUS = "Not Connected"
    else:
        STATUS = "Connected"

    if shared_data[1] == 1:         # new data available
        fp = open(temp, 'r')
        READ = fp.read()
        HIST = HIST + READ + '\n'

        fp.close()
        shared_data[1] = 0         # it's not new anymore


    text = "listenning on port {} .... {}".format(PORT, STATUS)

    canvas.itemconfigure(history, text=HIST)
    canvas.itemconfigure(reading, text=READ)
    canvas.itemconfigure(status, text=text)
    root.after(500, update_form)

#---------------------------------------------------------------------#



################## socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("0.0.0.0", PORT))
sock.listen(1)
#---------------------------------------------------------------------#

################## tkinter form
root = tk.Tk()
root.title("TCP monitor")
canvas = tk.Canvas(root, height=600, width=800, bg = '#000')

canvas.create_line(150,40 , 800,40 , width=2, fill='yellow' )
canvas.create_line(150,0 , 150,600 , width=2, fill='yellow' )

status  = canvas.create_text(160,0,fill='green', font="Times 20 italic bold" ,
                        text="listenning on port {} .... Not Connected".format(PORT), anchor="nw")
reading = canvas.create_text(475,290 ,fill='blue', font="Times 60 italic bold" ,text="NULL")
history = canvas.create_text(10, 600, anchor="sw", fill='blue', font="Times 18 italic bold" ,text=HIST)

canvas.pack()
update_form()

#---------------------------------------------------------------------#



#__________________ second thread
def tcp_handle(shared_data , temp):
    shared_data[0] = 0      #not connected yet
    shared_data[1] = 0      #no new value yet

    print(colorama.Fore.YELLOW +"[TCP ]waiting for incoming connection")
    conn , client = sock.accept()
    print(colorama.Fore.YELLOW +"[TCP ] TCP connection received")
    shared_data[0] = 1      #connected


    while True:
        data = conn.recv(25)
        data = data.decode('utf-8')
        print(data)

        fp = open(temp, 'w+')
        fp.write(data)
        fp.close()

        shared_data[1] = 1              # we got a new value
        while shared_data[1] == 1:      # he didn't read new data yet
            pass                        # just wait
#---------------------------------------------------------------------#



if __name__ == '__main__':
    th = multiprocessing.Process(target=tcp_handle, args=[shared_data,temp])
    th.start()
    root.mainloop()
    print ("form closed ")
    th.terminate()
    th.join()

    sock.detach()
    sock.close()
    print("socket closed")
#---------------------------------------------------------------------#
