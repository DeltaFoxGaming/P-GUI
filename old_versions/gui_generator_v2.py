import tkinter as tk
from tkinter import filedialog, messagebox
import os

# [AI-NOTE] Main Application Class
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Generator")
        self.root.geometry("600x700")
        
        # [AI-NOTE] Application State
        self.commands = [] # List of strings
        self.filepath = None # Current file path if editing
        
        self.show_start_screen()

    def show_start_screen(self):
        # [AI-NOTE] Clears window and shows start screen
        for widget in self.root.winfo_children():
            widget.destroy()
            
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        
        tk.Label(frame, text="Command Generator", font=("Arial", 20, "bold")).pack(pady=20)
        
        tk.Button(frame, text="New File", command=self.new_file, width=20, height=2).pack(pady=10)
        tk.Button(frame, text="Edit File", command=self.edit_file, width=20, height=2).pack(pady=10)

    def new_file(self):
        self.commands = []
        self.filepath = None
        self.show_editor()

    def edit_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, "r") as f:
                    content = f.read().strip()
                    if content:
                        self.commands = content.split("\n")
                    else:
                        self.commands = []
                self.filepath = path
                self.show_editor()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def show_editor(self):
        # [AI-NOTE] Main Editor Interface
        for widget in self.root.winfo_children():
            widget.destroy()

        # [AI-NOTE] Top Section: Command Buttons
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        # Helper to create button rows
        def create_cmd_row(parent, btn_text, label_text, cmd_func, needs_input=False, input_label=None):
            row = tk.Frame(parent)
            row.pack(fill=tk.X, pady=2)
            
            btn = tk.Button(row, text=btn_text, command=lambda: cmd_func(entry) if needs_input else cmd_func(), width=15)
            btn.pack(side=tk.LEFT)
            
            entry = None
            if needs_input:
                tk.Label(row, text=input_label or "Value:").pack(side=tk.LEFT, padx=5)
                entry = tk.Entry(row, width=15)
                entry.pack(side=tk.LEFT, padx=5)
            
            tk.Label(row, text=label_text, fg="gray").pack(side=tk.LEFT, padx=10)
            return entry

        # 1. HIDE_ALL
        create_cmd_row(top_frame, "HIDE_ALL", "hides all images/frames", 
                      lambda: self.add_command("HIDE_ALL"))

        # 2. SHOW [int]
        create_cmd_row(top_frame, "SHOW", "shows the image/frame entered", 
                      lambda e: self.add_command("SHOW", e), True, "Integer:")

        # 3. OPEN_URL [url]
        create_cmd_row(top_frame, "OPEN_URL", "makes Paicom open the specified URL", 
                      lambda e: self.add_command("OPEN_URL", e), True, "URL:")

        # 4. WAIT [int]
        create_cmd_row(top_frame, "WAIT", "wait time in ms before next command", 
                      lambda e: self.add_command("WAIT", e), True, "Integer:")

        # 5. HIDE [int]
        create_cmd_row(top_frame, "HIDE", "hide the specified image/frame", 
                      lambda e: self.add_command("HIDE", e), True, "Integer:")

        # [AI-NOTE] Middle Section: Draggable List
        list_frame_container = tk.Frame(self.root)
        list_frame_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Label(list_frame_container, text="Command List (Drag to reorder):").pack(anchor=tk.W)
        
        self.cmd_list_widget = DraggableListFrame(list_frame_container, self.commands, self.on_list_update)
        self.cmd_list_widget.pack(fill=tk.BOTH, expand=True)

        # [AI-NOTE] Bottom Section: Actions
        bottom_frame = tk.Frame(self.root, pady=10)
        bottom_frame.pack(fill=tk.X)
        
        tk.Button(bottom_frame, text="Done (Save)", command=self.save_file, bg="#dddddd", height=2).pack(side=tk.RIGHT, padx=20)
        tk.Button(bottom_frame, text="Back to Menu", command=self.show_start_screen).pack(side=tk.LEFT, padx=20)

    def add_command(self, cmd_type, entry_widget=None):
        val = ""
        if entry_widget:
            val = entry_widget.get().strip()
            
            # Validation
            if cmd_type in ["SHOW", "WAIT", "HIDE"]:
                if not val.isdigit():
                    messagebox.showerror("Error", f"{cmd_type} requires an integer value.")
                    return
            elif cmd_type == "OPEN_URL":
                if not val:
                    messagebox.showerror("Error", "URL cannot be empty.")
                    return

            cmd_str = f"{cmd_type} {val}"
            entry_widget.delete(0, tk.END)
        else:
            cmd_str = cmd_type

        self.commands.append(cmd_str)
        self.cmd_list_widget.refresh(self.commands)

    def on_list_update(self, new_commands):
        self.commands = new_commands

    def save_file(self):
        if not self.commands:
            messagebox.showwarning("Warning", "Command list is empty.")
            return

        # Always ask for save location/name as per "Done button to save and name the file"
        initial_dir = os.getcwd()
        path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            title="Save Text File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        
        if path:
            try:
                with open(path, "w") as f:
                    f.write("\n".join(self.commands))
                messagebox.showinfo("Success", "File saved successfully!")
                self.filepath = path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")


