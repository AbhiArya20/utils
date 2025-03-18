# Variables
$GITHUB_TOKEN="your_github_token_goes_here"
$UPDATE = "
    <ul>
      <li>The Admin setup is complete and ready for use.</li>
      <li>You can access and clone the code from https://$GITHUB_TOKEN@github.com/AbhyArya/admin.git.</li>
      <li>For detailed deployment instructions, please refer to the <code>readme.md</code> file in the repository.</li>
      <li>In-code documentation will be provided directly within the code files.</li>
      <li>Currently, no features have been added.</li>
    </ul>
    "
# Define credentials
$USERNAME = "emailtestotp19@gmail.com"
$PASSWORD = "your_password_goes_here"

$RECEIVER_NAME = "Kartik Sir"
$SENDER_NAME = "Abhishek Kumar"

# Define email parameters
$FROM = '"Admin Update - No Reply" <emailtestotp19@gmail.com>'
$EMAIL_RECIPIENTS = @("kartik@parikshalabs.com", "works.abhishekkumar@gmail.com")
$SUBJECT = "Admin Update"
$BODY = @"
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        color: #333;
        margin: 0;
        padding: 0;
      }
      .container {
        max-width: 600px;
        margin: 40px auto;
        background: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
      }
      h2 {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #444;
        margin-bottom: 20px;
      }
      p {
        display: inline-block;
        padding: 0;
        margin: 0;
        font-size: 16px;
        color: #555;
      }
      .button-wrapper {
        width: 100%;
        display: flex;
        flex-wrap: wrap;
      }
      .cta-button {
        display: inline-block;
        text-decoration: none;
        background-color: hsl(333deg, 100%, 52%);
        padding: 5px 10px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 5px;
        margin: 5px 5px;
        margin-left: 0;
        text-align: center;
        transition: background 0.3s ease;
      }
      .cta-button:hover {
        background-color: hsl(333deg, 100%, 63%);
      }
      .name {
        text-transform: capitalize;
        font-weight: bold;
        color: #333;
      }
      .message {
        margin: 20px 0;
        width: 100%;
      }
      h3 {
        margin: 0;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <p class="name">Hi, $RECEIVER_NAME</p>
      <div class="message">
        <div>$UPDATE</div>
        <ul>
          <p>You can access the admin website from the following link:</p>
          <div class="button-wrapper">
            <a href="https://admin.abhiarya.in" class="cta-button" style="color: white">See Admin</a>
          </div>
        </ul>
        <ul>
          <li>This is a system-generated email. Do not reply to this message.</li>
          <li>If you believe something is missing, needs to be changed, or a client does not require a feature, please contact</li>
          <a href="mailto:aky8507049610@gmail.com" class="cta-button" style="color: white;">Contact</a>
        </ul>
      </div>
      <div>
        <h3>Regards</h3>
        <h3>$SENDER_NAME</h3>
      </div>
    </div>
  </body>
</html>
"@


# Function to send APK via email
Write-Output "Sending email"
try {
  $smtpClient = New-Object System.Net.Mail.SmtpClient("smtp.gmail.com", 587)
  $smtpClient.EnableSsl = $true
  $smtpClient.Credentials = New-Object System.Net.NetworkCredential($USERNAME, $PASSWORD)
  $smtpClient.Timeout = 300000
  $mailMessage = New-Object System.Net.Mail.MailMessage
  $mailMessage.From = $FROM
  foreach ($RECIPIENT in $EMAIL_RECIPIENTS) {
    $mailMessage.To.Add($RECIPIENT)
  }
  $mailMessage.SUBJECT = $SUBJECT
  $mailMessage.Body = $BODY
  $mailMessage.IsBodyHtml = $true
  $smtpClient.Send($mailMessage)
  Write-Output "Emails Sent"
}
catch {
  Write-Output "Failed to send emails $_"
}
finally {
  # Dispose of objects
  if ($mailMessage) { $mailMessage.Dispose() }
  if ($smtpClient) { $smtpClient.Dispose() }
}
