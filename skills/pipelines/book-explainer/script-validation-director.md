# Script Validation Director

Validate the script before any paid TTS or image batch. Count Chinese characters and estimate speech duration using the
approved voice speed; require 18-25 minutes (default 20) with no more than 10% variance from the selected target.
If it fails, return to script for expansion or compression. Record the measured count, rate, and estimate in the stage review.

