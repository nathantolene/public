<?php

$link = mysqli_connect("localhost", "otter", "Overtguruboon3#", "utm_add_on");

if($link === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}

$sql = "select DISTINCT bldg_code from banner_pull;";

echo "<select name='Building'>";
if($result = mysqli_query($link, $sql)){
            echo "<table>";
            echo "<tr>";
                echo "<th>Subject</th>";
                echo "<th>Title</th>";
                echo "<th>Course #</th>";
                echo "<th>Instr. Last Name</th>";
		        echo "<th>Instr. First Name</th>";
		        echo "<th>Building Code</th>";
		        echo "<th>Room Number</th>";
		        echo "<th>Start Time</th>";
		        echo "<th>End Time</th>";
		        echo "<th>Sun</th>";
		        echo "<th>Mon</th>";
		        echo "<th>Tue</th>";
		        echo "<th>Wed</th>";
		        echo "<th>Thr</th>";
		        echo "<th>Fir</th>";
		        echo "<th>Sat</th>";
            echo "</tr>";
while($row = mysqli_fetch_array($result)){
echo "<option value='" . $row['bldg_code'] ."'>" . $row['bldg_code'] ."</option>";
}
echo "</select>";
}
echo "</table>";
