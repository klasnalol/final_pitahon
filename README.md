# Flask Social Media App

This is a Flask-based social media application where users can register, log in, create posts (with optional media attachments), and view other users' posts. It also includes APIs to fetch and create posts.

## Features

- **User Authentication**: Register, log in, and log out functionality with hashed passwords.
- **Post Creation**: Users can create posts with text content and optionally attach media.
- **User Profiles**: View profile pages with posts created by each user.
- **API Endpoints**:
  - **GET** `/api/posts`: Fetch posts in a paginated format.
  - **POST** `/api/post`: Create a new post through an API endpoint.

## Technology Stack

- **Backend**: Flask, Flask-Login, Flask-Bcrypt, SQLAlchemy
- **Frontend**: HTML, CSS, Jinja2 templates
- **Database**: SQLite (can be configured for other databases)
- **Image Processing**: Pillow (for resizing profile pictures)

## Installation and Setup

### Prerequisites

- Python 3.x installed on your machine
- A virtual environment (optional but recommended)
- Flask dependencies (install via `requirements.txt`)

### Installation

1. Clone the repository

2. Create and activate a virtual environment (optional):
    ```bash
    python -m venv venv
    source venv/bin/activate   # For Linux/macOS
    venv\Scripts\activate      # For Windows
    ```

3. Install the required packages:
    ```bash
    pip install -r nuzhna.txt
    ```


5. Run the application:
    ```bash
    flask run
    #or
    python3 run.py
    ```

6. Access the application at `http://127.0.0.1:5000`.

## Project Structure

- `app/`: Contains the main application code
  - `models.py`: Database models
  - `routes.py`: Main application routes
  - `forms.py`: Form handling with Flask-WTF
  - `static/`: Static files (e.g., CSS, images)
  - `templates/`: HTML templates
- `nuzhna.txt`: Lists dependencies for the project
- `run.py`: Entry point to run the Flask application

## API Documentation

### Authentication
API endpoints require the user to be authenticated, except for the `register` and `login` views in the main application.

### Endpoints

#### 1. **Fetch Posts**
   - **URL**: `/api/posts`
   - **Method**: `GET`
   - **Description**: Retrieves posts in a paginated format.
   - **Query Parameters**:
     - `page` (optional, default=1): Specifies the page number.
     - `per_page` (optional, default=10): Specifies the number of posts per page.
   - **Response**:
     - **200 OK**:
       ```json
       {
         "posts": [
           {
             "id": 1,
             "title": "Post Title",
             "content": "Post content",
             "media_file": "media_filename.jpg",
             "author": "username",
             "date_posted": "2023-11-18 12:34:56"
           },
           ...
         ],
         "page": 1,
         "total_pages": 5,
         "total_posts": 50
       }
       ```
     - **Example**:
       ```bash
       curl http://127.0.0.1:5000/api/posts?page=1&per_page=5
       ```

#### 2. **Create Post**
   - **URL**: `/api/post`
   - **Method**: `POST`
   - **Description**: Allows an authenticated user to create a new post.
   - **Request Body (JSON)**:
     - `title`: The title of the post (required)
     - `content`: The content of the post (required)
     - `media`: Media file (optional)
   - **Response**:
     - **201 Created**:
       ```json
       {
         "message": "Post created successfully",
         "post": {
           "id": 1,
           "title": "Post Title",
           "content": "Post content",
           "media_file": "media_filename.jpg",
           "author": "username",
           "date_posted": "2023-11-18 12:34:56"
         }
       }
       ```
     - **400 Bad Request**: If `title` or `content` is missing
     - **Example**:
       ```bash
       curl -X POST http://127.0.0.1:5000/api/post -H "Content-Type: application/json" -d '{"title": "New Post", "content": "This is the content of the post."}'
       ```

## Contributing

Feel free to fork the project and submit pull requests. For major changes, please open an issue to discuss them first.

## License

This project is licensed under the MIT License.
