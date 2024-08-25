# Adding new plugin

## Goals
- have access to plugin methods via app.method
- have .env config for enabling the plugin

## Steps
- add new plugin code
- add config flag ... to AppConfig
- add plugin to all_plugins dict
  - available_plugins in plugins/__init__.py

# Dev - lib preparation
## To check or set up
- getattr for App that checks all plugins for methods
- Config for app that allows to enable/disable plugins
  - 1) per plugin config flag
  - 2) plugins - config list of str
- [x] is there already all_plugins dict?
  - yes, available_plugins in __init__.py 

## Other necessary features
- [x] add plugin config 
