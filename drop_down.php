<?php

$link = mysqli_connect("localhost", "otter", "Overtguruboon3#", "utm_add_on");

if($link === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}

$sql = "select bldg_code from banner_pull;";

echo "<select name='Building'>";
if($result = mysqli_query($link, $sql)){
while($row = mysqli_fetch_array($result)){
echo "<option value='" . $row['bldg_code'] ."'>" . $row['bldg_code'] ."</option>";
}
echo "</select>";
}