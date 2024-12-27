#!/bin/bash

set -e

function usage {
    echo ""
    echo "Usage: $(basename "$0") [<tasks>] [<options>]"
    echo ""
    echo "Default tasks: package upload compile deploy"
    echo "Available tasks:"
    echo "    package               Package application files (platform/package.sh)"
    echo "    upload                Upload files to S3"
    echo "    compile               Execute compile actions"
    echo "    deploy                Execute deploy actions"
    echo "    release               Execute release actions"
    echo "    teardown              Execute teardown actions"
    echo ""
    echo "Available options:"
    echo "    -h, --help            Display this message"
    echo "    -c, --client          Client name, used for resource prefixes"
    echo "    -s, --scope           Scope name"
    echo "    -p, --portfolio       Portfolio name"
    echo "    -a, --app             App name"
    echo "    -b, --branch          Branch name"
    echo "    -n, --build           Build name"
    echo "    --aws-profile         AWS profile name"
    echo "    --bucket-name         S3 bucket name"
    echo "    --bucket-region       S3 bucket region, default ap-southeast-1"
    echo "    --automation-type     Automation type [deployspec, pipeline], default is pipeline"
    echo "    --extra-facts-json    Supply extra facts to the compiler. Must be a valid json string."
    echo "    --invoker-branch      Invoker Lambda branch. Takes precedence over the --invoker-name option."
    echo "    --invoker-region      Invoker Lambda region"
    echo "    --force               Set to 'true' to force through an action if it has protection checks on it -- see teardown."
    echo ""
    echo "Options can also be set via environment variables:"
    echo "    TASKS"
    echo "    PORTFOLIO, APP, BRANCH, BUILD"
    echo "    SCOPE"
    echo "    AUTOMATION_TYPE"
    echo "    BUCKET_NAME, BUCKET_REGION"
    echo "    INVOKER_LAMBDA_NAME, INVOKER_LAMBDA_REGION"
}

function fail {
    echo "ERROR: $1"
    exit 1
}

function on_exit {
    EXIT_CODE=$?
    [ $EXIT_CODE -eq 0 ] || echo -e "\nERROR: Encountered an error. See logs for details."
    exit $EXIT_CODE
}
trap on_exit EXIT

function print_json_file {
    FILE=$1

    # Try printing with python 2
    1>/dev/null which python && HAS_PYTHON="true" || HAS_PYTHON="false"
    if [ "$HAS_PYTHON" = "true" ]; then
        export PYTHONIOENCODING=utf8
        cat "$FILE" | python -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=4, sort_keys=True))"
        return
    fi

    # Try printing with python 3
    1>/dev/null which python3 && HAS_PYTHON3="true" || HAS_PYTHON3="false"
    if [ "$HAS_PYTHON3" = "true" ]; then
        cat "$FILE" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=4, sort_keys=True))"
        return
    fi

    # Try printing with jq
    1>/dev/null which jq && HAS_JQ="true" || HAS_JQ="false"
    if [ "$HAS_JQ" = "true" ]; then
        cat "$FILE" | jq -MS --indent 4
        return
    fi

    # Couldn't find suitable tool to pretty-print json, just print the file without any formatting
    cat "$FILE"
}

function check_released_build {
    lookup_key="{\"prn\": {\"S\": \"prn:$PORTFOLIO:$APP:$BRANCH\"}}"
    echo "Checking if prn:$PORTFOLIO:$APP:$BRANCH:$BUILD is the latest released build..."
    release_prn=$($AWS_CLI dynamodb $AWS_CLI_ARGS --region ap-southeast-1 get-item --table-name "${SCOPE_PREFIX}core-automation-${INVOKER_BRANCH}-api-db-items" --key "$lookup_key" --projection-expression released_build_prn --query Item.released_build_prn.S --output text)
    release_build_number="${release_prn##*:}"
    if [[ ("$BUILD" = "$release_build_number") && ! ("$FORCE" = "true") ]]; then
        echo "Cannot teardown released build '$release_prn' without --force true flag."
        exit 1
    fi
    # All other scenarios: not the released build, or using force flag = let action continue.
}

