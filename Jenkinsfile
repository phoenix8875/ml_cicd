pipeline {
    agent any
    environment {
        // This maps the Jenkins secret to a temporary variable called 'INJECTED_KEY'
        INJECTED_KEY = credentials('OMDB_API_KEY_ID')
    }
    stages {
        stage('Build Image') {
            steps {
                sh 'docker build -t my-movie-app .'
            }
        }
        stage('Deploy with Secret') {
            steps {
                // We stop any old version and start the new one with the key
                sh "docker stop movie-container || true"
                sh "docker rm movie-container || true"
                
                // The '-e' flag injects the secret into the container's environment
                sh "docker run -d -p 8501:8501 --name movie-container -e OMDB_API_KEY=${INJECTED_KEY} my-movie-app"
            }
        }
    }
}