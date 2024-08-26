# Manga Downloader

This is a simple web-based Manga downloader built with Flask. The application allows users to download manga chapters from a specified URL, convert the images to PDF format, and download all or selected chapters as a ZIP file. 

## Features

- Download manga chapters from a specified base URL.
- Convert downloaded images into a PDF for each chapter.
- Download all chapters as a single ZIP file.
- Download selected chapters as a ZIP file.
- Clear the database of downloaded files.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/manga-downloader.git
    cd manga-downloader
    ```

2. **Create a Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Flask Application:**

    ```bash
    python app.py
    ```

2. **Access the Application:**

    Open your web browser and go to `http://127.0.0.1:5000/`.

3. **Download Manga:**

    - Enter the base URL of the manga series you wish to download.
    - Specify the range of chapters you want to download.
    - Click the **Download** button.
    - Once the chapters are processed, you can download them individually, as a ZIP file containing all chapters, or selected chapters.

4. **Clear Database:**

    Use the **Clear Database** button to delete all downloaded files.

## Deploying on Render

To deploy this application on [Render](https://render.com/):

1. **Create a Render Account:**

    Sign up for a free account at [Render](https://render.com/).

2. **Create a New Web Service:**

    - Connect your GitHub repository to Render.
    - Select **Python** as the environment and **Flask** as the framework.
    - Render will automatically detect the `requirements.txt` and set up the environment.

3. **Set Environment Variables:**

    You might need to configure any required environment variables in the Render dashboard.

4. **Deploy:**

    Deploy the application and access it via the Render-generated URL.

## File Structure

```plaintext
├── app.py               # Main application script
├── index.html           # Frontend HTML template
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── static/              # Folder for serving static files
