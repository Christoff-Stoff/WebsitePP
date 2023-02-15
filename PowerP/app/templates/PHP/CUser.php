<?php
$servername = "127.0.0.1";
$username = "root";
$password = "PowerPartners1";
$dbname = "SystemSchema";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get the user information from the form
$username = $_POST["username"];
$email = $_POST["email"];
$password = $_POST["password"];


// Insert the user into the database
$sql = "INSERT INTO users (username, email, password)
VALUES ('$username', '$email', '$password')";

if ($conn->query($sql) === TRUE) {
    echo "New record created successfully";
} else {
    echo "Error: " . $sql . "<br>" . $conn->error;
}

$conn->close();
?>
