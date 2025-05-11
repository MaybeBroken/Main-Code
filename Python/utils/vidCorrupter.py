import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import random
import numpy as np

def loop_video_segment(video_path, start_frame, segment_length, loop_count, output_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video file.")
        return

    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Set up the video writer
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Ensure the start frame and segment length are within bounds
    if start_frame >= total_frames:
        print("Error: Start frame exceeds total frames in the video.")
        cap.release()
        out.release()
        return
    if start_frame + segment_length > total_frames:
        print("Error: Segment length exceeds total frames from the start frame.")
        cap.release()
        out.release()
        return

    # Move to the start frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # Read the segment frames
    frames = []
    for _ in range(segment_length):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    # Loop the segment frames
    for _ in range(loop_count):
        for frame in frames:
            out.write(frame)

    # Release resources
    cap.release()
    out.release()

def append_blank_frames(video_path, output_path):
    
    # Get video properties for appending blank frames
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        messagebox.showerror("Error", "Unable to open video file for appending blank frames.")
        return
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    # Calculate the number of blank frames to add (2 GB of blank frames)
    frame_size = width * height * 3  # 3 bytes per pixel (RGB)
    total_blank_frames = (2 * 1024**3) // frame_size

    # Open the video file for appending
    cap = cv2.VideoCapture(output_path)
    if not cap.isOpened():
        print("Error: Unable to open output video file.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

    # Append blank frames
    blank_frame = np.zeros((height, width, 3), dtype=np.uint8)
    for _ in range(total_blank_frames):
        out.write(blank_frame)

    # Release resources
    cap.release()
    out.release()

def browse_file(entry_widget):
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

def browse_output(entry_widget):
    file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Files", "*.mp4")])
    if file_path:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_path)

def modify_data(video_path, output_path):
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Unable to open video file.")
            return

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        # Set up the video writer
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        # Process each frame
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Randomly decide whether to corrupt the frame
            if random.random() < 0.1:  # 10% chance to corrupt a frame
                # Apply random noise to the frame
                noise = np.random.randint(0, 256, frame.shape, dtype=np.uint8)
                frame = cv2.addWeighted(frame, 0.5, noise, 0.5, 0)

            out.write(frame)

        # Release resources
        cap.release()
        out.release()


def execute_loop():
    video_path = video_path_entry.get()
    output_path = output_path_entry.get()
    try:
        start_frame = int(start_frame_entry.get())
        segment_length = int(segment_length_entry.get())
        loop_count = int(loop_count_entry.get())
    except ValueError:
        messagebox.showerror("Input Error", "Start Frame, Segment Length, and Loop Count must be integers.")
        return

    if not video_path or not output_path:
        messagebox.showerror("Input Error", "Please select both input and output file paths.")
        return

    loop_video_segment(video_path, start_frame, segment_length, loop_count, output_path)
    modify_data(output_path, output_path)
    messagebox.showinfo("Success", f"Video segment destroyed and saved to {output_path}")

# Create the main Tkinter window
root = tk.Tk()
root.title("Video Destroyer")

# Input video file
tk.Label(root, text="Input Video File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
video_path_entry = tk.Entry(root, width=50)
video_path_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_file(video_path_entry)).grid(row=0, column=2, padx=5, pady=5)

# Start frame
tk.Label(root, text="Start Frame:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
start_frame_entry = tk.Entry(root, width=20)
start_frame_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

# Segment length
tk.Label(root, text="Segment Length:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
segment_length_entry = tk.Entry(root, width=20)
segment_length_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

# Loop count
tk.Label(root, text="Loop Count:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
loop_count_entry = tk.Entry(root, width=20)
loop_count_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

# Output video file
tk.Label(root, text="Output Video File:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
output_path_entry = tk.Entry(root, width=50)
output_path_entry.grid(row=4, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=lambda: browse_output(output_path_entry)).grid(row=4, column=2, padx=5, pady=5)

# Execute button
tk.Button(root, text="Destroy Video Segment", command=execute_loop).grid(row=5, column=0, columnspan=3, pady=10)

# Append button
tk.Button(root, text="Append Blank Frames", command=lambda: append_blank_frames(video_path_entry.get(), output_path_entry.get())).grid(row=6, column=0, columnspan=3, pady=10)

# Run the Tkinter event loop
root.mainloop()