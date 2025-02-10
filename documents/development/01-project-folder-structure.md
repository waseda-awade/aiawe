# Project Folder Structure

This document provides a brief overview of the main folders in the AiAWE project.

## Core Directories

### `awe_system_ui/`

The main Django application directory containing:

- `static/` - Static files (CSS, JavaScript, fonts)
- `templates/` - HTML templates
- `core/` - Core functionality and utilities
- `contrib/` - Reusable Django components
- `users/` - User management related code

### `vue_frontend/`

The Vue.js frontend application:

- `src/` - Source code for the Vue application
  - `components/` - Reusable Vue components
  - `views/` - Page components
  - `stores/` - State management
  - `assets/` - Static assets (images, styles)
  - `lib/` - Utility functions and configurations

## Documentation & Configuration

### `documents/`

Project documentation:

- `manual/` - User and developer guides
- `reverse-proxy/` - Server setup instructions


### `envs/`

Environment configurations:

- `.local/` - Local development settings
- `.staging/` - Staging settings
- `.production/` - Production settings

## Other Important Directories

### `requirements/`

Python dependencies for the project:

- `base.txt` - Base requirements
- `local.txt` - Local development requirements
- `production.txt` - Production requirements
- `envs.txt` - For development environments

### `compose/`

Docker compose configuration files for different environments:

- `local/` - Local development setup
- `production/` - Production deployment setup

### `locale/`

> [!WARNING] This folder is not used. English is the only language supported.

Internationalization files:

- Translation files for different languages
- Localization configurations

## Development Files

- `.github/` - GitHub workflows and configurations
- `tools/` - Utility scripts for development and deployment
