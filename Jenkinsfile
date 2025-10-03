pipeline {
    agent any
    environment {
        BUILDTAG = "${env.BUILD_NUMBER}"
    }
        
    stages {
        stage('Build') {
            steps {
                echo 'Build stage'
                // Builds an image with the build tag of the current job and the latest tag
                bat """
                docker build -t omarnoman/python_login_webapp_webapp:${BUILDTAG} -t omarnoman/python_login_webapp:latest .
                 """
            }
        }

        stage('Test') {
            steps {
                echo 'Test stage'
                // Runs test using pytest as well as creating the coverage.xml file
                bat 'docker run --rm -v %CD%:/app omarnoman/python_login_webapp:latest pytest --cov=python_login_webapp --cov-report=term-missing --cov-report=xml:/app/coverage.xml --cov-config=.coveragerc'

            }
        }

        stage('Code Quality') {
            steps {
                echo 'Code Quality stage'
                // Connects and runs to sonarqube to test code quality
                script {
                    def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                    withCredentials([string(credentialsId: 'jenkins-sonar', variable: 'SONAR_TOKEN')]) {
                        withSonarQubeEnv('SonarQube-Local') {
                            bat """
                                ${scannerHome}\\bin\\sonar-scanner.bat ^
                                -Dsonar.projectKey=python_login_webapp ^
                                -Dsonar.sources=python_login_webapp ^
                                -Dsonar.tests=tests ^
                                -Dsonar.python.version=3.11 ^
                                -Dsonar.python.coverage.reportPaths=coverage.xml ^
                                -Dsonar.token=%SONAR_TOKEN%
                            """
                        }      
                    }
                }
            }
        }

        stage('Security') {
            steps {
                echo 'Security stage '
                // runs bandit to test security quality of program
                bat 'docker run --rm -e ENV=production -v %CD%:/app omarnoman/python_login_webapp:latest bandit -r /app -lll'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploy stage'
                // Building a new docker image to be ready for deployment
                bat"""
                docker build -t omarnoman/python_login_webapp:latest .
                """

                // Firstly stops any running containes thens removes them 
                bat """
                docker stop python_login_webapp-test || echo "pythong_login_webapp-test is not currently running"
                docker rm -f python_login_webapp-test || echo "python_login_webapp-prod does not exist"
                """
                
                // Runs the container
                bat """
                docker run -d --name python_login_webapp-test ^
                    -e CI=true ^
                    -p 5000:5000 ^
                    omarnoman/python_login_webapp:latest
                """

                // Waits 5 seconds to ensure container can start up and lists all the currently running containers
                bat"""
                timeout /t 5
                docker ps -a
                """
            }
        }

        stage('Release') {
            steps {
               echo "Building and pushing image to Docker Hub..."

                // Builds a production ready images with build tag and latest tag
                bat "docker build -t omarnoman/python_login_webapp:${BUILDTAG} -t omarnoman/python_login_webapp:latest ."

                // Connects to docker hub using credentials withing jenkins 
                withCredentials([string(credentialsId: 'dockerhub-credentials', variable: 'DOCKER_TOKEN')]) {
                    bat 'docker login -u omarnoman -p %DOCKER_TOKEN%'
                }   

                // Pushes the images into docker hub
                bat "docker push omarnoman/python_login_webapp:${BUILDTAG}"
                bat "docker push omarnoman/python_login_webapp:latest"

                echo "Images succesffuly pushed into docker hub"

                // Firstly stops any running containes thens removes them 
                bat """
                docker stop python_login_webapp-prod || echo "python_login_webapp-prod is not running"
                docker rm python_login_webapp-prod || echo "python_login_webapp-prod does not exist"
                """

                // Creates a new production container
                bat """
                docker run -d --name python_login_webapp-prod -e ENV=production -p 80:5000 omarnoman/python_login_webapp:${BUILDTAG}
                """

                bat "docker ps -a"
            }
        }

        stage('Monitoring') {
            steps {
                echo 'Monitoring stage'
                // Firstly stops any running containes thens removes them 
                bat """
                docker stop dd-agent || echo "datadog is not running"
                docker rm -f dd-agent || echo "datadog does not exist"
                """

                // Connects and runs to datadog for metric monitoring
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