function create_sts_session {
    CLIENT=$1
    IAM_AWS_PROFILE=$2
    TARGET_AWS_PROFILE=$3

    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo "DIR=${DIR}"

    # Load config vars from a standard location.
    CLIENT_CONFIG_DIR="$DIR/../../$CLIENT-config"
    source "$CLIENT_CONFIG_DIR/accounts.sh" # optional, bash 3 issue IIRC.

    for AN_AWS_REGION in "${!REGIONS[@]}"; do
      for AN_AWS_PROFILE in "${!ACCOUNTS[@]}"; do
        # echo "Profile : $AN_AWS_PROFILE"
        # echo "Account ID : ${ACCOUNTS[$AN_AWS_PROFILE]}"

        if [[ "${ACCOUNTS[$AN_AWS_PROFILE]}" == "$TARGET_AWS_PROFILE" ]]; then
            aws sts assume-role \
                --role-arn "arn:aws:iam::${ACCOUNTS[$AN_AWS_PROFILE]}:role/core-automation-role" \
                --role-session-name "$AN_AWS_PROFILE-core-automation-role-session" \
                --profile "$IAM_AWS_PROFILE" > "assume-role-${ACCOUNTS[$AN_AWS_PROFILE]}-output.txt"

            # echo ""
            # cat assume-role-${ACCOUNTS[$AN_AWS_PROFILE]}-output.txt
            # echo ""
	    fi
      done
    done
}

function get_sts_session {
    STS_FILE=$1

    # echo ""
    # cat $STS_FILE
    # echo ""

    AWS_ACCESS_KEY_ID_RAW=$(cat "$STS_FILE" | jq .Credentials.AccessKeyId)
    AWS_ACCESS_KEY_ID=$(echo "$AWS_ACCESS_KEY_ID_RAW" | sed 's/^.//;s/.$//')
    export AWS_ACCESS_KEY_ID

    AWS_SECRET_ACCESS_KEY_RAW=$(cat "$STS_FILE" | jq .Credentials.SecretAccessKey)
    AWS_SECRET_ACCESS_KEY=$(echo "$AWS_SECRET_ACCESS_KEY_RAW" | sed 's/^.//;s/.$//')
    export AWS_SECRET_ACCESS_KEY

    AWS_SESSION_TOKEN_RAW=$(cat "$STS_FILE" | jq .Credentials.SessionToken)
    AWS_SESSION_TOKEN=$(echo "$AWS_SESSION_TOKEN_RAW" | sed 's/^.//;s/.$//')
    export AWS_SESSION_TOKEN
}

function print_deployment_status {
    deployment_message=$1
	  deployment_state_file=$2

    CLIENT="simple"
    IAM_AWS_PROFILE="simple-iam"
    IAM_AWS_ACCOUNT_ID="272883990737"

    echo ""
    echo "$deployment_message"
    echo ""
    cat "$deployment_state_file"

    # create STS session
    echo ""
    echo "setting up jq"
    pip install jq > /dev/null 2>&1 || echo ""

    AUTOMATION_BIN="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

    # parse deploy.state
    declare -a input_array
    declare -a sts_created
    while IFS=":" read -a input_array
    do
        for string in "${input_array[@]}"
            do
                if [[ $string == "ap-southeast-1" || $string == "us-east-1" ]]; then
                    region=$string
                    echo ""
                    echo "Region         : $region"
                    continue
                fi
                re='^[0-9]+$'
                if [[ $string =~ $re && "${#string}" -ge 12 ]]; then    # string is a 12 char numbers
                    account_id=$string
                    echo "Account ID     : $account_id"
                    continue
                fi
                if [[ $string == *":stack/"* ]]; then                    # string contains "stack/"
                    stack_id="arn:aws:cloudformation:$region:$account_id:$string"
                    echo "Stack ID       : $stack_id"
                    if [[ ! -z $stack_id && ! -z $account_id ]]; then    # failed and stack_id is not empty
                        if [[ "$account_id" != "$IAM_AWS_ACCOUNT_ID" ]]; then
                            # get STS session
                            if [ -z "${sts_created[$account_id]}" ]; then
                              sts_created[$account_id]="yes"

                              echo "creating STS session for $account_id"
                              create_sts_session $CLIENT $IAM_AWS_PROFILE "$account_id"
                              echo ""
                            fi

                            get_sts_session "assume-role-$account_id-output.txt"
                            # echo $AWS_ACCESS_KEY_ID
                            # echo $AWS_SECRET_ACCESS_KEY
                            # echo $AWS_SESSION_TOKEN

                            aws cloudformation describe-stack-events \
                                --stack-name "$stack_id" \
                                --region "$region" | python3 "$AUTOMATION_BIN/describe_stack.py"
                        else
                            aws_profile=$IAM_AWS_PROFILE
                            aws cloudformation describe-stack-events \
                                --stack-name "$stack_id" \
                                --region "$region" \
                                --profile $aws_profile | python3 "$AUTOMATION_BIN/describe_stack.py"
                        fi
                    fi
                    continue
                fi
                if [[ $string == "failed" || $string == "complete" || $string == "running" ]]; then
                    if [[ ! -z $stack_id ]]; then
                        echo "StatusCode     : $string"
                        echo ""
                    fi
                    if [[ $string == "complete" || $string == "running" ]]; then
                        stack_id=""
                    fi
                fi
            done
    done < "$deployment_state_file"
}

