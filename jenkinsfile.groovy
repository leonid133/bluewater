def repository = 'leonid133/bluewater'

def buildAndPublishReleaseFunction = {
    //Buid app
    def curVersion = getVersion()
    sh "docker build -t docker.hydrosphere.io/bluewater ."
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
        {}
)