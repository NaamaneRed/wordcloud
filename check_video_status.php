<?php
// Pfad zur Videodatei
$videoPath = 'Replace_with_Path_to_your_Video';

// Standardantwort
$response = ['video_ready' => false];

if (file_exists($videoPath)) {
    // Datei existiert, Video ist bereit
    $response['video_ready'] = true;
}

// JSON-Antwort zurückgeben
echo json_encode($response);
?>
