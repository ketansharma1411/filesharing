# File Sharing

Welcome to **File Sharing**, a secure and fast web application that allows you to share files with anyone using a unique ID. The platform enables users to upload and download files, which are stored securely on **AWS S3** and accessed via unique identifiers.

## Live Demo

https://filezap.duckdns.org
<!-- ![FileSharing](https://vondy.com/deliverable/1c26f4cc-7076-4978-a47d-5a6677dac588) -->


---

## Features

- **User-Friendly Interface**: Simple design with drag-and-drop file upload.
- **Secure File Sharing**: Files are uploaded to AWS S3 and accessed via unique IDs.
- **PostgreSQL Database**: Stores metadata and tracks file-sharing history.
- **Cross-Platform Support**: Works seamlessly on both desktop and mobile devices.
- **Fast File Transfer**: Efficient upload and download speeds for large files.
- **Interactive Animations**: Enjoy smooth file upload/download animations!

---

## Tech Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **File Storage**: AWS S3
- **Deployment**: AWS (Elastic Beanstalk) 

---

## User Journey 🚀

Experience the simplicity and ease of using **FileSharing** through this quick user journey. With a sleek and smooth interface, sharing files has never been easier!

1. **Start by Uploading a File**:  
   Simply drag and drop your file, or use the upload button to select files from your device.

   <!-- ![File Upload](https://media.giphy.com/media/djJjflS7GYoVqcJviO/giphy.gif) -->

2. **File Upload in Progress**:  
   Watch as your file is uploaded smoothly. The progress bar ensures you know exactly how much time is left.
   <!-- ![Upload Progress](https://media.giphy.com/media/xT0Gqj58cTHfaA1z1C/giphy.gif) -->

3. **Get a Unique ID**:  
   Once uploaded, you receive a unique link to your file, which you can share with others.

   <!-- ![Unique ID](https://media.giphy.com/media/l1J9ptcxw44hDiIN2/giphy.gif) -->

4. **File Download**:  
   The recipient clicks the link to download the file, watching as the download progress animates in a clean, user-friendly way.

   <!-- ![File Download](https://media.giphy.com/media/l1J9ptcxw44hDiIN2/giphy.gif) -->

5. **Successful File Transfer**:  
   Once the download is complete, the recipient gets a success notification and can now access the file.

   <!-- ![Download Success](https://media.giphy.com/media/3o6Zt5pQ0V6V6V6V6A/giphy.gif) -->

---


## Installation

### Prerequisites

- Python 3.x
- Django
- PostgreSQL
- AWS S3 Access (for storing files)
- EC2 AWS (for deployment)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/ketansharma1411/filesharing.git
   cd filesharing