# Process script parameters
while test $# -gt 0; do
    case "$1" in
        -h|--help)
            usage; exit 0
            ;;
        --aws-profile)
            shift; AWS_PROFILE=$1; shift
            ;;
        -c|--client)
            shift; CLIENT=$1; shift
            ;;
        -s|--scope)
            shift; SCOPE=$1; shift
            ;;
        -p|--portfolio)
            shift; PORTFOLIO=$1; shift
            ;;
        -a|--app)
            shift; APP=$1; shift
            ;;
        -b|--branch)
            shift; BRANCH=$1; shift
            ;;
        -n|--build)
            shift; BUILD=$1; shift
            ;;
        --bucket-name)
            shift; BUCKET_NAME=$1; shift
            ;;
        --bucket-region)
            shift; BUCKET_REGION=$1; shift
            ;;
        --extra-facts-json)
            shift; EXTRA_FACTS=$1; shift
            ;;
        --invoker-branch)
            shift; INVOKER_BRANCH=$1; shift
            ;;
        --invoker-region)
            shift; INVOKER_LAMBDA_REGION=$1; shift
            ;;
        --automation-type)
            shift; AUTOMATION_TYPE=$1; shift
            ;;
        --force)
            shift; FORCE=$1; shift
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            [ -z "$TASKS" ] && TASKS="$1" || TASKS="$TASKS $1"
            shift
            ;;
    esac
done


TASKS="${TASKS:-package upload compile deploy}"

[ -z "$SCOPE" ] || SCOPE_PREFIX="${SCOPE}-"

# Environment variables - TODO move values into a config file?
if [ -z "$INVOKER_BRANCH" ]; then
    INVOKER_BRANCH="master"
fi

INVOKER_BRANCH_SHORT_NAME=$(echo "${INVOKER_BRANCH}" | tr '[:upper:]' '[:lower:]')
INVOKER_BRANCH_SHORT_NAME="${INVOKER_BRANCH_SHORT_NAME//[^a-z0-9\\-]/-}"
INVOKER_BRANCH_SHORT_NAME="${INVOKER_BRANCH_SHORT_NAME:0:20}"
INVOKER_BRANCH_SHORT_NAME="${INVOKER_BRANCH_SHORT_NAME%-}"

INVOKER_LAMBDA_NAME="${SCOPE_PREFIX}core-automation-$INVOKER_BRANCH_SHORT_NAME-invoker"

INVOKER_LAMBDA_REGION="${INVOKER_LAMBDA_REGION:-ap-southeast-1}"
BUCKET_REGION="${BUCKET_REGION:-ap-southeast-1}"
if [ -z "$BUCKET_NAME" ]; then
    [[ -z "$CLIENT" ]] && echo "ERROR: Must supply --bucket-name or --client" && usage && exit 1
    BUCKET_NAME="${SCOPE_PREFIX}$CLIENT-core-automation-$BUCKET_REGION"
fi
[ -z "$EXTRA_FACTS" ] && EXTRA_FACTS="{}"

