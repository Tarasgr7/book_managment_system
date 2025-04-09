
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
   cd <test_task>
   ```

2. **Configure `.env` file**:
   Make sure you have a `.env` file for settings such as database connection. If it doesn't exist, create a `.env` file in the root directory of the project, using the template provided in the repository.

3. **Build and Start the Project**:
   With Docker Compose, you can easily start all containers:

   ```bash
   docker-compose up --build
   ```

   This command will build the images for the containers (if needed) and start them. After this, you will be able to access the project through the browser or API.

4. **Apply Database Migrations**:
   If you are using Alembic for database migrations, apply them using the container:

   ```bash
   docker-compose exec web alembic upgrade head
   ```

   This will apply the latest migrations to the database. If you use a different tool for migrations, replace the command accordingly.

5. **Accessing the Application**:
   After starting the project, you can access the following URLs (depending on your configuration):

   - Web API: `http://localhost:8000`
   - Swagger Documentation: `http://localhost:8000/docs`

6. **Stopping the Project**:
   To stop the project, use the command:

   ```bash
   docker-compose down
   ```

   This will stop all containers but will not remove data from the database.

---

These are the basic instructions for running your project with Docker Compose.