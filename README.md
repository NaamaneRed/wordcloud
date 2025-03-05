This project generates a video which shows a wordcloud. It comes with a input hmtl formular and two php APIs, which manage the interaction between the scripts. 
You can use the input html form to enter words which will be saved in your table (in a database). The words from the table are used by the wordcloud_video.py script to generate a wordcloud.
inappropriate entries can be prevented by using a table named whitelist, which only contains legitimate entries, you need to enter these words in the table whitelist beforehand. 
Legitimate entries should be stored in a table named antworten. Replace the paths in the scripts with your paths.
The words appear one after the other and alphabetically. Except of the most frequent words, they appear in order of most frequency. The words will also have a random color.
The input html form was left in a neutral design so that individual adjustments can be made. All of the scripts should be stored in the same directory/path.

Requirements:

Two tables are required, ideally stored in a MySQL database. Once the table 'whitelist' and the table 'antworten'.
FFmpeg 6.1.1 must be installed previously.
PHP 7.2.5 or higher
MySQL 5.7.33 or higher
Python 3.13.0 