DELIVERED_BY="${bamboo_ManualBuildTriggerReason_userName:-automation}"

# Determine build agent type
if [ ! -z "$EXECUTOR_NUMBER" ]; then
    AGENT_TYPE="jenkins"
else
    AGENT_TYPE="other"
fi

# Handling for different agent types
if [ "$AGENT_TYPE" = "jenkins" ]; then
    echo "Detected Jenkins agent type - using combination of supplied parameters and environment variables"

    if [ -z "$PORTFOLIO" ] || [ -z "$APP" ]; then
        # Downcase, remove everything before / from the job name (folders, etc)
        JOB_NAME=$(echo "${JOB_NAME##*/}" | tr '[:upper:]' '[:lower:]')
        JOB_NAME="${JOB_NAME//[^a-z0-9]/-}"
    fi

    if [ -z "$PORTFOLIO" ]; then
        # Split JOB_NAME by the first '-' to retrieve portfolio and app name
        PORTFOLIO="${JOB_NAME%%-*}"
        [[ -z "$PORTFOLIO" ]] && echo "ERROR: Could not determine portfolio name from JOB_NAME environment variable"
    fi

    if [ -z "$APP" ]; then
        APP="${JOB_NAME#$PORTFOLIO}"
        APP="${JOB_NAME#*-}"
        [[ -z "$APP" ]] && echo "ERROR: Could not determine application name from JOB_NAME environment variable"
    fi

    if [ -z "$BRANCH" ]; then
        # Branch name: strip "origin/" from branch name
        BRANCH="${GIT_BRANCH#*/}"
        [[ -z "$BRANCH" ]] && echo "ERROR: Could not determine branch name from GIT_BRANCH environment variable"
    fi

    if [ -z "$BUILD" ]; then
        BUILD="$BUILD_NUMBER"
        [[ -z "$BUILD" ]] && echo "ERROR: Could not determine build from BUILD_NUMBER environment variable"
    fi
else
    echo "Other agent type - using only supplied parameters"
fi

# Short branch name: downcase, replace bad characters with '-', limit to 20 characters, strip trailing '-'
BRANCH_SHORT_NAME=$(echo "${BRANCH}" | tr '[:upper:]' '[:lower:]')
BRANCH_SHORT_NAME="${BRANCH_SHORT_NAME//[^a-z0-9\\-]/-}"
BRANCH_SHORT_NAME="${BRANCH_SHORT_NAME:0:20}"
BRANCH_SHORT_NAME="${BRANCH_SHORT_NAME%-}"

# Check we have all the required information to begin
[[ -z "$TASKS" ]] && echo "ERROR: Missing tasks" && usage && exit 1
[[ -z "$PORTFOLIO" ]] && echo "ERROR: Missing portfolio name" && usage && exit 1
[[ -z "$APP" ]] && echo "ERROR: Missing application name" && usage && exit 1
[[ -z "$BRANCH" ]] && echo "ERROR: Missing branch name" && usage && exit 1
[[ -z "$BRANCH_SHORT_NAME" ]] && echo "ERROR: Missing branch short name" && usage && exit 1
[[ -z "$BUILD" ]] && echo "ERROR: Missing build number" && usage && exit 1
AUTOMATION_TYPE="${AUTOMATION_TYPE:-pipeline}"

if [ ! -z "$AWS_PROFILE" ]; then
  AWS_CLI_ARGS="--profile $AWS_PROFILE"
fi

# Find the AWS CLI path
[[ ! -x "$AWS_CLI" ]] && AWS_CLI=$(which aws || echo "")
[[ ! -x "$AWS_CLI" ]] && AWS_CLI="/usr/local/bin/aws"
[[ ! -x "$AWS_CLI" ]] && echo "ERROR: Could not find AWS CLI" && exit 1

# Create the platform/files directory in case it doesn't exist
REPO_DIR=$(pwd)
PLATFORM_DIR="$REPO_DIR/platform"
FILES_DIR="$REPO_DIR/platform/files"
COMPONENTS_DIR="$PLATFORM_DIR/components"

