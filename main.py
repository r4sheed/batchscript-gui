import customtkinter as ctk
import subprocess
import threading
from tkinter import filedialog
import os
import time

class BatchScriptRunner(ctk.CTk):
    """
        A GUI application for running batch scripts.
    """

    def __init__(self):
        super().__init__()

        # Define window size variables
        app_width = 600
        app_height = 600

        # Configure window
        self.title("Batch Script Runner")
        self.geometry(f"{app_width}x{app_height}")  # Iinitial window size
        self.minsize(app_width, app_height)  # Min window size
        self.maxsize(app_width * 2, app_height * 1.5)  # Max window size
        self.configure(bg_color=("gray20", "black"))
        self.attributes('-alpha', 0.95)  # Make the window slightly transparent

        # Create GUI elements
        self.create_widgets()

        # Initialize variables
        self.background_thread = None
        self.stop_background = threading.Event()
        self.clear_output = False

    def create_widgets(self):
        # Header section
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=10)
        self.header_frame.pack(pady=10, padx=20, fill="x")

        self.header_label = ctk.CTkLabel(self.header_frame, text="Batch Script Runner",
                                        text_color="white", font=("Roboto Medium", 24))
        self.header_label.pack(side="left", padx=10)

        # Contact label
        self.contact_label = ctk.CTkLabel(self.header_frame, text="rasheed.",
                                        text_color="white", font=("Roboto Medium", 12))
        self.contact_label.pack(side="right", padx=10)

        # Script input label and text box
        self.script_label = ctk.CTkLabel(self, text="Enter Batch Script Path or Paste Code:",
                                         text_color="white", font=("Roboto Medium", 18), height=25)
        self.script_label.pack(pady=(20, 0))

        self.script_text = ctk.CTkTextbox(self, wrap="word", height=10)
        self.script_text.pack(pady=(5, 20), padx=20, fill="both", expand=True)

        # Load script button
        self.load_button = ctk.CTkButton(self, text="Load Script", command=self.load_script)
        self.load_button.pack(pady=10)

        # Run/Stop script button
        self.run_button = ctk.CTkButton(self, text="Run Script", command=self.toggle_script)
        self.run_button.pack(pady=10)

        # Switch for clearing output window
        self.clear_output_switch = ctk.CTkSwitch(self, text="Clear Output", command=self.toggle_clear_output)
        self.clear_output_switch.pack(pady=10)

        # Output label and text box
        self.output_label = ctk.CTkLabel(self, text="Output:",
                                         text_color="white", font=("Roboto Medium", 12), height=25)
        self.output_label.pack(pady=(10, 0))

        self.output_text = ctk.CTkTextbox(self, wrap="word", height=10, state="disabled")
        self.output_text.pack(pady=(5, 20), padx=20, fill="both", expand=True)

        # Label to display the status of the script
        self.script_status_label = ctk.CTkLabel(self, text="Script Status: Not Running",
                                                text_color="white", font=("Roboto Medium", 12))
        self.script_status_label.pack(pady=(10, 0))

        # Progress spinner
        self.spinner = ctk.CTkProgressBar(self, mode='indeterminate')

    def toggle_script(self):
        if self.background_thread and self.background_thread.is_alive():
            # Script is currently running, attempt to stop it
            self.stop_background.set()
            self.run_button.configure(text="Run Script")  # Change text back to "Run Script"
        else:
            # No script is currently running, prepare to start one
            script_content = self.script_text.get("1.0", "end").strip()
            if script_content:
                self.run_button.configure(text="Stop Script")
                self.run_button.configure(state="normal") # Enable the button to allow stopping the script

                self.script_status_label.configure(text="Script Status: Running")

                # Show the spinner
                self.spinner.pack(pady=10)
                self.spinner.start()

                # Clear previous output if needed
                if self.clear_output:
                    self.output_text.configure(state="normal")
                    self.output_text.delete("1.0", "end")
                    self.output_text.configure(state="disabled")

                # Start the background thread
                self.stop_background.clear()  # Clear the stop signal
                self.background_thread = threading.Thread(target=self.execute_script_continuously, args=(script_content,))
                self.background_thread.start()
            else:
                # If there's no script content, inform the user and do not change the button text
                self.output_text.configure(state="normal")
                self.output_text.insert("end", "No script content to execute.\n")
                self.output_text.configure(state="disabled")
                self.spinner.stop()  # Stop the spinner
                self.spinner.pack_forget()  # Hide the spinner

    def toggle_clear_output(self):
        self.clear_output = self.clear_output_switch.get()  # Get the current state of the switch
        
    def load_script(self):
        file_path = filedialog.askopenfilename(filetypes=[("Batch Files", ["*.bat"])])
        if file_path:
            with open(file_path, 'r') as file:
                script_content = file.read()
                self.script_text.delete(1.0, "end")
                self.script_text.insert("end", script_content)

    def execute_script_continuously(self, script_content):
        # Continuously execute the script until stop signal is received
        while not self.stop_background.is_set():
            try:
                # Create a temporary batch file
                temp_file = os.path.join(os.environ["TEMP"], "temp_script.bat")
                with open(temp_file, "w") as file:
                    file.write(script_content)
                
                # Execute the temporary batch file
                process = subprocess.Popen(f'cmd.exe /c "{temp_file}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Read the output of the process
                while True:
                    output = process.stdout.readline()
                    if output == b'' and process.poll() is not None:
                        break
                    if output:
                        self.output_text.configure(state="normal")
                        if self.clear_output:
                            self.output_text.delete("1.0", "end")  # Clear the output window each time
                        self.output_text.insert("end", output.strip().decode() + "\n")
                        self.output_text.configure(state="disabled")
                    if self.stop_background.is_set():
                        process.terminate()  # Terminate the process if stop signal is set
                        break

            except Exception as e:
                self.output_text.configure(state="normal")
                self.output_text.insert("end", str(e) + "\n")
                self.output_text.configure(state="disabled")
            
            finally:
                # Remove the temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            # Sleep for a short time before checking the stop signal again
            time.sleep(0.1)

        # Stop and hide the spinner after the script has been terminated
        self.spinner.stop()
        self.spinner.pack_forget()

        # If the loop breaks, indicate that the script has stopped
        self.output_text.configure(state="normal")
        self.output_text.insert("end", "Script execution stopped.\n")
        self.output_text.configure(state="disabled")
        self.run_button.configure(text="Run Script")
        self.script_status_label.configure(text="Script Status: Not Running")

if __name__ == "__main__":
    app = BatchScriptRunner()
    app.mainloop()
