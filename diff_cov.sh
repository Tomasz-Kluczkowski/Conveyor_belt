#!/usr/bin/env bash

# INSTRUCTIONS

# Command line arguments:

# -ft or --force-test
#   to force rerun of the test suite (and regeneration of the coverage.xml file).

# -nt or --no-test
#   to disable testing. If both -ft and -nt are specified we exit with an error.

# -cb <branch> or --compare-branch <branch> (i.e.: -cb upstream/master)
#   to change the default compare branch. If always using the same one just set it in the variables below.

# Info

# Use this script to run tests, generate coverage report and show lint / coverage ONLY for the diff on current branch.
# By default the diff is measured to origin/master - USE COMPARE_BRANCH variable to set a non standard main branch.

# Script needs flake8, pytest-cov and diff-cover packages to work - use pip install to get them.
# pip install flake8 pytest-cov diff-cover

# The diff-cover command requires project's coverage report which is stored in coverage.xml file.
# This will be created by pytest-cov (make sure you add coverage.xml to global .gitignore - info below).

# If you had to merge develop/master/etc. into your current branch during work,
# run diff_cov.sh with -ft argument to measure project's coverage again (otherwise the results will be skewed).

# If you have 100% lint quality and 100% code coverage in your diff the reports will only show file names present in
# your diff and 100% next to them.

# If you miss anything in any file it will be listed with the violation's description for the lint report or missed
# coverage lines in the coverage report.

# Partially covered code is also measured but all missed lines are shown as red (not yellow).

# The script will create two folders:

# diff_reports with 2 files:
#   diff_lint_report.html (pep8 violations)
#   diff_coverage_report.html (code coverage misses for the diff on your branch)
# Feel free to change those names as you wish.

# htmlcov - code coverage folder for the entire project

# Also coverage package itself will create files:
#   .coverage
#   .coverage.<name of your machine>
#   coverage.xml
# The .coverage* files are not needed and will get deleted after the script run.

# Add those two folders and files to global .gitignore to avoid polluting the project:
# - subl ~/.gitignore_global - to edit file, below is my global gitignore contents for now:
# .idea/
# .coverage.*
# coverage.xml
# htmlcov/
# diff_reports/

# git config --global core.excludesfile ~/.gitignore_global - to add to git

# SCRIPT - feel free to enhance it!

# Set default variables
REPORT_DIR='diff_reports/'
LINT_FILE='diff_lint_report.html'
COV_FILE='diff_coverage_report.html'
COMPARE_BRANCH=origin/master   # Change to whatever is your base branch. i.e. origin/develop etc.
                                # Make sure variable is not a string - no quotes here!!!
LINT_PATH="$REPORT_DIR"/"$LINT_FILE"
COV_PATH="$REPORT_DIR"/"$COV_FILE"
FORCE_TEST=false
NO_TEST=false

# Parse CLI arguments
while [[ "$#" > 0 ]]; do case $1 in
  -ft|--force-test) FORCE_TEST=true;;
  -nt|--no-test) NO_TEST=true;;
  -cb|--compare-branch) COMPARE_BRANCH="$2"; shift;;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

# Sanity checks.
if [[ "$FORCE_TEST" == true && "$NO_TEST" == true ]]; then
    echo "You have specified mutually exclusive arguments: force-test == true and no-test == true. Unable to continue."
    exit 1
fi

# Find if there is a diff on current branch.
# TODO: find if we can use semantic diff checking and reduce amount of tests to rerun.
DIFF=$(git diff HEAD)
if [[ ${#DIFF} > 0 ]]; then
    echo "Found diff to the last commit."
fi

# Create reports folder if not present.
if [[ ! -d "$REPORT_DIR" ]]; then
    mkdir "$REPORT_DIR"
fi

# Create coverage.xml - project's coverage report if not present or files were modified/added/deleted in the branch.
# IMPORTANT: rerun the script with -ft option after any merge into your work branch to have the newest report.
if [[ "$NO_TEST" == true ]]; then
    echo "Testing disabled. Not running test suite. Using existing coverage.xml report."
elif [[ (! -f coverage.xml  || ${#DIFF} > 0  || "$FORCE_TEST" == true) ]]; then
    echo "Running pytest and generating project's coverage report against branch: $COMPARE_BRANCH..."
    pytest --cov=src --cov-branch --cov-report html --cov-report term:skip-covered --cov-report xml
fi

echo "Running diff lint check..."
diff-quality --violations=flake8 --compare-branch="$COMPARE_BRANCH" --html-report "$LINT_PATH"

echo "Running diff coverage check..."
diff-cover coverage.xml --compare-branch="$COMPARE_BRANCH" --html-report "$COV_PATH"

echo "Deleting .coverage* files..."
rm -rf .coverage*

# Open reports in google chrome - opens 2 new windows every time - improvement to refresh on file change needed.
OS=`uname`
if [[ "$OS" == "Darwin" ]]; then
    open "$LINT_PATH"
    open "$COV_PATH"
elif [[ "$OS" == "Linux" ]]; then
    google-chrome "$LINT_PATH"
    google-chrome "$COV_PATH"
fi
