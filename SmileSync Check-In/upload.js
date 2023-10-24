const AWS = require('aws-sdk');
const fs = require('fs');
const path = require('path');

// AWS S3 configuration
const s3 = new AWS.S3({
  accessKeyId: 'XXXXXXXXXXXXXXXXXXXXXX',     // Enter your AWS accessKeyId
  secretAccessKey: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',      // Enter your AWS secretaccessKey 
  region: 'XXXXXXX',       // Enter your region
});

// Specify the S3 bucket and folder
const bucketName = 'fras';
const folderName = 'Attendance';

// Specify the subfolder name on your local machine
const subfolderName = 'attendance_files';

// Get today's date in YYYY-MM-DD format
const currentDate = new Date().toISOString().slice(0, 10);

// Read the files in the local subfolder
fs.readdir(path.join(__dirname, subfolderName), (err, files) => {
  if (err) {
    console.error('Error reading the local directory:', err);
    return;
  }

  // Filter files that contain today's date in the filename
  const filesToUpload = files.filter((file) => file.includes(currentDate));

  // Iterate over the filtered files and upload them to S3
  filesToUpload.forEach((file) => {
    const filePath = path.join(__dirname, subfolderName, file);

    // Read the local file
    fs.readFile(filePath, (err, data) => {
      if (err) {
        console.error(`Error reading ${file}:`, err);
        return;
      }

      // S3 upload parameters
      const params = {
        Bucket: bucketName,
        Key: `${folderName}/${file}`,
        Body: data,
      };

      // Upload the file to S3
      s3.upload(params, (err, data) => {
        if (err) {
          console.error(`Error uploading ${file} to S3:`, err);
        } else {
          console.log(`File ${file} uploaded to Cloud at ${data.Location}`);
        }
      });
    });
  });
});