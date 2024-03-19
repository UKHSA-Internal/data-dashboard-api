#!/bin/bash

function set_up_django() {
    source uhd.sh

    uhd django migrate
    uhd server setup-static-files

    local port=80
    uhd server run-production $port
}

set_up_django
