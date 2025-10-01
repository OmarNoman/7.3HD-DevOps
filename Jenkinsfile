pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Build stage'
                bat 'docker build -t python_login:latest .'
            }
        }

        stage('Test') {
            steps {
                echo 'Test stage'
                bat 'docker run --rm python_login:latest pytest -v'
            }
        }

        stage('Code Quality') {
            steps {
                echo 'Code Quality stage'
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withCredentials([string(credentialsId: 'jenkins-sonar', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv('SonarQube-Local') {
                            bat "${scannerHome}\\bin\\sonar-scanner.bat " +
                                "-Dsonar.projectKey=python_login " +
                                "-Dsonar.sources=. " +
                                "-Dsonar.login=%SONAR_TOKEN%"
                    }
                }
            }
        }
    }

        stage('Security') {
            steps {
                echo 'Security stage '
                bat 'docker run --rm -v %CD%:/app python_login:latest bandit -r /app -lll -x /app/venv'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploy stage'

                bat"""
                docker build -t omarnoman/python_login:latest
                """

                // Remove any existing container
                bat """
                docker stop myapp-test || echo "No running test container"
                docker rm myapp-test || echo "No container to remove"
                """
                
                // Run the container
                bat """
                docker run -d --name myapp-test ^
                    -e CI=true ^
                    -e USERNAME=test ^
                    -e PASSWORD=123 ^
                    -p 5000:5000 ^
                omarnoman/myapp:latest
                """

                bat"""
                timeout /t 5
                docker ps -a
                """
            }
        }

        stage('Release') {
            steps {
               echo "Building and pushing image to Docker Hub..."

                // Build production image
                bat 'docker build -t python_login:prod .'

                // Tag the image with your Docker Hub repo
                bat 'docker tag python_login:prod omarnoman/python_login:latest'

                // Login to Docker Hub using Jenkins credentials
                withCredentials([string(credentialsId: 'dockerhub-credentials', variable: 'DOCKER_TOKEN')]) {
                    bat 'docker login -u omarnoman -p %DOCKER_TOKEN%'
                }

                // Push image to Docker Hub
                bat 'docker push omarnoman/python_login:latest'

                echo "Image successfully pushed to Docker Hub!"
                
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Monitoring stage'
                

                withCredentials([string(credentialsId: 'datadog_api', variable: 'API_KEY')]) {
                    
                    bat '''
                    docker run -d --name dd-agent \
                        -e DD_API_KEY=%API_KEY% \
                        -e DD_SITE="ap2.datadoghq.com" \
                        -e DD_DOGSTATSD_NON_LOCAL_TRAFFIC=true \
                        -v /var/run/docker.sock:/var/run/docker.sock:ro \
                        -v /proc/:/host/proc/:ro \
                        -v /sys/fs/cgroup/:/host/sys/fs/cgroup:ro \
                        -v /var/lib/docker/containers:/var/lib/docker/containers:ro \
                        gcr.io/datadoghq/agent:7
                    '''
                }
                echo "Datadog has started monitoring"

            }
        }
    }
}








































