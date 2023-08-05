#!/usr/bin/env python3
# File: UI_utils.py
# Description - 
#
# History
# v 0.1 8/5/23 YF - Inception
import tkinter as tk
import tkinter.ttk as ttk

class UIPage:
    def __init__(self, tup_Name_Descrip):
        # assert somehow that tup_Name_Descrip is list of string pairs
        self.tup_Name_Descrip = tup_Name_Descrip
        self.selectedActions = () # empty tuple

        self.root = tk.Tk()
        self.root.title("Choose action")
        # Create a variable to hold the checkbox state
        
        self.cb_TakeData = tk.BooleanVar()
        self.cb_AnalyzeData = tk.BooleanVar()  
        self.lb_ScriptToRun = tk.Listbox( self.root )
        self.buildList()
       


    def buildList(self):
        lb = self.lb_ScriptToRun
        n=0
        # Populate the listbox
        for (s,d) in self.tup_Name_Descrip:
            lb.insert(n,s)
            n += 1
       
        lb.bind("<<ListboxSelect>>", self.on_select)

    def cb_clicked(self):
        """
        checkbox handler
        """

        txtA = ""
        txtB = ""

        if self.cb_TakeData.get():
            txtA= "TakeData"

        if self.cb_AnalyzeData.get():
            txtB ="Analyze"
            
        
        if txtA and txtB:
            txtA = txtA + " & "

        self.result_label.config(text=f"{txtA} {txtB}")
        self.selectedActions = self.cb_TakeData.get(), self.cb_AnalyzeData.get()
                                 

    def on_select(self,event):
        """
        listbox handler
        """

        lb = self.lb_ScriptToRun
        lbl = self.selection_label
        n = lb.curselection()
        descrip_text = self.tup_Name_Descrip[n[0]][1]
        lbl.config(text=f"Selected: {descrip_text}")
        self.selectedText = self.tup_Name_Descrip[ n[0] ][0]
    
    def show(self):
        # Create the main window
        
        # unpack to allow less typing
        td = self.cb_TakeData
        ad = self.cb_AnalyzeData
        root = self.root
        lb = self.lb_ScriptToRun

        r = 0

        # Create a checkbox
        checkbox1 = ttk.Checkbutton(root, 
            text="Take Data", variable=td, command=self.cb_clicked, padding=(5,5) )
        checkbox2 = ttk.Checkbutton(root, 
            text="Analyze Data", variable=ad, command=self.cb_clicked, padding = (5,5))
        
       # Grid layout for checkboxes
        checkbox1.grid(row=r, column=0)
        checkbox2.grid(row=r, column=1)
        r += 1
                
        # Create a label 
        lbl1 = tk.Label(root, text="Choose what to run:")
        lbl1.grid(row=r); r += 1



        # Create a label to display the selection
        self.selection_label = tk.Label(root, text="<Description>", wraplength=200)

        lb.grid(row=r, column=0, columnspan=2, padx=20); r += 1        
        self.selection_label.grid(row=r, columnspan=2); r += 1


        # Create a label to display the result
        self.result_label = ttk.Label(root, text="")
        self.result_label.grid(row=r, columnspan=2); r +=1

        # Start the GUI event loop
        root.mainloop()

# Entry point of the script
if __name__ == "__main__":
    lot = []
    lot.append( ("ABC", "A very very long and windy description for ABC"))
    lot.append( ("DEF", "Descrip _ DEF" ))
    
    ui = UIPage( lot )
    ui.show()