# Deployspec package
if [[ ("$TASKS" == *"package"*) && ("$AUTOMATION_TYPE" == "deployspec") ]]; then
    echo ""
    echo "== Task: package (deployspec) =="
    echo ""
    cd $REPO_DIR
    # Create a package zip of the repository (excluding .git)
    if [ -d "platform" ]; then
       cd platform
    fi
    echo "Creating deployspec package"
    rm -f "$REPO_DIR/package.zip"
    zip -r "$REPO_DIR/package.zip" . -x \*.git\* .DS_Store
    cd $REPO_DIR
fi

# Deployspec upload
if [[ ("$TASKS" == *"upload"*) && ("$AUTOMATION_TYPE" == "deployspec") ]]; then
    echo ""
    echo "== Task: upload (deployspec) =="
    echo ""

    [ -e "$REPO_DIR/package.zip" ] || fail "Could not find platform package - must run package task first"

    echo "Uploading deployment package"
    $AWS_CLI s3 $AWS_CLI_ARGS cp \
        --region "$BUCKET_REGION" \
        --sse AES256 \
        --acl bucket-owner-full-control \
        "$REPO_DIR/package.zip" \
        "s3://$BUCKET_NAME/packages/$PORTFOLIO/$APP/$BRANCH_SHORT_NAME/$BUILD/package.zip"
fi

# Pipeline package
if [[ ("$TASKS" == *"package"*) && ("$AUTOMATION_TYPE" == "pipeline") ]]; then
    echo ""
    echo "== Task: package (pipeline) =="
    echo ""

    # Assert requirements
    [ -d "$PLATFORM_DIR" ] || fail "Repository must contain a platform directory"
    [ -d "$COMPONENTS_DIR" ] || fail "Repository must contain a platform/components directory"

    mkdir -p "$FILES_DIR"

    # Execute platform/package.sh
    if [ -f "$PLATFORM_DIR/package.sh" ]; then
        echo "Executing platform/package.sh"

        # Set environment variables for the package script to use
        export REPO_DIR
        export PLATFORM_DIR
        export FILES_DIR
        export COMPONENTS_DIR
        export PORTFOLIO
        export APP
        export BRANCH
        export BRANCH_SHORT_NAME
        export BUILD

        # Execute the package.sh script
        cd "$PLATFORM_DIR"
        bash ./package.sh
        cd "$REPO_DIR"
    else
        echo "User package script (platform/package.sh) does not exist, skipping."
    fi

    # Create a package zip of the components and variables
    echo "Creating pipeline deployment package"
    rm -f "$PLATFORM_DIR/package.zip"
    cd "$PLATFORM_DIR"
    zip -r "$PLATFORM_DIR/package.zip" components vars
    cd "$REPO_DIR"
fi

# Pipeline upload
if [[ ("$TASKS" == *"upload"*) && ("$AUTOMATION_TYPE" == "pipeline") ]]; then
    echo ""
    echo "== Task: upload (pipeline) =="
    echo ""

    [ -e "$PLATFORM_DIR/package.zip" ] || fail "Could not find platform package - must run package task first"

    mkdir -p "$FILES_DIR"

    # Upload all files in platform/files to S3
    echo "Uploading platform/files to S3 (bucket = $BUCKET_NAME, region = $BUCKET_REGION)"
    $AWS_CLI s3 $AWS_CLI_ARGS cp \
        --region "$BUCKET_REGION" \
        --sse AES256 \
        --acl bucket-owner-full-control \
        --recursive \
        "$FILES_DIR" \
        "s3://$BUCKET_NAME/files/build/$PORTFOLIO/$APP/$BRANCH_SHORT_NAME/$BUILD/"

    echo "Uploading deployment package"
    $AWS_CLI s3 $AWS_CLI_ARGS cp \
        --region "$BUCKET_REGION" \
        --sse AES256 \
        --acl bucket-owner-full-control \
        "$PLATFORM_DIR/package.zip" \
        "s3://$BUCKET_NAME/packages/$PORTFOLIO/$APP/$BRANCH_SHORT_NAME/$BUILD/package.zip"
fi

