# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-22
### Added
- Complete rewrite of the documentation suite on MkDocs with Material theme.
- Added comprehensive theoretical explanation of shallow fusion pipeline.
- New standalone code examples for Batch Processing and Parameter Tuning.

### Changed
- Improved memory management in `asr_engine` for long-audio GPU batching.

## [0.9.0] - 2026-02-15
### Added
- Core implementation of the Trigger $\rightarrow$ Candidate $\rightarrow$ Context pipeline.
- Double Metaphone integration for phonetic candidate bounding.
- GPT-2 LM constraint context rescoring.
- Basic CLI for single-file processing.

### Fixed
- Addressed bug where confidence threshold triggering ignored trailing punctuation.
- Fixed an OOM error when scaling to Whisper `large-v3`.
