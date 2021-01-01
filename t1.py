import tkinter as tk
import tkinter.ttk as ttk
class menu:
    def __init__(self, master=None):
        # build ui
        
        menu_7 = tk.Menu(master)
        
        menu_7.add('command', label='command_1')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('command', label='command_2')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('command', label='command_3')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('command', label='command_4')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('separator')
        menu_7.add('radiobutton', label='radiobutton_1_2')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('radiobutton', label='radiobutton_3')
        #TODO: setup command_id_arg 'false' for menuitem.
        submenu_1 = tk.Menu(menu_7)
        menu_7.add(tk.CASCADE, menu=submenu_1, label='submenu_1')
        submenu_1.add('command', label='command_5')
        #TODO: setup command_id_arg 'false' for menuitem.
        submenu_1.add('command', label='command_6')
        #TODO: setup command_id_arg 'false' for menuitem.
        submenu_1.add('command', label='command_7')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('command', label='command_8')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('command', label='command_9')
        #TODO: setup command_id_arg 'false' for menuitem.
        menu_7.add('separator')
        menu_7.add('command', label='command_10')
        #TODO: setup command_id_arg 'false' for menuitem.

        # Main widget
        self.mainwindow = menu_7


    def run(self):
        self.mainwindow.mainloop()
class MyuiApp:
    def __init__(self, master=None):
        # build ui
        frame_6 = ttk.Frame(master)

        button_9 = ttk.Button(frame_6)
        button_9.config(text='page2')
        button_9.configure(command=self.topage2)
        button_9.pack(side='top')
        label_2 = ttk.Label(frame_6)
        label_2.config(text='label_2')
        label_2.pack(side='top')
        label_3 = ttk.Label(frame_6)
        label_3.config(text='label_3')
        label_3.pack(side='top')
        label_4 = ttk.Label(frame_6)
        label_4.config(text='label_4')
        label_4.pack(side='top')
        radiobutton_2 = ttk.Radiobutton(frame_6)
        radiobutton_2.config(text='radiobutton_2')
        radiobutton_2.pack(side='top')
        menubutton_3 = ttk.Menubutton(frame_6)
        menubutton_3.config(text='menubutton_3')
        menubutton_3.pack(side='top')
        frame_6.config(height='200', width='200')
        frame_6.pack(side='top')

     

        # Main widget
        self.mainwindow = frame_6
        self.window = self.mainwindow
        self.master = master

    def run(self):
        self.mainwindow.mainloop()
    def topage2(self):
        self.master.swap_to(page2)

class page2:
    def __init__(self, master=None):
        # build ui
        frame_7 = ttk.Frame(master)
        button_10 = ttk.Button(frame_7)
        button_10.config(compound='top', state='normal', text='back')
        button_10.configure(command=self.back)
        button_10.pack(side='top')
        button_11 = ttk.Button(frame_7)
        button_11.config(text='button_11')
        button_11.pack(side='top')
        button_12 = ttk.Button(frame_7)
        button_12.config(text='button_12')
        button_12.pack(side='top')
        frame_7.config(height='200', width='200')
        frame_7.pack(side='top')

        # Main widget
        self.window = frame_7

    

        self.master = master
    def run(self):
        self.mainwindow.mainloop()
    def back(self):
        self.master.swap_to(MyuiApp)

class myapp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.frame = 0
        self.swap_to(MyuiApp)
    def swap_to(self, page_class):
        newframe = page_class(self)
        if self.frame != 0:
            self.frame.window.destroy()
        self.frame = newframe 
        self.frame.window.pack()



if __name__ == '__main__':
    root = myapp()
    a = menu(root)
    root.config(menu=a.mainwindow)
    a.run()


