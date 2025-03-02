<?php
// Pfad zur Videodatei
$videoPath = 'C:/xampp/htdocs/use_case4_Wortwolke/wordcloud_video.mp4';

// Standardantwort
$response = ['video_ready' => false];

if (file_exists($videoPath)) {
    // Datei existiert, Video ist bereit
    $response['video_ready'] = true;
}

// JSON-Antwort zurückgeben
echo json_encode($response);
?>
