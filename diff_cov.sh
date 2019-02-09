#!/usr/bin/env bash

#INFO

# Use this script to run tests, generate coverage report and show lint / coverage ONLY for the diff on current branch.
# By default the diff is measured to origin/master - USE COMPARE_BRANCH variable to set a non standard main branch.
# It is now set to origin/develop which is what we use but if you based your branch on something else - use that.

# Needs flake8, pytest-cov and diff-cover packages to work - use pip install to get them.
# pip install flake8, pytest-cov, diff-cover (probably we just need diff-cover as the others are already installed)

# The diff-cover command requires project's coverage report which is stored in coverage.xml file.
# This will be created on first run for the branch (make sure you add coverage.xml to .gitignore) by pytest-cov.
# If you had to merge develop/master/etc. into your current branch during work,
# delete coverage.xml and run diff_cov.sh again to measure project's coverage again (otherwise the results will be
# skewed)

# If you have 100% lint quality and 100% code coverage in your diff the reports will only show file names present in
# your diff and 100% next# to them.

# If you miss anything in any file it will be listed with the violation's description for the lint report or missed
# coverage lines in the coverage report.

# Partially covered code is also measured but all missed lines are shown as red (not yellow).

# The script will create two folders:

# diff_reports with 2 files - pep8 violations and code coverage misses for the diff on your branch
# htmlcov - code coverage for entire project

# Also coverage will create files:
# .coverage
# .coverage.<name of your machine>
# coverage.xml

# Add those two folders and files to global gitignore:
# - subl ~/.gitignore_global - to edit file, below is my global gitignore contents for now:
# .idea/
# .coverage.*
# coverage.xml
# htmlcov/
# diff_reports/

# git config --global core.excludesfile ~/.gitignore_global - to add to git

# SCRIPT - feel free to enhance it!

REPORT_DIR='diff_reports/'
LINT_FILE='diff_lint_report.html'
COV_FILE='diff_coverage_report.html'
COMPARE_BRANCH=origin/master   # Change to whatever is your base branch. i.e. origin/develop etc.
                                # Make sure variable is not a string - no quotes here!!!
LINT_PATH="$REPORT_DIR"/"$LINT_FILE"
COV_PATH="$REPORT_DIR"/"$COV_FILE"

# Find diff in code or any new staged/unstaged files present in the branch - needed to rerun pytest with coverage and
# have an updated# coverage.xml report.
#NOTE: Once files are committed, they no longer show up in the diff reports - so make sure you fix the flaws before or
# this script will provide no value!
RERUN_TESTS=false
DIFF=$(git diff HEAD)
if [[ ${#DIFF} > 0 ]]; then
    echo "Found diff to the last commit."
    RERUN_TESTS=true
    echo "$RERUN_TESTS"
fi

# Create reports folder if not present.
if [[ ! -d "$REPORT_DIR" ]]; then
    mkdir "$REPORT_DIR"
fi

# Create coverage.xml - project's coverage report if not present or if any new tracked files were added to the branch.
# IMPORTANT: Delete this file and rerun the script after any merge into your work branch to have the newest report.
if [[ ! -f coverage.xml  || ${#STAGED_FILES} > 0 || ${#DIFF} > 0 ]]; then
    echo "Running pytest and generating project's coverage report..."
    pytest --cov=src --cov-branch --cov-report html --cov-report term:skip-covered --cov-report xml
#    pytest integration_tests/ platform/test data_integration/data_integration_test/ --cov-branchh --cov=flexciton --cov=camira_data_integration/src/camira_data_integration --cov=data_integration/src/data_integration --cov-report term --cov-report html --cov-report xml
fi

echo "Running diff lint check..."
diff-quality --violations=flake8 --compare-branch="$COMPARE_BRANCH" --html-report "$LINT_PATH"

echo "Running diff coverage check..."
diff-cover coverage.xml --compare-branch="$COMPARE_BRANCH" --html-report "$COV_PATH"

echo "Deleting .coverage* files..."
rm -rf .coverage*

# Open reports in google chrome - opens 2 new windows every time - improvement to refresh on file change needed.
google-chrome "$LINT_PATH"
google-chrome "$COV_PATH"
#open "$LINT_PATH"
#open "$COV_PATH"


