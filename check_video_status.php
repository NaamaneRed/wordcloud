<?php
// Path to the video-file
$videoPath = 'Replace_with_path_to_your_created_video_file';

// Standard answer
$response = ['video_ready' => false];

if (file_exists($videoPath)) {
    // File exists, video is ready
    $response['video_ready'] = true;
}

// Return JSON response
echo json_encode($response);
?>
