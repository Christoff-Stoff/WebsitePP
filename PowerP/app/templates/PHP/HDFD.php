<?php
//HDFD --> Hourly Data For a Day

// Connect to the database
$conn = new mysqli("127.0.0.1", "root", "PowerPartners1", "SystemSchema");

// Check connection
if (!$conn) {
    die("Connection failed: " . mysqli_connect_error());
}

// Get the date parameter from the front-end
//$date = $_POST['date'];

// Prepare and execute the join query
$query = "SELECT 
  DATE(h.date) as day,
  SUM(h.generated_power) as generated_power,
  SUM(h.consumed_power) as consumed_power,
  SUM(h.exported_power) as exported_power,
  d.savings as savings
FROM HourlySummary h
JOIN DailySummary d ON DATE(h.date) = d.date
WHERE DATE(h.date) = '2001-01-21'
GROUP BY day";

$result = mysqli_query($conn, $query);

// Store the result in an array
$data = array();
while ($row = mysqli_fetch_assoc($result)) {
    $data[] = $row;
}

echo json_encode($data);
// Close the connection
mysqli_close($conn);
?>

