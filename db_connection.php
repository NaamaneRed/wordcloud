<?php
// Verbindung zu lokalen MySQL-DB
$servername = "Replace_with_Servername";
$username = "";
$password = ""; 
$dbname = "";

$conn = new mysqli($servername, $username, $password, $dbname);

// Verbindung prüfen
if ($conn->connect_error) {
    die("Verbindung fehlgeschlagen: " . $conn->connect_error);
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);

    if (!isset($data['eingabe']) || empty($data['eingabe'])) {
        echo json_encode(["success" => false, "message" => "Ungültige Eingabe."]);
        exit();
    }

    $userInput = $data['eingabe']; // Originale Eingabe ohne Escaping

    // Prepared Statement verwenden
    $stmt = $conn->prepare("SELECT * FROM whitelist WHERE 
        LOWER(tier) = LOWER(?) OR 
        LOWER(person) = LOWER(?) OR 
        LOWER(beruehmte_orte) = LOWER(?) OR 
        LOWER(essen) = LOWER(?) OR 
        LOWER(dinge) = LOWER(?)");

    if ($stmt) {
        // Eingabe binden
        $stmt->bind_param("sssss", $userInput, $userInput, $userInput, $userInput, $userInput);
        
        // Abfrage ausführen
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $datum = date('Y-m-d H:i:s');
            $insertSql = "INSERT INTO [Replace_with_table_of_your_words] (eingabe, datum) VALUES (?, ?)";
            
            $insertStmt = $conn->prepare($insertSql);
            if ($insertStmt) {
                $insertStmt->bind_param("ss", $userInput, $datum);
                if ($insertStmt->execute()) {
                    $updateSql = "UPDATE [Replace_with_table_of_your_words] SET eingabe = eingabe";
                    $conn->query($updateSql);
                    // wordcloud_video.py ausführen für Video-Erstellung
                    $pythonScriptPath = 'Replace_with_path_to_your_video';
                    $command = escapeshellcmd("python3 $pythonScriptPath");
                    $output = [];
                    $retval = null;
                    exec($command, $output, $retval);

                    if ($retval === 0) {
                        echo json_encode(["success" => true, "message" => "Eingabe erfolgreich gespeichert und Video erstellt!"]);
                    } else {
                        echo json_encode(["success" => false, "message" => "Eingabe gespeichert, aber Video konnte nicht erstellt werden."]);
                    }
                } else {
                    echo json_encode(["success" => false, "message" => "Fehler beim Einfügen in die Datenbank."]);
                }
                $insertStmt->close();
            }
        } else {
            echo json_encode(["success" => false, "message" => "Eingabe nicht in der Whitelist."]);
        }
        $stmt->close();
    } else {
        echo json_encode(["success" => false, "message" => "Datenbankfehler beim Erstellen des Statements."]);
    }
}

$conn->close();
?>