if [[ "$TASKS" == *"compile"* ]]; then
    echo ""
    echo "== Task: compile =="
    echo "Invoker Lambda: ${INVOKER_LAMBDA_REGION} / ${INVOKER_LAMBDA_NAME}"
    echo ""
    echo "Triggering compile:"

    cat > compile-payload.txt << EOF
{
    "Task": "compile-${AUTOMATION_TYPE}",
    "Package": {
        "BucketName": "$BUCKET_NAME",
        "BucketRegion": "$BUCKET_REGION",
        "Key": "packages/$PORTFOLIO/$APP/$BRANCH_SHORT_NAME/$BUILD/package.zip",
        "VersionId": null
    },
    "DeploymentDetails": {
        "Portfolio": "$PORTFOLIO",
        "App": "$APP",
        "Branch": "$BRANCH",
        "BranchShortName": "$BRANCH_SHORT_NAME",
        "Build": "$BUILD"
    },
    "Facts": $EXTRA_FACTS
}
EOF

    cat compile-payload.txt
    echo ""

    rm -f compile-response.txt
    $AWS_CLI lambda $AWS_CLI_ARGS invoke \
        --region "$INVOKER_LAMBDA_REGION" \
        --invocation-type "RequestResponse" \
        --function-name "$INVOKER_LAMBDA_NAME" \
        --payload "file://compile-payload.txt" \
        "compile-response.txt" > /dev/null

    echo "Compile response:"
    print_json_file compile-response.txt
    echo ""

    cat compile-response.txt | grep "\"Status\": \"error\"" >/dev/null && ERROR="true"
    [ "$ERROR" = "true" ] && fail "Received an error response"
fi

if [[ "$TASKS" == *"deploy"* ]]; then
    echo ""
    echo "== Task: deploy =="
    echo "Invoker Lambda: ${INVOKER_LAMBDA_REGION} / ${INVOKER_LAMBDA_NAME}"
    echo ""
    echo "Triggering deploy:"
    cat > deploy-payload.txt << EOF
{
    "Task": "deploy",
    "DeploymentDetails": {
        "DeliveredBy": "$DELIVERED_BY",
        "Portfolio": "$PORTFOLIO",
        "App": "$APP",
        "Branch": "$BRANCH",
        "BranchShortName": "$BRANCH_SHORT_NAME",
        "Build": "$BUILD"
    }
}
EOF
    cat deploy-payload.txt

    rm -f deploy-response.txt
    $AWS_CLI lambda $AWS_CLI_ARGS invoke \
        --region "$INVOKER_LAMBDA_REGION" \
        --invocation-type "RequestResponse" \
        --function-name "$INVOKER_LAMBDA_NAME" \
        --payload "file://deploy-payload.txt" \
        "deploy-response.txt" > /dev/null

    cat deploy-response.txt | grep "\"Status\": \"error\"" && ERROR="true"
    echo ""

    [ "$ERROR" = "true" ] && fail "Received an error response"

    # Wait for all the stack to complete before proceeding
    $AWS_CLI s3 $AWS_CLI_ARGS cp \
        --region "$BUCKET_REGION" \
        "s3://$BUCKET_NAME/artefacts/$PORTFOLIO/$APP/$BRANCH_SHORT_NAME/$BUILD/deploy.actions" \
        deploy.actions &> /dev/null
    stack_to_deploy=$(grep -o DependsOn deploy.actions | wc -l)

    time_start=$SECONDS
    time_out=240 # 240 seconds (4 minutes), aligned to Execute Lambda timeout_imminent function
    time_wait=90 # 90 seconds, (1 minute 5 sec), wait 90 seconds for deploy.state file as for bigger run, file is getting generated late

    echo ""
    echo "Task: deploy in progress ... "
    echo ""
    while :
    do
        ## Remove deploy.state if exist, to start from clean state
        if [ -e deploy.state ]; then
            rm deploy.state
        fi

        ## Wait for deploy.state
        echo "Wait for $time_wait seconds ... "
        sleep $time_wait
        $AWS_CLI s3 $AWS_CLI_ARGS cp \
            --region "$BUCKET_REGION" \
            "s3://$BUCKET_NAME/artefacts/$PORTFOLIO/$APP/$BRANCH_SHORT_NAME/$BUILD/deploy.state" deploy.state &> /dev/null

        stack_running=$(grep -o running deploy.state | wc -l)
        stack_completed=$(grep -o complete deploy.state | wc -l)
        stack_failed=$(grep -o failed deploy.state | wc -l)
        stack_deployed=$(($stack_completed + $stack_failed))
        echo "$(date +'%Y-%m-%d %H:%M:%S') Action:${stack_to_deploy}|Running:${stack_running}|Completed:${stack_deployed} -- Success:${stack_completed}|Fail:${stack_failed}"

        time_now=$SECONDS
        time_lapse=$((time_now-time_start))

        if [ "$stack_failed" -ge 1 ]; then
            if [[ $time_lapse -ge $time_out || $stack_to_deploy -eq $stack_deployed || $(grep -o ValidationError deploy.state) ]]; then
                print_deployment_status \
                    "Task: deploy failed" \
                    deploy.state
                exit 2
                break;
            fi
        fi
        if [ $time_lapse -ge $time_out ]; then
            print_deployment_status \
                "Task: deploy time lapsed waiting for completion, please wait for a while before checking the status in AWS accounts" \
                deploy.state
            exit 0
            break;
        fi
        if [ "$stack_to_deploy" -eq "$stack_deployed" ]; then
            print_deployment_status \
                "Task: deploy completed" \
                deploy.state
            exit 0
            break;
        fi
    done
