<?php
if ($_REQUEST['method'] && function_exists($_REQUEST['method'])) {
    $_REQUEST['method']();
}

function sendCommand($str) {
    $writer = fopen('../in.fifo', 'w');
    fwrite($writer, $str . "\n");
    fclose($writer);
}

function sendCommandAndGetResponse($str) {
    $reader = fopen('../out.fifo', 'r');
    sendCommand($str);
    $line = fgets($reader);
    fclose($reader);
    return trim($line);
}

function setPosition() {
    $kpa = $_REQUEST['kPa'];
    $position = $_REQUEST['position'];
    $positions = getPositionsFromFile();
    $positions[$kpa] = $position;
    writePositionsToFile($positions);
}

function setCurrentAsZero() {
    sendCommand('MZR:0');
}

function moveMotor() {
    $steps = $_REQUEST['steps'];
    sendCommand("MTR:$steps");
}

function moveMotorTo() {
    $pos = $_REQUEST['position'];
    sendCommand("KPA:$pos");
}

function getCurrentPosition() {
    $pos = sendCommandAndGetResponse('KPQ:0');
    echo json_encode(['position' => $pos]);
}

function getPositions() {
    echo json_encode(getPositionsFromFile());
}

function writePositionsToFile($positions) {
    $str = '';
    foreach ($positions as $kpa => $pos) {
        $str .= "$kpa:$pos\n";
    }
    file_put_contents('../kPaPositions.txt', $str);
    getPositions();
}

function getPositionsFromFile() {
    $file = file('../kPaPositions.txt');
    $kPaPositions = [];
    foreach ($file as $line) {
        list($kPa, $position) = explode(':', trim($line), 2);
        $kPaPositions[$kPa] = $position;
    }
    return $kPaPositions;
}
?>
