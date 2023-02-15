<?php
// Database server info
$servername = "127.0.0.1";
$username = "root";
$password = "PowerPartners1";
$dbname = "SystemSchema";

//Waits for the user to select a date
$selected_date = $_POST["selected-date"];
// Create connection to Database server
$conn = mysqli_connect($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}


// Filter the data for the date supplied by the user
$sql = "SELECT *
FROM DailySummary
WHERE MONTH(date) = Month('$selected_date')";
$result = $conn->query($sql);

// Create an array to store the data
$data = array();


// Loop through the result and store the data in the array
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

// Encode the data as JSON and send it to the .html page
echo json_encode($data);

// Close the connection
$conn->close();
?>




