#!/bin/bash

DATADIR=/home/pi/brewpi-data
CONTAINER=brewpi
IMAGE=brewpi/brewpi-raspbian
PRG=$( basename $0 )


function is_running() {
    [[ $DEBUG -eq 1 ]] && set -x
    num=$( docker ps -q \
           --filter "name=$CONTAINER" \
           --filter "status=running" \
           | wc -l )
    [[ $num -gt 0 ]]
}


function container_id() {
    [[ $DEBUG -eq 1 ]] && set -x
    docker ps -a -f "status=exited" --format '{{.ID}} {{.Names}}' \
    | grep "$CONTAINER" \
    | cut -d' ' -f1
}


function container_exists() {
    [[ $DEBUG -eq 1 ]] && set -x
    [[ -n $(container_id) ]]
}


function docker_start_old() {
    [[ $DEBUG -eq 1 ]] && set -x
    docker container restart $( container_id )
}


function docker_start_new() {
    [[ $DEBUG -eq 1 ]] && set -x
    docker run -d \
    --name $CONTAINER \
    -p 80:80 \
    -v ~/brewpi-data:/data \
    -v /etc/timezone:/etc/timezone \
    -v /etc/localtime:/etc/localtime \
    --restart always \
    brewpi/brewpi-raspbian $*
}


function docker_start() {
    [[ $DEBUG -eq 1 ]] && set -x
    if is_running; then
        : #do nothing
    elif container_exists; then
        docker_start_old
    else
        docker_start_new $*
    fi
}

function docker_stop() {
    [[ $DEBUG -eq 1 ]] && set -x
    is_running && {
        docker ps -q --filter "name=brewpi" \
        | xargs -r docker stop
    }
}


function docker_status() {
    [[ $DEBUG -eq 1 ]] && set -x
    rc=1
    msg=Stopped
    is_running && {
        msg=Running
        rc=0
    }
    echo $msg
    return $rc
}


function docker_clean() {
    [[ $DEBUG -eq 1 ]] && set -x
    container_id | xargs -r  docker rm 
}


function check_update() {
    ###
    # Return 0 (true) if update is available, 1 (false) otherwise
    ###
    [[ $DEBUG -eq 1 ]] && set -x
    parts=( $( docker images $IMAGE --format '{{.Tag}} {{.CreatedAt}}' ) )
    tag=${parts[0]}
    current=$( date -d "${parts[1]} ${parts[2]}" "+%s" )
    registry="https://registry.hub.docker.com/v2/repositories"
    url="$registry/$IMAGE/tags/"
    latest=$( 
        curl -s "$url" \
        | jq ".results[] | select( .name == \"$tag\" ).last_updated" \
        | xargs -n1 -I{} date -d "{}" "+%s" )
    rc=1
    if [[ $latest -gt $current ]] ; then
        old=$( date -d @$current "+%Y-%m-%d %H:%M:%S" )
        new=$( date -d @$latest  "+%Y-%m-%d %H:%M:%S" )
        echo "Update available: ${IMAGE}:$tag  (current:$old) [latest:$new]"
        rc=0
    fi
    return $rc
}


function usage() {
    CMDS=( status start stop restart mkdatadir clean )
    cat <<ENDHERE
Usage: $0 CMD
where CMD is one of: ${CMDS[@]}
ENDHERE
}


### Process cmdline options
DEBUG=0
while getopts ":d" opt; do
    case $opt in
        d) DEBUG=1 ;;
    esac
done
shift $((OPTIND-1))
[[ $DEBUG -eq 1 ]] && set -x


action=$1
shift
case $action in
    status)
        docker_status
        ;;
    start)
        docker_start
        ;;
    stop)
        docker_stop
        ;;
    restart)
        docker_stop
        sleep 1
        docker_start
        ;;
    mkdatadir)
        [[ -d $DATADIR ]] || docker_start sleep 1
        ;;
    clean)
        docker_clean
        ;;
    check-update)
        check_update
        ;;
    update)
        docker_stop
        sleep 1
        docker_clean
        sleep 1
        docker pull $IMAGE
        sleep 1
        docker_start
        ;;
    test)
        container_exists && echo "true" || echo "false"
        ;;
    *)
        usage
        ;;
esac
