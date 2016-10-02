#!/usr/bin/env groovy
node {
    try {
        echo 'Updating github status'
        step([$class: 'GitHubSetCommitStatusBuilder', statusMessage: [content: 'pending']])

        checkout scm  // Checkout the repo

        def commit_id = sh 'git rev-parse HEAD'

        def pwd = sh 'ls'
        echo pwd

        stage 'Build'
        docker.withRegistry('http://registry.hub.docker.com', 'docker-login') {

            // Build the docker images
            def app_image = docker.build 'trumpet2012/network-trace'
            def nginx_image = docker.build('trumpet2012/network-trace-nginx', '-f Nginx.Dockerfile')

            // Publish the docker images
            app_image.push 'latest'
            app_image.push '${commit_id}'

            nginx_image.push 'latest'
            nginx_image.push '${commit_id}'

            echo "Docker images updated"
            step([$class: 'GitHubSetCommitStatusBuilder', statusMessage: [content: 'success']])
        }
    } catch(err) {
        step([$class: 'GitHubSetCommitStatusBuilder', statusMessage: [content: 'error']])
        echo "Failed with" + err
    }
}