# [AI-NOTE] Custom Widget for Drag-and-Drop List
class DraggableListFrame(tk.Frame):
    def __init__(self, parent, items, update_callback):
        super().__init__(parent)
        self.items = items
        self.update_callback = update_callback
        
        # Scrollable Canvas Setup
        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.refresh(self.items)

    def refresh(self, items):
        self.items = items
        # Clear existing
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Rebuild
        for idx, item in enumerate(self.items):
            self.create_row(idx, item)
            
        self.update_callback(self.items)

    def create_row(self, idx, text):
        row = tk.Frame(self.scrollable_frame, bd=1, relief=tk.RAISED)
        row.pack(fill=tk.X, pady=1, anchor="n")
        
        # Drag Handle / Label
        lbl = tk.Label(row, text=f" {text}", anchor="w", cursor="hand2", width=40, bg="#f0f0f0")
        lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Drag Events
        lbl.bind("<Button-1>", lambda e, i=idx: self.start_drag(e, i))
        lbl.bind("<B1-Motion>", self.do_drag)
        lbl.bind("<ButtonRelease-1>", self.stop_drag)

        # Delete Button
        del_btn = tk.Button(row, text="Delete", fg="red", command=lambda i=idx: self.delete_item(i))
        del_btn.pack(side=tk.RIGHT)

    def delete_item(self, index):
        if 0 <= index < len(self.items):
            self.items.pop(index)
            self.refresh(self.items)

    # -- Drag and Drop Logic --
    def start_drag(self, event, index):
        self.drag_start_index = index
        self.drag_data = {"y": event.y_root, "item": self.items[index]}
        
        # Visual feedback could be added here (e.g., change color)
        # For simplicity, we just track the index.

    def do_drag(self, event):
        # We could implement a floating window here for visual feedback
        pass

    def stop_drag(self, event):
        # Calculate new index based on y-coordinate release
        # This is a bit tricky with scrollable frames.
        # Simplified: find the row widget under the mouse pointer
        
        x, y = self.canvas.winfo_pointerxy()
        widget_under_mouse = self.canvas.winfo_containing(x, y)
        
        if not widget_under_mouse:
            return

        # Find which row this widget belongs to
        target_index = -1
        
        # Iterate through rows to check geometry
        # This is a robust way to find where we dropped it
        rows = self.scrollable_frame.winfo_children()
        
        # Check if we dropped on a label or the row frame itself
        for i, row in enumerate(rows):
            # Check if mouse is within this row's vertical bounds
            row_y_root = row.winfo_rooty()
            row_h = row.winfo_height()
            
            if row_y_root <= y <= row_y_root + row_h:
                target_index = i
                break
        
        if target_index != -1 and target_index != self.drag_start_index:
            # Move item
            item = self.items.pop(self.drag_start_index)
            self.items.insert(target_index, item)
            self.refresh(self.items)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
