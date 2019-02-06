#!/usr/bin/env bash

# Use this script to run tests, generate coverage report and show lint / coverage for the diff on current branch.
# By default the diff is measured to origin/master - USE COMPARE_BRANCH variable to set a non standard main branch.

# Needs flake8, pytest-cov and diff_cover packages to work - use pip install to get them.
# pip install flake8, pytest-cov, diff_cover

# If you have 100% lint quality and 100% code coverage in your diff the reports will only show file names and 100% next
# to them.
# If you miss anything in any file it will be listed with the violation's description for the lint report or missed
# coverage lines in the coverage report.
# Partially covered code is also measured but all missed lines are shown as red (not yellow).

REPORT_DIR='diff_reports/'
LINT_FILE='diff_lint_report.html'
COV_FILE='diff_coverage_report.html'
COMPARE_BRANCH='origin/master' # Change to whatever is your main branch. i.e. origin/develop etc.

LINT_PATH="$REPORT_DIR"/"$LINT_FILE"
COV_PATH="$REPORT_DIR"/"$COV_FILE"

# Create reports folder if not present.
if [[ ! -d "$REPORT_DIR" ]]; then
    mkdir "$REPORT_DIR"
fi

echo "Running pytest with coverage"
pytest --cov=src --cov-branch --cov-report html --cov-report xml --cov-report term:skip-covered

echo "Fetching branch $COMPARE_BRANCH"
git fetch origin master:refs/remotes/origin/master

echo "Running diff lint check"
diff-quality --violations=flake8 --html-report "$LINT_PATH"

echo "Running diff coverage check"
diff-cover coverage.xml --compare-branch="$COMPARE_BRANCH" --html-report "$COV_PATH"

# Open reports in google chrome - opens 2 new windows every time - improvement to refresh on file change needed.
google-chrome "$LINT_PATH"
google-chrome "$COV_PATH"