fi

if [[ "$TASKS" == *"release"* ]]; then
    echo ""
    echo "== Task: release =="
    echo "Invoker Lambda: ${INVOKER_LAMBDA_REGION} / ${INVOKER_LAMBDA_NAME}"
    echo ""

    echo "Triggering release:"
    cat > release-payload.txt << EOF
{
    "Task": "release",
    "DeploymentDetails": {
        "DeliveredBy": "$DELIVERED_BY",
        "Portfolio": "$PORTFOLIO",
        "App": "$APP",
        "Branch": "$BRANCH",
        "BranchShortName": "$BRANCH_SHORT_NAME",
        "Build": "$BUILD"
    }
}
EOF
    cat release-payload.txt

    rm -f release-response.txt
    $AWS_CLI lambda $AWS_CLI_ARGS invoke \
        --region "$INVOKER_LAMBDA_REGION" \
        --invocation-type "RequestResponse" \
        --function-name "$INVOKER_LAMBDA_NAME" \
        --payload "file://release-payload.txt" \
        "release-response.txt" > /dev/null

    cat release-response.txt | grep "\"Status\": \"error\"" && ERROR="true"
    echo ""

    [ "$ERROR" = "true" ] && fail "Received an error response"
fi

if [[ "$TASKS" == *"teardown"* ]]; then

    check_released_build

    echo ""
    echo "== Task: teardown =="

    echo "Triggering teardown"
    cat > teardown-payload.txt << EOF
{
    "Task": "teardown",
    "DeploymentDetails": {
        "DeliveredBy": "$DELIVERED_BY",
        "Portfolio": "$PORTFOLIO",
        "App": "$APP",
        "Branch": "$BRANCH",
        "BranchShortName": "$BRANCH_SHORT_NAME",
        "Build": "$BUILD"
    }
}
EOF
    cat teardown-payload.txt

    rm -f teardown-response.txt
    $AWS_CLI lambda $AWS_CLI_ARGS invoke \
        --region "$INVOKER_LAMBDA_REGION" \
        --invocation-type "RequestResponse" \
        --function-name "$INVOKER_LAMBDA_NAME" \
        --payload "file://teardown-payload.txt" \
        "teardown-response.txt" > /dev/null

    cat teardown-response.txt | grep "\"Status\": \"error\"" && ERROR="true"
    echo ""

    [ "$ERROR" = "true" ] && fail "Received an error response"
fi

if [[ "$TASKS" == *"cleanup"* ]]; then
    echo ""
    echo "== Task: cleanup =="

    rm -f compile-payload.txt
    rm -f compile-response.txt
    rm -f deploy-payload.txt
    rm -f deploy-response.txt
    rm -f release-payload.txt
    rm -f release-response.txt
    rm -f teardown-payload.txt
    rm -f teardown-response.txt

    rm -f "$PLATFORM_DIR/package.zip"
    rm -f "$REPO_DIR/package.zip"
fi

echo "Done"
