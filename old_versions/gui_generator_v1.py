import tkinter as tk
from tkinter import filedialog, messagebox

# [AI-NOTE] This class handles the main GUI logic for generating commands.
# [AI-NOTE] Start of class definition.
class CommandGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Command Generator")
        
        # [AI-NOTE] Stores the list of generated commands to be written to file.
        self.commands = []
        
        self.create_widgets()

    def create_widgets(self):
        # [AI-NOTE] Creates the input area for HIDE_ALL button.
        self.hide_btn = tk.Button(self.root, text="Add HIDE_ALL", command=self.add_hide_all)
        self.hide_btn.pack(pady=5)
        
        # [AI-NOTE] Creates input area for SHOW command. Includes entry for integer and button.
        self.show_frame = tk.Frame(self.root)
        self.show_frame.pack(pady=5)
        tk.Label(self.show_frame, text="Integer:").pack(side=tk.LEFT)
        self.show_entry = tk.Entry(self.show_frame, width=10)
        self.show_entry.pack(side=tk.LEFT, padx=5)
        self.show_btn = tk.Button(self.show_frame, text="Add SHOW", command=self.add_show)
        self.show_btn.pack(side=tk.LEFT, padx=5)
        
        # [AI-NOTE] Creates input area for OPEN_URL command. Includes entry for URL and button.
        self.url_frame = tk.Frame(self.root)
        self.url_frame.pack(pady=5)
        tk.Label(self.url_frame, text="URL:").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(self.url_frame, width=30)
        self.url_entry.pack(side=tk.LEFT, padx=5)
        self.url_btn = tk.Button(self.url_frame, text="Add OPEN_URL", command=self.add_url)
        self.url_btn.pack(side=tk.LEFT, padx=5)
        
        # [AI-NOTE] Text area to display current list of commands. Used for preview.
        self.output_text = tk.Text(self.root, height=10, width=50)
        self.output_text.pack(pady=10)
        
        # [AI-NOTE] Frame for bottom action buttons (Clear, Save).
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(pady=5)

        # [AI-NOTE] Button to clear the current list.
        self.clear_btn = tk.Button(self.bottom_frame, text="Clear List", command=self.clear_list)
        self.clear_btn.pack(side=tk.LEFT, padx=10)

        # [AI-NOTE] Button to save the commands to a file.
        self.save_btn = tk.Button(self.bottom_frame, text="Save to File", command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=10)

    def add_hide_all(self):
        # [AI-NOTE] Adds HIDE_ALL command to list and updates display.
        self.commands.append("HIDE_ALL")
        self.update_display()

    def add_show(self):
        # [AI-NOTE] Validates integer input and adds SHOW command if valid.
        val = self.show_entry.get()
        if val.isdigit():
            self.commands.append(f"SHOW {val}")
            self.update_display()
            self.show_entry.delete(0, tk.END)
        else:
            # [AI-NOTE] Error handling for non-integer input. Shows popup.
            messagebox.showerror("Error", "Please enter a valid integer for SHOW.")

    def add_url(self):
        # [AI-NOTE] Adds OPEN_URL command. Checks if empty.
        url = self.url_entry.get()
        if url.strip():
            self.commands.append(f"OPEN_URL {url}")
            self.update_display()
            self.url_entry.delete(0, tk.END)
        else:
            # [AI-NOTE] Error handling for empty URL.
            messagebox.showerror("Error", "Please enter a URL.")

    def clear_list(self):
        # [AI-NOTE] Clears the internal command list and the display.
        self.commands = []
        self.update_display()

    def update_display(self):
        # [AI-NOTE] Refreshes the text area with current commands joined by newlines.
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "\n".join(self.commands))

    def save_file(self):
        # [AI-NOTE] Opens file dialog to save commands to a text file.
        if not self.commands:
            messagebox.showwarning("Warning", "No commands to save.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            try:
                with open(filepath, "w") as f:
                    f.write("\n".join(self.commands))
                messagebox.showinfo("Success", "File saved successfully!")
            except Exception as e:
                # [AI-NOTE] Error handling for file write issues.
                messagebox.showerror("Error", f"Failed to save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    # [AI-NOTE] Setting geometry can be helpful but optional.
    # root.geometry("400x500") 
    app = CommandGenerator(root)
    root.mainloop()
