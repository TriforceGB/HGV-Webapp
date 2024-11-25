<?php

error_reporting(E_ALL);
ini_set('display_errors', 1);

// Check if the form is submitted
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Collect the data from the form
    $firstName = htmlspecialchars($_POST['fname']);
    $lastName = htmlspecialchars($_POST['lname']);
    $email = htmlspecialchars($_POST['email']);
    $message = htmlspecialchars($_POST['message']);

    // Set the recipient email address (where the form data will be sent)
    $to = "zsaiyed138@gmail.com";

    // Set the subject of the email
    $subject = "New Problem Report from $firstName $lastName";

    // Create the email content
    $emailContent = "
    <html>
    <head>
        <title>$subject</title>
    </head>
    <body>
        <h2>$subject</h2>
        <p><strong>First Name:</strong> $firstName</p>
        <p><strong>Last Name:</strong> $lastName</p>
        <p><strong>Email:</strong> $email</p>
        <p><strong>Message:</strong><br>$message</p>
    </body>
    </html>
    ";

    // Set the headers for the email
    $headers = "MIME-Version: 1.0" . "\r\n";
    $headers .= "Content-Type: text/html; charset=UTF-8" . "\r\n";
    $headers .= "From: $email" . "\r\n";
    $headers .= "Reply-To: $email" . "\r\n";

    // Send the email
    if (mail($to, $subject, $emailContent, $headers)) {
        echo "Your message has been sent successfully.";
    } else {
        echo "There was an error sending your message. Please try again later.";
    }
} else {
    // If the form isn't submitted, redirect to the form page
    header("Location: reportprob.html");
    exit();
}
?>
 