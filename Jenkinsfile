pipeline {
    agent any
    triggers{
        upstream(upstreamProjects: 'Jenkins', threshold: hudson.model.Result.SUCCESS)
    }
    environment{
        TAG1='xe5700/rime-dict-update'
    }
    stages {
        stage('Build') {
            steps {
                sh '''
                    docker build ./rime_dictionaries_update -t $TAG1
                '''
            }
        }
    }
    post{
        success{
            sh 'docker push $TAG1'
		}
    }
}