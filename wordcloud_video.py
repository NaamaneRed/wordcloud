from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mysql.connector
import subprocess
import os
import shutil
import stat

# Paths for frames and video
output_dir = 'Replace_With_Path_To_Your_Frames'
output_video = 'Replace_With_Path_To_Your_Videos'

def cleanup():
    def on_error(func, path, exc_info):
        print(f"Error by deleting: {path}. Try again with admin-rights.")
        # Remove read-only 
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Deleting frames-folder
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir, onexc=on_error)
            print(f"Existing frames-folder '{output_dir}' got deleted.")
        except Exception as e:
            print(f"Error by deleting the existing frames-folder: {e}")

    # Deleting video-file
    if os.path.exists(output_video):
        try:
            os.remove(output_video)
            print(f"Existing video-file '{output_video}' got deleted.")
        except Exception as e:
            print(f"Error by deleting the existing video-file: {e}")

    # Creating new frames-folder
    os.makedirs(output_dir, exist_ok=True)
    print(f"New frames-folder '{output_dir}' is created.")

# Function frequencies of DB
def retrieve_word_frequencies():
    try:
        # Connection to DB
        connection = mysql.connector.connect(
            host="Replace_with_your_hostname_Or_localhost",
            user="Replace_with_username_such_as_root",  
            password="",  
            database="Replace_With_Database_Name",
        )
        cursor = connection.cursor()
        cursor.execute("SELECT eingabe, COUNT(*) AS frequency FROM [Replace_with_table_of_your_words] GROUP BY eingabe")
        result = cursor.fetchall()

        # Closing the connection
        cursor.close()
        connection.close()

        # Return the entries as a dictionary {word: frequency}
        return {row[0]: row[1] for row in result}
    except mysql.connector.Error as err:
        print(f"Error by connecting to the database: {err}")
        return {}

# Retrieve frequencies from the "answer" table
word_frequencies = retrieve_word_frequencies()
if not word_frequencies:
    print("No data or frequencies available from table [Replace_with_table_of_your_words]. The program will end.")
    exit()

print(f"Word frequencies from the table 'answer': {word_frequencies}")

# Frame generation based on frequencies
def generate_frames():
    # Generate the wordcloud based on the frequencies
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        collocations=False,
        normalize_plurals=False,
        max_font_size=100,  # Font size max for common words
        min_font_size=10,  # Normal font size for rare words
        relative_scaling=0.5  # Frequency has a stronger influence on font size
    ).generate_from_frequencies(word_frequencies)

    fixed_layout = wc.layout_  # Save layout for fixed positions

    for frame_idx in range(1, len(fixed_layout) + 1):
        wc.layout_ = fixed_layout[:frame_idx]  # Show words step by step
        wc_image = wc.to_image()
        frame_path = os.path.join(output_dir, f"frame_{frame_idx:04d}.png").replace("\\", "/")
        wc_image.save(frame_path)

    # Creation of extra frame with all words
    final_frame_path = os.path.join(output_dir, f"frame_{len(fixed_layout) + 1:04d}.png").replace("\\", "/")
    wc.layout_ = fixed_layout  # Shows the complete word cloud
    wc_image = wc.to_image()
    wc_image.save(final_frame_path)

    print(f"Frames were generated and saved in: {output_dir}")

# Video creation with FFmpeg
def create_video():
    absolute_output_dir = os.path.abspath(output_dir).replace("\\", "/")
    print(f"Frames-path: {absolute_output_dir}")

    # Calculation of duration per frame
    frame_count = len([f for f in os.listdir(output_dir) if f.endswith(".png")])
    if frame_count > 60:
        frame_duration = 60 / frame_count  # Maximum 60 seconds video
    else:
        frame_duration = 1  # 1 sec per frame

    
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-framerate', f"{1 / frame_duration}",  # Calculate frame rate from frame duration
        '-i', os.path.join(absolute_output_dir, 'frame_%04d.png'),
        '-vf', 'setpts=PTS',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        output_video
    ]    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Video created successfully: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")

# Main program
if __name__ == '__main__':
    
    cleanup()
    generate_frames()
    create_video()
