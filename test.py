import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def create_chart():
    # Sample data
    categories = ['A', 'B', 'C', 'D']
    values = [4, 7, 1, 8]

    # Create a figure and a single set of axes
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)

    # Create a bar chart
    ax.bar(categories, values)

    # Add titles and labels
    ax.set_title('Simple Bar Chart')
    ax.set_xlabel('Categories')
    ax.set_ylabel('Values')

    # Embed the chart in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Set up the main application window
root = tk.Tk()
root.title("Bar Chart Integration")

# Create and show the chart

create_chart()

def on_close():
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
# Start the Tkinter event loop
root.mainloop()
