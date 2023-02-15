<?php
// Code for the real-time-data

// Connect to the database
$conn = new mysqli("127.0.0.1", "root", "PowerPartners1", "wp_database");

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get data from the real_time_data table
$sql = "SELECT * FROM real_time_data";
// Delete data in a table
//$sql = "DELETE FROM real_time_data";
$result = $conn->query($sql);

// Create an array to store the data
$data = array();

// Loop through the result and store the data in the array
if ($result->num_rows > 0) {
    while ($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

// Encode the data as JSON and send it to the plot.html page
echo json_encode($data);

// Close the connection
$conn->close();
?>

