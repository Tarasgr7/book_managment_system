
---

# Project Setup

## Requirements

- Docker
- Docker Compose

## Running the Project Locally

1. **Clone the Repository**:
   Clone the repository using Git:

   ```bash
   git clone https://github.com/Tarasgr7/book_managment_system.git
   cd book_managment_system
   ```

2. **Configure .env file**:  
Create a `.env` file in the root directory and copy all content from `.env.example` into it.

3. **Build and Start the Project**:
   With Docker Compose, you can easily start all containers:

   ```bash
   docker-compose up --build
   ```

   This command will build the images for the containers (if needed) and start them. After this, you will be able to access the project through the browser or API.

4. **Accessing the Application**:
   After starting the project, you can access the following URLs (depending on your configuration):

   - Web API: `http://localhost:8000`
   - Swagger Documentation: `http://localhost:8000/docs`

5. **Stopping the Project**:
   To stop the project, use the command:

   ```bash
   docker-compose down
   ```

   This will stop all containers but will not remove data from the database.

---

These are the basic instructions for running your project with Docker Compose.
