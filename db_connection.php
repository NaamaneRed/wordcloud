<?php
// Connection to the MySQL-DB
$servername = "Replace_with_your_servername";
$username = "Replace_with_your_username";
$password = ""; 
$dbname = "Replace_with_your_DBname";

$conn = new mysqli($servername, $username, $password, $dbname);

// Checking connection
if ($conn->connect_error) {
    die("Connection error: " . $conn->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);

    if (!isset($data['eingabe']) || empty($data['eingabe'])) {
        echo json_encode(["success" => false, "message" => "Invalid input."]);
        exit();
    }

    $userInput = $data['eingabe']; // Original input without escaping

    // Prepared Statement
    $stmt = $conn->prepare("SELECT * FROM whitelist WHERE 
        LOWER(Name_of_the_column) = LOWER(?) OR 
        LOWER(Name_of_the_column) = LOWER(?) OR 
        LOWER(Name_of_the_column) = LOWER(?) OR 
        LOWER(Name_of_the_column) = LOWER(?) OR 
        LOWER(Name_of_the_column) = LOWER(?)");

    if ($stmt) {
        // Bind input
        $stmt->bind_param("sssss", $userInput, $userInput, $userInput, $userInput, $userInput);
        
        // Execute query
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $datum = date('Y-m-d H:i:s');
            $insertSql = "INSERT INTO antworten (eingabe, datum) VALUES (?, ?)";
            
            $insertStmt = $conn->prepare($insertSql);
            if ($insertStmt) {
                $insertStmt->bind_param("ss", $userInput, $datum);
                if ($insertStmt->execute()) {
                    $updateSql = "UPDATE antworten SET eingabe = eingabe";
                    $conn->query($updateSql);
                    // Run wordcloud_video.py for video creation
                    $pythonScriptPath = 'Path_to_the_wordcloud_video.py_script';
                    $command = escapeshellcmd("python3 $pythonScriptPath");
                    $output = [];
                    $retval = null;
                    exec($command, $output, $retval);

                    if ($retval === 0) {
                        echo json_encode(["success" => true, "message" => "Entry saved successfully and video created!"]);
                    } else {
                        echo json_encode(["success" => false, "message" => "Input saved but video could not be created."]);
                    }
                } else {
                    echo json_encode(["success" => false, "message" => "Error inserting into database."]);
                }
                $insertStmt->close();
            }
        } else {
            echo json_encode(["success" => false, "message" => "Input not in the whitelist."]);
        }
        $stmt->close();
    } else {
        echo json_encode(["success" => false, "message" => "Database error while creating the statement."]);
    }
}

$conn->close();
?>
