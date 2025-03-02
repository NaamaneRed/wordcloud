from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mysql.connector
import subprocess
import os
import shutil
import stat

# Pfade für frames und Video
output_dir = 'Replace_With_Path_To_Your_Frames'
output_video = 'Replace_With_Path_To_Your_Videos'

def cleanup():
    def on_error(func, path, exc_info):
        print(f"Fehler beim Löschen: {path}. Erneuter Versuch mit Schreibrechten.")
        # Entfernung read-only 
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Frames-Ordner löschen
    if os.path.exists(output_dir):
        try:
            shutil.rmtree(output_dir, onexc=on_error)
            print(f"Bestehender Frames-Ordner '{output_dir}' wurde gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen des Frames-Ordners: {e}")

    # Video löschen
    if os.path.exists(output_video):
        try:
            os.remove(output_video)
            print(f"Bestehende Video-Datei '{output_video}' wurde gelöscht.")
        except Exception as e:
            print(f"Fehler beim Löschen der Video-Datei: {e}")

    # Frames-Ordner neu erstellen
    os.makedirs(output_dir, exist_ok=True)
    print(f"Neuer Frames-Ordner '{output_dir}' wurde erstellt.")

# Funktion Häufigkeiten aus DB
def retrieve_word_frequencies():
    try:
        # Verbindung DB
        connection = mysql.connector.connect(
            host="Replace_with_your_hostname_Or_localhost",
            user="Replace_with_username_such_as_root",  
            password="",  
            database="Replace_With_Database_Name",
        )
        cursor = connection.cursor()
        cursor.execute("SELECT eingabe, COUNT(*) AS frequency FROM [Replace_with_table_of_your_words] GROUP BY eingabe")
        result = cursor.fetchall()

        # Schließen der Verbindung
        cursor.close()
        connection.close()

        # Rückgabe der Einträge als Dictionary {Wort: Häufigkeit}
        return {row[0]: row[1] for row in result}
    except mysql.connector.Error as err:
        print(f"Fehler bei der Verbindung zur Datenbank: {err}")
        return {}

# Häufigkeiten aus der Tabelle "antworten" abrufen
word_frequencies = retrieve_word_frequencies()
if not word_frequencies:
    print("Keine Daten oder Häufigkeiten aus der Tabelle [Replace_with_table_of_your_words] verfügbar. Das Programm wird beendet.")
    exit()

print(f"Wortfrequenzen aus der Tabelle 'antworten': {word_frequencies}")

# Frame-Generierung basierend auf Häufigkeiten
def generate_frames():
    # Erzeuge die Wordcloud basierend auf den Häufigkeiten
    wc = WordCloud(
        width=800,
        height=400,
        background_color="white",
        collocations=False,
        normalize_plurals=False,
        max_font_size=100,  # Schriftgröße max für häufige Wörter
        min_font_size=10,  # Normale Schriftgröße für seltene Wörter
        relative_scaling=0.5  # Häufigkeit hat stärkeren Einfluss auf Schriftgröße
    ).generate_from_frequencies(word_frequencies)

    fixed_layout = wc.layout_  # Speichere Layout für feste Positionen

    for frame_idx in range(1, len(fixed_layout) + 1):
        wc.layout_ = fixed_layout[:frame_idx]  # Wörter schrittweise anzeigen
        wc_image = wc.to_image()
        frame_path = os.path.join(output_dir, f"frame_{frame_idx:04d}.png").replace("\\", "/")
        wc_image.save(frame_path)

    # Erstellung extra Frame mit allen Wörtern
    final_frame_path = os.path.join(output_dir, f"frame_{len(fixed_layout) + 1:04d}.png").replace("\\", "/")
    wc.layout_ = fixed_layout  # Zeigt die vollständige Wordcloud
    wc_image = wc.to_image()
    wc_image.save(final_frame_path)

    print(f"Frames wurden generiert und gespeichert in: {output_dir}")

# Video-Erstellung mit FFmpeg
def create_video():
    absolute_output_dir = os.path.abspath(output_dir).replace("\\", "/")
    print(f"Frames-Pfad: {absolute_output_dir}")

    # Berechnung der Dauer pro Frame
    frame_count = len([f for f in os.listdir(output_dir) if f.endswith(".png")])
    if frame_count > 60:
        frame_duration = 60 / frame_count  # Maximal 60 Sekunden Video
    else:
        frame_duration = 1  # 1 Sec pro Frame

    
    ffmpeg_cmd = [
        'ffmpeg',
        '-y',
        '-framerate', f"{1 / frame_duration}",  # Berechne Framerate aus Frame-Dauer
        '-i', os.path.join(absolute_output_dir, 'frame_%04d.png'),
        '-vf', 'setpts=PTS',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        output_video
    ]    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Video erfolgreich erstellt: {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg-Fehler: {e}")

# Hauptprogramm
if __name__ == '__main__':
    
    cleanup()
    generate_frames()
    create_video()
