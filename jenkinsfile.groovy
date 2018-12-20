def repository = 'leonid133/bluewater'

def buildAndPublishReleaseFunction = {
    //Buid app
    def curVersion = getVersion()
    sh "docker build -t docker.hydrosphere.io/bluewater:${curVersion} ."
}


def deploy() {
    return { image, curVersion, env ->
        def sha = sh(script: "docker inspect --format='{{index .RepoDigests 0}}' docker.hydrosphere.io/bluewater:${curVersion}", returnStdout: true).trim().replace("/", "\\/")
        build job: 'CD/bluewater_cd', parameters: [[$class: 'StringParameterValue', name: 'image', value: sha]]
    }
}

pipelineCommon(
        repository,
        false, //needSonarQualityGate,
        ["docker.hydrosphere.io/bluewater"],
        {},
        buildAndPublishReleaseFunction,
        buildAndPublishReleaseFunction,
        buildAndPublishReleaseFunction,
        null,
        "hydro_private_docker_registry",
        "docker.hydrosphere.io",
        {},
        deploy()
)