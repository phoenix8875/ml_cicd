pipeline {
    agent any

    environment {
        // Must match the ID you created in Jenkins -> Credentials
        INJECTED_KEY = credentials('OMDB_API_KEY_ID')
        IMAGE_NAME = "my-movie-app"
        CONTAINER_NAME = "movie-container"
    }

    stages {
        stage('Checkout') {
            steps {
                // Pulls your code and 32M models from GitHub
                checkout scm
            }
        }

        stage('Build Image') {
            steps {
                echo 'Starting Docker Build...'
                // Using 'bat' for Windows compatibility
                bat "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Deploy with Secret') {
            steps {
                echo 'Deploying to Docker...'
                bat """
                    @echo off
                    :: 1. Stop and remove the old container if it exists
                    docker stop ${CONTAINER_NAME} >nul 2>&1 || ver >nul
                    docker rm ${CONTAINER_NAME} >nul 2>&1 || ver >nul
                    
                    :: 2. Run the new container with the key injected via -e
                    docker run -d ^
                        -p 8501:8501 ^
                        --name ${CONTAINER_NAME} ^
                        -e OMDB_API_KEY=${INJECTED_KEY} ^
                        ${IMAGE_NAME}:latest
                """
            }
        }

        stage('Clean Up') {
            steps {
                echo 'Cleaning up old Docker images to save space...'
                // Removes unused images from previous builds
                bat "docker image prune -f"
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Movie App is live at http://localhost:8501"
        }
        failure {
            echo "FAILURE: Check the Jenkins console output for errors."
        }
    }
}