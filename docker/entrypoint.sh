#!/bin/bash

function set_up_django() {
    source uhd.sh

    uhd django migrate
    uhd server setup-static-files

    uhd server run-production
}

set_up_django
